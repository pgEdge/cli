// FIXME: add environment/config support (user specifies config file, we convert that into a set of env variables)
//

#include <vector>
#include <unordered_map>
#include <string>
#include <iostream>
#include <fstream>
#include <regex>
#include <filesystem>
#include <getopt.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>

#define VERSION_STRING "1.0"

using namespace std;

namespace fs = std::filesystem;

typedef vector<string>  stringList;
typedef unordered_map<string, string> stringMap;

static void      expandSchedule(stringList &tests, const string &schedule);
static void		 addEnvironment(stringList &env, const string &configFileName);
static void		 usage(int argc, char *argv[]);
static bool		 parseArgs(stringList &tests, stringList &environmentVariables, int argc, char *argv[]);
static string	&ltrim(string &s);
static string	&rtrim(string &s);
static string	&trim(string &s);
static void		 reportError(const string &message);
static void		 dumpTests(stringList &tests);
static void		 dumpEnv(stringList &env);
static void		 runTests(stringList &tests);

int main(int argc, char *argv[]);

class Command;
class CommandResult;
class testRunner;
class testContext;

static void
usage(int argc, char *argv[])
{
	cout << argv[0] << endl;
	cout << "  --help     | -h : print this message" << endl;
	cout << "  --version  | -v : display version" << endl;
	cout << "  --schedule | -s <filename> : run tests according to a schedule file" << endl;
	cout << "  --test     | -t <testname> : include given testname in test run" << endl;
	cout << "  --config   | -c <config filename> : create environment from given filename" << endl;
	cout << "  --debug    | -d : emit extra debugging output" << endl;
}

static bool
parseArgs(stringList &tests, stringList &environmentVariables, int argc, char *argv[])
{
	const char short_options[] = "+hvs:t:c:";
	int optchar;
	int optind = 0;
	struct option long_options[] =
	{
		{"help",     no_argument,       NULL, 'h'},
		{"version",  no_argument,       NULL, 'v'},
		{"debug",    no_argument,       NULL, 'd' },
		{"schedule", required_argument, NULL, 's'},
		{"test",     required_argument, NULL, 't'},
		{"config",   required_argument, NULL, 'c'},
		{0,          0,                 0,     0 }
	};
	
	bool debug = false;
	
	while (true)
	{
		optchar = getopt_long(argc, argv, short_options, long_options, &optind);

		if (optchar == -1)
			break;
		
		switch (optchar)
		{
			case 'h':
				usage(argc, argv);
				exit(EXIT_SUCCESS);
				break;

			case 'v':
				cout << VERSION_STRING << endl;
				exit(EXIT_SUCCESS);
				break;

			case 's':
				expandSchedule(tests, optarg);
				break;

			case 't':
				tests.push_back(optarg);
				break;

			case 'c':
				addEnvironment(environmentVariables, optarg);
				break;

			case 'd':
				debug = true;
				break;
				
			default:
				usage(argc, argv);
				exit(EXIT_FAILURE);
				break;
		}
	}

	return debug;
}

////////////////////////////////////////////////////////////////////////////////
// ltrim()
//
//  Removes leading whitespace from given string (modified in-place)

static string &
ltrim(string &s) 
{
    s.erase(s.begin(), find_if(s.begin(), s.end(), not1(ptr_fun<int, int>(isspace))));

    return s;
}

////////////////////////////////////////////////////////////////////////////////
// rtrim()
//
//  Removes trailing whitespace from given string (modified in-place)

static string &
rtrim(string &s)
{
    s.erase(find_if(s.rbegin(), s.rend(), not1(ptr_fun<int, int>(isspace))).base(), s.end());

    return s;
}

////////////////////////////////////////////////////////////////////////////////
// trim()
//
//  Removes leading trailing whitespace from given string (modified in-place)

static  string &
trim(string &s) 
{
    return ltrim(rtrim(s));
}

////////////////////////////////////////////////////////////////////////////////
// expandSchedule()
//
//   Read the given schedule and write each line into the tests stringList

static void
expandSchedule(stringList &tests, const string &schedule)
{
	ifstream infile(schedule);
	string line;

	while(getline(infile, line))
	{
		if (line.find("#") != string::npos)
			line.erase(line.find("#"));

		trim(line);

		if (line.size())
			tests.push_back(line);
	}
}

////////////////////////////////////////////////////////////////////////////////
// addEnvironment()))
//
//   Reads the given configFileName and writes keyword=value pairs into the
//   env stringList. This function builds an environment for child processes

static void
addEnvironment(stringList &env, const string &configFileName)
{
	ifstream infile(configFileName);
	string line;
	stringList result;
	
	while (getline(infile, line))
	{
		if (line.find("#") != string::npos)
			line.erase(line.find("#"));

		trim(line);

		if (line.size())
			env.push_back(line);
	}
}

////////////////////////////////////////////////////////////////////////////////
// reportError()
//
//   Prints the given message to stderr (aka cerr)

static void
reportError(const string &message)
{
	cerr << "ERROR: " << message << endl;
}

////////////////////////////////////////////////////////////////////////////////
// dumpTests()
//
//  DEBUG - prints each test found in the given list of tests

static void
dumpTests(stringList &tests)
{
    for (auto test : tests)
		cout << test << endl;
}

////////////////////////////////////////////////////////////////////////////////
// dumpEnv()
//
//    DEBUG - prints each environment variable in the given stringList

static void
dumpEnv(stringList &env)
{
	for (auto var : env)
		cout << var << endl;
}

////////////////////////////////////////////////////////////////////////////////
// class CommandResult
//
// An object of type CommandResult holds the stdout, stderr, and exit status.
//
// CommandResults are returned by the Command::exec() function.
////////////////////////////////////////////////////////////////////////////////

struct CommandResult
{
	string stdoutString;
	string stderrString;
	int    exitStatus;
};

////////////////////////////////////////////////////////////////////////////////
// class Command
//
//  This class provides a function (exec()) that invokes a test and returns the
//  result of that test in a CommandResult object

class Command
{

public:

	// Execute given command an returns a CommandResult object
	//
	// From https://stackoverflow.com/questions/72687632/how-to-store-command-output-and-exitcode-from-terminal-in-a-variable

	static CommandResult exec(const string &command, const string &testName)
	{
		int stdoutPipe[2], stderrPipe[2];

		pipe(stdoutPipe);
		pipe(stderrPipe);

		pid_t pid = fork();
	
		if (pid == 0)
		{
			// Child process
			close(stdoutPipe[0]);
			close(stderrPipe[0]);

			// Redirect stdout to the write end of the stdout pipe
			dup2(stdoutPipe[1], STDOUT_FILENO);

			// Redirect stderr to the write end of the stderr pipe
			dup2(stderrPipe[1], STDERR_FILENO);

			// Execute the requested program 
			execlp(command.c_str(), command.c_str(), testName.c_str(), (char *) NULL) ;

			cerr << "Failed to execute the program!" << endl;
			exit(1);
		}
		else if (pid > 0)
		{
			// Parent process - Close the write end of the stdout pipe and the write end of the stderr pipe
			close(stdoutPipe[1]);
			close(stderrPipe[1]);

			// Read the output from the child process's stdout
			char	stdoutBuffer[4096];
			ssize_t stdoutBytesRead;
			string	stdoutData;

			while ((stdoutBytesRead = read(stdoutPipe[0], stdoutBuffer, sizeof(stdoutBuffer))) > 0)
				stdoutData += string(stdoutBuffer, stdoutBytesRead);

			// Read the output from the child process's stderr
			char	stderrBuffer[4096];
			ssize_t stderrBytesRead;
			string	stderrData;

			while ((stderrBytesRead = read(stderrPipe[0], stderrBuffer, sizeof(stderrBuffer))) > 0)
				stderrData += string(stderrBuffer, stderrBytesRead);

			close(stdoutPipe[0]);
			close(stderrPipe[0]);

			// Wait for the child process to exit and copy the exit status
			int status;
			waitpid(pid, &status, 0);

			// Print the captured stdout, stderr, and exit status
			return CommandResult {stdoutData, stderrData, WEXITSTATUS(status)};
		}
		else
		{
			cerr << "Failed to fork!" << endl;
			return CommandResult{"", "Failed to fork", EXIT_SUCCESS};
		}
	}
};

////////////////////////////////////////////////////////////////////////////////
// class testRunner
////////////////////////////////////////////////////////////////////////////////

class testRunner
{
public:
	CommandResult exec(const string &cmd, const string &testName);

};

CommandResult
testRunner::exec(const string &cmd, const string &testName)
{
	return Command::exec(cmd, testName);
}

////////////////////////////////////////////////////////////////////////////////
// class testContext
////////////////////////////////////////////////////////////////////////////////

class testContext
{
public:
	testContext(stringList &tests)
		: _tests(tests),
		  _passCount(0),
		  _failCount(0),
		  _errorCount(0)
	{
		// Build a file name from the current date/time - we use
		// the following format: YYYMMDD_hhmmss
		time_t rawtime;
		struct tm *timeinfo;

		time(&rawtime);
		timeinfo = localtime(&rawtime);

		strftime(_logFileName, 80, "%Y%m%d_%H%M%S.log", timeinfo);

		// auto-flush the log file so a user may watch the output
		// in real time using (for example) "tail -F ./latest.log"

		_clog << std::unitbuf;
		_clog.open(_logFileName);

		initRunners();
	}

	~testContext()
	{
		_clog.close();
	}

	void runAll();
	void runTest(const string &test);
	void initRunners();
	bool runRunner(CommandResult &result, const string &command, const string &testName);
	int  getPassCount()  { return _passCount; }
	int  getFailCount()  { return _failCount; }
	int  getErrorCount() { return _errorCount; }

	char _logFileName[80];

private:

	stringList & _tests;
	stringMap    _runners;           // Maps an extension (.py, .pl, ...) to a command
	int          _passCount;
	int          _failCount;
	int          _errorCount;
	ofstream     _clog;
  
	void logTestOutput(const string &test, bool pass, CommandResult &result);
};

void
testContext::initRunners()
{
	_runners[".py"] = "/usr/bin/python";
	_runners[".pl"] = "/usr/bin/perl";
	_runners[".sh"] = "bash %f";
}

void
testContext::runAll()
{
    for (auto test : _tests)
		runTest(test);
}

bool
testContext::runRunner(CommandResult &result, const string &command, const string &testName)
{
	testRunner runner;

	result = runner.exec(command, testName);
	
	return result.exitStatus == 0;
}

void
testContext::logTestOutput(const string &test, bool pass, CommandResult &result)
{
	_clog << "**************************************************" << endl;
	_clog << test << " (" << (pass ? "pass" : "fail") << ")" << endl;
	_clog << "**************************************************" << endl;
	_clog << result.stdoutString << endl;
	_clog << result.stderrString << endl;
}

void
testContext::runTest(const string &test)
{
	// We find the runner command by looking in the _runners array
	// for a key that matches the extension found in test
   
	string extension = test.substr(test.rfind('.'));
	string command(_runners[extension]);

	if (command.empty())
	{
		reportError("cannot find test runner for " + test);
		_errorCount++;
	}
	else
	{
		command = regex_replace(command, regex("%f"), test);

		int dotCount = 60;

		dotCount -= test.size();
		dotCount -= strlen("pass");
			
		cout << test << string(dotCount, '.') << std::flush;

		CommandResult result;
		
		if (runRunner(result, command, test))
		{
			logTestOutput(test, true, result);
			cout << "pass" << endl;
			_passCount++;
		}
		else
		{
			logTestOutput(test, false, result);
			cout << "fail" << endl;
			_failCount++;
		}
	}
}

///////////////////////////////////////////////////////////////////////y/////////

static void
runTests(stringList &tests)
{
	testContext  ctx(tests);

	cout << "Test output can be found in ./latest.log (or ./" << ctx._logFileName << ")" << endl;

	// delete the ./latest.log file and create a symlink between the
	// the log file we just created and ./latest.log
	//
	// the idea here is that latest.log will always point to the most
	// recently created log file
	
	fs::remove("./latest.log");
	fs::create_symlink(ctx._logFileName, "./latest.log");

	ctx.runAll();

	cout << endl;
	cout << "pass:   " << ctx.getPassCount() << endl;
	cout << "fail:   " << ctx.getFailCount() << endl;
	cout << "errors: " << ctx.getErrorCount() << endl;
	cout << endl;
}

int
main(int argc, char *argv[])
{
	stringList environmentVariables;
	stringList tests;
	
	bool debug = parseArgs(tests, environmentVariables, argc, argv);

	if (debug)
	{
		dumpTests(tests);              // for debugging
		dumpEnv(environmentVariables); // for debugging
	}

	runTests(tests);
}

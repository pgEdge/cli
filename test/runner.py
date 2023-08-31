#!/usr/bin/python

import getopt, sys, re
import subprocess, os
from datetime import datetime

global glDebug
glDebug = False

global glLogger
glLogger = ""

################################################################################
#  runners{}
#
#  This dictionary maps a file extension (such as .py or .pl) to the name of
#  an interpeter that can execute the indicated type of script

runners = {
    ".py" : "/usr/bin/python",
    ".pl" : "/usr/bin/perl",
    ".sh" : "bash %f"
}

################################################################################
# expandSchedule()
#
#  Given the name of a schedule file, this function opens the named file, reads
#  each line in that file (ignoring comments) and writes the entries into the
#  result[] array

def expandSchedule(scheduleFileName):
    result = []

    with open(scheduleFileName) as file:
        for line in file:
            line = (line.rstrip()).lstrip()
            line = re.sub('#.*', '', line)
            if line != '':
                result.append(line)
                
    return result

################################################################################
# parseCmdLine()
#
#  Parses the command line and returns an array of test file names. When the
#  caller specifies a schedule name, that file is "expanded" into the tests[]
#  array. When the caller spcifies a test name, that name is added to the tests[]
#  array.  You can intermingle as many schedule names and test names as you like.

def parseCmdLine():

    opts, args = getopt.getopt(sys.argv[1:], "s:t:vdh", ["schedule=", "test=", "version", "debug", "help"])
                  
    tests = []

    for opt, val in opts:
        if opt in["-s", "--schedule"]:
            tests += expandSchedule(val)
        
        elif opt in ["-t", "--test"]:
            tests.append(val)
        
        elif opt in ["-v", "--version"]:
            print("version=3.14")

        elif opt in ["-d", "--debug"]:
            global glDebug
            glDebug = True
            
        elif opt in ["-h", "--help"]:
            print("Usage: " + sys.argv[0] + "  [option] ...")
            print("")
            print(" -s scheduleFileName : execute tests listed in given scheduleFileName")
            print(" -t testFileName     : execute the given test script")
            print(" -v                  : displays version number")
            print(" -h                  : display this usafe information")
            print(" -d                  : print extra information useful for debugging")
            sys.exit(0)
            
    # Now create a log file - the name of the log file is based on the
    # current date and time
            
    now = datetime.now()

    logFileName = now.strftime("%Y%m%d_%H%M%S.log")

    global glLogger
    glLogger = open(logFileName, "w")

    # And create a symbolic link named lastest.log that points to the
    # the logFileName we just created

    if (os.path.exists("./latest.log")):
        os.remove("./latest.log")
        
    os.symlink(logFileName, "./latest.log")

    print("")
    print("Test output can be found in ./latest.log (or ./" + logFileName + ")")
    print("")
    
    return tests

################################################################################
# logTestOutput()
#
#  Writes a test summary (test name, pass/fail status, stdout, stderr) to the
#  current logger.

def logTestOutput(testName, completedProcess):
    global glLogger

    if (completedProcess.returncode == 0):
        status = "pass"
    else:
        status = "fail"

    print("**************************************************", file=glLogger)
    print(testName + " (" + status + ")", file=glLogger)
    print("**************************************************", file=glLogger)
    print(completedProcess.stdout, file=glLogger)
    print(completedProcess.stderr, file=glLogger)

################################################################################
# runTest()
#
#    Runs the specified test, captures the stdout and stderr output and writes
#    that output to the current log file.  If the test program completes and
#    returns a 0, the test is presumed to have passed, otherwise the test is
#    treated as a failure
        
def runTest(testName):

    passCount  = 0
    failCount  = 0
    errorCount = 0
    
    # We find the runner command by looking in the runners array
    # for a key that matches the extension found in testName
    #
    # For example, if testName = t/0050_misc.py, we find the extension
    # (.py) and search for that key in runners[].  The value in that
    # key/value pair will be the name of the python interpreter that we
    # want to use in order to run test script

    extension = testName[testName.rfind('.')::]
    command = runners[extension]

    if (len(command) == 0):
        reportError("cannot find test runner for " + testName)
        errorCount += 1
    else:
        dotCount = 60

        dotCount -= len(testName)
        dotCount -= len("pass")

        print(testName, '.' * dotCount, end="")

        # Run the command and capture the stdout and stderr.  The run() function
        # returns a CompletedProcess object that will contain (at least) the
        # following:
        #   returncode - exit code returned by the child process
        #   stdout     - a string containing all of the stdout written the child
        #   stderr     - a string containing all of the stderr written the child
        #
        # We Use the returncode to decide whether the test passes (exit(0)) or
        # fails (any returncode other than zero).
        #
        # We write stdout and stderr to the current log file

        result = subprocess.run([command, testName], capture_output=True, text=True)

        if (result.returncode == 0):
            logTestOutput(testName, result)
            print("pass")
            passCount += 1
        else:
            logTestOutput(testName, result)
            print("fail")
            failCount += 1

    status = { 'passCount': passCount, 'failCount': failCount, 'errorCount': errorCount}

    return status

################################################################################
# runTests()
#
#    Given a list of test names (testList), this function runs each test and
#    then prints a summary of the test suite

def runTests(testList):

    passCount  = 0
    failCount  = 0
    errorCount = 0
    
    for test in testList:
        result = runTest(test)

        passCount  = passCount + result.get('passCount')
        failCount  = failCount + result.get('failCount')
        errorCount = errorCount + result.get('errorCount')

    print("pass:   " + str(passCount))
    print("fail:   " + str(failCount))
    print("errors: " + str(errorCount))

################################################################################
# main()
#
#  This function is the entry point for runner.py.  We start by parsing the
#  commnd-line arguments, then run each test (found in the testList) and finish
#  up by printing a summary of the test run (pass count, fail count, error count)

def main():
    testList = parseCmdLine()

    global glDebug
    
    if glDebug:
        for test in testList:
            print(test)

    runTests(testList)
         
    print("complete")

    global glLogger
    glLogger.close()
    
if __name__ == "__main__":
    main()

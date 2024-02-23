## Using the Test Harness

### The test harness directory structure in the cli repo

`test` - contains the test harness, and is where you must invoke the tests from.

`test/schedule_files` - contains the schedule files; each schedule file is made up of a set of scripts that set up and tear down a cluster.

`test/t` - contains the test scripts and a file of the python utilities (util_test.py).
Test scripts can be written in either perl (file.pl) or python (file.py) and the file types can be mixed within a schedule.

`test/t/lib` - contains the environment variable file and the perl utility files. Source the environment variable file before running the scripts.

### Prerequisites on a clean Rocky 9 VM to run the test harness

Disable `firewalld`
    You can use the following command to disable firewalld: 
    `sudo systemctl stop firewalld`

Configure passwordless `sudo`
    To configure passwordless sudo, edit the `/etc/sudoers` file.  Locate the line that contains i`includedir /etc/sudoers.d`; add a line below that line that specifies: `your_user_name ALL=(ALL) NOPASSWD:ALL`

Configure passwordless `ssh`
    To configure passwordless ssh, execute the following commands:
    ```sh
    ssh-keygen -t rsa
    cd ~/.ssh
    cat id_rsa.pub >> authorized_keys
    chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
    ```

Disable `SELinux`
    To disable SELinux, edit the `/etc/sysconfig/selinux` file, setting `SELINUX=disabled`; then reboot your system.

`yum update`

`cd ~/`
`mkdir work`
`cd work`
`yum install git`

Clone the cli git repo into `work`:

`git clone https://github.com/pgEdge/cli.git`

Move into the `test` directory:

`cd cli/test`

Ensure that any prerequisites are met:

`sudo yum install perl`
`sudo yum install perl-cpan`
`sudo dnf install perl-File-Which`
`sudo dnf install perl-Try-Tiny perl-JSON perl-List-MoreUtils perl-DBD-Pg`
`sudo dnf install python3`
`sudo yum install pip`
`pip install psycopg`
`pip install python-dotenv`

Review the environment variables in the `t/lib/config.env` file and make any adjustments required; then source the environment variables:

`source t/lib/config.env`

Then you're ready to run a test.

### Invoking the test harness (`runner.py`)

Invoke the following commands from the `test` directory.

Use the following command to invoke a schedule:
`runner.py -s schedule_files/schedule_file_name`

Use the following command to invoke a test script:
`runner.py -t t/script_name`

There is also a help file for the test script:
`runner.py --help`

To see a list of the environment variables used, invoke the following command:
`perl t/lib/variables.pl`

As each test script executes (individually or through a schedule), it returns a `pass` or `fail` on the command line. The result of each file executed, along with the commands invoked and detailed log are also written to a timestamped logfile (symlinked to `latest.log`) in the `test` directory.





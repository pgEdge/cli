# PGEDGE NodeCtl Project


## Creating a build environment on Rocky Linux 8 or 9

### 1.) Create a directory named ~/dev

### 2.) Clone the nodectl repo into ~/dev

### 3.) cd into ~/dev/nodectl/devel/setup

### 4.) Run ./setupInitial.sh to configure OS environment 
          (On EL8/9 it will configure for building binaries. On Debian based
           systems it will only do the setup for working with python3 devel)

### 5.) Configure your ~/.aws/config credentials for access to s3://pgedge-upstream/IN

### 6.) Source your bash profile with the command: source ~/.bashrc

### 7.) run ./setupBLD-IN.sh to pull in the IN directory from S3

### 8.) (Only if you are building C binaries): Setup Src builds for PGBIN from devel/pgbin/build

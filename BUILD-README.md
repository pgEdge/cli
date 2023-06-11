# PGEDGE NodeCtl Project


## Creating a build environment on el9

### 1.) Create a directory named ~/dev

### 2.) Clone the nodectl repo into ~/dev

### 3.) cd into ~/dev/nodectl/devel/setup

### 4.) Run ./2a-initial.sh to configure OS environment 
          (On el9 it will configure for building binaries.)

### 5.) Configure your ~/.aws/config credentials for access to s3://pgedge-upstream/IN

### 6.) Source your bash profile with the command: source ~/.bashrc

### 7.) run ./2b-BLD-IN.sh to pull in the IN directory from S3

### 8.) (Only if you are building C binaries): Setup Src builds for PGBIN from devel/pgbin/build

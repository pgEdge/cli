# PGEDGE NodeCtl Project


## Creating a build environment on el8

### 1.) Create a directory named ~/dev

### 2.) Clone the nodectl repo into ~/dev

### 3.) cd into ~/dev/nodectl

### 4.) Run ./setupInitial.sh to configure OS environment (on EL8 it will configure you for building binaries)

### 5.) Configure your ~/.aws/config credentials for access to s3://pgedge-upstream

### 6.) Source your bash profile with the command: source ~/.bashrc (or source ~/.bash_profile)

### 7.) run ./setupBLD-IN.sh to pull in the IN directory from S3

### 8.) (Only if you are building C binaries on EL8): Setup Src builds for PGBIN from devel/pgbin/build

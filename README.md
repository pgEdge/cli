# The pgEdge Command Line Interface

This repo contains the code for the pgEdge Command Line Interface (CLI); for usage information, see the pgEdge [online documentation](https://docs.pgedge.com/).  You can also review the [release notes](https://docs.pgedge.com/platform/pgedge_rel_notes) to learn more about our recent enhancements and fixes.

## Getting Started with pgEdge

To learn more about pgEdge and sign up for a pgEdge [Cloud](https://www.pgedge.com/products/pgedge-cloud) or [Platform](https://www.pgedge.com/products/pgedge-platform) account, visit the [pgEdge website](https://www.pgedge.com/).

### Creating a Development Environment

1.) Clone this repository

2.) cd cli/devel/setup

3.) run `./10-toolset.sh` through `30-bashrc.sh`

4.) source ~/.bashrc

5.) run `40-awscli.sh` to install aws in virtual env

6.) configure your ~/.aws/config credentials

7.) run `1d-pull-IN.sh` to retrieve REPO files

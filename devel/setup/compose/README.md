# Compose Setup for pgEdge Development

This setup allows you to build and run a multi-node pgEdge setup using Docker Compose. Below are the instructions and available arguments to customize your setup.

## Prerequisites

- Docker
- Docker Compose

## Files

- `docker-compose.yaml`: Defines the services and configurations for the Docker Compose setup.
- `Makefile`: Contains the commands to manage the Docker Compose setup.
- `proxy_server.py`: Contains the code which enables the repo proxy container
- `Dockerfile.node.<os>`: Dockerfiles for each supported operating system
- `Dockerfile.repo`: Dockerfile for the repo proxy server

## Usage

### Starting the Environment

To start the environment, run the following command:

```sh
make compose-up
```

This will build and start the services defined in the `docker-compose.yaml` file in Docker.

### Stopping the Environment

To stop the environment, run:

```sh
make compose-down
```

### Accessing the build container

The build container is where you make code changes and build packages.

To access the build container, run:

```sh
make exec-build
```

### Configuring the build container

The build container is setup the same as a standard development environment outside of Docker.

Required credentials (AWS, Git) are not configured on the build container.

You must configure these after starting the environment, and run `50-pull-IN.sh` if needed for your work.

### Understanding the repo container

The repo container serves as a local http server inside the network for fetching CLI packages.

It's setup as a proxy, where the default behavior is to serve a local package if it exists.

If a local package does not exist, it will fallback to a package available in the chosen REPO.

The chosen repo corresponds to the URL that you choose to configure:

- http://repo:8000/download corresponds with https://pgedge-download.s3.amazonaws.com/REPO
- http://repo:8000/upstream corresponds with https://pgedge-upstream.s3.amazonaws.com/REPO
- http://repo:8000/devel corresponds with https://pgedge-devel.s3.amazonaws.com/REPO

The `out` directory within the build container is mounted in the repo container to enable this setup.

You can monitor the behavior of the proxy via `docker logs pgedge-repo-1`

### Building the CLI packages

A common workflow in this setup is to leverage already built packages to increase development velocity.

If you are only working on the CLI code, you can typically just build that component:

```
source env.sh
./build.sh -X posix -c $bundle-cli -N $hubV
```

From there, utilize the node containers to test out your changes. Other packages will be pulled from the configured REPO.

### Accessing node containers

node containers are used to test changes you have developed within the build container.

You can access individual node containers using the following commands:

```sh
make exec-n1
make exec-n2
# ... up to make exec-n10
```

Once connected, you can setup the pgEdge CLI using the repo container:

```
wget $REPO/install.py
python3 install.py
cd pgedge
```

## Networking

All containers in the compose setup are attached to the same docker bridge network. This makes it easier to connect across nodes using hostnames.

- `repo` and `build` can be accessed directly by these hostnames since there are no replicas
- nodes can be accessed via hostnames prefixed with the compose name `pgedge-node-1`

## Available arguments

You can customize the setup using the following arguments:

- `NUM_NODES`: Number of node containers to deploy. Default is `2`.
- `OS_ARCH`: The OS architecture for the node containers. Default is `linux/$(uname -m)`.
- `OS_FLAVOR`: The OS flavor for the node containers. Supported values are `rocky95` and `ubuntu2204`. Default is `rocky95`.
- `BUILD_OS_FLAVOR`: The OS architecture for the build container. Default is `linux/$(uname -m)`.
- `BUILD_OS_ARCH`: The OS flavor for the build container. Supported values are `rocky95` and `rocky810`. Default is `rocky95`.
- `REPO`: The repository URL for downloading dependencies. Default is `http://repo:8000/download`.

### Example

To start the environment with 3 nodes and using `ubuntu2204` as the OS flavo, with the REPO set to upstream, run:

```sh
REPO=http://repo:8000/upstream NUM_NODES=3 OS_FLAVOR=ubuntu2204 make compose-up
```

## Notes

- Passwordless SSH is setup between the nodes to make it easier to test the cluster module
- The `PGBACKREST_REPO1_CIPHER_PASS` environment variable is set to `supersecret` by default. Change it as needed.

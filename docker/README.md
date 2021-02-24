# Docker images

## Overview

This directory contains multiple Dockerfiles for building multiple docker images.
These docker images use the package found in this repository.
They also define gRPC services to provide interfaces for specific tasks.

## Images

### Base

#### Overview

This docker image creates a base image the package found in this repository.
This package installs an API to access the OpenPose network.
It also installs the python gRPC package.

The generated image can be further extended with specific purposes that use the installed package, such as python scripts to call the OpenPose API or running gRPC servers.

#### Usage

In order to use this docker image execute the following steps:

 * Build the image:

 ```
 $ docker build --tag sipgisr/open-pose-grpc:base-latest -f docker/base.Dockerfile .
 ```

 * Run a container with the image:

 ```
 $ docker run --rm -it sipgisr/open-pose-grpc:base-latest
 ```

### Key Points Estimation

#### Overview

This image offers a service for estimating key points for human poses in a given image.

#### Usage

In order to use this docker image execute the following steps:

 * Build the image:

 ```
 $ docker build --tag sipgisr/open-pose-grpc:kp-estimation-latest -f docker/kp-estimation.Dockerfile .
 ```

 * Run a container with the image *(The port to publish can change, but the server expects port 8061)*:

 ```
 $ docker run --rm -it -p 8061:8061 sipgisr/open-pose-grpc:kp-estimation-latest
 ```
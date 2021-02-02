# Base image for building gRPC services with open pose
FROM ubuntu:latest AS builder

RUN apt-get update && \
    apt-get install -y git && \
    git clone --depth 1 https://github.com/DuarteMRAlves/open-pose-grpc-service.git open-pose-grpc

FROM tensorflow/tensorflow:1.14.0-py3

RUN apt-get update && \
    pip install --upgrade pip && \ 
    apt-get install --no-install-recommends -y \
        libsm6 \
        libxext6 \
        libxrender-dev && \
    # Install headless version of opencv-python for server usage
    # Does not install graphical modules
    # See https://github.com/opencv/opencv-python#installation-and-usage
    pip install opencv-python-headless Cython grpcio==1.21.1 grpcio-reflection==1.21.1 protobuf==3.8.0 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /open-pose-grpc/ /open-pose-grpc/
WORKDIR /open-pose-grpc/

# Install local package
RUN pip install .

# Remove package sources
WORKDIR /
RUN rm -rf /open-pose-grpc

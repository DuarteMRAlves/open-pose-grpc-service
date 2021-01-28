# Dockerfile for service that receives images
# and uses open pose to estimate human poses
FROM open-pose-grpc-base:latest

COPY run.py /open-pose-grpc/run.py
COPY images /open-pose-grpc/images/
WORKDIR /open-pose-grpc/

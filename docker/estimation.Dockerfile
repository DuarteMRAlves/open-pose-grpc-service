# Dockerfile for service that receives images
# and uses open pose to estimate human poses

ARG WORKSPACE=/workspace
ARG PROTO_FILE=open_pose_estimation.proto

# Use builder to generate proto .py files
FROM python:3.6.12-slim-buster AS builder
# Renew build args
ARG WORKSPACE
ARG PROTO_FILE

ARG PROTOS_FOLDER_DIR=protos

RUN pip install grpcio==1.21.1 grpcio-tools==1.21.1 protobuf==3.8.0

COPY ${PROTOS_FOLDER_DIR} ${WORKSPACE}/
WORKDIR ${WORKSPACE}/

# Compile proto file and remove it
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ${PROTO_FILE}


# Build the final image
FROM open-pose-grpc-base:latest
# Renew build args
ARG WORKSPACE
ARG PROTO_FILE

ARG USER=runner
ARG GROUP=runner-group
ARG GRPC_SERVICES_DIR=grpc_services

# Define PORT environment variable for the server according to AI4EU specifications
ENV PORT=8061

RUN echo ${USER}:${GROUP} with workdir ${WORKSPACE}

# Add non-privileged user to execute the container
RUN addgroup --system ${GROUP} && \
    adduser --system --no-create-home --ingroup ${GROUP} ${USER} && \
    mkdir ${WORKSPACE} && \
    chown -R ${USER}:${GROUP} ${WORKSPACE}


# COPY .proto file to root to meet ai4eu specifications
COPY --from=builder --chown=${USER}:${GROUP} ${WORKSPACE}/${PROTO_FILE} /

# Copy generated code to workspace
COPY --from=builder --chown=${USER}:${GROUP} ${WORKSPACE}/*.py ${WORKSPACE}/
# Copy code
COPY ${GRPC_SERVICES_DIR} ${WORKSPACE}/

# Change user
USER ${USER}

EXPOSE ${PORT}

WORKDIR ${WORKSPACE}/

CMD ["python", "estimation_server.py"]

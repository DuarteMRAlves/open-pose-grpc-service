# Dockerfile for service that receives images
# and uses open pose to estimate human poses

ARG WORKDIR=/open-pose-grpc

# Use builder to generate proto .py files
FROM python:3.6.12-slim-buster AS builder
# Renew workdir arg
ARG WORKDIR

ARG PROTOS_FOLDER_DIR=protos

RUN pip install grpcio==1.21.1 grpcio-tools==1.21.1 protobuf==3.8.0

COPY ${PROTOS_FOLDER_DIR} ${WORKDIR}/
WORKDIR ${WORKDIR}/

# Compile proto file and remove it
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. open_pose_estimation.proto && \
    rm open_pose_estimation.proto

# Build the final image
FROM open-pose-grpc-base:latest
# Renew workdir arg
ARG WORKDIR

ARG USER=runner
ARG GROUP=runner-group
ARG GRPC_SERVICES_DIR=grpc_services

RUN echo ${USER}:${GROUP} with workdir ${WORKDIR}

# Add non-privileged user to execute the container
RUN addgroup --system ${GROUP} && \
    adduser --system --no-create-home --ingroup ${GROUP} ${USER}

# Copy proto py files
COPY --from=builder --chown=${USER}:${GROUP} ${WORKDIR}/ ${WORKDIR}/
# Copy code
COPY ${GRPC_SERVICES_DIR} ${WORKDIR}/

# Change user
USER ${USER}

WORKDIR ${WORKDIR}/

CMD ["python", "estimation_server.py"]

import argparse
import cv2
import concurrent.futures as futures
import grpc
import logging
import numpy as np
import open_pose_estimation_pb2_grpc as pose_grpc
import open_pose_estimation_pb2 as pose_pb2
import os
import tf_pose
import time


_PORT_ENV_VAR = 'PORT'
_DEFAULT_PORT = 50051


# Model to use
_MODEL = 'mobilenet_thin'

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class PoseEstimationService(pose_grpc.OpenPoseEstimatorServicer):

    def __init__(self):
        # Use default width and height
        self.__estimator = tf_pose.get_estimator(_MODEL)

    def estimate(self, request: 'pose_pb2.Image', context: 'grpc.ServicerContext'):
        """
        Handle an estimate request
        Args:
            request: request with the image bytes to use
            context: context of the call
        Returns:
            a message with the key-points of the detected poses
        """

        # Preprocess image
        img_bytes = request.data
        img_array = np.frombuffer(img_bytes, np.uint8)
        img_np = cv2.imdecode(img_array, -1)
        # Infer poses
        poses = self.__estimator.inference(
            img_np,
            resize_to_default=True,
            upsample_size=4.0)
        # Build response
        return self.__build_detected_poses(poses)

    @staticmethod
    def __build_detected_poses(poses):
        return pose_pb2.DetectedPoses(
            poses=map(
                PoseEstimationService.__build_pose,
                poses))

    @staticmethod
    def __build_pose(pose):
        return pose_pb2.Pose(
            key_points=map(
                PoseEstimationService.__build_key_point,
                pose.body_parts.values()))

    @staticmethod
    def __build_key_point(body_part):
        return pose_pb2.KeyPoint(
            index=body_part.part_idx,
            x=body_part.x,
            y=body_part.y,
            score=body_part.score)


def get_port():
    """
    Parses the port where the server should listen
    Exists the program if the environment variable
    is not an int or the value is not positive
    Returns:
        the port where the server should listen
    """
    try:
        server_port = int(os.getenv(_PORT_ENV_VAR, _DEFAULT_PORT))
        if server_port <= 0:
            logging.error('Port should be greater than 0')
            exit(1)
        return server_port
    except ValueError:
        logging.exception('Unable to parse port')
        exit(1)


def parse_args():
    """
    Parse the command line arguments
    Returns:
        An object with the values for the received arguments
    """

    def port_type(x):
        if not isinstance(x, int) or x <= 0:
            raise argparse.ArgumentTypeError('Port must be positive integer')
        return x

    parser = argparse.ArgumentParser(description='Open Pose Representation gRPC Service')
    parser.add_argument(
        '--port',
        default=50051,
        # Port should be positive integer
        type=port_type,
        help='POrt where the server should listen')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig()
    server = grpc.server(futures.ThreadPoolExecutor())
    pose_grpc.add_OpenPoseEstimatorServicer_to_server(
        PoseEstimationService(),
        server)
    port = get_port()
    target = f'[::]:{port}'
    server.add_insecure_port(target)
    server.start()
    print(f'Server started at {target}')
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

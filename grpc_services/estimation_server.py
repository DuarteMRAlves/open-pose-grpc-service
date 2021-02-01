import cv2
import concurrent.futures as futures
import grpc
import logging
import numpy as np
import open_pose_estimation_pb2_grpc as pose_grpc
import open_pose_estimation_pb2 as pose_pb2
import tf_pose
import time


# Model to use
_MODEL = 'mobilenet_thin'

_ADDRESS = '[::]:50051'

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



if __name__ == '__main__':
    logging.basicConfig()
    server = grpc.server(futures.ThreadPoolExecutor())
    pose_grpc.add_OpenPoseEstimatorServicer_to_server(
        PoseEstimationService(),
        server)
    server.add_insecure_port(_ADDRESS)
    server.start()
    logging.getLogger().info("Server started")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

# Test for the estimation of a single image key-points

import argparse
import grpc
import matplotlib.pyplot as plt
import open_pose_estimation_pb2 as pose_estimation
import open_pose_estimation_pb2_grpc as pose_estimation_grpc
import PIL.Image as PIL_image


# Pairs for the connections between key point indices.
# The last two are suggested in COCO_BODY_PARTS but are not
# in the display skeleton and make no sense.
_PAIRS = [
    (1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9), (9, 10), (1, 11),
    (11, 12), (12, 13), (1, 0), (0, 14), (14, 16), (0, 15), (15, 17),  # (2, 16), (5, 17)
]


def estimate_image(stub, image_path):
    print(f'Estimating image: \'{image_path}\'')
    with open(image_path, 'rb') as fp:
        image_bytes = fp.read()
    request = pose_estimation.Image(data=image_bytes)
    return stub.estimate(request)


def display_pose(ax, pose, img_width, img_height):
    key_points = {}
    x = []
    y = []
    for point in pose.key_points:
        key_points[point.index] = (point.x, point.y)
        x.append(point.x * img_width)
        y.append(point.y * img_height)
    ax.scatter(x, y, s=5)
    for kp1, kp2 in _PAIRS:
        if kp1 in key_points and kp2 in key_points:
            x_values = [
                key_points[kp1][0] * img_width,
                key_points[kp2][0] * img_width
            ]
            y_values = [
                key_points[kp1][1] * img_height,
                key_points[kp2][1] * img_height
            ]
            ax.plot(x_values, y_values)


def display_poses(image_path, detected_poses):
    img = PIL_image.open(image_path)
    width = img.width
    height = img.height
    ax = plt.gca()
    ax.imshow(img)
    for pose in detected_poses.poses:
        display_pose(ax, pose, width, height)
    plt.show()


def parse_args():
    """
    Parse arguments for test setup
    Returns: The arguments for the test
    """
    parser = argparse.ArgumentParser(description='Test for OpenPose gRPC Service')
    parser.add_argument(
        'image',
        help='Path to the image to send to the server')
    parser.add_argument(
        '--target',
        metavar='target',
        default='localhost:8061',
        help='Location of the tested server (defaults to localhost:8061)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    target = args.target
    image_path = args.image
    with grpc.insecure_channel(target) as channel:
        estimator_stub = pose_estimation_grpc.OpenPoseEstimatorStub(channel)
        try:
            response = estimate_image(estimator_stub, image_path)
            display_poses(image_path, response)
        except grpc.RpcError as rpc_error:
            print('An error has occurred:')
            print(f'  Error Code: {rpc_error.code()}')
            print(f'  Details: {rpc_error.details()}')

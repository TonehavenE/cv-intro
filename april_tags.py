from dt_apriltags import Detector
import numpy as np
import cv2
from pid import *

def get_tags(img) -> list:
    """Gets a list of tags from an image.

    Args:
        img: the image, in grayscale

    Returns:
        list: the list of tags found in the image
    """
    cameraMatrix = np.array([1060.71, 0, 960, 0, 1060.71, 540, 0, 0, 1]).reshape((3, 3))

    camera_params = (
        cameraMatrix[0, 0],
        cameraMatrix[1, 1],
        cameraMatrix[0, 2],
        cameraMatrix[1, 2],
    )
    at_detector = Detector(
        families="tag36h11",
        nthreads=1,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0,
    )

    tags = at_detector.detect(img, True, camera_params=camera_params, tag_size=True)
    return tags


def get_positions(tags: list) -> list[tuple[float, float, int]]:
    """A representation of the tag using only the pixel coordinates.

    Args:
        tags (list): the list of tags to process

    Returns:
        list[tuple[float, float, int]]: the list of tags, each defined as [x, y, tag_id]
    """
    return [[tag.center[0], tag.center[1], tag.tag_id] for tag in tags]


def error_relative_to_center(
    centers: list[tuple[float, float, int]], width: int, height: int
) -> list[tuple[float, float, int]]:
    """The error relative to the center of the image. Used for PID.

    Args:
        centers (list[tuple[float, float, int]]): the list of tags, typically the output of get_positions
        width (int): the width of the image
        height (int): the height of the image

    Returns:
        list[tuple[float, float, int]]: the list of error values for each tag
    """
    x_center = height / 2
    y_center = width / 2
    return [
        [center[0] - x_center, y_center - center[1], center[2]] for center in centers
    ]


def output_from_tags(errors, horizontal_pid: PID, vertical_pid: PID) -> tuple[list[float], list[float]]:
    horizontal_output = [horizontal_pid.update(error[0]) for error in errors]
    vertical_output = [vertical_pid.update(error[1]) for error in errors]
    return (horizontal_output, vertical_output)

def draw_outputs(img, outputs: tuple[list[float], list[float]], tags):
    for i in range(len(outputs) - 1):
        tag = tags[i]
        horizontal = outputs[0][i]
        vertical = outputs[1][i]
        cv2.putText(
            img,
            f"Horizontal: {horizontal * 100:.2f}%",
            org=(int(tag.corners[0][0]), int(tag.corners[0][1])),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 255, 0),
        )
        cv2.putText(
            img,
            f"Vertical: {vertical * 100:.2f}%",
            org=(int(tag.corners[3][0]), int(tag.corners[3][1])),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 255, 0),
        )
    return img


def render_tags(tags, img):
    """Renders a list of tags into the image.

    Args:
        tags (list[tag]): the list of tags to render
        img (_type_): the image to render tags on

    Returns:
        img: the image with tags drawn onto it
    """
    for tag in tags:
        for idx in range(len(tag.corners)):
            cv2.line(
                img,
                tuple(tag.corners[idx - 1, :].astype(int)),
                tuple(tag.corners[idx, :].astype(int)),
                (0, 255, 0),
                thickness=10,
            )

    return img

from multiprocessing import Process

from lane_detection import *
from lane_following import *
from pid import *


def process_frame(frame, lateral_pid, longitudinal_pid, yaw_pid):
    """Applies a sequence of image filtering and processing to suggest PID movements to center the lane.

    ### Parameters
        frame: the frame to process/render
        lateral_pid (PID): the horizontal PID control object
        longitudinal_pid (PID): the forward/backward PID control object
        yaw_pid (PID): the yaw PID control object

    ### Returns
        (float, float, float): the percent outputs for each of longitudinal, lateral, and yaw
    """
    lateral = 0
    longitudinal = 0
    yaw = 0
    # Process image
    sliced = split(frame)
    height = sliced.shape[0]
    width = sliced.shape[1]
    gray = to_gray(sliced)
    blurred = to_blurred(gray)
    bw = to_bw(blurred)

    # Edge/line detection
    edges = find_edges(bw)
    lines = find_lines(edges)
    if len(lines) > 1:
        grouped_lines = group_lines(
            lines, height, slope_tolerance=0.1, x_intercept_tolerance=50
        )  # group lines
        merged_lines = merge_lines(
            grouped_lines, height, width
        )  # merge groups of lines

        # Lane Detection
        lanes = detect_lanes(bw, merged_lines, 500, 200, 10)

        # Lane picking
        center_lines = merge_lane_lines(lanes, height)  # find the center of each lane
        center_line = pick_center_line(center_lines, width)  # find the closest lane
        (longitudinal_error, lateral_error, yaw_error) = error_from_line(
            center_line, width
        )
        
        longitudinal = longitudinal_pid(longitudinal_error)
        lateral = lateral_pid(lateral_error)
        yaw = yaw_pid(yaw_error)

    return (longitudinal, lateral, yaw)

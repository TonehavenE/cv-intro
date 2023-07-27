import numpy as np


def get_lane_center(lanes):
    """Get the center slope and x-intercept of the line closest to the center"""
    slopes = []
    x_intercepts = []

    # Find the mean x-intercept and slope of each lane
    for lane in lanes:
        (line1, line2) = (lane[0], lane[1])
        x_intercepts.append((line1.x_intercept + line2.x_intercept) / 2)
        slopes.append((line1.slope + line2.slope) / 2)

    # Find the midpoint of ALL the lanes
    lanes_midpoint = (min(x_intercepts) + max(x_intercepts)) / 2
    # Find the index of the x-intercept that is closest to lanes_midpoint
    x_array = np.asarray(x_intercepts)
    index = (np.abs(x_array - lanes_midpoint)).argmin()
    return (slopes[index], x_intercepts[index])


def recommend_direction(x_intercept, slope, width=1920) -> str:
    """Recommend a direction for the AUV to travel in.

    Args:
        x_intercept (_type_): the x-intercept
        slope (_type_): the slope of the line
        width (int, optional): the width of the image. Defaults to 1920.

    Returns:
        str: the string recommending the direction
    """
    forward_tol = 200
    mid = width / 2
    mid_left = mid - forward_tol
    mid_right = mid + forward_tol
    print(f"Center x_intercept: {x_intercept = }")

    if x_intercept > mid_right:
        # the lane center is right of the middle,
        strafe_direction = "right"

    elif x_intercept < mid_left:
        # the lane center is left of the middle
        strafe_direction = "left"

    else:
        # the lane center is in the middle region
        strafe_direction = "forward"
    
    if 1/slope > 0:
        print("turn left")
    if 1/slope < 0:
        print("turn right")

    return strafe_direction

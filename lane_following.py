import lane_detection
import numpy as np
def get_lane_center(lanes):
    lane_slopes = []
    for lane in lanes:
        lines = [lane[0], lane[1]]
        (slopes, x_intercepts) = lane_detection.get_slopes_intercepts(lines)
        lane_slopes.append(np.mean(slopes))


## check if x1 and x2 has a dark spot between them
# if the two slopes are almost opposites, then we have a centered slope
# if they are off to the side, then look to see if the slopes are similar and the x-intercepts are similar. Also check that they are on the same side of the picture

# to find center, calculate midpoint
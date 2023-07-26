"""
Detect lines/lanes
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
from sklearn.cluster import DBSCAN

class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.slope = self.calculate_slope()
        self.x_intercept = self.calculate_x_intercept()

    def calculate_slope(self):
        if self.x1 == self.x2:
            return None
        else:
            return (self.y2 - self.y1) / (self.x2 - self.x1)
        
    def calculate_x_intercept(self):
        if self.y1 == self.y2:
            return None
        else:
            return ((self.slope * self.x1) - self.y1) / self.slope
        
    def get_points(self):
        return [self.x1, self.y1, self.x2, self.y2]
        
def detect_lines(
    img, threshold1=50, threshold2=150, apertureSize=3, minLineLength=100, maxLineGap=10
):
    """Takes an image and parameters to detect lines.

    Args:
        img (result of cv2.imread()): the image to process
        threshold1 (int, optional): the first threshold for the Canny edge detector. Defaults to 50.
        threshold2 (int, optional): the second threshold for the Canny edge detector. Defaults to 150.
        apertureSize (int, optional): the aperture size for the Sobel operator. Defaults to 3.
        minLineLength (int, optional): the minimum length of a line. Defaults to 100.
        maxLineGap (int, optional): the maximum gap between two points to be considered in the same line. Defaults to 10.

    Returns:
        the list of lines (list)
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grayscale
    edges = cv2.Canny(
        gray, threshold1, threshold2, apertureSize=apertureSize
    )  # detect edges
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        100,
        minLineLength=minLineLength,
        maxLineGap=maxLineGap,
    )  # detect lines
    line_objs = [Line(line[0][0], line[0][1],line[0][2],line[0][3]) for line in lines]
    return line_objs


def draw_lines(img, lines, color=(0, 255, 0)):
    for line in lines:
        cv2.line(img, (line.x1, line.y1), (line.x2, line.y2), color, 10)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def get_slopes_intercepts(lines):
    slopes = []
    intercepts = []
    for line in lines:
        slopes.append(line.slope)
        intercepts.append((line.x_intercept, 0))
    return (slopes, intercepts)


def merge_colinear_lines(lines):
    """
    Attempts to merge colinear lines.
    """
    (slopes, _) = get_slopes_intercepts(lines)
    slopes = np.array(slopes).reshape(-1, 1)  # convert slopes to a 2d array

    # DBSCAN clustering to group colinear lines
    # `eps` is the maximum distance between two samples for them to be part of the same cluster
    # `min_samples` is the minimum number of samples for something to become its own cluster
    dbscan = DBSCAN(eps=0.1, min_samples=2)
    labels = dbscan.fit_predict(slopes)  # labels is a list of clusters, basically

    # Group lines based on the cluster labels
    grouped_lines = {}
    for idx, line in enumerate(lines):
        label = labels[idx]
        if label not in grouped_lines:
            grouped_lines[label] = []
        grouped_lines[label].append(line)

    # Calculate the average slope for each cluster
    merged_lines = []
    for label, cluster_lines in grouped_lines.items():
        # (slopes, _) = get_slopes_intercepts(cluster_lines)
        # average_slope = np.mean(slopes)
        merged_lines.append(cluster_lines.get_points())

    return merged_lines


def detect_lanes(lines):
    lanes = []
    lines.sort(key=lambda x: x.x_intercept)

    for i, line1 in enumerate(lines[:-1]):
        line2 = lines[i + 1]
        if math.isclose(line1.slope, -1 * lines2.slope):


    for i, (intercept, line1) in enumerate(intercepts_and_lines[:-1]):
        line2 = intercepts_and_lines[i + 1]
        if math.isclose(line1.slope, line2.slope)

    # first compare the second line to the first and third.
    # if it closer to the first, then make that a lane. Then, each subsuquent pair, 3rd and 4th, 5th and 6th
    # If it is closer to the third, then make that a lane.
    # find the first lane
    if len(intercepts_and_lines) >= 3:
        (intercept, line) = intercepts_and_lines[1]
        gap1 = abs(intercept - intercepts_and_lines[0][0])
        gap2 = abs(intercepts_and_lines[2][0] - intercept)
        if gap1 > gap2:
            lanes.append((intercepts_and_lines[0][1], line))
            start_index = 2
        else:
            lanes.append((line, intercepts_and_lines[2][1]))
            start_index = 3
    for i, (intercept, line) in enumerate(intercepts_and_lines[start_index:-1]):
        lanes.append((line, intercepts_and_lines[i + 1][1]))

    return lanes


def draw_lanes(img, lanes):
    lines = []
    for lane in lanes:
        for line in lane:
            lines.append(line)
    return draw_lines(img, lines)

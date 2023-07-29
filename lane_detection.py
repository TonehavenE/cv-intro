"""
Detect lines/lanes

First, let's define the target workflow:
You are given a frame, which is an image from the AUV of the pool.
The image can be read using cv2.imread
"""
import cv2
import numpy as np
import math
import lane_following
from random import randrange
from sklearn.cluster import DBSCAN


class Line:
    img_height = 1080

    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        self.slope = self.calculate_slope()
        self.x_intercept = self.calculate_x_intercept()
        self.line = np.vectorize(self.line_eq)
        self.paired = False

    def calculate_slope(self) -> float:
        if self.x1 == self.x2:
            return np.power(10, 10)
        else:
            return (self.y2 - self.y1) / (self.x2 - self.x1)

    def calculate_x_intercept(self) -> float:
        if self.y1 == self.y2:
            return np.inf
        else:
            # return ((self.slope * self.x1) - self.y1) / self.slope
            return round(((self.img_height - self.y1) / self.slope) + self.x1, 0)

    def get_points(self) -> list[int, int, int, int]:
        return [self.x1, self.y1, self.x2, self.y2]

    def line_eq(self, X):
        return self.slope * (X - self.x1) + self.y1

    def is_paired(self):
        return self.paired


def detect_lines(
    img, threshold1=50, threshold2=150, apertureSize=3, minLineLength=100, maxLineGap=10
) -> list[Line]:
    """Takes an image and parameters to detect lines.

    Args:
        img (result of cv2.imread()): the image to process
        threshold1 (int, optional): the first threshold for the Canny edge detector. Defaults to 50.
        threshold2 (int, optional): the second thlane_detection.pyreshold for the Canny edge detector. Defaults to 150.
        apertureSize (int, optional): the aperture size for the Sobel operator. Defaults to 3.
        minLineLength (int, optional): the minimum length of a line. Defaults to 100.
        maxLineGap (int, optional): the maximum gap between two points to be considered in the same line. Defaults to 10.

    Returns:
        the list of lines (list)
    """
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grayscale
    blurred_img = cv2.GaussianBlur(img, (13, 13), 100)
    edges = cv2.Canny(
        blurred_img, threshold1, threshold2, apertureSize=apertureSize
    )  # detect edges
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=minLineLength,
        maxLineGap=maxLineGap,
    )  # detect lines
    line_objs = [Line(line[0][0], line[0][1], line[0][2], line[0][3]) for line in lines]
    return line_objs


def draw_lines(
    img, lines: list[Line], color: tuple[int, int, int] = (0, 255, 0), random=False
):
    to_draw = img.copy()
    for line in lines:
        if random:
            color = (randrange(127, 255), randrange(127, 255), randrange(127, 255))
        cv2.line(to_draw, (line.x1, line.y1), (line.x2, line.y2), color, 3)
    return to_draw


def get_slopes_intercepts(lines: list[Line]) -> tuple[list[float], list[int]]:
    slopes = []
    intercepts = []
    for line in lines:
        slopes.append(line.slope)
        intercepts.append((line.x_intercept, 0))
    return (slopes, intercepts)


def merge_colinear_lines(lines: list[Line], width=1920) -> list[Line]:
    """
    Attempts to merge colinear lines.
    """
    slopes = [line.slope for line in lines]
    slopes = np.array(slopes).reshape(-1, 1)  # convert slopes to a 2d array

    # DBSCAN clustering to group colinear lines
    # `eps` is the maximum distance between two samples for them to be part of the same cluster
    # `min_samples` is the minimum number of samples for something to become its own cluster
    slope_tolerance = 0.5
    dbscan = DBSCAN(eps=slope_tolerance, min_samples=2)
    labels = dbscan.fit_predict(slopes)  # labels is a list of clusters, basically

    # Group lines based on the cluster labels
    grouped_lines = {}
    for idx, line in enumerate(lines):
        label = labels[idx]
        if label not in grouped_lines:
            grouped_lines[label] = []
        grouped_lines[label].append(line)

    # Calculate the average line for each cluster
    merged_lines = []
    for label, cluster_lines in grouped_lines.items():
        # x1 = np.mean([line.x1 for line in cluster_lines])
        # y1 = np.mean([line.y1 for line in cluster_lines])
        # x2 = np.mean([line.x2 for line in cluster_lines])
        # y2 = np.mean([line.y2 for line in cluster_lines])
        x = [line.x1 for line in cluster_lines] + [line.x2 for line in cluster_lines]
        y = [line.y1 for line in cluster_lines] + [line.y2 for line in cluster_lines]
        a, b = np.polyfit(x, y, 1)

        x = [0, width]
        y = [a * x[0] + b, a * x[1] + b]
        merged_line = Line(x[0], y[0], x[1], y[1])
        merged_lines.append(merged_line)

    return merged_lines

def detect_lanes(
    lines: list[Line],
    height: int = 1080,
    width: int = 1920,
    center_lane_tol=0.5,
    parallel_tol=0.5,
    x_intercept_tol=250,
) -> list[tuple[Line, Line]]:
    center = width / 2
    lanes = []
    lines.sort(key=lambda x: x.x_intercept)

    for i in range(len(lines[:-1])):
        line1 = lines[i]
        line2 = lines[i + 1]

        if math.isclose(line1.slope, -1 * line2.slope, rel_tol=center_lane_tol):
            # lines are a lane near the center
            lanes.append((line1, line2))
            break  # line 1 has a match with line 2, so pick a new line 1

        elif math.isclose(line1.slope, line2.slope, rel_tol=parallel_tol):
            # slopes are close to parallel
            if math.isclose(
                line1.x_intercept, line2.x_intercept, rel_tol=x_intercept_tol
            ):
                # x-intercepts are close
                if ((line1.x_intercept > center) and (line2.x_intercept > center)) or (
                    (line1.x_intercept < center) and (line2.x_intercept < center)
                ):
                    # the lines are probably a pair
                    lanes.append((line1, line2))
                    break  # found a pair, so start a new
    return lanes


def draw_lanes(img, lanes):
    drawn_img = img
    for lane in lanes:
        lane_lines = []
        for line in lane:
            lane_lines.append(line)
        drawn_img = draw_lines(
            drawn_img, lane_lines, (randrange(255), randrange(255), randrange(255))
        )
    return drawn_img

"""
Detect lines/lanes
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


def detect_lines(
    img, threshold1=50, threshold2=150, apertureSize=3, minLineLength=100, maxLineGap=10
) -> list[Line]:
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
    # blurred_img = cv2.GaussianBlur(gray, (9, 9), 0)
    edges = cv2.Canny(
        gray, threshold1, threshold2, apertureSize=apertureSize
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


def draw_lines(img, lines: list[Line], color: tuple[int, int, int] = (0, 255, 0)):
    for line in lines:
        cv2.line(img, (line.x1, line.y1), (line.x2, line.y2), color, 3)
    return img


def get_slopes_intercepts(lines: list[Line]) -> tuple[list[float], list[int]]:
    slopes = []
    intercepts = []
    for line in lines:
        slopes.append(line.slope)
        intercepts.append((line.x_intercept, 0))
    return (slopes, intercepts)


def merge_colinear_lines(lines: list[Line]) -> list[Line]:
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
        merged_lines.append(cluster_lines[0])

    return merged_lines

def toby_lines(lines: list[Line]) -> list[Line]:
    cleaned_lines = []
    for line in lines:
        can_add = True
        for cleaned_line in cleaned_lines:
            if abs(cleaned_line.slope - line.slope) < 0.5:
                can_add = False

        if can_add:
            cleaned_lines.append(line)
    # DONE MERGING LINES
    #------
    # DELETE LINES NOT PART OF A LANE

    sorted_lines = cleaned_lines
    sorted_lines.sort(key=lambda x: x.x_intercept)
    one_to_zero = sorted_lines[1].x_intercept - sorted_lines[0].x_intercept
    two_to_one = sorted_lines[2].x_intercept - sorted_lines[1].x_intercept
    if(two_to_one < one_to_zero):
        sorted_lines.pop(0)
    if len(sorted_lines) % 2 != 0:
        sorted_lines.pop(len(sorted_lines) - 1)
    # DONE DELETING LINES NOT IN LANE
    #------
    return lines

def detect_lanes(lines: list[Line], width: int = 1920) -> list[tuple[Line, Line]]:
    center = width / 2
    center_lane_tol = 0.5
    parallel_tol = 0.5
    x_intercept_tol = 250
    lanes = []
    lines.sort(key=lambda x: x.x_intercept)

    for i in range(len(lines[:-1])):
        line1 = lines[i]
        for j in range(i+1, len(lines[:-1])):
            line2 = lines[j]

            if math.isclose(line1.slope, -1 * line2.slope, rel_tol=center_lane_tol):
                # lines are a lane near the center
                lanes.append((line1, line2))
                break # line 1 has a match with line 2, so pick a new line 1

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
                        break # found a pair, so start a new
    return lanes


def draw_lanes(img, lanes):
    drawn_img = img
    lines = []
    for lane in lanes:
        lane_lines = []
        for line in lane:
            lane_lines.append(line)
        drawn_img = draw_lines(drawn_img, lane_lines, (randrange(255),randrange(255),randrange(255)))
    return drawn_img
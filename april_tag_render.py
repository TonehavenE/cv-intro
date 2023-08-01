import numpy as np
from dt_apriltags import Detector
import matplotlib.pyplot as plt
import cv2
import april_tags
import time
from pid import *

cameraMatrix = np.array([ 1060.71, 0, 960, 0, 1060.71, 540, 0, 0, 1]).reshape((3,3))

camera_params = ( cameraMatrix[0,0], cameraMatrix[1,1], cameraMatrix[0,2], cameraMatrix[1,2] )

at_detector = Detector(families='tag36h11',
                       nthreads=1,
                       quad_decimate=1.0,
                       quad_sigma=0.0,
                       refine_edges=1,
                       decode_sharpening=0.25,
                       debug=0)

if __name__ == "__main__":
    # The video writer
    cap = cv2.VideoCapture("April_Tag_Test.mkv")
    ret, frame1 = cap.read()

    height, width, layers = frame1.shape
    size = (width, height)

    out = cv2.VideoWriter("april_tag_render.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 30, size)

    count = 0  # the amount of frames that have been read
    # create PID objects, no idea what the right values are
    horizontal_pid = PID(0.1, 0, 0, 100)
    vertical_pid = PID(0.1, 0, 0, 100)

    # Video reading loop
    while ret:
        ret, frame = cap.read()
        if not ret:
            break

        print(f"now on frame {count}...")

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        tags = at_detector.detect(
            gray, estimate_tag_pose=True, camera_params=camera_params, tag_size=True
        )

        if len(tags) > 0:
            positions = april_tags.get_positions(tags)
            errors = april_tags.error_relative_to_center(
                positions, frame.shape[0], frame.shape[1]
            )
            outputs = april_tags.output_from_tags(errors, horizontal_pid, vertical_pid)
            frame = april_tags.render_tags(tags, frame)
            frame = april_tags.draw_outputs(frame, outputs, tags)

        out.write(frame)
        count += 1

    cap.release()
    out.release()
    print("Finished rendering the video.")
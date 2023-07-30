from multiprocessing import Process

from lane_detection import *
from lane_following import *


def render_frame(frame):
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
    grouped_lines = group_lines(lines, height, slope_tolerance=0.1, x_intercept_tolerance=50) # group lines
    merged_lines = merge_lines(grouped_lines, height, width) # merge groups of lines

    # Lane Detection
    lanes = detect_lanes(bw, merged_lines, 500, 200, 10)

    # Lane picking
    center_lines = merge_lane_lines(lanes, height) # find the center of each lane
    center_line = pick_center_line(center_lines, width) # find the closest lane
    (move, turn) = suggest_direction(center_line, width) # textual suggestion of how to move
    text = f"The AUV should move {move} and turn {turn}"

    # Drawing
    # frame = draw_lanes(frame, lanes, offset=True)
    frame = draw_lines(frame, [center_line], (0, 0, 255), offset=True)
    frame = cv2.putText(frame, text, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
    return frame

if __name__ == "__main__":
    cap = cv2.VideoCapture('AUV_Vid.mkv')
    ret, frame1 = cap.read()
    height, width, layers = frame1.shape
    size = (width, height)
    out = cv2.VideoWriter("rendered_video.avi", cv2.VideoWriter_fourcc(*'DIVX'), 30, size)

    count = 0 # the number of frames since the last    
    while ret:
        ret, frame = cap.read()
        # if count == 1879:
        print(f"now on frame {count}...")
        try:
            frame = render_frame(frame)
        except Exception as e:
            print(f"failed to render frame {count}. Error: {e}")
            pass
        
            
        out.write(frame)

        count += 1

    cap.release()
    out.release()
import re
import pyautogui
import time
import os

# Canvas corners
CANVAS_TOP_LEFT = (724, 121)
CANVAS_BOTTOM_RIGHT = (1815, 835)

# Parse G-code file
def parse_gcode(file_path):
    points = []
    with open(file_path, "r") as f:
        x, y = 0, 0
        for line in f:
            line = line.strip()
            if line.startswith(("G0", "G1")):  # movement commands
                cmd = "G1" if line.startswith("G1") else "G0"
                x_match = re.search(r"X([-+]?\d*\.?\d+)", line)
                y_match = re.search(r"Y([-+]?\d*\.?\d+)", line)

                if x_match:
                    x = float(x_match.group(1))
                if y_match:
                    y = float(y_match.group(1))

                points.append((cmd, x, y))
    return points

def normalize_and_scale(points):
    xs = [p[1] for p in points]
    ys = [p[2] for p in points]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x
    height = max_y - min_y

    canvas_width = CANVAS_BOTTOM_RIGHT[0] - CANVAS_TOP_LEFT[0]
    canvas_height = CANVAS_BOTTOM_RIGHT[1] - CANVAS_TOP_LEFT[1]

    scale = min(canvas_width / width, canvas_height / height)

    scaled_points = []
    for cmd, x, y in points:
        sx = CANVAS_TOP_LEFT[0] + (x - min_x) * scale
        sy = CANVAS_TOP_LEFT[1] + (max_y - y) * scale  # flip Y so it's not upside down
        scaled_points.append((cmd, sx, sy))
    return scaled_points

def draw_gcode(points):
    print(f"[INFO] Drawing {len(points)} points from G-code...")
    pen_down = False
    for cmd, x, y in points:
        if cmd == "G0" and pen_down:
            pyautogui.mouseUp()
            pen_down = False

        pyautogui.moveTo(x, y, duration=0.002)

        if cmd == "G1" and not pen_down:
            pyautogui.mouseDown()
            pen_down = True

    if pen_down:
        pyautogui.mouseUp()

if __name__ == "__main__":
    gcode_path = input("Enter full path to the G-code file: ").strip('"')

    if not os.path.isfile(gcode_path):
        print("[ERROR] File not found. Please check the path and try again.")
        exit(1)

    print("[INFO] Parsing G-code...")
    points = parse_gcode(gcode_path)

    if not points:
        print("[ERROR] No G0/G1 movements found in file.")
        exit(1)

    scaled_points = normalize_and_scale(points)

    print("[INFO] Switch to the Graffiti window now! Starting in 3 seconds...")
    time.sleep(3)

    draw_gcode(scaled_points)

    print("[DONE] Finished drawing.")

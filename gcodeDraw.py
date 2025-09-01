import pyautogui
import time
import re

# === CONFIGURATION ===
# Canvas corners (from your earlier message)
CANVAS_X0, CANVAS_Y0 = 724, 121
CANVAS_X1, CANVAS_Y1 = 1815, 835

# === FUNCTIONS ===
def parse_gcode(file_path):
    """
    Parse G-code and extract G0/G1 moves as a list of (x, y, pen_down).
    """
    points = []
    current_x, current_y = 0, 0
    pen_down = False

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue

            # Detect G0 (travel) vs G1 (drawing)
            if line.startswith("G0") or line.startswith("G00"):
                pen_down = False
            elif line.startswith("G1") or line.startswith("G01"):
                pen_down = True

            # Extract X and Y if present
            x_match = re.search(r'X([-+]?\d*\.?\d+)', line)
            y_match = re.search(r'Y([-+]?\d*\.?\d+)', line)

            if x_match:
                current_x = float(x_match.group(1))
            if y_match:
                current_y = float(y_match.group(1))

            if x_match or y_match:
                points.append((current_x, current_y, pen_down))

    return points


def get_bounds(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), max(xs), min(ys), max(ys)


def map_to_canvas(x, y, bounds):
    min_x, max_x, min_y, max_y = bounds
    canvas_width = CANVAS_X1 - CANVAS_X0
    canvas_height = CANVAS_Y1 - CANVAS_Y0

    cx = CANVAS_X0 + ((x - min_x) / (max_x - min_x)) * canvas_width
    cy = CANVAS_Y0 + ((y - min_y) / (max_y - min_y)) * canvas_height
    return cx, cy


def draw_path(points):
    bounds = get_bounds(points)
    print(f"[INFO] G-code bounds: {bounds}")

    print("[INFO] Starting in 3 seconds - switch to your graffiti window!")
    time.sleep(3)

    last_pen_state = False

    for x, y, pen_down in points:
        cx, cy = map_to_canvas(x, y, bounds)

        if pen_down and not last_pen_state:
            pyautogui.mouseDown(cx, cy)
        elif not pen_down and last_pen_state:
            pyautogui.mouseUp()

        pyautogui.moveTo(cx, cy)  # Smooth motion
        last_pen_state = pen_down

    pyautogui.mouseUp()  # Ensure we release at the end


# === MAIN SCRIPT ===
if __name__ == "__main__":
    gcode_path = input("Enter full path to the G-code file: ").strip('"')
    print("[INFO] Parsing G-code...")
    points = parse_gcode(gcode_path)

    if not points:
        print("[ERROR] No points found in G-code.")
    else:
        draw_path(points)

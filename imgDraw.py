import pyautogui
import time
from PIL import Image
import numpy as np
import os

# ---- SETTINGS ----
# Canvas positions (from your message)
CANVAS_TOP_LEFT = (724, 121)
CANVAS_BOTTOM_RIGHT = (1815, 835)

# Color palette positions (x, y) on screen
COLOR_POSITIONS = {
    (0, 0, 0): (959, 944),      # Black
    (255, 255, 255): (1040, 944), # White
    (255, 0, 0): (1125, 944),   # Red
    (0, 255, 0): (1198, 944),   # Green
    (0, 0, 255): (1278, 944),   # Blue
}

PALETTE = list(COLOR_POSITIONS.keys())

# Calculate canvas resolution
canvas_width = CANVAS_BOTTOM_RIGHT[0] - CANVAS_TOP_LEFT[0]
canvas_height = CANVAS_BOTTOM_RIGHT[1] - CANVAS_TOP_LEFT[1]

# Define target "pixel grid" resolution (larger number = more accurate)
GRID_WIDTH = 32
GRID_HEIGHT = 32

# Calculate pixel size
PIXEL_SIZE_X = canvas_width / GRID_WIDTH
PIXEL_SIZE_Y = canvas_height / GRID_HEIGHT

def nearest_color(pixel):
    """Return the closest color in PALETTE to the given pixel."""
    return min(
        PALETTE,
        key=lambda c: (c[0]-pixel[0])**2 + (c[1]-pixel[1])**2 + (c[2]-pixel[2])**2
    )

def select_color(color):
    """Click the palette position for the given color."""
    if color in COLOR_POSITIONS:
        pyautogui.click(COLOR_POSITIONS[color])
        time.sleep(0.05)  # small delay to ensure UI registers

def draw_image(image_path):
    # Load and convert image
    img = Image.open(image_path).convert("RGB")
    img = img.resize((GRID_WIDTH, GRID_HEIGHT))

    pixels = np.array(img)
    h, w, _ = pixels.shape

    print(f"[INFO] Drawing {w}x{h} image with brush strokes...")

    # Process row by row
    for y in range(h):
        x = 0
        while x < w:
            current_color = nearest_color(tuple(pixels[y, x]))
            stroke_start = x
            stroke_end = x

            # Group consecutive pixels of same color
            while stroke_end + 1 < w and nearest_color(tuple(pixels[y, stroke_end + 1])) == current_color:
                stroke_end += 1

            # Only draw if this color is in our palette
            if current_color in PALETTE:
                select_color(current_color)

                start_x = CANVAS_TOP_LEFT[0] + stroke_start * PIXEL_SIZE_X + PIXEL_SIZE_X / 2
                start_y = CANVAS_TOP_LEFT[1] + y * PIXEL_SIZE_Y + PIXEL_SIZE_Y / 2
                end_x = CANVAS_TOP_LEFT[0] + stroke_end * PIXEL_SIZE_X + PIXEL_SIZE_X / 2
                end_y = start_y

                pyautogui.moveTo(start_x, start_y)
                pyautogui.mouseDown()
                pyautogui.moveTo(end_x, end_y, duration=0.01)
                pyautogui.mouseUp()

            x = stroke_end + 1
            time.sleep(0.0001)

if __name__ == "__main__":
    image_path = input("Enter full path to the image: ").strip('"')

    if not os.path.isfile(image_path):
        print("[ERROR] File not found. Please check the path and try again.")
        exit(1)

    print("[INFO] Switch to the Graffiti window now! Starting in 3 seconds...")
    time.sleep(3)

    draw_image(image_path)

    print("[DONE] Finished drawing.")

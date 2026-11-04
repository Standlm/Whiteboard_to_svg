from geometry_corection import reconstruct_shapes
import cv2
import numpy as np
import svgwrite
from pathlib import Path

OUTPUT = Path("outputs")
OUTPUT.mkdir(exist_ok=True)

# Four board corners, selected clockwise:
# top-left, top-right, bottom-right, bottom-left
corners = []

WIDTH = 1000
HEIGHT = 700


def on_mouse(event, x, y, flags, userdata):
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(corners) < 4:
            corners.append((x, y))


def rectify_board(image, points):
    source = np.float32(points)

    destination = np.float32([
        [0, 0],
        [WIDTH - 1, 0],
        [WIDTH - 1, HEIGHT - 1],
        [0, HEIGHT - 1]
    ])

    matrix = cv2.getPerspectiveTransform(
        source, destination
    )

    return cv2.warpPerspective(
        image, matrix, (WIDTH, HEIGHT)
    )

def export_svg(paths):
    drawing = svgwrite.Drawing(
        str(OUTPUT / "drawing.svg"),
        size=("1000", "700"),
        viewBox=f"0 0 {WIDTH} {HEIGHT}",
        profile="tiny"
    )

    for points in paths:
        if len(points) < 2:
            continue

        # Remove repeated closing vertex
        closed = len(points) > 2 and points[0] == points[-1]

        if closed:
            points = points[:-1]

        # Build SVG path commands
        commands = [
            f"M {points[0][0]} {points[0][1]}"
        ]

        for x, y in points[1:]:
            commands.append(f"L {x} {y}")

        if closed:
            commands.append("Z")

        path = drawing.path(
            d=" ".join(commands),
            fill="none",
            stroke="black",
            stroke_width=2
        )

        drawing.add(path)

    drawing.save(pretty=True)

def process_board(image):
    board = rectify_board(image, corners)

    cv2.imwrite(
        str(OUTPUT / "whiteboard.png"),
        board
    )

    paths = reconstruct_shapes(board)
    preview = board.copy()

    for path in paths:
        for i in range(len(path) - 1):
            cv2.line(
                preview,
                tuple(map(int, path[i])),
                tuple(map(int, path[i + 1])),
                (0, 0, 255),
                2
            )

    cv2.imwrite(
        str(OUTPUT / "corrected_lines.png"),
        preview
    )

    export_svg(paths)
    print(f"Generated {len(paths)} reconstructed shapes")

def main():
    global frame

    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        raise RuntimeError("Camera unavailable")

    cv2.namedWindow("Whiteboard")
    cv2.setMouseCallback("Whiteboard", on_mouse)

    while True:
        success, frame = camera.read()

        if not success:
            break

        display = frame.copy()

        for point in corners:
            cv2.circle(
                display, point, 5,
                (0, 255, 0), -1
            )

        if len(corners) == 4:
            cv2.polylines(
                display,
                [np.array(corners, dtype=np.int32)],
                True,
                (0, 255, 0),
                2
            )

        cv2.imshow("Whiteboard", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c") and len(corners) == 4:
            process_board(frame.copy())

        elif key == ord("r"):
            corners.clear()

        elif key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


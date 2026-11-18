import argparse
from pathlib import Path

import cv2
import numpy as np
import svgwrite

from geometry_corection import reconstruct_shapes
from robot_paths import export_robot_paths

OUTPUT = Path("outputs")
WIDTH, HEIGHT = 1000, 700
corners = []  # Top-left, top-right, bottom-right, bottom-left.


def open_camera(index=None):
    """Find a camera that can supply frames, retaining its first frame."""
    for candidate in ([index] if index is not None else range(5)):
        camera = cv2.VideoCapture(candidate)
        if camera.isOpened():
            success, frame = camera.read()
            if success and frame is not None:
                print(f"Using camera {candidate}")
                return camera, frame
        camera.release()
    raise RuntimeError(
        "No readable camera found. Connect a camera and allow camera access "
        "for your terminal, or choose one with --camera INDEX."
    )


def on_mouse(event, x, y, flags, userdata):
    if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 4:
        corners.append((x, y))


def rectify_board(image, points):
    destination = np.float32([
        [0, 0], [WIDTH - 1, 0],
        [WIDTH - 1, HEIGHT - 1], [0, HEIGHT - 1],
    ])
    matrix = cv2.getPerspectiveTransform(np.float32(points), destination)
    return cv2.warpPerspective(image, matrix, (WIDTH, HEIGHT))


def export_svg(paths):
    drawing = svgwrite.Drawing(
        str(OUTPUT / "drawing.svg"),
        size=(str(WIDTH), str(HEIGHT)),
        viewBox=f"0 0 {WIDTH} {HEIGHT}",
    )
    for points in paths:
        closed = points[0] == points[-1]
        shape = drawing.polygon if closed else drawing.polyline
        drawing.add(shape(
            points=points[:-1] if closed else points,
            fill="none", stroke="black", stroke_width=2,
        ))
    drawing.save(pretty=True)


def process_board(image, args, rectify=True):
    OUTPUT.mkdir(exist_ok=True)
    board = rectify_board(image, corners) if rectify else cv2.resize(image, (WIDTH, HEIGHT))
    paths = reconstruct_shapes(board, simplification_factor=args.simplification)
    preview = board.copy()
    for path in paths:
        points = np.array(path, dtype=np.int32)
        cv2.polylines(preview, [points], False, (0, 0, 255), 2)

    cv2.imwrite(str(OUTPUT / "whiteboard.png"), board)
    cv2.imwrite(str(OUTPUT / "corrected_lines.png"), preview)
    export_svg(paths)
    export_robot_paths(paths, OUTPUT, (WIDTH, HEIGHT), args.width_m, args.height_m,
                       args.pen_z, args.lift_m, args.spacing_m, args.frame_id)
    print(f"Exported {len(paths)} strokes to {OUTPUT.resolve()}")
    return preview


def main():
    parser = argparse.ArgumentParser(description="Trace clear board lines into robot waypoints")
    parser.add_argument('--image', type=Path, help='Process an already cropped board image without a camera')
    parser.add_argument('--camera', type=int, help='Camera index (default: search indices 0–4)')
    parser.add_argument('--width-m', type=float, default=0.3)
    parser.add_argument('--height-m', type=float, default=0.21)
    parser.add_argument('--pen-z', type=float, default=0.0)
    parser.add_argument('--lift-m', type=float, default=0.02)
    parser.add_argument('--spacing-m', type=float, default=0.002)
    parser.add_argument('--frame-id', default='drawing_plane')
    parser.add_argument('--simplification', type=float, default=0.025, help='Polygon simplification factor')
    args = parser.parse_args()
    if args.image:
        image = cv2.imread(str(args.image))
        if image is None:
            parser.error(f'Cannot read image: {args.image}')
        process_board(image, args, rectify=False)
        return

    camera, frame = open_camera(args.camera)
    corners.clear()
    print("Click top-left, top-right, bottom-right, bottom-left of the drawing area.")
    print("Move hands out of view, then press s or c to capture, process, and export; r resets corners; q quits.")
    try:
        cv2.namedWindow("Whiteboard")
        cv2.setMouseCallback("Whiteboard", on_mouse)
        while True:
            display = frame.copy()
            for number, point in enumerate(corners, 1):
                cv2.circle(display, point, 5, (0, 255, 0), -1)
                cv2.putText(display, str(number), (point[0] + 8, point[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 180, 0), 2)
            if len(corners) == 4:
                cv2.polylines(display, [np.array(corners, dtype=np.int32)],
                              True, (0, 255, 0), 2)
            instruction = ("s/c: capture + process | r: reset | q: quit" if len(corners) == 4
                           else "Click corners: top-left, top-right, bottom-right, bottom-left")
            cv2.putText(display, instruction, (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 0, 255), 1)
            cv2.imshow("Whiteboard", display)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("s"), ord("c")) and len(corners) == 4:
                preview = process_board(frame.copy(), args)
                cv2.imshow("Exported drawing", preview)
            elif key == ord("r"):
                corners.clear()
            elif key == ord("q") or cv2.getWindowProperty("Whiteboard", cv2.WND_PROP_VISIBLE) < 1:
                break
            success, frame = camera.read()
            if not success or frame is None:
                raise RuntimeError("Camera stopped delivering frames. Reconnect it and restart.")
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


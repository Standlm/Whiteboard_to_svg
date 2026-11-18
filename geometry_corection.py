
import numpy as np
import cv2

def reconstruct_shapes(image, simplification_factor=0.025):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    binary = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31, 10
    )

    # Join small breaks in marker strokes
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (5, 5)
    )
    # binary = cv2.morphologyEx(
    #     binary, cv2.MORPH_CLOSE, kernel
    # )

    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    paths = []

    for contour in contours:
        # Skip small contours that are likely noise - lowering this value adds more of the small objects
        if cv2.contourArea(contour) < 00:
            continue

        perimeter = cv2.arcLength(contour, True)

        # Use polygonal approximation to simplify the contour - lowering the simplification factor adds more points to the polygon
        polygon = cv2.approxPolyDP(
            contour,
            simplification_factor * perimeter,
            True
        )

        if len(polygon) < 3:
            polygon = cv2.approxPolyDP(
                contour,
                0.05 * perimeter,
                True
            )

        points = [
            tuple(map(int, p[0]))
            for p in polygon
        ]

        points.append(points[0])
        paths.append(points)

    return paths


import numpy as np
import cv2

def reconstruct_shapes(image):
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
    binary = cv2.morphologyEx(
        binary, cv2.MORPH_CLOSE, kernel
    )

    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    paths = []

    for contour in contours:
        if cv2.contourArea(contour) < 500:
            continue

        perimeter = cv2.arcLength(contour, True)

        polygon = cv2.approxPolyDP(
            contour,
            0.025 * perimeter,
            True
        )

        if len(polygon) < 3:
            continue

        points = [
            tuple(map(int, p[0]))
            for p in polygon
        ]

        points.append(points[0])
        paths.append(points)

    return paths

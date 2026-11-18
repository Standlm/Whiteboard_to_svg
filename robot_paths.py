"""Export drawing-plane waypoints; execution and robot calibration are separate."""
import csv
import json
import math

#spacing_m=0.002,  # spacing between waypoints in meters, can be set to 0 for no spacing to increase speed.
def export_robot_paths(paths, output, image_size, width_m=0.3, height_m=0.21,
                       pen_z=0.0, lift_m=0.02, spacing_m=0.002,
                       frame_id='drawing_plane'):
    values = (width_m, height_m, lift_m, spacing_m)
    if not all(math.isfinite(v) and v > 0 for v in values) or not math.isfinite(pen_z):
        raise ValueError('Dimensions, lift, and spacing must be finite and positive')
    width, height = image_size
    strokes, waypoints = [], []
    for path in paths:
        points = []
        for x, y in path:
            point = [x / (width - 1) * width_m,
                     (1 - y / (height - 1)) * height_m, pen_z]
            if points:
                previous = points[-1]
                steps = max(1, math.ceil(math.dist(previous, point) / spacing_m))
                points.extend([[a + (b - a) * i / steps for a, b in zip(previous, point)]
                               for i in range(1, steps + 1)])
            else:
                points.append(point)
        if len(points) < 2:
            continue
        stroke_id = len(strokes)
        strokes.append(points)
        waypoints.append(dict(stroke_id=stroke_id, pen_down=False,
                              x=points[0][0], y=points[0][1], z=pen_z + lift_m))
        for x, y, z in points:
            waypoints.append(dict(stroke_id=stroke_id, pen_down=True, x=x, y=y, z=z))
        waypoints.append(dict(stroke_id=stroke_id, pen_down=False,
                              x=points[-1][0], y=points[-1][1], z=pen_z + lift_m))
    payload = dict(frame_id=frame_id, units='meters', strokes=strokes, waypoints=waypoints)
    (output / 'drawing_paths.json').write_text(json.dumps(payload, indent=2) + '\n')
    with (output / 'drawing_waypoints.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['stroke_id', 'pen_down', 'x', 'y', 'z'])
        writer.writeheader()
        writer.writerows(waypoints)
    return payload

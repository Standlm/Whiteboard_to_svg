## How to Run so far:

Download the repository
```
git clone git@github.com:Standlm/Whiteboard_to_svg.git
cd whiteboard_to_svg
```

Set up the virtual enviroment
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run main.py and click the four corners of the whiteboard starting with the top left.  type ```c``` to capture an image ```q``` to quit, and ```r``` to reset the corners.

```
python3 main.py
```
## Todo nov 4th

Output directly to location coordinates instead of SVG so ros2.0 can access it.

Work on movement detection, goal is to capture image from whiteboard presenter

## Next steps

### Auto Whiteboard detection

### increase support for curved lines and strokes rather than just polygons

# Road Lane Detection

This project is a Python program that uses OpenCV to detect lanes on roads. Unlike other lane detection programs, this one dynamically calculates the mask based on the color of the road, making it more adaptable to different environments.

## Features

- **Dynamic Mask Calculation**: Adjusts the mask according to the road color.
- **Lane Detection**: Identifies and highlights lanes on the road.

## Requirements

- Python 3.x
- OpenCV (`opencv-python`)

## Canny edge detection API

`canny_edge_detection(frame)` accepts an OpenCV-compatible BGR image, converts
it to grayscale, applies a 5x5 Gaussian blur, then runs Canny edge detection
with thresholds 50 and 150. It returns a single-channel edge image and does
not modify `frame`.

```python
import cv2

from dik2_1 import canny_edge_detection

frame = cv2.imread("road.png")
if frame is None:
	raise FileNotFoundError("Could not read road.png")

edges = canny_edge_detection(frame)
```

Importing `dik2_1` exposes the processing functions without opening the video;
run the interactive demo with `python dik2_1.py` from this directory.

## Acknowledgements

- OpenCV documentation
- Various online tutorials and resources

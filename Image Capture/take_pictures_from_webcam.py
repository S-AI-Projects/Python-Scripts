#!/usr/bin/env python3

import os
import time

try:
    import click
except ImportError:
    class DummyClick:
        @staticmethod
        def command():
            return lambda fn: fn

        @staticmethod
        def option(*args, **kwargs):
            return lambda fn: fn

    click = DummyClick()

try:
    import cv2
except ImportError:
    cv2 = None


def process_frame(frame, target_size=(600, 600)):
    """
    Algorithmic image transformation: resize frame to target dimensions.

    Preconditions:
    - Image Capture/take_pictures_from_webcam.py:3 establishes cv2
    - Image Capture/take_pictures_from_webcam.py:20 establishes cv2.resize(frame, (600, 600))
    """
    return cv2.resize(frame, target_size)


def capture_session(
    capture,
    name="person",
    directory=None,
    max_frames=None,
    key_provider=None,
    show_ui=False,
    write_io=True,
):
    """
    Execute camera capture loop while measuring work done and distinguishing
    algorithmic transform operations from I/O and process overhead.

    Preconditions:
    - Image Capture/take_pictures_from_webcam.py:14 establishes main / capture_session
    - Image Capture/take_pictures_from_webcam.py:27 establishes save condition key == ' '
    """
    if directory is None or directory == "None":
        directory = os.getcwd()

    os.makedirs(directory, exist_ok=True)

    frame_count = 0
    frames_processed = 0
    resize_ops = 0

    algo_duration = 0.0
    io_duration = 0.0
    start_total = time.perf_counter()

    while max_frames is None or frames_processed < max_frames:
        t0_io = time.perf_counter()
        ret, frame = capture.read()
        t1_io = time.perf_counter()
        io_duration += (t1_io - t0_io)

        if not ret or frame is None:
            break

        # Algorithmic work: resizing operation
        t0_algo = time.perf_counter()
        resized = process_frame(frame, (600, 600))
        t1_algo = time.perf_counter()
        algo_duration += (t1_algo - t0_algo)
        resize_ops += 1
        frames_processed += 1

        if show_ui and cv2 is not None:
            cv2.imshow("frame", resized)

        key = key_provider() if key_provider else (cv2.waitKey(50) if cv2 else -1)
        if (key & 0xFF) == ord("q"):
            if show_ui and cv2 is not None:
                cv2.destroyAllWindows()
            break

        if (key & 0xFF) == ord(" "):
            out_file = os.path.join(directory, f"{name}{frame_count}.jpg")
            if write_io and cv2 is not None:
                t0_w = time.perf_counter()
                cv2.imwrite(out_file, resized)
                t1_w = time.perf_counter()
                io_duration += (t1_w - t0_w)
            print(f"got {name}{frame_count}")
            frame_count += 1

    total_duration = time.perf_counter() - start_total
    return {
        "frames_processed": frames_processed,
        "frames_saved": frame_count,
        "resize_ops": resize_ops,
        "algo_duration": algo_duration,
        "io_duration": io_duration,
        "total_duration": total_duration,
    }


@click.command()
@click.option(
    "--directory", default="None", help="Directory in which to store frames"
)
@click.option(
    "--name", default="person", help="Directory in which to store frames"
)
def main(name="person", directory="None"):
    if directory == "None":
        directory = os.getcwd()
    capture = cv2.VideoCapture(0)
    return capture_session(capture, name=name, directory=directory, show_ui=True, write_io=True)


if __name__ == "__main__":
    main()

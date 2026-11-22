import math
import os
import sys
import time

# Fallback-safe imports for optional/platform dependencies
try:
    import numpy as np
except ImportError:
    np = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None

try:
    import handTrackingModule as htm
except ImportError:
    try:
        from . import handTrackingModule as htm
    except Exception:
        htm = None

try:
    from ctypes import POINTER, cast
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    AudioUtilities = None
    IAudioEndpointVolume = None
    CLSCTX_ALL = None
    cast = None
    POINTER = None

# Global configuration constants and state variables
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

LastPx = 800
LastPy = 0

Percent = 0


def calculate_distance(x0, y0, x1=None, y1=None):
    """Calculate Euclidean distance between two 2D points.

    Can be invoked as calculate_distance(x0, y0, x1, y1) or calculate_distance((x0, y0), (x1, y1)).
    """
    if y1 is None:
        p1, p2 = x0, y0
        x0, y0 = p1[0], p1[1]
        x1, y1 = p2[0], p2[1]
    return math.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0))


def distance_to_percent(distance):
    """Convert distance to volume percentage clamped between 50 and 250 pixels.

    Formula from source:
        if distance < 50: distance = 50
        elif distance > 250: distance = 250
        Percent = round((distance - 50.0) / 2)

    Boundaries:
        - Lower boundary: 50.0 -> 0%
        - Upper boundary: 250.0 -> 100%
        - Below 50.0 is clamped to 50.0 -> 0%
        - Above 250.0 is clamped to 250.0 -> 100%
    """
    if distance < 50:
        d = 50
    elif distance > 250:
        d = 250
    else:
        d = distance
    return round((d - 50.0) / 2)


def percent_to_volume_change(percent):
    """Calculate decibel change based on volume percentage.

    Formula from source:
        Changevolume = round(math.log((Percent / 10) + 1) * 50 * 0.54)

    Domain:
        (Percent / 10) + 1 must be strictly positive (> 0), i.e., Percent > -10.
        For Percent <= -10, raises ValueError: math domain error.
    """
    return round(math.log((percent / 10.0) + 1.0) * 50.0 * 0.54)


def compute_master_volume(change_volume):
    """Compute target master volume dB from change_volume.

    Formula from source: -65.25 + Changevolume
    """
    return -65.25 + change_volume


def percent_to_bar_height(percent):
    """Calculate UI rectangle top coordinate for the volume display bar.

    Formula from source: int(340 - (Percent * 2.0))
    """
    return int(340 - (percent * 2.0))


def interpolate(x, in_min, in_max, out_min, out_max):
    """Linear interpolation equivalent to np.interp with clamping."""
    if np is not None:
        return float(np.interp(x, (in_min, in_max), (out_min, out_max)))
    if x <= in_min:
        return float(out_min)
    if x >= in_max:
        return float(out_max)
    return float(out_min + (x - in_min) * (out_max - out_min) / (in_max - in_min))


def detect_fingers(lmList, tip_ids=None):
    """Detect which fingers are extended based on landmark coordinates.

    Args:
        lmList (list): List of landmarks [id, x, y].
        tip_ids (list, optional): Landmark IDs for tips. Defaults to [4, 8, 12, 16, 20].

    Returns:
        list: Binary list representing finger states [thumb, index, middle, ring, pinky].
    """
    if not lmList:
        return []
    if tip_ids is None:
        tip_ids = [4, 8, 12, 16, 20]

    fingers = []
    # Thumb
    if lmList[tip_ids[0]][1] > lmList[tip_ids[0] - 1][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # 4 fingers
    for id_idx in range(1, len(tip_ids)):
        if lmList[tip_ids[id_idx]][2] < lmList[tip_ids[id_idx] - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


def init_audio_volume():
    """Initialize audio endpoint volume using PyCAW on Windows platforms."""
    if AudioUtilities is None or IAudioEndpointVolume is None or CLSCTX_ALL is None:
        return None
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except Exception:
        return None


# Module-level volume attribute for backwards compatibility
volume = init_audio_volume()


def main(cap=None, vol=None, detector=None, max_iterations=None):
    """Run hand volume control loop."""
    global plocX, plocY, clocX, clocY, pTime, Percent

    if vol is None:
        vol = volume
    if vol is None:
        vol = init_audio_volume()

    if detector is None and htm is not None:
        detector = htm.handDetector(detectionCon=0.75)

    if cap is None and cv2 is not None:
        cap = cv2.VideoCapture(0)
        if cap is not None:
            cap.set(3, wCam)
            cap.set(4, hCam)

    iteration_count = 0
    tipId = [4, 8, 12, 16, 20]

    while True:
        if max_iterations is not None and iteration_count >= max_iterations:
            break
        iteration_count += 1

        if cap is None:
            break

        success, img = cap.read()
        if not success or img is None:
            break

        if detector is not None:
            img = detector.findHands(img, draw=True)
            lmList = detector.findPosition(img, draw=False)
        else:
            lmList = []

        if len(lmList) != 0:
            fingers = detect_fingers(lmList, tipId)

            if len(fingers) >= 2 and fingers[1] == 1 and fingers[0] == 1:
                x1, y1 = lmList[8][1:]  # Index finger
                x0, y0 = lmList[4][1:]  # Thumb

                # Index finger interpolation & smoothing
                x3 = interpolate(x1, frameR, wCam - frameR, 0, 1080)
                y3 = interpolate(y1, frameR, hCam - frameR, 0, 720)
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                if cv2 is not None:
                    cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

                # Thumb interpolation & smoothing
                x3 = interpolate(x0, frameR, wCam - frameR, 0, 1080)
                y3 = interpolate(y0, frameR, hCam - frameR, 0, 720)
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                if cv2 is not None:
                    cv2.circle(img, (x0, y0), 15, (0, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

                if cv2 is not None:
                    cv2.line(img, (x1, y1), (x0, y0), (0, 0, 255), 2)
                distance = calculate_distance(x0, y0, x1, y1)

                Percent = distance_to_percent(distance)

        Changevolume = percent_to_volume_change(Percent)
        print(Changevolume)
        if vol is not None:
            vol.SetMasterVolumeLevel(-65.25 + Changevolume, None)

        height = percent_to_bar_height(Percent)
        print(height)
        if cv2 is not None:
            cv2.rectangle(img, (570, height), (620, 340), (0, 255, 0), -1)
            cv2.rectangle(img, (570, 140), (620, 340), (255, 0, 0), 2)
            img = cv2.flip(img, 1)

            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfText = (15, 130)
            fontScale = 1
            fontColor = (0, 0, 0)
            lineType = 2
            cv2.putText(
                img, f"{Percent}%", bottomLeftCornerOfText, font, fontScale, fontColor, lineType
            )

            cTime = time.time()
            fps = 1.0 / float(cTime - pTime) if (cTime - pTime) > 0 else 0.0
            pTime = cTime
            cv2.imshow("image", img)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    if cap is not None and hasattr(cap, "release"):
        cap.release()
    if cv2 is not None and hasattr(cv2, "destroyAllWindows"):
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

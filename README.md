# Gameplay Opponent Engagement Tracker using YOLOv11

## Project Overview
This project provides a Python-based tool to analyze short gameplay videos (10–15 seconds) to detect and track opponents (bots) using a custom-trained YOLOv11 object detection model. Instead of simply counting unique opponents, this tool counts **Windows of Opportunity**—distinct time intervals when an opponent is visible and vulnerable to be engaged.

The primary goal is to deliver actionable tactical insights by measuring how many times and for how long bots are exposed, helping gamers understand their reaction opportunities during gameplay.

---

## Features
- Detects opponents in gameplay video frames using YOLOv11 object detection.
- Tracks each bot with persistent IDs using advanced tracking algorithms (ByteTrack/BoT-SORT).
- Counts each distinct exposure window when a bot appears or re-appears.
- Measures the exposure duration (in seconds) per bot.
- Saves frames corresponding to engagement opportunities for later review.
- Optimized for slower, predictable bot behavior with configurable frame sampling to save compute time.

---

## What This Repository Contains
- `analyze_bot_exposure.py` : Main script that performs video processing, object detection, tracking, and reporting.
- `weights.pt` : (Not included) Placeholder name used in the code for your trained YOLOv11 weights file — replace with your actual model file.
- `engagements/` : Output folder where captured engagement frames and `exposure_timeline.png` are saved.

---

## How the Code Works (Detailed)

1. Configuration
- The script exposes a few top-level variables you should update before running:
  - `VIDEO_PATH` : Path to the gameplay video (e.g., `gameplay.mp4`).
  - `MODEL_PATH` : Path to YOLOv11 `.pt` weights (e.g., `weights.pt`).
  - `OUTPUT_DIR` : Output directory for saved engagement frames and timeline chart (default `engagements`).
  - `CONFIDENCE_THRESHOLD` : Minimum confidence to keep a detection (default `0.5`).

2. Loading the model
- The script loads the model via `model = YOLO(MODEL_PATH)`. If loading fails the script prints the error and exits. Ensure the `ultralytics` package and compatible weights are available.

3. Frame processing and tracking
- The video is read with OpenCV (`cv2.VideoCapture`) and processed frame-by-frame. By default the script processes every 2nd frame to reduce compute (frame skipping).
- Tracking is run using `model.track(...)` with `persist=True` so that detections are assigned persistent track IDs across frames. The script uses an explicit tracker config (e.g., `botsort.yaml`) which you can change to `bytetrack.yaml` or other supported trackers in the `ultralytics` config.

4. Exposure windows
- The script keeps an `active_exposures` dictionary that opens a new window when a new track ID appears and closes it when that ID is no longer detected in the next processed frame. Each completed window is recorded with `id`, `class`, `start`, `end`, and `duration`.

5. Post-processing and merging
- To avoid fragmented events caused by brief occlusions or tracker flicker, the `merge_exposures()` function merges exposures for the same ID that are separated by a small gap (default `0.5` seconds).

6. Visualization and reporting
- The script generates a Gantt-style timeline chart saved as `exposure_timeline.png` (in `OUTPUT_DIR`) using `matplotlib` with color-coded bars for different classes (CT, T, CT_HEAD, T_HEAD).
- A console report lists all merged exposures, separates head vs body exposures, and annotates each exposure with a tactical category determined by `get_tactical_category()` (Flash/Noise, Standard, HIGH VULNERABILITY).

---

## Expected Outputs
- Saved engagement frames: `engagements/engagement_id_<ID>_time_<TIME>.jpg` — annotated frames showing the detection and bounding boxes.
- Timeline chart: `engagements/exposure_timeline.png` — a visual summary of when each tracked opponent was exposed.
- Console report: A textual summary including counts, IDs, durations, and tactical categories.

---

## Commands
1. Install dependencies (recommended inside a virtual environment):
```powershell
pip install ultralytics opencv-python matplotlib
```

2. Adjust configuration at the top of `analyze_bot_exposure.py` (set `VIDEO_PATH` and `MODEL_PATH`).

3. Run the analysis:
```powershell
python analyze_bot_exposure.py
```

---

## Troubleshooting
- Model loading errors: If `model = YOLO(MODEL_PATH)` fails, check that `MODEL_PATH` points to a valid `.pt` and that the installed `ultralytics` version supports the model.
- No detections: Increase `CONFIDENCE_THRESHOLD` sensitivity (lower the value), check that your model classes align with labels used by the script (CT, T, CT_HEAD, T_HEAD), and ensure input video resolution is compatible with the model.
- Slow performance: Use GPU-enabled Python + CUDA drivers, or increase the frame skip (process every Nth frame) to reduce inference calls.

---

## Notes & Limitations
- The tool is optimized for slow, predictable bot movement and may not generalize well to high-speed, human players.
- Tracking re-identification failures (ID flips) may still occur after long occlusions — merging helps but does not fully solve re-ID problems.

---

## Future Improvements
- Add a small config or CLI to adjust frame stride, confidence, tracker selection, and output paths without editing the script.
- Add a lightweight dashboard to inspect saved frames and timelines interactively.
- Integrate a re-identification model to reduce ID flips across long occlusions.

---

## License & Attribution
This project uses the YOLOv11 model and Ultralytics framework. Please follow the license terms of the model and libraries you use.

---

## Author / Maintainer
Aditya Behera  
Email: 123aditya6025@sjcem.edu.in  
GitHub: https://github.com/AdiArtifice

---

## Requirements

- Python 3.8 or higher
- GPU recommended for faster inference (optional but recommended)
- Python packages:
  - ultralytics (for YOLOv11 model and tracking)
  - opencv-python (for video handling and saving frames)

Install dependencies via pip:
```
pip install ultralytics opencv-python
```

Ensure you have your YOLOv11 `.pt` weights file downloaded and accessible.

---

## Usage

1. Place your gameplay video file and the YOLOv11 model weights in the project directory.
2. Update the `VIDEO` and `MODEL` variables in the script with your file names.
3. Run the script:
```
python analyze_bot_exposure.py
```
4. The script processes the video, detecting and tracking bots, logging each new "Window of Opportunity," and calculating exposure durations.
5. Frames capturing these moments are saved in an output folder (`engagements/`) for visual analysis.
6. Review the console output for a tactical summary.

---

## How It Works

- The YOLOv11 model processes video frames and detects opponents classified as CT, T, CT_head, or T_head.
- Tracking assigns unique IDs to bots to maintain persistence across frames, enabling differentiation of distinct exposures.
- A new exposure window starts when a new ID appears or an existing ID reappears after disappearance.
- Exposure duration is calculated as time visible between first detection and last frame seen.
- The logic is optimized for slow-moving bots, leveraging frame skipping (processing every 2nd frame) to balance speed and accuracy.

---

## Limitations

- Designed specifically for bots with slow, predictable movement patterns.
- May not generalize well to fast-moving or human opponents with erratic behavior.
- Re-identification errors possible if bots leave and re-enter view after long occlusions.
- Accuracy depends on quality and suitability of the YOLOv11 weights and video resolution.

---

## Future Improvements

- Integrate advanced re-identification models to reduce ID flips after long occlusions.
- Extend support to human players with dynamic movement.
- Add visualization dashboards for post-match tactical review.
- Optimize inference speed for real-time or longer gameplay analysis.

---

## License

This project uses the YOLOv11 model licensed under the AGPL-3.0 license. Commercial use is permitted under the license terms. Please refer to the model license for details.

---

## Author / Maintainer

Aditya Behera  
Email: 123aditya6025@sjcem.edu.in  
GitHub: https://github.com/AdiArtifice

---

## Acknowledgments

- Ultralytics for the YOLO object detection framework  
- OpenCV for video processing utilities  
- The gaming community inspiring tactical analysis tools

---#   C S 2 - O p p o n e n t - E x p o s u r e - T r a c k e r .  
 
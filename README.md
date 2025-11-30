# Gameplay Opponent Engagement Tracker (YOLOv11)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![YOLOv11](https://img.shields.io/badge/YOLOv11-Ultralytics-00FFFF.svg)
![License](https://img.shields.io/badge/AGPL--3.0-green.svg)

A lightweight computer vision tool designed to analyze Counter-Strike 2 gameplay clips. It detects and tracks opponents (`CT`, `T`) and their hitboxes (`HEAD`) using a custom YOLOv11 model combined with the BoT-SORT tracking algorithm. The tool generates a tactical vulnerability report, identifying how long opponents are exposed to the player.

---

## Features
- **Advanced Tracking:** Uses YOLOv11 for detection and **BoT-SORT** for persistent object tracking across frames.
- **Smart Exposure Merging:** Automatically merges fragmented detection intervals (gaps < 0.5s) to handle flickering or brief occlusions.
- **Tactical Classification:** Categorizes exposures based on duration:
  - **Flash/Noise:** < 0.2s
  - **Standard:** 0.2s – 1.0s
  - **HIGH VULNERABILITY:** > 1.0s
- **Visual Analytics:**
  - Generates a **Gantt-style timeline** of all opponent exposures.
  - Exports **annotated frames** (JPEG) at the moment a new target is detected.
- **Performance Optimization:** Processes every 2nd frame to speed up analysis without significantly compromising tracking accuracy.

---

## Project Layout

```text
.
├── analyze_bot_exposure.py   # Main analysis script
├── weights.pt                # YOLOv11 trained model weights
├── gameplay.mp4              # Input video file (user provided)
├── requirements.txt          # Python dependencies
└── engagements/              # Output directory (auto-created)
    ├── engagement_*.jpg      # Snapshots of detected targets
    └── exposure_timeline.png # Visualization chart
```

---

## Requirements
- Python 3.8+
- (Recommended) GPU + CUDA for faster inference
- Python packages:
```bash
pip install -r requirements.txt
```

---

## Configuration

You can adjust the following constants at the top of [`analyze_bot_exposure.py`](analyze_bot_exposure.py ) to fit your specific video or model:

| Constant | Default | Description |
| :--- | :--- | :--- |
| [`VIDEO_PATH`](analyze_bot_exposure.py ) | `"gameplay.mp4"` | Path to the input video file. |
| [`MODEL_PATH`](analyze_bot_exposure.py ) | `"weights.pt"` | Path to the trained YOLOv11 `.pt` file. |
| [`OUTPUT_DIR`](analyze_bot_exposure.py ) | `"engagements"` | Folder where results will be saved. |
| [`CONFIDENCE_THRESHOLD`](analyze_bot_exposure.py ) | `0.5` | Minimum confidence (0.0-1.0) to accept a detection. |

---

## How to Run

1. Place your video file in the project root and rename it to [`gameplay.mp4`](gameplay.mp4 ) (or update the script).
2. Ensure your model weights are saved as [`weights.pt`](weights.pt ).
3. Run the script:

```bash
python analyze_bot_exposure.py
```

---

## Outputs

The script produces a console report and files in the [`engagements`](engagements ) folder.

### 1. Console Report
Separates detections into **Body Exposures** (Full Target) and **Head Exposures** (Partial Target).

```text
TACTICAL VULNERABILITY REPORT (MERGED)
============================================================
Total Distinct Targets: 3
Total Exposure Events: 5
------------------------------------------------------------

BODY EXPOSURES (Full Target)
ID    | Class      | Start    | End      | Duration   | Tactical Category
---------------------------------------------------------------------------
1     | T          | 0.50     | 2.30     | 1.80       | HIGH VULNERABILITY
2     | CT         | 4.10     | 4.25     | 0.15       | Flash/Noise
---------------------------------------------------------------------------
```

### 2. Visual Timeline (`exposure_timeline.png`)
A Gantt chart showing exactly when each unique ID appeared and for how long.
- **Blue/Cyan:** CT / CT Head
- **Orange/Yellow:** T / T Head

### 3. Engagement Snapshots
Images like `engagement_id_1_time_0.50s.jpg` are saved to visually verify the start of an engagement.

---

## Limitations

1. **Hardcoded Class Names:** The visualization logic specifically looks for class names containing "CT", "T", or "HEAD" to assign colors. Using a model with different class names (e.g., "person", "car") will result in default gray bars in the timeline.
2. **Frame Skipping:** The script processes every **2nd frame** to improve speed. While generally effective, extremely fast peeks (under ~33ms at 60fps) might be missed or have slightly inaccurate start/end times.
3. **Occlusion Handling:** While the script merges gaps smaller than 0.5s, longer occlusions (e.g., an enemy running behind a wall for 2 seconds) will be treated as two separate engagement events with the same ID (if the tracker maintains the ID) or different IDs.
4. **Single Video Processing:** The script is currently designed to process one video file defined in the code variables, rather than a batch of videos or command-line arguments.

---

## Author

Aditya Behera
GitHub: [https://github.com/AdiArtifice](https://github.com/AdiArtifice)
Email: [123aditya6025@sjcem.edu.in](mailto:123aditya6025@sjcem.edu.in)

---

## Citation

```bibtex
@software{behera2025engagement,
  author = {Behera, Aditya},
  title = {Gameplay Opponent Engagement Tracker using YOLOv11},
  year = {2025},
  url = {https://github.com/AdiArtifice/gameplay-engagement-tracker}
}
```

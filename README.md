```markdown
# Gameplay Opponent Engagement Tracker (YOLOv11)

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![YOLOv11](https://img.shields.io/badge/YOLOv11-Ultralytics-00FFFF.svg)
![License](https://img.shields.io/badge/AGPL--3.0-green.svg)

Lightweight tool that detects and tracks opponents in short gameplay clips (10–15s) using a custom YOLOv11 model and a multi-object tracker. Produces annotated frames, exposure windows (timestamps + durations), and a visibility timeline.

---

## Features
- Detects: `CT`, `T`, `CT_HEAD`, `T_HEAD`  
- Persistent tracking via ByteTrack / BoT-SORT  
- Exposure window segmentation and merging (reduces flicker)  
- Annotated frame exports and Gantt-style timeline PNG  
- Configurable frame skipping and confidence threshold

---

## Project layout
```

.
├── analyze_bot_exposure.py
├── weights.pt                # add your YOLOv11 model file
└── engagements/              # outputs (auto-created)

````

---

## Requirements
- Python 3.8+  
- (Recommended) GPU + CUDA  
- Python packages:
```bash
pip install ultralytics opencv-python matplotlib
````

---

## Quick setup

```bash
git clone https://github.com/AdiArtifice/gameplay-engagement-tracker.git
cd gameplay-engagement-tracker
pip install ultralytics opencv-python matplotlib
```

Edit configuration values at the top of `analyze_bot_exposure.py`:

```py
VIDEO_PATH = "gameplay.mp4"
MODEL_PATH = "weights.pt"
FRAME_SKIP = 2
CONFIDENCE_THRESHOLD = 0.5
TRACKER_CONFIG = "bytetrack.yaml"
```

---

## Run

```bash
python analyze_bot_exposure.py
```

Outputs (saved to `engagements/`):

* `engagement_*.jpg` — annotated frames with timestamps
* `exposure_timeline.png` — Gantt-style timeline
* Console summary listing exposure windows and durations

---

## Example console snippet

```
=== EXPOSURE ANALYSIS REPORT ===
Total Exposure Windows: 8
Unique Bot IDs: 3

ID 3 (T_HEAD): 5.10s–8.20s (3.10s) [HIGH VULNERABILITY]
ID 1 (T): 0.50s–2.30s (1.80s) [Standard]
```

---

## Notes & limitations

* Optimized for bots / predictable movement. Performance on fast human players may vary.
* Re-identification errors can occur after long occlusions; exposure merging mitigates short flickers.
* Best used with short clips (10–15 seconds) for now.

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

```
```

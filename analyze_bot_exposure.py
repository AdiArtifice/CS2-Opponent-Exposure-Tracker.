import cv2
from ultralytics import YOLO
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- Configuration ---
# Update these paths with your actual file names
VIDEO_PATH = "gameplay.mp4"  # Replace with your video file
MODEL_PATH = "weights.pt"    # Replace with your trained .pt file
OUTPUT_DIR = "engagements"
CONFIDENCE_THRESHOLD = 0.5   # Minimum confidence to count as a detection

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def merge_exposures(exposures, gap_threshold=0.5):
    """
    Merges exposure intervals for the same ID if they are within gap_threshold seconds.
    """
    if not exposures:
        return []
    
    # Sort by ID then by start time
    sorted_exposures = sorted(exposures, key=lambda x: (x['id'], x['start']))
    merged = []
    
    if not sorted_exposures:
        return []

    current_exp = sorted_exposures[0].copy()
    
    for next_exp in sorted_exposures[1:]:
        # Check if same ID and gap is within threshold
        if (next_exp['id'] == current_exp['id'] and 
            next_exp['start'] - current_exp['end'] <= gap_threshold):
            # Merge
            current_exp['end'] = max(current_exp['end'], next_exp['end'])
            current_exp['duration'] = current_exp['end'] - current_exp['start']
            # Keep the class from the first detection (or could prioritize HEAD if mixed)
        else:
            merged.append(current_exp)
            current_exp = next_exp.copy()
            
    merged.append(current_exp)
    return merged

def generate_timeline(exposures, output_path):
    """
    Generates a Gantt chart of exposures.
    """
    if not exposures:
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Get unique IDs for Y-axis
    ids = sorted(list(set(e['id'] for e in exposures)))
    id_map = {id_val: i for i, id_val in enumerate(ids)}
    
    # Colors for classes
    colors = {'CT': 'blue', 'T': 'orange', 'CT_HEAD': 'cyan', 'T_HEAD': 'yellow'}
    default_color = 'gray'

    for exp in exposures:
        y = id_map[exp['id']]
        start = exp['start']
        duration = exp['duration']
        cls = exp['class']
        
        # Determine color based on class (simple check)
        color = default_color
        for key, c in colors.items():
            if key in cls.upper():
                color = c
                break
        
        ax.barh(y, duration, left=start, height=0.6, color=color, edgecolor='black', alpha=0.8)
        
    ax.set_yticks(range(len(ids)))
    ax.set_yticklabels([f"ID {i}" for i in ids])
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Opponent ID")
    ax.set_title("Opponent Exposure Timeline")
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    
    # Add legend
    legend_elements = [patches.Patch(facecolor=c, edgecolor='black', label=k) for k, c in colors.items()]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def get_tactical_category(duration):
    if duration < 0.2:
        return "Flash/Noise"
    elif duration < 1.0:
        return "Standard"
    else:
        return "HIGH VULNERABILITY"

def analyze_exposure():
    # Check if files exist
    if not os.path.exists(VIDEO_PATH):
        print(f"Error: Video file '{VIDEO_PATH}' not found.")
        print("Please update the VIDEO_PATH variable in the script.")
        return
    
    # Load the YOLOv11 model
    print(f"Loading model: {MODEL_PATH}...")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have the ultralytics package installed and the model path is correct.")
        return

    # Open the video file
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Error: Could not open video file {VIDEO_PATH}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / fps if fps > 0 else 0
    
    print(f"Processing video: {VIDEO_PATH}")
    print(f"Duration: {duration_sec:.2f}s, FPS: {fps}, Total Frames: {total_frames}")
    print("-" * 50)

    # Tracking state
    # active_exposures: { track_id: { 'start_frame': int, 'start_time': float, 'max_conf': float, 'class': str } }
    active_exposures = {} 
    # completed_exposures: list of dicts
    completed_exposures = []

    frame_idx = 0
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Optimization: Process every 2nd frame (vid_stride=2 equivalent logic)
        if frame_idx % 2 != 0:
            frame_idx += 1
            continue

        current_time_sec = frame_idx / fps

        # Run YOLOv11 tracking
        # persist=True is crucial for keeping IDs across frames
        # tracker="botsort.yaml" or "bytetrack.yaml" are available. BoT-SORT is default in some versions, but explicit is good.
        results = model.track(frame, persist=True, verbose=False, tracker="botsort.yaml", conf=CONFIDENCE_THRESHOLD)
        
        current_frame_track_ids = set()

        if results and results[0].boxes and results[0].boxes.id is not None:
            boxes = results[0].boxes
            track_ids = boxes.id.int().cpu().tolist()
            clss = boxes.cls.int().cpu().tolist()
            confs = boxes.conf.cpu().tolist()

            for track_id, cls_id, conf in zip(track_ids, clss, confs):
                class_name = model.names[cls_id]
                current_frame_track_ids.add(track_id)

                if track_id not in active_exposures:
                    # OPEN WINDOW OF OPPORTUNITY
                    print(f"[Time {current_time_sec:.2f}s] New Target Detected! ID: {track_id} ({class_name})")
                    active_exposures[track_id] = {
                        'start_frame': frame_idx,
                        'start_time': current_time_sec,
                        'class': class_name,
                        'max_conf': conf
                    }
                    
                    # Save frame for this engagement
                    filename = f"{OUTPUT_DIR}/engagement_id_{track_id}_time_{current_time_sec:.2f}s.jpg"
                    # Draw box on frame for visualization
                    annotated_frame = results[0].plot()
                    cv2.imwrite(filename, annotated_frame)
                else:
                    # SUSTAIN WINDOW
                    # Update max confidence if higher
                    if conf > active_exposures[track_id]['max_conf']:
                        active_exposures[track_id]['max_conf'] = conf

        # CLOSE WINDOW logic
        # Check for IDs that were active but are not in the current frame
        active_ids = list(active_exposures.keys())
        for track_id in active_ids:
            if track_id not in current_frame_track_ids:
                # Window closed
                data = active_exposures.pop(track_id)
                duration = current_time_sec - data['start_time']
                
                completed_exposures.append({
                    'id': track_id,
                    'class': data['class'],
                    'start': data['start_time'],
                    'end': current_time_sec,
                    'duration': duration
                })
                print(f"  -> Target ID {track_id} lost. Exposure: {duration:.2f}s")

        frame_idx += 1

    # End of video: Close any remaining windows
    final_time = frame_idx / fps
    for track_id, data in active_exposures.items():
        duration = final_time - data['start_time']
        completed_exposures.append({
            'id': track_id,
            'class': data['class'],
            'start': data['start_time'],
            'end': final_time,
            'duration': duration
        })
        print(f"  -> Video ended. Target ID {track_id} exposure closed. Duration: {duration:.2f}s")

    cap.release()

    # --- Post-Processing: Merge Fragmented Exposures ---
    print("\nPost-processing: Merging fragmented exposures (gap < 0.5s)...")
    merged_exposures = merge_exposures(completed_exposures, gap_threshold=0.5)
    
    # --- Visualization: Generate Timeline ---
    timeline_path = os.path.join(OUTPUT_DIR, "exposure_timeline.png")
    print(f"Generating timeline visualization: {timeline_path}")
    generate_timeline(merged_exposures, timeline_path)

    # --- Final Report ---
    print("\n" + "="*60)
    print("TACTICAL VULNERABILITY REPORT (MERGED)")
    print("="*60)
    
    # Separate Head vs Body (using merged data)
    head_classes = ['CT_HEAD', 'T_HEAD', 'CT_head', 'T_head']
    
    head_exposures = []
    body_exposures = []
    
    for exp in merged_exposures:
        # Check if class name contains 'HEAD' (case insensitive)
        if exp['class'] in head_classes or 'HEAD' in exp['class'].upper():
            head_exposures.append(exp)
        else:
            body_exposures.append(exp)
            
    print(f"Total Distinct Targets: {len(set(e['id'] for e in merged_exposures))}")
    print(f"Total Exposure Events: {len(merged_exposures)}")
    print("-" * 60)

    def print_table(exposures, title):
        if not exposures:
            return
        print(f"\n{title}")
        print(f"{'ID':<5} | {'Class':<10} | {'Start':<8} | {'End':<8} | {'Duration':<10} | {'Tactical Category'}")
        print("-" * 75)
        for exp in exposures:
            category = get_tactical_category(exp['duration'])
            print(f"{exp['id']:<5} | {exp['class']:<10} | {exp['start']:<8.2f} | {exp['end']:<8.2f} | {exp['duration']:<10.2f} | {category}")
        print("-" * 75)

    if body_exposures:
        print_table(body_exposures, "BODY EXPOSURES (Full Target)")

    if head_exposures:
        print_table(head_exposures, "HEAD EXPOSURES (Partial Target)")
            
    if not merged_exposures:
        print("No opponents detected.")
            
    print("="*60)
    print(f"Engagement frames saved to: {os.path.abspath(OUTPUT_DIR)}")
    print(f"Timeline chart saved to: {os.path.abspath(timeline_path)}")

if __name__ == "__main__":
    analyze_exposure()

This project is a comprehensive toolkit designed to conduct and analyze **Just Noticeable Difference (JND)** experiments for human auditory frequency perception. It includes tools for generating precise audio stimuli, creating instructional and explanatory visualizations using Manim, batch-processing video files, and analyzing survey results with automated scoring and data visualization.

It is part of the SMC - Music Perception and Cognition Project 2025-2026 by Olly, Jenny and Yuhang


---

## 📂 Project Structure

### 1. Audio Generation (`/audio`)

* **`make_audio_record.py`**: The primary engine for generating JND test batteries. It creates randomized pairs of sine waves at specific center frequencies (e.g., 200Hz, 1000Hz, 5000Hz) and logs the correct "Answer Key" to a CSV.
* **`make_audio.py`**: A utility script for generating audio clips by decreasing frequency differences at set intervals.
* **`control_volume.py`**: A calibration tool that generates alternating high and low volume sine waves to help participants normalize their listening levels before the test.

### 2. Visuals & Animations (`/visuals`)

* **`intro.py`**: A Manim script that generates an introductory video explaining the survey rules and the concept of JND.
* **`Whole_audio.py`**: Provides a visual representation of the 4-pair audio structure, using horizontal lines to represent high/low pitch patterns.
* **`make_anima.py`**: Creates a dynamic trend-line visualization showing how frequency levels change across different segments.
* **`make_Video.py`**: A utility script using **FFmpeg** to batch-combine generated WAV files with a static background image to create MP4 videos for survey platforms.

### 3. Data Analysis (`/analysis`)

* **`judge.py`**: A robust processing script that reads raw survey exports (CSV), maps them against the randomized answer keys, and calculates error counts for every frequency delta.
* **`plot.py`**: Generates individual performance reports for each participant. It produces a three-panel bar chart (200Hz, 1000Hz, 5000Hz) showing error counts relative to the frequency difference.

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.8+**
* **FFmpeg** (for video synthesis)
* **Required Libraries**:
```bash
pip install numpy scipy pandas matplotlib manim

```



### Workflow

1. **Calibration**: Run `control_volume.py` to produce a `calibration200HZ.wav` file for users.
2. **Generate Stimuli**: Run `make_audio_record.py`. Enter your desired center frequency and step size. This will output a folder of `.wav` files and a `_result_record.csv`.
3. **Create Survey Videos**: Use `make_Video.py` to convert those WAVs into MP4s for easier web playback.
4. **Analyze Results**: Place your survey response CSV in the directory and run `judge.py` to grade the responses, followed by `plot.py` to visualize the JND thresholds.

---

## 📊 Analysis Outputs

The analysis scripts output a `final_scored_grouped.csv` which organizes results by:

* **Metadata**: User ID, device type, and duration.
* **Frequency Deltas**: Error counts for specific differences (e.g., a "2 (200Hz)" column shows errors when the difference was only 2Hz at a 200Hz base).
* **Visual Reports**: PNG files named by User ID showing their specific "Error Curve."


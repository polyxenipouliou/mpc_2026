
# mpc_2026 — Frequency JND Survey Toolkit

A small Python toolkit to **run a frequency discrimination (JND) survey** end-to-end:
- generate **tone-pair WAV stimuli** (with randomized order + answer keys),
- create **instruction animations** (Manim) for participants,
- optionally package WAVs into **MP4** (static image + audio) for survey platforms,
- **clean / translate** exported survey CSVs,
- **score** responses and **plot** per-participant error profiles.

---

## What the audio looks like (stimulus design)

Each “audio clip” contains **4 pairs**.  
Each pair is:

- 200 ms silence
- 500 ms tone #1
- 200 ms silence
- 500 ms tone #2
- followed by extra silence padding (several 200 ms blanks)

Participants answer, for each pair: **which tone is higher** (“First” / “Second”). :contentReference[oaicite:0]{index=0}

---

## Requirements

### Python
- Python 3.9+ recommended
- Packages:
  - `numpy`, `scipy`
  - `pandas`
  - `matplotlib`
  - `manim` (only if you want the animations)

### System tools
- **FFmpeg**


Install Python deps:
```bash
pip install numpy scipy pandas matplotlib manim
```

---

## Typical workflow (quick start)

### 1) (Optional) Generate a calibration file

Creates a 20s **200 Hz** calibration WAV with alternating loud/quiet segments. 

```bash
python control_volume.py
```

Output:

* `calibration200HZ.wav`

---

### 2) Generate survey audio stimuli (WAV)

#### Option A — interactive generator (simple)

Prompts for center frequency / step / number of pairs, outputs WAVs into a folder named by the center frequency. 

```bash
python make_audio.py
```

#### Option B — recorded generator (recommended)

Edits are made at the top of the script (center frequency, step size, number of pairs, output folder). It also writes a **CSV record** that includes the **answer key string** (e.g., `FSFF`). 

```bash
python make_audio_record.py
```

Outputs:

* `MPC_Audio/*.wav`
* `MPC_Audio/<GROUP_NAME>_result_record.csv`

---

### 3) (Optional) Make instruction animations (Manim)

These scripts render short MP4 instruction clips into `output/videos`:

* `intro.py` (welcome + instructions) 
* `ready_for_your_test.py` (ready screen) 
* `two_sin_wave.py` (visual example with two sine waves) 
* `we_shoose.py` (explains “choose Second”) 
* `Whole_audio.py` (shows a full 4-pair pattern) 
* `make_anima.py` (trend-line visualization demo) 

Run any one:

```bash
python intro.py
python ready_for_your_test.py
python two_sin_wave.py
python we_shoose.py
python Whole_audio.py
python make_anima.py
```

---

### 4) (Optional) Convert WAV → MP4 (static image + audio)

Useful if your survey platform prefers video uploads.

Edit the paths inside `make_Video.py` (the defaults are Windows example paths), then run: 

```bash
python make_Video.py
```

---

### 5) Process survey export CSV (translate + flatten answers)

`transfer.py`:

* handles typical Chinese-encoded exports,
* translates metadata columns to English,
* collapses “Pair 1-First/Second/Equal” style columns into a single value per pair. 

```bash
python transfer.py
```

Output:

* `processed_data_english.csv`

---

### 6) Score the survey (error counts by ΔHz)

`judge.py`:

* uses a **hard-coded answer key** for three parts:

  * center 200 Hz
  * center 1000 Hz
  * center 5000 Hz
* computes error counts (0–4) for each audio block and groups them into columns like `8 (1000Hz)` where `8` is `|f - center|`. 

**Important:** the scoring assumes the CSV audio blocks appear in this order:

* `Audio 1..10` → Part A (200 Hz)
* `Audio 1.1..10.1` → Part B (1000 Hz)
* `Audio 1.2..10.2` → Part C (5000 Hz) 

Run:

```bash
python judge.py
```

Output:

* `final_scored_grouped.csv`

---

### 7) Plot per-participant results

`plot.py` generates bar charts (one PNG per participant), showing error counts across ΔHz for each center frequency group. 

```bash
python plot.py
```

Outputs:

* `1.png`, `2.png`, `3.png`, ...

---

## Notes / customization

* Change experiment parameters in `make_audio_record.py` (`CENTER_FREQ`, `STEP_HZ`, `NUM_PAIRS`, etc.). 
* If you change stimuli generation/order, you **must update the answer key** inside `judge.py` to match your survey’s audio ordering. 
* `plot.py` sets a Chinese-capable font list; if you don’t have those fonts installed, adjust `plt.rcParams['font.sans-serif']`. 

---

## License

Add your license here (MIT/Apache-2.0/etc.).


## 📜 License
This project is licensed under the [MIT License](LICENSE).  
Copyright (c) 2026 Olly, Jenny and Johann


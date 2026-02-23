import numpy as np
from scipy.io.wavfile import write
import random
import os
import csv

# ==========================================
# ## Parameter Definitions (User Configuration)
# ==========================================

# 1. Basic Audio Parameters
SAMPLE_RATE = 44100  # Sampling rate
DURATION_200MS = int(0.2 * SAMPLE_RATE)  # Interval/Blank: 200ms
DURATION_500MS = int(0.5 * SAMPLE_RATE)  # Tone duration: 500ms
BLANK_SIGNAL = np.zeros(DURATION_200MS)  # Blank signal data

# 2. Experiment Parameters
CENTER_FREQ = 5000  # Center frequency (Hz)
STEP_HZ = 6  # Step size (Hz)
NUM_PAIRS = 10  # Number of frequency pairs to generate
GROUP_NAME = "5000"  # Group name (used for file naming, e.g., A1.wav)
OUTPUT_DIR = "MPC_Audio"  # Output folder name


# ==========================================
# ## Core Logic
# ==========================================

def generate_sine_wave(frequency, duration):
    """Generate a sine wave with specified frequency and duration."""
    t = np.linspace(0, duration / SAMPLE_RATE, duration, endpoint=False)
    # Use float32 to prevent overflow during calculation; convert to int16 at the end
    return np.sin(2 * np.pi * frequency * t).astype(np.float32)


def create_audio_for_pair(center_freq, comp_freq):
    """
    Generate an audio clip containing 4 comparison pairs.

    Args:
        center_freq: Center frequency (High pitch)
        comp_freq: Comparison frequency (Low pitch)

    Returns:
        1. full_audio: The synthesized audio data
        2. code_str: A string like "FSFF"
           - F (First): The first tone is higher (High, Low)
           - S (Second): The second tone is higher (Low, High)
    """
    audio_segments = []
    code_str_parts = []

    for _ in range(4):  # Repeat each pair 4 times
        # Randomly decide the order
        # Case: (center, comp) = (High, Low) -> First is Higher -> F
        # Case: (comp, center) = (Low, High) -> Second is Higher -> S

        is_first_high = random.choice([True, False])

        if is_first_high:
            freq_1, freq_2 = center_freq, comp_freq
            code = "F"
        else:
            freq_1, freq_2 = comp_freq, center_freq
            code = "S"

        segment = np.concatenate([
            BLANK_SIGNAL,
            generate_sine_wave(freq_1, DURATION_500MS),
            BLANK_SIGNAL,
            generate_sine_wave(freq_2, DURATION_500MS),
            BLANK_SIGNAL,
            BLANK_SIGNAL,
            BLANK_SIGNAL,
            BLANK_SIGNAL
        ])
        audio_segments.append(segment)
        code_str_parts.append(code)

    full_audio = np.concatenate(audio_segments)
    code_str = "".join(code_str_parts)
    return full_audio, code_str


def main():
    random.seed(None)  # Set to None for true randomness on each run; set to a fixed number for reproducibility

    # 1. Prepare output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created folder: {OUTPUT_DIR}")
    else:
        print(f"Using existing folder: {OUTPUT_DIR}")

    # 2. Generate frequency pool and shuffle randomly
    # Logic: Center Frequency - (i * Step Size)
    freq_pool = []
    for i in range(NUM_PAIRS):
        diff = (i + 1) * STEP_HZ
        current_comp_freq = CENTER_FREQ - diff
        freq_pool.append(current_comp_freq)

    # Shuffle the frequency list (e.g., from [199, 198, 197] to [197, 199, 198])
    random.shuffle(freq_pool)
    print(f"Generated random frequency order (comparison frequencies): {freq_pool}")

    # 3. Prepare CSV data
    csv_headers = ["Filename", "Center_Freq(Hz)", "Comp_Freq(Hz)", "Answer_Key(FSFF)"]
    csv_rows = []

    # 4. Loop to generate audio files
    print("-" * 30)
    for idx, comp_freq in enumerate(freq_pool, 1):  # idx starts from 1

        # Generate audio and answer code
        audio_data, answer_code = create_audio_for_pair(CENTER_FREQ, comp_freq)
        # Filename: GroupName-Index-CompFreq-AnswerCode.wav (e.g., A1-1-4994-FSFF.wav)
        filename = f"{GROUP_NAME}-{idx}-{comp_freq}-{answer_code}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Convert to 16-bit PCM and save
        final_audio = np.int16(audio_data * 32767)
        write(filepath, SAMPLE_RATE, final_audio)

        # Log information
        print(f"[{idx}/{NUM_PAIRS}] Generated: {filename} | Comparison: {comp_freq:.1f}Hz | Answer: {answer_code}")

        csv_rows.append([filename, CENTER_FREQ, comp_freq, answer_code])

    # 5. Write to CSV file
    csv_path = os.path.join(OUTPUT_DIR, f"{GROUP_NAME}_result_record.csv")
    with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        writer.writerows(csv_rows)

    print("-" * 30)
    print(f"Processing complete! All audio files and CSV records saved to: {OUTPUT_DIR}")
    print(f"CSV file path: {csv_path}")


if __name__ == "__main__":
    main()
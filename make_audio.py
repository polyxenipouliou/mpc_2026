import numpy as np
from scipy.io.wavfile import write
import random
import os

# Parameter definitions
SAMPLE_RATE = 44100  # Sampling rate
DURATION_200MS = int(0.2 * SAMPLE_RATE)  # 200ms duration
DURATION_500MS = int(0.5 * SAMPLE_RATE)  # 500ms duration
BLANK = np.zeros(DURATION_200MS)  # 200ms blank signal

def generate_sine_wave(frequency, duration):
    """Generate a sine wave with the specified frequency and duration."""
    t = np.linspace(0, duration / SAMPLE_RATE, duration, endpoint=False)
    return np.sin(2 * np.pi * frequency * t)

def create_audio_for_pair(freq_A, freq_B):
    """Generate audio for a given frequency pair, returning the full audio clip and the corresponding sequence description."""
    audio_segments = []
    order_str_parts = []  # Store string parts of the frequency order

    for _ in range(4):  # Repeat each audio four times
        order = random.choice([(freq_A, freq_B), (freq_B, freq_A)])  # Randomly choose frequency order
        segment = np.concatenate([
            BLANK,
            generate_sine_wave(order[0], DURATION_500MS),
            BLANK,
            generate_sine_wave(order[1], DURATION_500MS),
            BLANK,
            BLANK,
            BLANK,
            BLANK
        ])
        audio_segments.append(segment)
        order_str_parts.append(f"-{order[0]:.0f}{order[1]:.0f}-")  # Record current order

    # Concatenate all audio segments
    full_audio = np.concatenate(audio_segments)
    order_str = "".join(order_str_parts)  # Join all orders into a string (e.g., "ABBAABAB")
    return full_audio, order_str

def main(input_frequency, step, output_dir="output", num=10):
    """Main function: Generate several frequency pairs and synthesize audio by decreasing frequency difference with a set step."""
    random.seed(42)  # Set random seed for reproducibility
    os.makedirs(output_dir, exist_ok=True)  # Create output directory

    frequency_pairs = []

    # Generate 'num' frequency pairs, with each step differing by 'step' Hz
    for i in range(num):
        diff = (i + 1) * step  # Gradually increase the difference starting from 'step'
        freq_B = input_frequency - diff
        frequency_pairs.append((input_frequency, freq_B))

    # Synthesize audio for each frequency pair
    for idx, (freq_A, freq_B) in enumerate(frequency_pairs):
        print(f"Processing pair {idx + 1}: A={freq_A:.2f} Hz, B={freq_B:.2f} Hz")
        audio, order_str = create_audio_for_pair(freq_A, freq_B)
        final_audio = np.int16(audio * 32767)  # Convert to 16-bit PCM format

        # Filename format: pair_index_A_freq_B_freq_order_sequence.wav
        output_filename = f"pair_{idx + 1}_A{freq_A:.2f}_B{freq_B:.2f}_order_{order_str}.wav"
        output_path = os.path.join(output_dir, output_filename)

        write(output_path, SAMPLE_RATE, final_audio)
        print(f"Audio file saved to: {output_path}")

if __name__ == "__main__":
    input_freq = float(input("Please enter the center frequency (Hz): "))
    input_step = int(input("Please enter the step size (Hz): "))
    input_num = int(input("Please enter the number of frequency pairs to generate: "))
    main(input_freq, input_step, output_dir=str(int(input_freq)), num=input_num)
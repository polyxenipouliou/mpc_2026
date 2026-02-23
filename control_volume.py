import numpy as np
from scipy.io.wavfile import write

# Parameter settings
sample_rate = 44100       # Sampling rate (Hz)
duration_total = 20       # Total duration (seconds)
freq = 200                # Frequency (Hz)
segment_duration = 0.3    # Segment duration (seconds)
interval = 0.3            # Interval (seconds)
volume_high = 0.2         # High volume
volume_low = 0.000719     # Low volume

# Calculate the number of samples per segment, interval, and cycle
samples_per_segment = int(sample_rate * segment_duration)
samples_per_interval = int(sample_rate * interval)
samples_per_cycle = samples_per_segment + samples_per_interval

# Calculate the total number of cycles
num_cycles = int(duration_total / (segment_duration + interval))

# Build the time axis and audio data
t = np.linspace(0, segment_duration, samples_per_segment, False)

# Generate sine wave template
sine_wave = np.sin(2 * np.pi * freq * t)

# Initialize audio array
audio_data = np.array([], dtype=np.float32)

# Loop to generate alternating high and low volume audio segments
for i in range(num_cycles):
    volume = volume_high if i % 2 == 0 else volume_low
    segment = sine_wave * volume
    # Append audio segment
    audio_data = np.concatenate((audio_data, segment))
    # Append silent interval
    audio_data = np.concatenate((audio_data, np.zeros(samples_per_interval)))

# Pad with silence if total duration is less than 20 seconds
total_samples_needed = sample_rate * duration_total
if len(audio_data) < total_samples_needed:
    padding = np.zeros(total_samples_needed - len(audio_data))
    audio_data = np.concatenate((audio_data, padding))

# Normalize to [-1, 1]
audio_data = audio_data / np.max(np.abs(audio_data))

# Save as WAV file
write("calibration200HZ.wav", sample_rate, audio_data)

print("Audio saved as calibration200HZ.wav")
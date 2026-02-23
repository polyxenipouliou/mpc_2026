import os
import subprocess

def combine_wav_and_png_to_mp4(wav_folder, png_path, output_folder):
    """
    Batch combine WAV files with a PNG image into MP4 files.

    :param wav_folder: Path to the folder containing WAV files
    :param png_path: Path to the PNG image
    :param output_folder: Path to the folder for output MP4 files
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all WAV files in the input folder
    for wav_file in os.listdir(wav_folder):
        if wav_file.lower().endswith(".wav"):  # Ensure only WAV files are processed
            wav_path = os.path.join(wav_folder, wav_file)
            output_name = os.path.splitext(wav_file)[0][:26] + ".mp4"  # Replace .wav with .mp4
            output_path = os.path.join(output_folder, output_name)

            # Build the FFmpeg command
            command = [
                "ffmpeg",
                "-loop", "1",                    # Loop the static image
                "-i", png_path,                   # Input image
                "-i", wav_path,                   # Input audio
                "-c:v", "libx264",                # Video codec
                "-tune", "stillimage",            # Optimize for still images
                "-c:a", "aac",                    # Audio codec
                "-b:a", "192k",                   # Audio bitrate
                "-shortest",                      # Match video length to audio
                output_path                       # Output file path
            ]

            # Execute the FFmpeg command
            try:
                print(f"Processing: {wav_file}")
                subprocess.run(command, check=True)
                print(f"Finished: {output_name}")
            except subprocess.CalledProcessError as e:
                print(f"Error processing {wav_file}: {e}")

# Main function
if __name__ == "__main__":
    # Set paths
    wav_folder = r"D:\Python_All\Util\Master_Util\call"      # Folder containing WAV files
    png_path = r"D:\Python_All\Util\Master_Util\MPC\black.png"         # Static image path
    output_folder = r"D:\Python_All\Util\Master_Util\MPC\call"  # Folder for output MP4 files

    # Call the function
    combine_wav_and_png_to_mp4(wav_folder, png_path, output_folder)
import librosa
import numpy as np
import soundfile as sf
import random

def extract_random_segment(input_wav, output_wav, segment_duration=5):
    # Load the audio file
    y, sr = librosa.load(input_wav, sr=None)  # Load with original sample rate
    total_duration = librosa.get_duration(y=y, sr=sr)

    if total_duration <= segment_duration:
        print("Audio file is too short for a random segment. Copying entire file.")
        sf.write(output_wav, y, sr)
        return

    # Compute random start time
    max_start_time = total_duration - segment_duration
    start_time = random.uniform(0, max_start_time)

    # Convert start time to sample index
    start_sample = int(start_time * sr)
    end_sample = start_sample + int(segment_duration * sr)

    # Extract the segment
    segment = y[start_sample:end_sample]

    # Save the segment as a new WAV file
    sf.write(output_wav, segment, sr)
    print(f"Extracted segment from {start_time:.2f} to {start_time + segment_duration:.2f} seconds.")

# Example usage
input_wav = "input.wav"  # Change this to your WAV file path
output_wav = "output_segment.wav"
extract_random_segment(input_wav, output_wav)
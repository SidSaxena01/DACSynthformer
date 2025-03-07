#!/bin/bash

# Check if input and output directories are provided
if [[ $# -ne 2 ]]; then
  echo "Usage: bash $0 <input_directory> <output_directory>"
  exit 1
fi

input_dir="$1"
output_dir="$2"

# Ensure input directory exists
if [[ ! -d "$input_dir" ]]; then
  echo "Error: Input directory does not exist."
  exit 1
fi

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through all supported audio files in the input directory
for file in "$input_dir"/*.{mp3,wav,flac,aac,m4a,ogg,opus}; do
  # Skip if no matching files exist
  [ -e "$file" ] || continue
  
  filename=$(basename "$file")  # Extract filename
  filename="${filename%.*}"  # Remove file extension

  # Get duration in seconds using ffprobe
  duration=$(ffprobe -i "$file" -show_entries format=duration -v quiet -of csv="p=0")
  total_seconds=$(printf "%.0f" "$duration")  # Convert to integer

  if [[ $total_seconds -gt 5 ]]; then
    max_start_time=$((total_seconds - 5))  # Maximum possible start time
    
    # Cross-platform random number generation (0 to max_start_time)
    if [[ "$OSTYPE" == "darwin"* || "$OSTYPE" == "linux-gnu"* ]]; then
      start_time=$(( RANDOM % (max_start_time + 1) ))
    else
      start_time=$(awk -v min=0 -v max=$max_start_time 'BEGIN{srand(); print int(min+rand()*(max-min+1))}')
    fi

    ffmpeg -i "$file" -ss "$start_time" -t 5 -ar 44100 -ac 1 -acodec pcm_s16le "$output_dir/${filename}.wav"
    echo "Processed: $file → $output_dir/${filename}.wav"
  else
    echo "Skipping: $file (Too short for a 5-second clip)"
  fi
done
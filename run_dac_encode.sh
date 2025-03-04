#!/bin/bash

python3 $(dirname "$0")/dac_encode_cpu.py \
  --input_dir '/Users/sid/Music/OST/Dark Cloud Soundtrack 8-bit Remix/wav' \
  --output_dir '/Users/sid/Music/OST/Dark Cloud Soundtrack 8-bit Remix/dac' \
  --model_bitrate '8kbps' \
  --n_quantizers 4 \
  --device 'cpu'

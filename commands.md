# Commands for Preprocessing of Dataset

## Conversion from MP3 to WAV

This script converts all MP3 files in the current directory to WAV format.
It extracts a random 5-second clip from each MP3 file and saves it as a WAV file.
The output files are saved in the "wav" directory.

```bash
bash convert_audio.sh
```

## Encode the wav files to DAC

```bash
python3 scripts/dac_encode.py --input_dir '/wav/' --output_dir '/dac/' --class-name [class-name] --randomize_param1
```

## Rename dac files and delete subdirectories

```bash
python3 scripts/rename_files.py --target_dir '/dac'
```

## Rename dac files to work around duplicates

```bash
python3 scripts/rename_files.py --target_dir '/dac'
```

## Create Excel file from DAC files for Training with required format

```bash
python3 scripts/testdata/fname2Pandas.py 'data/dac-raw' 'data/dac-train.xlsx' 
```

## Split Excel File with DAC files into Train and Test Splits

```bash
python3 scripts/split_excel_data.py data/dac-train.xlsx --samples 50 --seed 123456
```

## Reorganize DAC files from raw directory into Train and Test Splits based on Excel

```bash
python3 scripts/reorganize_dac_files.py --train-excel data/dac-train.xlsx --val-excel data/dac-val.xlsx --source-dir data/dac-raw --train-dir data/dac-train --val-dir data/dac-val
```

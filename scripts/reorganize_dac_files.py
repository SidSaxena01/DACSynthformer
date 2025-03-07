import os
import shutil
import pandas as pd
import argparse
from tqdm import tqdm

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Reorganize .dac files according to train/val splits defined in Excel files')
    
    parser.add_argument('--train-excel', type=str, required=True, help='Path to the training Excel file')
    parser.add_argument('--val-excel', type=str, required=True, help='Path to the validation Excel file')
    parser.add_argument('--source-dir', type=str, default='data/dac-raw', help='Source directory containing .dac files')
    parser.add_argument('--train-dir', type=str, default='data/dac-train', help='Destination directory for training files')
    parser.add_argument('--val-dir', type=str, default='data/dac-val', help='Destination directory for validation files')
    parser.add_argument('--move', action='store_true', help='Move files instead of copying them')
    
    args = parser.parse_args()
    
    # Create destination directories if they don't exist
    os.makedirs(args.train_dir, exist_ok=True)
    os.makedirs(args.val_dir, exist_ok=True)
    
    # Read excel files
    print("Reading Excel files...")
    try:
        train_df = pd.read_excel(args.train_excel)
        val_df = pd.read_excel(args.val_excel)
        
        # Extract file names
        train_files = train_df['Full File Name'].tolist()
        val_files = val_df['Full File Name'].tolist()
        
        print(f"Found {len(train_files)} training files and {len(val_files)} validation files")
        
    except Exception as e:
        print(f"Error reading Excel files: {e}")
        return
    
    # Verify that files exist
    all_files = os.listdir(args.source_dir)
    missing_train = [f for f in train_files if f not in all_files]
    missing_val = [f for f in val_files if f not in all_files]
    
    if missing_train:
        print(f"Warning: {len(missing_train)} training files not found in source directory")
        if len(missing_train) < 10:
            print(f"Missing files: {missing_train}")
    
    if missing_val:
        print(f"Warning: {len(missing_val)} validation files not found in source directory")
        if len(missing_val) < 10:
            print(f"Missing files: {missing_val}")
    
    # Function to process files
    def process_files(file_list, dest_dir, desc):
        print(f"Processing {desc} files...")
        
        for file_name in tqdm(file_list):
            src_path = os.path.join(args.source_dir, file_name)
            dest_path = os.path.join(dest_dir, file_name)
            
            if os.path.exists(src_path):
                if args.move:
                    shutil.move(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
            else:
                print(f"Warning: File not found: {src_path}")
    
    # Process files
    process_files(train_files, args.train_dir, "training")
    process_files(val_files, args.val_dir, "validation")
    
    print("Done!")

if __name__ == "__main__":
    main()

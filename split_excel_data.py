import pandas as pd
import numpy as np
import os
import argparse

def create_train_val_split(input_excel_path, output_dir=None, samples_per_class=25, train_ratio=0.8, random_seed=42):
    """
    Takes samples from each class and splits them into train and validation Excel files.
    
    Args:
        input_excel_path (str): Path to the input Excel file
        output_dir (str, optional): Directory to save output files. Defaults to same directory as input.
        samples_per_class (int, optional): Number of samples to take from each class. Defaults to 25.
        train_ratio (float, optional): Ratio of samples to put in training set. Defaults to 0.8.
        random_seed (int, optional): Random seed for reproducibility. Defaults to 42.
    """
    # Set random seed for reproducibility
    np.random.seed(random_seed)
    
    # Read the Excel file
    df = pd.read_excel(input_excel_path)
    
    # Use 'Class Name' as the class column
    class_column = 'Class Name'
    
    # Get unique classes
    unique_classes = df[class_column].unique()
    
    train_samples = []
    val_samples = []
    
    # Calculate exact counts for train and validation
    train_count = int(samples_per_class * train_ratio)
    val_count = samples_per_class - train_count
    
    print(f"For each class: {train_count} samples for training, {val_count} samples for validation")
    
    # For each class, sample and split
    for cls in unique_classes:
        # Get all samples of this class
        class_samples = df[df[class_column] == cls]
        
        # Check if we have enough samples
        if len(class_samples) < samples_per_class:
            print(f"Warning: Class {cls} has only {len(class_samples)} samples, fewer than the requested {samples_per_class}")
            if len(class_samples) == 0:
                print(f"Skipping class {cls} as it has no samples")
                continue
                
            # Adjust counts proportionally
            adjusted_train = max(1, int(len(class_samples) * train_ratio))
            adjusted_val = len(class_samples) - adjusted_train
            sampled_data = class_samples
        else:
            # Sample randomly without replacement
            sampled_data = class_samples.sample(n=samples_per_class, random_state=random_seed)
            adjusted_train = train_count
            adjusted_val = val_count
        
        # Split into train and validation
        train_data = sampled_data.sample(n=adjusted_train, random_state=random_seed)
        val_data = sampled_data.drop(train_data.index)
        
        # Add to respective lists
        train_samples.append(train_data)
        val_samples.append(val_data)
    
    # Combine all samples
    train_df = pd.concat(train_samples, ignore_index=True)
    val_df = pd.concat(val_samples, ignore_index=True)
    
    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(input_excel_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to Excel files
    train_path = os.path.join(output_dir, 'dac-train.xlsx')
    val_path = os.path.join(output_dir, 'dac-val.xlsx')
    
    train_df.to_excel(train_path, index=False)
    val_df.to_excel(val_path, index=False)
    
    print(f"\nCreated training set with {len(train_df)} samples at {train_path}")
    print(f"Created validation set with {len(val_df)} samples at {val_path}")
    
    # Verify class distribution
    print("\nClass distribution:")
    for cls in unique_classes:
        train_count = train_df[train_df[class_column] == cls].shape[0]
        val_count = val_df[val_df[class_column] == cls].shape[0]
        total = train_count + val_count
        if total > 0:  # Avoid division by zero
            print(f"Class {cls}: {train_count} train ({train_count/total:.1%}), {val_count} val ({val_count/total:.1%})")
        else:
            print(f"Class {cls}: No samples")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Split Excel data into train and validation sets.')
    parser.add_argument('input_file', help='Path to the input Excel file')
    parser.add_argument('--output-dir', help='Directory to save output files')
    parser.add_argument('--samples', type=int, default=25, help='Number of samples per class')
    parser.add_argument('--train-ratio', type=float, default=0.8, help='Ratio of samples for training')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    create_train_val_split(
        args.input_file,
        args.output_dir,
        args.samples,
        args.train_ratio,
        args.seed
    )

import os
import re
import glob

def rename_dac_files(directory):
    """
    Renames DAC files by keeping only the pattern "Zelda--param1-00.XX" 
    (where XX is a decimal between 0 and 1) and the .dac extension.
    """
    # Get all .dac files in the directory
    dac_files = glob.glob(os.path.join(directory, "*.dac"))
    
    # Regular expression to match the pattern we want to extract
    pattern = r"(Zelda--param1-\d+\.\d+).*?(\.dac)"
    
    for old_path in dac_files:
        filename = os.path.basename(old_path)
        
        # Apply the regex pattern
        match = re.match(pattern, filename)
        
        if match:
            # Extract the parts we want to keep
            base = match.group(1)
            ext = match.group(2)
            
            # Create the new filename
            new_filename = base + ext
            new_path = os.path.join(directory, new_filename)
            
            if old_path != new_path:
                if os.path.exists(new_path):
                    print(f"Warning: {new_filename} already exists, skipping {filename}")
                else:
                    print(f"Renaming {filename} -> {new_filename}")
                    os.rename(old_path, new_path)
        else:
            print(f"Warning: {filename} does not match the expected pattern, skipping")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.path.join("data", "dac-raw")
    
    if os.path.exists(directory):
        rename_dac_files(directory)
        print(f"Successfully processed files in {directory}")
    else:
        print(f"Error: Directory {directory} does not exist")

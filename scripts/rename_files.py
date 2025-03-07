#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Rename files by moving them out of subdirectories")
    parser.add_argument(
        "--target_dir", "--target-dir", default=".", help="Directory containing the dac subdirectories (default: current directory)"
    )
    args = parser.parse_args()
    
    base_dir = Path(args.target_dir)
    if not base_dir.exists():
        logger.error(f"Target directory {base_dir} does not exist.")
        return

    for subdir in base_dir.iterdir():
        if subdir.is_dir() and subdir.name.endswith(".dac"):
            files = list(subdir.glob("*"))
            if len(files) == 0:
                logger.info(f"Directory {subdir} is empty, removing it")
                subdir.rmdir()
            elif len(files) == 1 and files[0].is_file():
                # Handle the single file case as before
                src_file = files[0]
                dest_file = base_dir / subdir.name
                # Append a suffix if destination exists
                if dest_file.exists():
                    suffix = 1
                    new_dest = base_dir / f"{subdir.name}_{suffix}"
                    while new_dest.exists():
                        suffix += 1
                        new_dest = base_dir / f"{subdir.name}_{suffix}"
                    dest_file = new_dest
                logger.info(f"Renaming {src_file} to {dest_file}")
                shutil.move(str(src_file), str(dest_file))
                subdir.rmdir()
            else:
                # Handle multiple files in directory
                logger.info(f"Directory {subdir} contains {len(files)} files, processing each file")
                for file in files:
                    if file.is_file():
                        # Create a filename that combines directory name and original filename
                        new_filename = f"{subdir.stem}--{file.name}"
                        dest_file = base_dir / new_filename
                        
                        # Handle destination file already existing
                        if dest_file.exists():
                            suffix = 1
                            new_dest = base_dir / f"{new_filename}_{suffix}"
                            while new_dest.exists():
                                suffix += 1
                                new_dest = base_dir / f"{new_filename}_{suffix}"
                            dest_file = new_dest
                            
                        logger.info(f"Moving {file} to {dest_file}")
                        shutil.move(str(file), str(dest_file))
                
                # Check if directory is now empty before trying to remove it
                remaining_files = list(subdir.glob("*"))
                if not remaining_files:
                    logger.info(f"Removing now-empty directory {subdir}")
                    subdir.rmdir()
                else:
                    logger.warning(f"Directory {subdir} still contains {len(remaining_files)} items, not removing")

if __name__ == "__main__":
    main()

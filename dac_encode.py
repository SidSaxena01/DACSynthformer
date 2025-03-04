#!/usr/bin/env python3
import argparse
import logging
import random
import warnings
from pathlib import Path

import torch
from dac.utils.encode import encode

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Suppress the weight_norm deprecation warning
warnings.filterwarnings("ignore", message=".*weight_norm is deprecated.*")


def get_available_device(requested_device):
    """Determine the best available device, with fallback to CPU."""
    # If user explicitly specified a device other than 'auto', use that
    if requested_device.lower() != "auto":
        logger.info(f"Using user-specified device: {requested_device}")
        return requested_device

    # Check for MPS (Apple Silicon) support
    if torch.backends.mps.is_available():
        try:
            # Test MPS device creation
            logger.info("MPS (Apple Silicon) device detected, attempting to use it...")
            test_tensor = torch.zeros(1).to("mps")
            logger.info("MPS device is working properly")
            return "mps"
        except Exception as e:
            logger.warning(f"MPS device failed initialization: {e}")

    # Check for CUDA
    if torch.cuda.is_available():
        try:
            test_tensor = torch.zeros(1).to("cuda")
            logger.info("CUDA device is working properly")
            return "cuda"
        except Exception as e:
            logger.warning(f"CUDA device failed initialization: {e}")

    # Fallback to CPU
    logger.info("Using CPU as fallback device")
    return "cpu"


def format_param_value(value):
    """Format parameter value to have consistent formatting (e.g., 0.5 becomes '00.50')"""
    # Ensure value is between 0 and 1
    value = max(0.0, min(1.0, value))
    # Format to 2 decimal places with leading zeros before decimal point
    return f"{value:05.2f}"[
        :5
    ]  # 05.2f gives format like 00.50, slice to ensure it's 5 chars


def generate_output_filename(original_name, class_name, param1):
    """Generate output filename based on class name and parameter value"""
    # Format param1 with proper formatting
    formatted_param1 = format_param_value(param1)

    # Create filename following the pattern: {className}--param1-{paramValue}
    return f"{class_name}--param1-{formatted_param1}.dac"


def main():
    parser = argparse.ArgumentParser(
        description="Encode audio using DAC with automatic device selection"
    )
    parser.add_argument(
        "--input_dir",
        "--input-dir",
        required=True,
        help="Directory containing input audio files",
    )
    parser.add_argument(
        "--output_dir",
        "--output-dir",
        required=True,
        help="Directory for output encoded files",
    )
    parser.add_argument(
        "--model_bitrate",
        "--model-bitrate",
        default="8kbps",
        help="Model bitrate (default: 8kbps)",
    )
    parser.add_argument(
        "--n_quantizers",
        "--n-quantizers",
        type=int,
        default=4,
        help="Number of quantizers (default: 4)",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help="Device to use (auto, cpu, cuda, mps). Default: auto - will try mps then cpu",
    )
    parser.add_argument(
        "--batch_size",
        "--batch-size",
        type=int,
        default=1,
        help="Batch size (default: 1)",
    )
    # Add new arguments for class name and parameters
    parser.add_argument(
        "--class_name",
        "--class-name",
        required=True,
        help="Class name to use in output filename",
    )
    parser.add_argument(
        "--param1",
        type=float,
        default=1.0,
        help="Parameter 1 value between 0.0 and 1.0 (default: 1.0)",
    )
    parser.add_argument(
        "--randomize_param1",
        "--randomize-param1",
        action="store_true",
        help="Randomize param1 values between 0.0 and 1.0",
    )

    args = parser.parse_args()

    # Ensure param1 is within valid range
    args.param1 = max(0.0, min(1.0, args.param1))

    # Ensure directories exist
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    if not input_dir.exists():
        logger.error(f"Input directory {input_dir} does not exist")
        return

    # Select the best available device or use the explicitly specified one
    device = get_available_device(args.device)

    logger.info(f"Encoding files from {input_dir} to {output_dir}")
    logger.info(f"Using device: {device}")
    logger.info(f"Model bitrate: {args.model_bitrate}")
    logger.info(f"Number of quantizers: {args.n_quantizers}")
    logger.info(f"Class name: {args.class_name}")

    if args.randomize_param1:
        logger.info("Randomizing param1 values between 0.0 and 1.0")
    else:
        logger.info(f"Using param1 value: {args.param1}")

    try:
        # Explicitly disable gradients to save memory
        with torch.no_grad():
            # Check if input_dir is a directory or a single file
            if input_dir.is_dir():
                # Process each file individually to apply the naming convention
                audio_files = list(input_dir.glob("*.wav")) + list(
                    input_dir.glob("*.mp3")
                )
                logger.info(
                    f"Found {len(audio_files)} audio files in directory: {input_dir}"
                )

                for audio_file in audio_files:
                    # Determine parameter value for this file
                    param1 = random.random() if args.randomize_param1 else args.param1

                    # Generate the output filename based on class name and parameter value
                    output_filename = generate_output_filename(
                        audio_file.stem, args.class_name, param1
                    )
                    output_file = output_dir / output_filename

                    logger.info(f"Processing {audio_file.name} -> {output_filename}")
                    encode(
                        input=str(audio_file),
                        output=str(output_file),
                        model_bitrate=args.model_bitrate,
                        n_quantizers=args.n_quantizers,
                        device=device,
                        batch_size=args.batch_size,
                    )

                logger.info(f"All files encoded to: {output_dir}")
            else:
                # Single file processing
                param1 = random.random() if args.randomize_param1 else args.param1
                output_filename = generate_output_filename(
                    input_dir.stem, args.class_name, param1
                )
                output_file = output_dir / output_filename

                encode(
                    input=str(input_dir),
                    output=str(output_file),
                    model_bitrate=args.model_bitrate,
                    n_quantizers=args.n_quantizers,
                    device=device,
                    batch_size=args.batch_size,
                )
                logger.info(f"Encoded single file to: {output_file}")

        logger.info(f"Encoding completed successfully!")
    except AssertionError as e:
        logger.error(f"Assertion error: {e}")
        # If device isn't CPU and we get an error, suggest trying CPU
        if device != "cpu":
            logger.info(f"If {device} error, try again with --device cpu")
    except Exception as e:
        logger.error(f"Error during encoding: {e}")
        import traceback

        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()

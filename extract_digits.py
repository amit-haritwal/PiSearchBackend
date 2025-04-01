import os
from tqdm import tqdm

def extract_digits_to_text(input_file: str, output_file: str, num_digits: int = 1_000_000_000):
    """Extract digits from binary file and save to text file."""
    
    # Calculate number of bytes needed (2 digits per byte)
    num_bytes = num_digits // 2
    
    # Open output file
    with open(output_file, 'w') as f:
        # Process in chunks to manage memory
        chunk_size = 1024 * 1024  # 1MB chunks
        bytes_processed = 0
        
        with open(input_file, 'rb') as input_f:
            with tqdm(total=num_bytes, unit='B', unit_scale=True) as pbar:
                while bytes_processed < num_bytes:
                    # Calculate current chunk size
                    current_chunk = min(chunk_size, num_bytes - bytes_processed)
                    
                    # Read chunk from local file
                    chunk_data = input_f.read(current_chunk)
                    
                    # Process chunk
                    for byte in chunk_data:
                        # Extract two digits from each byte
                        first_digit = (byte >> 4) & 0x0F
                        second_digit = byte & 0x0F
                        f.write(f"{first_digit}{second_digit}")
                    
                    bytes_processed += current_chunk
                    pbar.update(current_chunk)

if __name__ == "__main__":
    INPUT_FILE = "pi_digits.bin"
    OUTPUT_FILE = "pi_dev-2t_02.txt"
    
    print(f"Extracting first billion digits to {OUTPUT_FILE}...")
    extract_digits_to_text(INPUT_FILE, OUTPUT_FILE)
    print("Done!") 
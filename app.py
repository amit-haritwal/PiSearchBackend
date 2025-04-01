import os
import struct
import mmap
import time
from typing import List, Optional
from flask import Flask, request, jsonify

class PiSearch:
    """Python implementation of PiSearch, for searching digits of π."""
    
    def __init__(self, pi_file_path: str):
        """Initialize PiSearch with a path to a binary file containing π digits.
        
        Args:
            pi_file_path: Path to the binary file containing π digits
        """
        self.pi_file_path = pi_file_path
        self._file_size = os.path.getsize(pi_file_path)
        self._num_digits = self._file_size * 2  # Each byte stores 2 digits
        
    @property
    def num_digits(self) -> int:
        """Get the number of digits of π available for searching."""
        return self._num_digits
    
    def _digit_at_position(self, position: int) -> int:
        """Get the digit at a specific position in π.
        
        Args:
            position: Position in π (0-indexed, where 0 is the first digit, 3)
            
        Returns:
            The digit at the specified position
            
        Raises:
            ValueError: If position is out of range or if invalid digit is found
        """
        if position < 0 or position >= self._num_digits:
            raise ValueError(f"Position {position} outside available range of 0-{self._num_digits-1}")
        
        byte_position = position // 2
        
        with open(self.pi_file_path, 'rb') as f:
            f.seek(byte_position)
            byte = f.read(1)[0]
            
        # Each byte contains 2 digits, need to extract the correct one
        digit = (byte >> 4) if position % 2 == 0 else (byte & 0x0F)
        
        # Validate that the digit is in range 0-9
        if not 0 <= digit <= 9:
            raise ValueError(f"Invalid digit {digit} found at position {position}")
            
        return digit
    
    def get_digits(self, start_position: int, count: int) -> List[int]:
        """Get a sequence of digits from π.
        
        Args:
            start_position: Starting position in π (0-indexed)
            count: Number of digits to retrieve
            
        Returns:
            List of digits
            
        Raises:
            ValueError: If start position is out of range or if invalid digits are found
        """
        if start_position < 0 or start_position >= self._num_digits:
            raise ValueError(f"Start position {start_position} outside available range of 0-{self._num_digits-1}")
        
        if start_position + count > self._num_digits:
            count = self._num_digits - start_position
            
        result = []
        byte_start = start_position // 2
        byte_end = (start_position + count - 1) // 2 + 1
        bytes_to_read = byte_end - byte_start
        
        with open(self.pi_file_path, 'rb') as f:
            f.seek(byte_start)
            data = f.read(bytes_to_read)
            
        # Handle first digit if starting at odd position
        position = start_position
        while position < start_position + count:
            byte_position = (position - start_position) // 2
            digit = (data[byte_position] >> 4) if position % 2 == 0 else (data[byte_position] & 0x0F)
            
            # Validate that the digit is in range 0-9
            if not 0 <= digit <= 9:
                raise ValueError(f"Invalid digit {digit} found at position {position}")
                
            result.append(digit)
            position += 1
            
        return result
    
    def _extract_digit_from_byte(self, byte: int, is_first_digit: bool) -> int:
        """Extract a digit from a byte.
        
        Args:
            byte: The byte to extract from
            is_first_digit: True if extracting first digit (upper 4 bits), False for second digit (lower 4 bits)
            
        Returns:
            The extracted digit (0-9)
        """
        digit = (byte >> 4) if is_first_digit else (byte & 0x0F)
        if not 0 <= digit <= 9:
            raise ValueError(f"Invalid digit {digit} extracted from byte {byte}")
        return digit

    def search(self, pattern: List[int], start_position: int = 0) -> int:
        """Search for a pattern in π, starting from a specific position.
        
        Args:
            pattern: List of digits to search for
            start_position: Position to start searching from (0-indexed)
            
        Returns:
            Position where pattern was found, or -1 if not found
            
        Raises:
            ValueError: If pattern contains invalid digits or start position is out of range
        """
        if not pattern:
            return -1
            
        # Validate pattern digits
        if not all(0 <= digit <= 9 for digit in pattern):
            raise ValueError("Pattern contains invalid digits (must be 0-9)")
            
        if start_position < 0 or start_position >= self._num_digits:
            raise ValueError(f"Start position {start_position} outside available range of 0-{self._num_digits-1}")
            
        pattern_length = len(pattern)
        if pattern_length > self._num_digits - start_position:
            return -1  # Pattern is longer than remaining digits
            
        # For efficient searching, use memory mapping
        with open(self.pi_file_path, 'rb') as f:
            mmapped_file = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            
            position = start_position
            while position <= self._num_digits - pattern_length:
                # Read all bytes needed for the pattern
                start_byte = position // 2
                end_byte = (position + pattern_length - 1) // 2 + 1
                bytes_needed = end_byte - start_byte
                
                mmapped_file.seek(start_byte)
                bytes_data = mmapped_file.read(bytes_needed)
                
                # Extract and verify all digits
                match = True
                for i in range(pattern_length):
                    byte_idx = i // 2
                    is_first_digit = (i % 2 == 0)
                    
                    try:
                        digit = self._extract_digit_from_byte(bytes_data[byte_idx], is_first_digit)
                        if digit != pattern[i]:
                            match = False
                            break
                    except ValueError as e:
                        print(f"Error at position {position + i}: {str(e)}")
                        match = False
                        break
                
                if match:
                    # Double check the match by reading the sequence again
                    mmapped_file.seek(start_byte)
                    verify_bytes = mmapped_file.read(bytes_needed)
                    verify_match = True
                    
                    for i in range(pattern_length):
                        byte_idx = i // 2
                        is_first_digit = (i % 2 == 0)
                        digit = self._extract_digit_from_byte(verify_bytes[byte_idx], is_first_digit)
                        if digit != pattern[i]:
                            verify_match = False
                            break
                    
                    if verify_match:
                        mmapped_file.close()
                        return position
                    else:
                        print(f"Verification failed at position {position}")
                
                position += 1
                
            mmapped_file.close()
            return -1
    
    def search_string(self, pattern_str: str, start_position: int = 0) -> int:
        """Search for a string pattern in π.
        
        Args:
            pattern_str: String of digits to search for
            start_position: Position to start searching from (0-indexed)
            
        Returns:
            Position where pattern was found, or -1 if not found
            
        Raises:
            ValueError: If pattern contains non-digit characters
        """
        if not pattern_str:
            return -1
            
        if not pattern_str.isdigit():
            raise ValueError("Pattern must contain only digits")
            
        try:
            pattern = [int(c) for c in pattern_str]
            return self.search(pattern, start_position)
        except ValueError as e:
            raise ValueError(f"Invalid pattern: {str(e)}")

# Initialize Flask app
app = Flask(__name__)

# Configure the pi file path - can be set via environment variable
PI_FILE_PATH = os.environ.get('PI_FILE_PATH', 'pi_digits.bin')

# Initialize PiSearch once at startup
pi_search = PiSearch(PI_FILE_PATH)

# Enable CORS for API access from any origin
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/api/search', methods=['GET', 'POST'])
def search_api():
    """API endpoint to search for a pattern in pi."""
    
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        pattern = data.get('pattern', '')
        
        start_position = data.get('start_position', 0)
    else:  # GET
        pattern = request.args.get('pattern', '')
        start_position = int(request.args.get('start_position', 0))
    print("pattern",pattern)
    # Validate input
    if not pattern:
        return jsonify({'error': 'No pattern provided'}), 400
    
    if not pattern.isdigit():
        return jsonify({'error': 'Pattern must contain only digits'}), 400
    
    # Perform search
    start_time = time.time()
    try:
        position = pi_search.search_string(pattern, start_position)
        search_time = time.time() - start_time
        
        if position >= 0:
            # Get some context around the found position
            context_start = max(0, position - 10)
            context_length = len(pattern) + 20
            context_digits = pi_search.get_digits(context_start, context_length)
            context_str = ''.join(str(d) for d in context_digits)
            
            # Verify the pattern matches at the found position
            found_digits = pi_search.get_digits(position, len(pattern))
            found_str = ''.join(str(d) for d in found_digits)
            
            if found_str != pattern:
                return jsonify({
                    'success': False,
                    'error': f'Pattern mismatch at position {position}. Expected: {pattern}, Found: {found_str}'
                }), 500

            # Add debug information
            debug_info = {
                'pattern_length': len(pattern),
                'start_byte': position // 2,
                'end_byte': (position + len(pattern) - 1) // 2 + 1,
                'bytes_needed': ((position + len(pattern) - 1) // 2 + 1) - (position // 2)
            }
            
            result = {
                'success': True,
                'found': True,
                'pattern': pattern,
                'position': position,
                'context': {
                    'start_position': context_start,
                    'digits': context_str,
                    'pattern_index': position - context_start,
                    'pattern_length': len(pattern)
                },
                'debug_info': debug_info,
                'search_time_seconds': search_time
            }
        else:
            result = {
                'success': True,
                'found': False,
                'pattern': pattern,
                'search_time_seconds': search_time
            }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 4000))
    
    # Check if pi file exists
    if not os.path.exists(PI_FILE_PATH):
        print(f"ERROR: Pi digits file not found at {PI_FILE_PATH}")
        print("Please set the PI_FILE_PATH environment variable or place the file at the default location.")
        exit(1)
    
    # Print info about the pi file
    num_digits = "{:,}".format(pi_search.num_digits)
    file_size_mb = os.path.getsize(PI_FILE_PATH) / (1024 * 1024)
    
    
    # Run the Flask app in debug mode for development
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
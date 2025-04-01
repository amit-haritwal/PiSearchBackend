import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from typing import List

# Load environment variables from .env file
load_dotenv()

class PiSearch:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._file_size = os.path.getsize(file_path)
        self._num_digits = self._file_size - 1 

    @property
    def num_digits(self) -> int:
        return self._num_digits

    def _get_digit_range(self, start: int, end: int) -> str:
        with open(self.file_path, 'r') as f:
            f.seek(start)
            return f.read(end - start)

    def _digit_at_position(self, position: int) -> int:
        if position < 0 or position >= self._num_digits:
            raise ValueError(f"Position {position} is out of range.")

        digit = int(self._get_digit_range(position, position + 1))
        if not 0 <= digit <= 9:
            raise ValueError(f"Invalid digit {digit} found at position {position}")
        
        return digit

    def get_digits(self, start_position: int, count: int) -> List[int]:
        if start_position < 0 or start_position >= self._num_digits:
            raise ValueError(f"Start position {start_position} is out of range.")

        if start_position + count > self._num_digits:
            count = self._num_digits - start_position

        digits_str = self._get_digit_range(start_position, start_position + count)
        return [int(d) for d in digits_str]

    def find_pattern(self, pattern: str, start_position: int = 0) -> int:
        """Find the first occurrence of the pattern starting from start_position."""
        pattern_digits = [int(d) for d in pattern]
        pattern_length = len(pattern_digits)
        
        # Read a chunk of digits to search through
        chunk_size = 10000  # Adjust this value based on performance needs
        current_pos = start_position
        
        while current_pos < self._num_digits:
            # Get a chunk of digits
            end_pos = min(current_pos + chunk_size, self._num_digits)
            chunk = self.get_digits(current_pos, end_pos - current_pos)
            
            # Search for pattern in the chunk
            for i in range(len(chunk) - pattern_length + 1):
                if chunk[i:i + pattern_length] == pattern_digits:
                    return current_pos + i
            
            # Move to next chunk, overlapping by pattern_length - 1 to handle patterns that span chunk boundaries
            current_pos += chunk_size - (pattern_length - 1)
        
        return -1


# Flask setup
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File path for the π digits
PI_FILE_PATH = 'pi_dev-2t_02.txt'

# Initialize PiSearch with the text file
pi_search = PiSearch(PI_FILE_PATH)

@app.route('/api/search', methods=['POST'])
def search_api():
    data = request.get_json()
    
    if not data or 'pattern' not in data:
        return jsonify({'error': 'Pattern is required'}), 400
        
    pattern = data.get('pattern', '')
    start_position = int(data.get('start_position', 0))

    if not pattern or not pattern.isdigit():
        return jsonify({'error': 'Invalid pattern'}), 400

    start_time = time.time()
    try:
        found_position = pi_search.find_pattern(pattern, start_position)
        search_time = time.time() - start_time

        # Get 20 characters around the found position (10 before and 10 after)
        context_start = max(0, found_position - 10)
        context_end = min(pi_search.num_digits, found_position + len(pattern) + 10)
        context = pi_search.get_digits(context_start, context_end - context_start)
        context_str = ''.join(str(d) for d in context)

        return jsonify({
            'success': True,
            'found': found_position != -1,
            'position': found_position,
            'search_time_seconds': search_time,
            'pattern': pattern,
            'context': {
                'digits': context_str,
                'pattern_index': found_position - context_start if found_position != -1 else -1,
                'pattern_length': len(pattern),
                'start_position': context_start
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)

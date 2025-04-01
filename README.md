# PiSearch

A Python implementation for searching digits of π (pi) in a binary file.

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd PiSearch
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the server:
```bash
python app.py
```

The server will automatically download and use the pi digits file from Mega.

2. The API will be available at `http://localhost:4000`

### API Endpoints

- `GET /api/search?pattern=<digits>` - Search for a pattern in π
- `POST /api/search` - Search for a pattern in π (JSON body with `pattern` and optional `start_position`)
- `GET /api/digit/<position>` - Get a single digit at the specified position
- `GET /api/digits?position=<start>&count=<length>` - Get a range of digits
- `GET /api/info` - Get information about the pi digits file
- `GET /api/health` - Health check endpoint

## Environment Variables

- `MEGA_URL`: URL to the Mega file containing π digits (default: provided Mega URL)
- `PORT`: Server port (default: 4000)
- `FLASK_DEBUG`: Enable debug mode (default: False)

## License

MIT License 
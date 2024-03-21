# Sudoku Solver for [sudoku.com](https://sudoku.com)

## How does it work?

1. Take a screenshot of the sudoku board
2. Find the sudoku board in the screenshot
3. Extract the numbers from the board
4. Solve the sudoku

## Build

```bash
git clone https://github.com/lucascompython/sudoku
cd sudoku

# Install uv https://github.com/astral-sh/uv

# Create and activate a virtual environment
uv venv

source .venv/bin/activate
# Or
.\.venv\Scripts\Activate.ps1

# Install dependencies
uv pip sync requirements.txt

# Run
./develop.sh
# Or
./develop.ps1

# Adjust the screen capture area if needed
```

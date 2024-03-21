param (
    [Parameter(Mandatory = $true)]
    [string]$command
)

if ($command -eq "run") {
    maturin build
}

if ($command -eq "release") {
    maturin build --release
}

uv pip install --refresh --reinstall-package sudoku "sudoku @ ."
python main.py
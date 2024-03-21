#!/usr/bin/env bash

if [ "$1" == "run" ]; then
    maturin build
fi

if [ "$1" == "release" ]; then
    maturin build --release 
fi

uv pip install --refresh --reinstall-package sudoku "sudoku @ ." 
sudo -E python main.py
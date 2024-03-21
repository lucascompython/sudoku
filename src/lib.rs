use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

struct Sudoku {
    constraints: [u32; 27],
}

impl Sudoku {
    fn new(board: &[[usize; 9]; 9]) -> Self {
        let mut s = Sudoku {
            constraints: [0; 27],
        };
        for i in 0..9 {
            for j in 0..9 {
                if board[i][j] != 0 {
                    s.set(i, j, board[i][j]);
                }
            }
        }
        s
    }

    fn set(&mut self, row: usize, col: usize, num: usize) {
        let mask = 1 << num;
        self.constraints[row] |= mask;
        self.constraints[9 + col] |= mask;
        self.constraints[18 + (row / 3) * 3 + col / 3] |= mask;
    }

    fn is_valid(&self, row: usize, col: usize, num: usize) -> bool {
        let mask = 1 << num;
        if self.constraints[row] & mask != 0 {
            return false;
        }
        if self.constraints[9 + col] & mask != 0 {
            return false;
        }
        if self.constraints[18 + (row / 3) * 3 + col / 3] & mask != 0 {
            return false;
        }
        true
    }
}

#[pyfunction]
fn solve(mut board: [[usize; 9]; 9]) -> PyResult<[[usize; 9]; 9]> {
    if !solve_sudoku(&mut board) {
        return Err(PyErr::new::<PyValueError, _>("No solution found"));
    }
    Ok(board)
}

fn solve_sudoku(board: &mut [[usize; 9]; 9]) -> bool {
    let s = Sudoku::new(board);

    let (mut min_row, mut min_col, mut min_count) = (0, 0, 10);
    for row in 0..9 {
        for col in 0..9 {
            if board[row][col] == 0 {
                let count = (1..10)
                    .map(|num| 1 << num)
                    .filter(|&mask| {
                        s.constraints[row] & mask == 0
                            && s.constraints[9 + col] & mask == 0
                            && s.constraints[18 + (row / 3) * 3 + col / 3] & mask == 0
                    })
                    .count();
                if count < min_count {
                    min_row = row;
                    min_col = col;
                    min_count = count;
                }
            }
        }
    }

    // If no empty cell found, the puzzle is solved
    if min_count == 10 {
        return true;
    }

    // Try all possible numbers for the most constrained cell
    for num in 1..10 {
        if s.is_valid(min_row, min_col, num) {
            board[min_row][min_col] = num;
            if solve_sudoku(board) {
                return true;
            }
            board[min_row][min_col] = 0;
        }
    }

    false // No valid number found for this cell
}

#[pyfunction]
fn print_board(board: [[usize; 9]; 9]) {
    for i in 0..9 {
        if i % 3 == 0 && i != 0 {
            println!("------+-------+------");
        }
        for j in 0..9 {
            if j % 3 == 0 && j != 0 {
                print!("| ");
            }
            print!("{} ", board[i][j]);
        }
        println!();
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn sudoku(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve, m)?)?;
    m.add_function(wrap_pyfunction!(print_board, m)?)?;
    Ok(())
}

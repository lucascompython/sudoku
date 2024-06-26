import sudoku
import cv2
from cv2.typing import MatLike
import keyboard
import numpy as np
import pyscreenshot
from time import sleep
from tensorflow.keras.models import load_model
from imutils import grab_contours
from typing import Any


DELAY = 0.1
BOUNDING_BOX = (380, 580, 900, 1100)


def get_perspective(img: MatLike, location, height=900, width=900) -> MatLike:
    """Takes an image and location of interested region.
    And return the only the selected region with a perspective transformation"""
    pts1 = np.float32([location[0], location[3], location[1], location[2]])
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

    # Apply Perspective Transform Algorithm
    matrix: MatLike = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, matrix, (width, height))


def find_board(img: MatLike) -> tuple[MatLike, MatLike | Any]:
    """Takes an image as input and finds a sudoku board inside of the image"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 13, 20, 20)
    edged = cv2.Canny(bfilter, 30, 180)
    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = grab_contours(keypoints)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
    location = None

    # Finds rectangular contour
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 15, True)
        if len(approx) == 4:
            location = approx
            break
    result = get_perspective(img, location)
    return result, location


def split_boxes(board: MatLike, input_size: int = 48) -> list:
    """Takes a sudoku board and split it into 81 cells.
    each cell contains an element of that board either given or an empty cell."""
    rows = np.vsplit(board, 9)
    boxes = []
    for r in rows:
        cols = np.hsplit(r, 9)
        for box in cols:
            box = cv2.resize(box, (input_size, input_size)) / 255.0
            boxes.append(box)
    return boxes


def get_numbers(model) -> np.ndarray:
    img = pyscreenshot.grab(bbox=BOUNDING_BOX)
    img.save("sudoku.png")

    img = cv2.imread("sudoku.png")

    board, _ = find_board(img)

    gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)

    rois = split_boxes(gray)
    rois = np.array(rois).reshape(-1, 48, 48, 1)

    predictions = model.predict(rois)

    predicted_numbers = np.argmax(predictions, axis=1)

    predicted_numbers = np.where(predicted_numbers == 0, 0, predicted_numbers)

    predicted_numbers = predicted_numbers.reshape(9, 9)

    return predicted_numbers


def type_numbers(
    original_board: list[list[int]] | np.ndarray,
    solved_board: list[list[int]] | np.ndarray,
) -> None:
    for even, i in enumerate(range(9)):
        if even % 2 == 0:
            for j in range(9):
                if original_board[i][j] == 0:
                    keyboard.write(str(solved_board[i][j]))
                keyboard.press_and_release("right")
                sleep(DELAY)
        else:
            for j in range(8, -1, -1):
                if original_board[i][j] == 0:
                    keyboard.write(str(solved_board[i][j]))
                keyboard.press_and_release("left")
                sleep(DELAY)
        keyboard.press_and_release("down")
        sleep(DELAY)


def main() -> None:
    model = load_model("model-OCR.h5")

    try:
        while True:
            print("Press 'esc' to take a screenshot of the sudoku board")
            while True:
                if keyboard.is_pressed("esc"):
                    break
                sleep(0.1)
            predicted_numbers = get_numbers(model)

            print("Unsolved board")
            sudoku.print_board(predicted_numbers)

            solved_board = sudoku.solve(predicted_numbers)
            print("\nSolved board")
            sudoku.print_board(solved_board)

            type_numbers(predicted_numbers, solved_board)
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()

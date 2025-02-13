# Este código fue generado por la IA DeepSeek como parte del video del Canal de Youtube
# Computadoras y Sensores Capítulo 197

import machine
import time
import urandom as random
from ssd1306 import SSD1306_I2C

# Initialize display
i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4))
oled = SSD1306_I2C(128, 64, i2c)

# Button setup (using internal pull-ups)
button_left = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button_right = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],          # I
    [[1, 1], [1, 1]],        # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

def rotate_shape(shape):
    """Rotate shape 90 degrees clockwise"""
    return [list(row) for row in zip(*shape[::-1])]

def new_piece():
    """Generate a new random piece"""
    shape = random.choice(SHAPES)
    return {
        'x': (10 - len(shape[0])) // 2,
        'y': 0,
        'shape': shape
    }

def check_collision(board, piece):
    """Check if piece collides with board boundaries or existing blocks"""
    x, y, shape = piece['x'], piece['y'], piece['shape']
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col]:
                board_x = x + col
                board_y = y + row
                if board_x < 0 or board_x >= 10 or board_y >= 20:
                    return True
                if board_y >= 0 and board[board_y][board_x]:
                    return True
    return False

def merge_piece(board, piece):
    """Merge piece into the board"""
    x, y, shape = piece['x'], piece['y'], piece['shape']
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col] and y + row >= 0:
                board[y + row][x + col] = 1

def clear_lines(board):
    """Clear completed lines and return number of cleared lines"""
    lines_cleared = 0
    new_board = []
    for row in board:
        if all(row):
            lines_cleared += 1
        else:
            new_board.append(row)
    # Add new empty lines at top
    for _ in range(lines_cleared):
        new_board.insert(0, [0]*10)
    board[:] = new_board + [[0]*10]*(20 - len(new_board))
    return lines_cleared

def draw_game(board, piece, score):
    """Draw game state on OLED"""
    oled.fill(0)
    # Draw board
    for y in range(20):
        for x in range(10):
            if board[y][x]:
                oled.fill_rect(x*6, y*3, 5, 2, 1)
    # Draw current piece
    x, y, shape = piece['x'], piece['y'], piece['shape']
    for row in range(len(shape)):
        for col in range(len(shape[row])):
            if shape[row][col]:
                oled.fill_rect((x + col)*6, (y + row)*3, 5, 2, 1)
    # Draw score
    oled.text("Sc: {}".format(score), 70, 0)
    oled.show()

def game_over(score):
    """Display game over screen"""
    oled.fill(0)
    oled.text("GAME OVER", 15, 20)
    oled.text("Score: {}".format(score), 15, 40)
    oled.show()
    time.sleep(3)

def main():
    """Main game loop"""
    board = [[0]*10 for _ in range(20)]
    score = 0
    piece = new_piece()
    last_drop = time.ticks_ms()
    drop_interval = 1000

    while True:
        # Handle input
        left = not button_left.value()
        right = not button_right.value()

        new_piece_state = None
        
        if left and right:
            # Rotate piece
            rotated = rotate_shape(piece['shape'])
            new_piece_state = {'x': piece['x'], 'y': piece['y'], 'shape': rotated}
        elif left:
            new_piece_state = {'x': piece['x']-1, 'y': piece['y'], 'shape': piece['shape']}
        elif right:
            new_piece_state = {'x': piece['x']+1, 'y': piece['y'], 'shape': piece['shape']}

        if new_piece_state and not check_collision(board, new_piece_state):
            piece = new_piece_state

        # Auto-drop
        if time.ticks_ms() - last_drop > drop_interval:
            new_piece_state = {'x': piece['x'], 'y': piece['y']+1, 'shape': piece['shape']}
            if not check_collision(board, new_piece_state):
                piece = new_piece_state
            else:
                merge_piece(board, piece)
                lines = clear_lines(board)
                score += lines * 100
                piece = new_piece()
                if check_collision(board, piece):
                    game_over(score)
                    return
            last_drop = time.ticks_ms()

        draw_game(board, piece, score)
        time.sleep(0.05)

if __name__ == "__main__":
    main()
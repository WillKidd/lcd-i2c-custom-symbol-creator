import tkinter as tk

# Constants for grid size and square size
WIDTH = 80
HEIGHT = 16
SQUARE_SIZE = 20  # Size of each square in pixels
SEGMENT_WIDTH = 5  # Width of each segment in squares
SEGMENT_HEIGHT = 8  # Height of each segment in squares

# Initialize the Tkinter window
root = tk.Tk()
root.title("16x80 Clickable Grid")

# Calculate the total canvas size
canvas_width = WIDTH * SQUARE_SIZE
canvas_height = HEIGHT * SQUARE_SIZE

# Create a canvas to draw the grid
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Function to toggle square state
def toggle_square(row, col):
    current_state = grid_state[row][col]
    new_state = 0 if current_state else 1
    grid_state[row][col] = new_state
    color = "black" if new_state else "white"
    canvas.itemconfig(squares[row][col], fill=color)

# Initialize grid state and squares
grid_state = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
squares = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Create the grid of squares and bind events
for row in range(HEIGHT):
    for col in range(WIDTH):
        x1 = col * SQUARE_SIZE
        y1 = row * SQUARE_SIZE
        x2 = x1 + SQUARE_SIZE
        y2 = y1 + SQUARE_SIZE
        square = canvas.create_rectangle(x1, y1, x2, y2, fill="white")
        squares[row][col] = square

# Variables to track the last toggled square
last_row = None
last_col = None

# Bind mouse motion and click to toggle squares
def on_drag_or_click(event):
    global last_row, last_col
    col = event.x // SQUARE_SIZE
    row = event.y // SQUARE_SIZE
    if (0 <= col < WIDTH and 0 <= row < HEIGHT) and (row != last_row or col != last_col):
        toggle_square(row, col)
        last_row, last_col = row, col

canvas.bind("<B1-Motion>", on_drag_or_click)
canvas.bind("<Button-1>", on_drag_or_click)

# Draw the 5x8 segment boundaries
for col in range(0, WIDTH, SEGMENT_WIDTH):
    for row in range(0, HEIGHT, SEGMENT_HEIGHT):
        x1 = col * SQUARE_SIZE
        y1 = row * SQUARE_SIZE
        x2 = x1 + SEGMENT_WIDTH * SQUARE_SIZE
        y2 = y1 + SEGMENT_HEIGHT * SQUARE_SIZE
        canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)

# Function to clear all squares
def clear_all_squares():
    for row in range(HEIGHT):
        for col in range(WIDTH):
            grid_state[row][col] = 0
            canvas.itemconfig(squares[row][col], fill="white")

# Function to convert grid state to uint8_t arrays and save to file
def save_to_file():
    create_char_commands = []
    cursor_and_write_commands = []
    global_index = 0  # Running index for each square
    lcd_index = 0  # LCD character index

    with open("grid_state.txt", "w") as file:
        for segment in range(0, WIDTH, 5):  # Process 5 columns at a time
            for row_block in range(0, HEIGHT, 8):  # Process 8 rows at a time
                array_name = f"square{global_index}_{segment // 5}_{row_block // 8}"
                array_data = []

                for row in range(row_block, row_block + 8):
                    row_data = 0
                    for col in range(segment, segment + 5):
                        bit_position = 4 - (col - segment)
                        row_data |= grid_state[row][col] << bit_position
                    array_data.append(row_data)

                if any(array_data):  # Check if the array contains any non-zero data
                    file.write(f"uint8_t {array_name}[8] =\n{{\n")
                    for data in array_data:
                        file.write(f"    0b{data:05b},\n")
                    file.write("};\n\n")
                    create_char_commands.append(f"lcd.createChar({lcd_index}, {array_name});")
                    cursor_and_write_commands.append(f"lcd.setCursor({segment // 5},{row_block // 8});\nlcd.write({lcd_index});")
                    
                    lcd_index = (lcd_index + 1) % 8  # Cycle LCD character index from 0 to 7
                global_index += 1

        # Write the lcd.createChar commands at the end
        for command in create_char_commands:
            file.write(command + "\n")
        for command in cursor_and_write_commands:
            file.write(command + "\n")

# Buttons for clearing squares and saving to file
clear_button = tk.Button(root, text="Clear All", command=clear_all_squares)
clear_button.pack(side=tk.LEFT)

# Button to save uint8_t arrays to a file
save_button = tk.Button(root, text="Save to File", command=save_to_file)
save_button.pack(side=tk.RIGHT)

# Run the Tkinter loop
root.mainloop()
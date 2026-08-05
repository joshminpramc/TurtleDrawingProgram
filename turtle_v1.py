"""Turtle Drawer stage 1: Open a window with a blank canvas."""

import tkinter as tk
from tkinter import ttk


# these are the sizes i picked for the drawing screen.
# keeping them up here means i dont have to hunt around the whole code
# to change something, i just change it once here.
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 520


# this class is basically where the whole program is.
# it keeps the window, the canvas and the drawing together.
class TurtleDrawer:
    """Keep the window, canvas and drawing together."""

    # this runs when i first open the program.
    # it sets up the window and builds everything inside it.
    def __init__(self, window):
        self.window = window
        self.window.title("Turtle Shape Drawer")
        self.make_interface()

    # this is where i put together the actual screen people click on.
    # the canvas goes on the left and the tools go on the right.
    def make_interface(self):
        self.canvas = tk.Canvas(
            self.window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white"
        )
        self.canvas.pack(side="left", anchor="n", padx=10, pady=10)

        tools = ttk.Frame(self.window, padding=10)
        tools.pack(side="right", fill="both")
        ttk.Label(tools, text="Turtle Shape Drawer").pack(pady=5)


# starting point for the program so its clear how everything launches.
def main():
    # make the real tkinter window and hand it into the app class.
    window = tk.Tk()
    TurtleDrawer(window)
    # this keeps the window open so buttons and clicks actually work.
    window.mainloop()


# only start the app when this file is run directly, not if another file
# imports it.
if __name__ == "__main__":
    main()

"""Turtle Drawer stage 4: Clear the drawing."""

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
    # it sets up the window and makes the empty list that holds the points.
    def __init__(self, window):
        self.window = window
        self.window.title("Turtle Shape Drawer")

        # every click on the canvas gets saved in here as an (x, y) pair.
        self.points = []
        # small message under the buttons so the user knows whats happening.
        self.status = tk.StringVar(
            value="Click on the canvas to place your first point."
        )

        self.make_interface()
        self.redraw_canvas()

    # this is where i put together the actual screen people click on.
    # the canvas goes on the left and the tools go on the right.
    def make_interface(self):
        self.canvas = tk.Canvas(
            self.window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white"
        )
        self.canvas.pack(side="left", anchor="n", padx=10, pady=10)
        # every left click on the canvas calls add_point.
        self.canvas.bind("<Button-1>", self.add_point)

        tools = ttk.Frame(self.window, padding=10)
        tools.pack(side="right", fill="both")
        ttk.Label(tools, text="Turtle Shape Drawer").pack(pady=5)

        ttk.Button(
            tools, text="Clear everything", command=self.clear_all
        ).pack(fill="x", pady=3)

        ttk.Label(tools, textvariable=self.status, wraplength=250).pack(
            pady=10
        )

    # this repaints the entire drawing area from scratch.
    # sounds like a lot but for a few dots and lines its simple and quick.
    def redraw_canvas(self):
        # remove whats there first so we dont draw copies on top.
        self.canvas.delete("all")
        # a small red dot for every point so you can see where you clicked.
        for x, y in self.points:
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")
        # a line needs at least two points to join up. tkinter wants one
        # flat list of x and y values, not pairs.
        if len(self.points) >= 2:
            flat = []
            for x, y in self.points:
                flat.extend([x, y])
            self.canvas.create_line(flat, width=2)

    # this runs whenever you click the drawing area.
    # it saves the mouse position as a new point.
    def add_point(self, event):
        point = (event.x, event.y)
        self.points.append(point)
        self.status.set(f"Point {len(self.points)} added at {point}.")
        self.redraw_canvas()

    # this resets the whole drawing so the user can start again.
    def clear_all(self):
        self.points.clear()
        self.redraw_canvas()
        self.status.set("The drawing was cleared.")


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

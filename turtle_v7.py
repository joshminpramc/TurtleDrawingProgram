"""Turtle Drawer stage 7: Export outlines as Turtle pen movements."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# these are the sizes i picked for the drawing screen.
# keeping them up here means i dont have to hunt around the whole code
# to change something, i just change it once here.
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 520


# this writes a whole other python program that redraws the outlines with
# a turtle pen. the canvas starts at the top left with y going down, but
# turtle starts in the middle with y going up, so every point gets moved
# and flipped on the way out.
def make_python(parts):
    """Make a Python Turtle program that redraws the outlines."""
    lines = ["import turtle", "", "pen = turtle.Turtle()", "pen.speed(3)"]
    for points in parts:
        # lift the pen so theres no line from the last outline.
        lines.append("pen.penup()")
        for index, (x, y) in enumerate(points):
            turtle_x = x - CANVAS_WIDTH // 2
            turtle_y = CANVAS_HEIGHT // 2 - y
            lines.append(f"pen.goto({turtle_x}, {turtle_y})")
            # put the pen down once its at the first corner.
            if index == 0:
                lines.append("pen.pendown()")
    lines.extend(["pen.hideturtle()", "turtle.done()", ""])
    return "\n".join(lines)


# this class is basically where the whole program is.
# it keeps the drawing, the buttons and the file exports together.
class TurtleDrawer:
    """Keep the drawing, buttons and file actions together."""

    # this runs when i first open the program.
    # it sets up the window and makes the empty lists that hold the drawing.
    def __init__(self, window):
        self.window = window
        self.window.title("Turtle Shape Drawer")

        # finished outlines go in here. each one is its own list of points.
        self.parts = []
        # these are only the unfinished points the user is clicking now.
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
            tools, text="Finish outline", command=self.finish_part
        ).pack(fill="x", pady=3)
        ttk.Button(
            tools, text="Undo point", command=self.undo_point
        ).pack(fill="x", pady=3)
        ttk.Button(
            tools, text="Cancel unfinished outline", command=self.cancel_points
        ).pack(fill="x", pady=3)

        ttk.Button(
            tools, text="Export Python", command=self.export_python
        ).pack(fill="x", pady=3)
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
        # the finished outlines get drawn first, then the unfinished one.
        for points in self.parts + [self.points]:
            # a small red dot for every point so you can see the corners.
            for x, y in points:
                self.canvas.create_oval(
                    x - 3, y - 3, x + 3, y + 3, fill="red"
                )
            # a line needs at least two points to join up. tkinter wants
            # one flat list of x and y values, not pairs.
            if len(points) >= 2:
                flat = []
                for x, y in points:
                    flat.extend([x, y])
                self.canvas.create_line(flat, width=2)

    # this runs whenever you click the drawing area.
    # it saves the mouse position as a new point.
    def add_point(self, event):
        point = (event.x, event.y)
        self.points.append(point)
        self.status.set(f"Point {len(self.points)} added at {point}.")
        self.redraw_canvas()

    # click this after placing all the corners for one outline.
    # it moves the unfinished points into the finished outlines.
    def finish_part(self):
        # a line needs at least two points, so dont finish anything shorter.
        if len(self.points) < 2:
            self.status.set("An outline needs at least 2 points.")
            return
        # copy matters because im about to empty the unfinished points.
        self.parts.append(self.points.copy())
        self.points.clear()
        self.redraw_canvas()
        self.status.set("The outline is finished. You can start another one.")

    # this is only for the unfinished outline, not the finished ones.
    def undo_point(self):
        # only try popping a point if theres actually one there.
        if self.points:
            # pop removes the most recent click, like a one step undo.
            self.points.pop()
            self.redraw_canvas()
            self.status.set("The last point was removed.")
        else:
            self.status.set("There are no unfinished points to undo.")

    # instead of one undo, this throws away every unfinished point at once.
    def cancel_points(self):
        self.points.clear()
        self.redraw_canvas()
        self.status.set("The unfinished points were cleared.")

    # this resets the whole drawing so the user can start again.
    def clear_all(self):
        self.parts.clear()
        self.points.clear()
        self.redraw_canvas()
        self.status.set("The drawing was cleared.")

    # before exporting i make sure theres actually a finished shape, so
    # nobody saves an empty file or forgets their last bit.
    def ready_to_export(self):
        if self.points or not self.parts:
            self.status.set("Finish your drawing before exporting.")
            return False
        return True

    # the export button uses this to actually write the file. keeping it
    # separate means the error handling doesnt get mixed in with the rest.
    def write_file(self, path, content):
        # file stuff can fail because of permissions or a folder that got
        # deleted, so this shows an error instead of crashing.
        try:
            # with closes the file for me, even if writing goes wrong.
            # utf-8 means names with accents or emoji save properly.
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
        except OSError as error:
            messagebox.showerror(
                "Could not save", f"The file could not be saved.\n{error}"
            )
            return

        self.status.set(f"Saved your file to {path}")
        messagebox.showinfo("File saved", "Your file has been saved.")

    # this asks where to save, then writes the turtle program there.
    def export_python(self):
        if not self.ready_to_export():
            return
        path = filedialog.asksaveasfilename(
            title="Export your Turtle program",
            defaultextension=".py",
            filetypes=[("Python files", "*.py")],
        )
        # an empty path means they cancelled the save box.
        if path:
            self.write_file(path, make_python(self.parts))


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

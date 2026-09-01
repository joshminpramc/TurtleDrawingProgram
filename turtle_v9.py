"""Turtle Drawer stage 9: Give the shape and its parts names."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# these are the sizes i picked for the drawing screen.
# keeping them up here means i dont have to hunt around the whole code
# to change something, i just change it once here.
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 520

# every finished part is blue with a dark outline for now.
DEFAULT_FILL = "#3498db"
DEFAULT_OUTLINE = "#222222"


# a closed shape needs at least 3 corners to have an inside, so this
# checks that before a part gets saved. if theres a problem it sends back
# a message, and if its fine it sends back "".
def polygon_error(points):
    """Give a useful message if a polygon cannot be drawn properly."""
    if len(points) < 3:
        return "You need at least 3 points to finish a part."
    return ""


# this writes a whole other python program that redraws the parts with a
# turtle pen. the points are already turtle coordinates, so they go
# straight in.
# !r puts quotes around the names properly, even if a name has quotes in it.
def make_python(shape_name, parts):
    """Make a Python Turtle program that redraws the parts."""
    lines = [
        "import turtle",
        "",
        "screen = turtle.Screen()",
        f"screen.title({shape_name!r})",
        "pen = turtle.Turtle()",
        "pen.speed(3)",
    ]
    for part in parts:
        # going back to the first corner at the end closes the shape.
        closed = part["points"] + [part["points"][0]]
        # lift the pen so theres no line from the last part.
        lines.extend(["", f"# {part['name']}", "pen.penup()"])
        for index, (x, y) in enumerate(closed):
            lines.append(f"pen.goto({x}, {y})")
            # put the pen down once its at the first corner.
            if index == 0:
                lines.append("pen.pendown()")
    lines.extend(["", "pen.hideturtle()", "turtle.done()", ""])
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

        # finished parts go in here. every part is a dictionary with its
        # name and points. later parts get drawn on top.
        self.parts = []
        # these are only the unfinished points the user is clicking now.
        self.points = []
        # StringVar keeps the text box and the actual value connected.
        self.shape_name = tk.StringVar(value="my_shape")
        self.part_name = tk.StringVar(value="Part 1")
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

        # the shape name goes into the exported program, and each part gets
        # its own name like roof, door or window.
        ttk.Label(tools, text="Shape name").pack(anchor="w")
        ttk.Entry(tools, textvariable=self.shape_name).pack(fill="x")
        ttk.Label(tools, text="Name for the next part").pack(anchor="w")
        ttk.Entry(tools, textvariable=self.part_name).pack(
            fill="x", pady=(0, 5)
        )

        ttk.Button(
            tools, text="Finish part", command=self.finish_part
        ).pack(fill="x", pady=3)
        ttk.Button(
            tools, text="Undo point", command=self.undo_point
        ).pack(fill="x", pady=3)
        ttk.Button(
            tools, text="Cancel unfinished part", command=self.cancel_points
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
    # sounds like a lot but for these small shapes its simple and quick.
    def redraw_canvas(self):
        # remove whats there first so we dont draw copies on top.
        self.canvas.delete("all")

        # draws each finished polygon from the back layer to the front one.
        for part in self.parts:
            # the points are turtle coordinates, so they get turned back
            # into canvas pixels. tkinter wants one flat list of x and y
            # values, not pairs.
            canvas_points = []
            for x, y in part["points"]:
                canvas_points.extend(
                    [x + CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - y]
                )
            self.canvas.create_polygon(
                canvas_points,
                fill=DEFAULT_FILL,
                outline=DEFAULT_OUTLINE,
                width=2,
            )

        # little numbered dots for the part thats still being drawn, so you
        # can see the order the corners join up in.
        canvas_points = []
        for number, (x, y) in enumerate(self.points, start=1):
            px = x + CANVAS_WIDTH // 2
            py = CANVAS_HEIGHT // 2 - y
            canvas_points.extend([px, py])
            self.canvas.create_oval(
                px - 4, py - 4, px + 4, py + 4,
                fill=DEFAULT_FILL, outline=DEFAULT_OUTLINE,
            )
            self.canvas.create_text(
                px + 12, py - 11, text=str(number), fill="#303b49",
                font=("Arial", 9),
            )

        # a line needs at least two points, which is 4 numbers in the list.
        if len(canvas_points) >= 4:
            self.canvas.create_line(
                canvas_points, fill=DEFAULT_FILL, width=2, dash=(5, 3)
            )

    # this runs whenever you click the drawing area.
    # it turns the mouse position into turtle coordinates and saves it.
    def add_point(self, event):
        # tkinter starts at the top left with y going down, but turtle
        # starts in the middle with y going up. saving turtle coordinates
        # means the export doesnt have to change anything.
        point = (event.x - CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - event.y)
        self.points.append(point)
        self.status.set(f"Point {len(self.points)} added at {point}.")
        self.redraw_canvas()

    # click this after placing all the corners for one piece of the shape.
    # it checks the points before turning them into a finished part.
    def finish_part(self):
        # let the polygon checker decide if the part is good enough.
        problem = polygon_error(self.points)
        # show the actual problem instead of silently ignoring the button.
        if problem:
            messagebox.showwarning("Check your points", problem)
            return

        # if they leave the name blank i make one so it still looks tidy.
        name = self.part_name.get().strip() or f"Part {len(self.parts) + 1}"
        # copy matters because im about to empty the unfinished points.
        self.parts.append({"name": name, "points": self.points.copy()})
        self.points.clear()
        self.part_name.set(f"Part {len(self.parts) + 1}")
        self.redraw_canvas()
        self.status.set(f"{name} is finished. You can start another part.")

    # this is only for the unfinished part, not the already saved parts.
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

    # grab what they typed for the shape name, with a backup if its empty.
    def get_shape_name(self):
        return self.shape_name.get().strip() or "my_shape"

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
            content = make_python(self.get_shape_name(), self.parts)
            self.write_file(path, content)


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

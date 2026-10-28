"""Turtle Drawer stage 23: Make the exported files safer and tidier."""

import os
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk


# these are the sizes and limits i picked for the drawing screen.
# keeping them up here means i dont have to hunt around the whole code
# to change something, i just change it once here.
CANVAS_WIDTH = 700
CANVAS_HEIGHT = 520
# every 50 turtle units i draw a grid line so its easier to line stuff up.
GRID_SIZE = 50

# a polygon needs at least 3 corners to have an inside to fill.
MIN_POINTS = 3
# limits so someone cant add hundreds of parts or corners and slow it down.
MAX_POINTS = 60
MAX_PARTS = 25
# names get cut to this length so they fit nicely in the list.
MAX_NAME_LENGTH = 30

# starting colours for the shapes. blue for the inside and a dark outline.
DEFAULT_FILL = "#3498db"
DEFAULT_OUTLINE = "#222222"
# how many points go on each line of an exported file. without this a
# shape with lots of corners ends up as one massive line.
POINTS_PER_LINE = 4
# if the exported program is saved as turtle.py, python imports that file
# instead of the real turtle module and the program crashes.
BLOCKED_FILE_NAMES = ("turtle", "tkinter")


# names go into the list and into the exported program, so i tidy them
# up first. pasted text can have new lines in it, and a new line inside a
# comment in the exported program would turn the rest into broken code.
def clean_name(text, backup):
    """Return a tidy one-line name, or the backup name if it is blank."""
    # anything that cant be printed (like a new line) becomes a space.
    printable = ""
    for char in text:
        if char.isprintable():
            printable += char
        else:
            printable += " "
    # split and join squashes extra spaces down to single spaces.
    name = " ".join(printable.split())[:MAX_NAME_LENGTH].strip()
    return name or backup


# this works out which way you turn going from a to b to c.
# bigger than 0 is a left turn, smaller than 0 is a right turn and
# exactly 0 means all three points are in a straight line.
def turn(a, b, c):
    """Return the direction of the turn from a to b to c."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


# checks if point c is inside the box that has a and b as its corners.
# i only use this when i already know the three points are in a line.
def in_box(a, b, c):
    """Return True if c is inside the box with corners a and b."""
    return (min(a[0], b[0]) <= c[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))


# two edges cross if each one has the other edges ends on opposite sides.
# the second part catches edges that only just touch or lie on each other.
def edges_touch(a, b, c, d):
    """Return True if edge a-b crosses or touches edge c-d."""
    turn_a, turn_b = turn(c, d, a), turn(c, d, b)
    turn_c, turn_d = turn(a, b, c), turn(a, b, d)
    if turn_a * turn_b < 0 and turn_c * turn_d < 0:
        return True
    return ((turn_a == 0 and in_box(c, d, a))
            or (turn_b == 0 and in_box(c, d, b))
            or (turn_c == 0 and in_box(a, b, c))
            or (turn_d == 0 and in_box(a, b, d)))


# a shape like a bow tie has an outline that crosses over itself, so it
# doesnt have a proper inside. this compares every edge with every other
# edge to find any that cross.
def outline_crosses_itself(points):
    """Return True if any two edges of the closed outline meet."""
    count = len(points)
    # each edge goes from one point to the next, and the last point
    # joins back to the first one to close the shape.
    edges = []
    for index in range(count):
        edges.append((points[index], points[(index + 1) % count]))

    for first in range(count):
        a, b = edges[first]
        # edges next to each other always share a corner, so they only
        # count if the outline goes straight back the way it came.
        c = edges[(first + 1) % count][1]
        goes_back = ((a[0] - b[0]) * (c[0] - b[0])
                     + (a[1] - b[1]) * (c[1] - b[1]))
        if turn(a, b, c) == 0 and goes_back > 0:
            return True
        # starting two edges along skips the neighbour i just checked.
        for second in range(first + 2, count):
            # the first and last edges are neighbours too, so skip them.
            if first == 0 and second == count - 1:
                continue
            if edges_touch(a, b, *edges[second]):
                return True
    return False


# this checks if the points make a proper polygon before i save the part.
# if theres a problem it sends back a message, and if its fine it sends "".
# the checks go from simplest to hardest so the user sees the most basic
# problem first.
def polygon_error(points):
    """Give a useful message if a polygon cannot be drawn properly."""
    if len(points) < MIN_POINTS:
        return f"You need at least {MIN_POINTS} points to finish a part."

    # turning the points into a set gets rid of duplicates.
    # if the number changes it means the same spot got used twice.
    if len(set(points)) != len(points):
        return "A part cannot have the same point twice."

    # if every point makes a 0 turn with the first two, theyre all in
    # one straight line and theres nothing to fill.
    first, second = points[0], points[1]
    if all(turn(first, second, point) == 0 for point in points):
        return "These points are in a straight line. Try a different shape."

    if outline_crosses_itself(points):
        return ("The outline crosses over itself. "
                "Place the points in order around the edge.")

    return ""


# makes a safe file name out of the shape name, so "my cool shape!"
# becomes "my_cool_shape". this is what shows up in the save box.
def suggested_file_name(shape_name):
    """Turn a shape name into a file name without the extension."""
    letters = ""
    for char in shape_name:
        if char.isalnum():
            letters += char
        else:
            letters += " "
    name = "_".join(letters.split()) or "my_shape"
    if name.lower() in BLOCKED_FILE_NAMES:
        name += "_shape"
    return name


# writes the points as a python tuple spread over a few short lines,
# so the exported files are actually readable.
def format_points(points):
    """Write points as a Python tuple with a few points per line."""
    rows = []
    for start in range(0, len(points), POINTS_PER_LINE):
        row_points = points[start:start + POINTS_PER_LINE]
        row = ", ".join(repr(point) for point in row_points)
        rows.append(f"    {row},")
    return "(\n" + "\n".join(rows) + "\n)"


# this is the easy export, it just makes a readable txt file.
# it doesnt draw anything, just saves the names colours and coordinates.
def make_text(shape_name, parts):
    """Make a text file with coordinates that can be copied into Python."""
    # i build the whole file as a list of text lines first, then join
    # them together with new lines right at the end.
    lines = [
        "CUSTOM TURTLE SHAPE COORDINATES",
        f"Shape name: {shape_name}",
        "",
        "The centre of the drawing is (0, 0) and positive y goes up.",
        "Use setheading(90) on your turtle so the shape shows the same",
        "way up as it was drawn.",
        "",
    ]

    # enumerate gives me the part number without needing another counter.
    for number, part in enumerate(parts, start=1):
        lines.extend([
            f"Part {number}: {part['name']}",
            f"Fill colour: {part['fill']}",
            f"Outline colour: {part['outline']}",
            f"part_{number}_points = {format_points(part['points'])}",
            "",
        ])

    return "\n".join(lines)


# this is the big export function. it writes a whole other python program.
# the new file uses turtle to register the drawing as a custom shape.
# !r puts quotes around the names properly, even if a name has quotes in it.
def make_python(shape_name, parts):
    """Make a complete Python Turtle program from the finished parts."""
    lines = [
        '"""A custom Turtle shape made with Turtle Shape Drawer."""',
        "import turtle",
        "",
        "# Set up the Turtle window.",
        "screen = turtle.Screen()",
        f"screen.title({shape_name!r})",
        f"screen.setup({CANVAS_WIDTH + 100}, {CANVAS_HEIGHT + 100})",
        'screen.bgcolor("#f0f4f8")',
        "",
    ]

    # if theres only one part, turtle can register that polygon on its own.
    if len(parts) == 1:
        part = parts[0]
        lines.extend([
            "# The outline of the shape you drew.",
            f"points = {format_points(part['points'])}",
            f"screen.register_shape({shape_name!r}, points)",
            "",
            "# A plain polygon shape takes its colours from the turtle.",
            "drawer = turtle.Turtle()",
            f"drawer.shape({shape_name!r})",
            f"drawer.color({part['outline']!r}, {part['fill']!r})",
        ])
    # more than one part means they get joined into one compound shape,
    # where every part keeps its own colours.
    else:
        lines.extend([
            "# Join the coloured parts into one shape. Later parts are",
            "# drawn on top of earlier ones.",
            'custom_shape = turtle.Shape("compound")',
            "",
        ])
        for number, part in enumerate(parts, start=1):
            lines.extend([
                f"# Part {number}: {part['name']}",
                f"part_{number}_points = {format_points(part['points'])}",
                f"custom_shape.addcomponent(part_{number}_points, "
                f"{part['fill']!r}, {part['outline']!r})",
                "",
            ])
        lines.extend([
            f"screen.register_shape({shape_name!r}, custom_shape)",
            "",
            "drawer = turtle.Turtle()",
            f"drawer.shape({shape_name!r})",
        ])

    # these lines are the same for both kinds of shape.
    # turtle points a custom shape the way the turtle is facing, and it
    # starts facing right, so without setheading(90) the shape comes out
    # on its side.
    lines.extend([
        "drawer.penup()",
        "",
        "# Face up so the shape shows the same way up as it was drawn.",
        "drawer.setheading(90)",
        "# Match the outline thickness from the drawing program.",
        "drawer.shapesize(outline=2)",
        "",
        "# Stamp the finished shape in the middle of the screen.",
        "drawer.stamp()",
        "drawer.hideturtle()",
        "",
        "# To add more copies, move the turtle and stamp again:",
        "# drawer.goto(150, 0)",
        "# drawer.stamp()",
        "",
        "turtle.done()",
        "",
    ])

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
        self.window.configure(bg="#eef2f7")

        # finished parts go in here. every part is a dictionary with its
        # name, points and colours. later parts get drawn on top.
        self.parts = []
        # these are only the unfinished points the user is clicking now.
        self.points = []
        # counts every part ever finished. removing a part doesnt lower
        # it, so the default names like "Part 4" never repeat.
        self.parts_made = 0
        # remember the colours for the NEXT part, not the finished ones.
        self.fill = DEFAULT_FILL
        self.outline = DEFAULT_OUTLINE
        # StringVar keeps the text box and the actual value connected.
        self.shape_name = tk.StringVar(value="my_shape")
        self.part_name = tk.StringVar(value=self.next_part_name())
        # small message at the bottom so the user knows whats happening.
        self.status = tk.StringVar(
            value="Click on the canvas to place your first point."
        )

        self.make_interface()
        self.redraw_canvas()

        # instead of guessing a window size, i let tkinter work out how
        # much room everything needs, then stop it shrinking past that.
        self.window.update_idletasks()
        self.window.minsize(
            self.window.winfo_reqwidth(), self.window.winfo_reqheight()
        )

    # the default name for the next part, like "Part 3".
    def next_part_name(self):
        return f"Part {self.parts_made + 1}"

    # this is where i put together the actual screen people click on.
    # theres a bunch of tkinter stuff in here but its mostly just layout.
    def make_interface(self):
        # using ttk for nicer looking buttons than the old default ones.
        # "clam" looks about the same on every computer.
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#eef2f7")
        style.configure("TButton", padding=6, font=("Arial", 10))
        style.configure("TLabel", font=("Arial", 10), background="#eef2f7")
        style.configure("Title.TLabel", font=("Arial", 18, "bold"))
        style.configure("Heading.TLabel", font=("Arial", 11, "bold"))

        # top title part, just to make it obvious what the program is.
        heading = ttk.Frame(self.window, padding=(18, 12, 18, 7))
        heading.pack(fill="x")
        ttk.Label(
            heading, text="Turtle Shape Drawer", style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            heading,
            text="Click to draw a shape, choose its colours, "
                 "and export it to Python.",
        ).pack(anchor="w")

        # the status bar gets packed BEFORE the work area. if i pack it
        # last it can get squashed off the bottom when the window shrinks.
        ttk.Label(
            self.window, textvariable=self.status, anchor="w",
            padding=(18, 9),
        ).pack(side="bottom", fill="x")

        # the drawing canvas sits on the left and the tools on the right.
        work_area = ttk.Frame(self.window, padding=(18, 3, 18, 3))
        work_area.pack(fill="both", expand=True)

        # crosshair cursor makes it feel more like a drawing program.
        self.canvas = tk.Canvas(
            work_area,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="white",
            highlightthickness=1,
            highlightbackground="#c5ceda",
            cursor="crosshair",
        )
        self.canvas.pack(side="left", anchor="n", padx=(0, 17))
        # every left click on the canvas calls add_point.
        self.canvas.bind("<Button-1>", self.add_point)

        tools = ttk.Frame(work_area)
        tools.pack(side="left", fill="both", expand=True)

        # the shape name goes into the exported program, and each part gets
        # its own name like roof, door or window.
        ttk.Label(tools, text="Shape name", style="Heading.TLabel").pack(
            anchor="w"
        )
        ttk.Entry(tools, textvariable=self.shape_name).pack(
            fill="x", pady=(3, 10)
        )
        ttk.Label(
            tools, text="Name for the next part", style="Heading.TLabel"
        ).pack(anchor="w")
        ttk.Entry(tools, textvariable=self.part_name).pack(
            fill="x", pady=(3, 10)
        )

        # picked colours show up in these little sample squares too.
        ttk.Label(
            tools, text="Colours for the next part", style="Heading.TLabel"
        ).pack(anchor="w")
        colour_row = ttk.Frame(tools)
        colour_row.pack(fill="x", pady=(3, 10))
        ttk.Button(
            colour_row, text="Fill colour", command=self.choose_fill
        ).pack(side="left")
        self.fill_sample = tk.Label(
            colour_row, bg=self.fill, width=3, relief="solid", bd=1
        )
        self.fill_sample.pack(side="left", padx=(5, 13))
        ttk.Button(
            colour_row, text="Outline", command=self.choose_outline
        ).pack(side="left")
        self.outline_sample = tk.Label(
            colour_row, bg=self.outline, width=3, relief="solid", bd=1
        )
        self.outline_sample.pack(side="left", padx=(5, 0))

        # finish and undo sit beside each other to save space.
        draw_row = ttk.Frame(tools)
        draw_row.pack(fill="x", pady=(0, 5))
        ttk.Button(
            draw_row, text="Finish part", command=self.finish_part
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(
            draw_row, text="Undo point", command=self.undo_point
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))
        ttk.Button(
            tools, text="Cancel unfinished part", command=self.cancel_points
        ).pack(fill="x", pady=(0, 11))

        # the list shows the front part at the top, like the layers panel in
        # most drawing programs. that way "bring forward" moves a part UP the
        # list, which is what people expect.
        ttk.Label(
            tools, text="Finished parts (front at the top)",
            style="Heading.TLabel",
        ).pack(anchor="w")
        self.part_list = tk.Listbox(
            tools,
            height=7,
            font=("Arial", 10),
            selectmode="browse",
            # keeps the selection when text gets selected somewhere else.
            exportselection=False,
        )
        self.part_list.pack(fill="x", pady=(4, 5))
        # picking a part redraws the canvas so its outline looks thicker.
        self.part_list.bind(
            "<<ListboxSelect>>", lambda event: self.redraw_canvas()
        )

        # a small loop instead of writing the same button code three times.
        edit_row = ttk.Frame(tools)
        edit_row.pack(fill="x", pady=(0, 12))
        for text, action in [
            ("Bring forward", lambda: self.move_part(1)),
            ("Send backward", lambda: self.move_part(-1)),
            ("Remove", self.remove_part),
        ]:
            ttk.Button(edit_row, text=text, command=action).pack(
                side="left", fill="x", expand=True, padx=2
            )

        # two exports, a python turtle program and a text list of coordinates.
        ttk.Label(
            tools, text="Export your shape", style="Heading.TLabel"
        ).pack(anchor="w")
        export_row = ttk.Frame(tools)
        export_row.pack(fill="x", pady=(4, 5))
        ttk.Button(
            export_row, text="Export Python .py", command=self.export_python
        ).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(
            export_row, text="Save points .txt", command=self.export_text
        ).pack(side="left", fill="x", expand=True, padx=(3, 0))
        # theres a confirmation on this one so its not too easy to lose work.
        ttk.Button(
            tools, text="Clear everything", command=self.clear_all
        ).pack(fill="x")

    # the list shows the parts backwards (front first), so a row in the
    # list and a position in self.parts are different numbers. the same
    # sum swaps between them in both directions.
    def flip_position(self, position):
        return len(self.parts) - 1 - position

    # get the position in self.parts of the part picked in the list.
    # if they havent picked one then just return None.
    def get_selected_part(self):
        # tkinter gives the selection as a tuple, even for one item.
        selected = self.part_list.curselection()
        if not selected:
            return None
        return self.flip_position(selected[0])

    # whenever parts are added, removed or moved, rebuild the list so it
    # matches. i can pass in a part to keep it highlighted after a move.
    def refresh_list(self, selected=None):
        # clear the old names first or theyd keep piling up in the list.
        self.part_list.delete(0, tk.END)
        # reversed puts the front part (the last one drawn) at the top.
        for number in range(len(self.parts), 0, -1):
            part = self.parts[number - 1]
            self.part_list.insert(
                tk.END,
                f"{number}. {part['name']} ({len(part['points'])} points)",
            )
        if selected is not None:
            row = self.flip_position(selected)
            self.part_list.selection_set(row)
            self.part_list.see(row)
        self.redraw_canvas()

    # this repaints the entire drawing area from scratch.
    # sounds like a lot but for these small shapes its simple and quick.
    def redraw_canvas(self):
        # remove whats there first so we dont draw copies on top.
        self.canvas.delete("all")

        # the grid starts from the centre and works outwards, so every line
        # lands on a multiple of GRID_SIZE in turtle coordinates.
        centre_x = CANVAS_WIDTH // 2
        centre_y = CANVAS_HEIGHT // 2
        furthest = max(centre_x, centre_y)
        for step in range(GRID_SIZE, furthest + 1, GRID_SIZE):
            # one line each side of the centre. lines past the edge of the
            # canvas just dont show up, so i dont need to check for them.
            for x in (centre_x - step, centre_x + step):
                self.canvas.create_line(
                    x, 0, x, CANVAS_HEIGHT, fill="#ecf0f4"
                )
            for y in (centre_y - step, centre_y + step):
                self.canvas.create_line(
                    0, y, CANVAS_WIDTH, y, fill="#ecf0f4"
                )
        # these darker dashed lines cross at turtle's (0, 0).
        self.canvas.create_line(
            centre_x, 0, centre_x, CANVAS_HEIGHT,
            fill="#a9b8cb", dash=(4, 4),
        )
        self.canvas.create_line(
            0, centre_y, CANVAS_WIDTH, centre_y,
            fill="#a9b8cb", dash=(4, 4),
        )

        # draws each finished polygon from the back layer to the front one.
        selected = self.get_selected_part()
        for index, part in enumerate(self.parts):
            # the points are turtle coordinates, so they get turned back
            # into canvas pixels. tkinter wants one flat list of x and y
            # values, not pairs.
            canvas_points = []
            for x, y in part["points"]:
                canvas_points.extend(
                    [x + CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - y]
                )
            # the selected part gets a thicker outline so it stands out.
            if index == selected:
                width = 3
            else:
                width = 2
            self.canvas.create_polygon(
                canvas_points,
                fill=part["fill"],
                outline=part["outline"],
                width=width,
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
                fill=self.fill, outline=self.outline,
            )
            self.canvas.create_text(
                px + 12, py - 11, text=str(number), fill="#303b49",
                font=("Arial", 9),
            )

        # a line needs at least two points, which is 4 numbers in the list.
        if len(canvas_points) >= 4:
            self.canvas.create_line(
                canvas_points, fill=self.fill, width=2, dash=(5, 3)
            )

    # this runs whenever you click the drawing area.
    # it turns the mouse position into turtle coordinates and saves it.
    def add_point(self, event):
        # dont let new points get added if the drawing is full of parts.
        if len(self.parts) >= MAX_PARTS:
            self.status.set(
                f"You have reached the limit of {MAX_PARTS} parts. "
                "Remove one to add more."
            )
            return
        # also stop when the current part has reached the point limit.
        if len(self.points) >= MAX_POINTS:
            self.status.set(
                f"A part can have up to {MAX_POINTS} points. "
                "Finish this one first."
            )
            return

        # tkinter starts at the top left with y going down, but turtle
        # starts in the middle with y going up. saving turtle coordinates
        # means the export doesnt have to change anything.
        point = (event.x - CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - event.y)
        # clicking the exact same spot twice wouldnt help, so i block it.
        if point in self.points:
            self.status.set(
                "You already placed a point there. Try another spot."
            )
            return

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
        name = clean_name(self.part_name.get(), self.next_part_name())
        # copy matters because im about to empty the unfinished points.
        self.parts.append({
            "name": name,
            "points": self.points.copy(),
            "fill": self.fill,
            "outline": self.outline,
        })
        self.parts_made += 1
        self.points.clear()
        self.part_name.set(self.next_part_name())
        self.refresh_list()
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

    # opens the colour picker for the inside of the next part.
    def choose_fill(self):
        # askcolor returns two things and the second one is the colour
        # code i need. if they cancel, its None so the old colour stays.
        colour = colorchooser.askcolor(
            color=self.fill, title="Choose a fill colour"
        )[1]
        if colour:
            self.fill = colour
            self.fill_sample.configure(bg=colour)
            self.redraw_canvas()

    # same colour picker idea but this one changes the border colour.
    def choose_outline(self):
        colour = colorchooser.askcolor(
            color=self.outline, title="Choose an outline colour"
        )[1]
        if colour:
            self.outline = colour
            self.outline_sample.configure(bg=colour)
            self.redraw_canvas()

    # delete whichever finished part the user selected in the list.
    def remove_part(self):
        selected = self.get_selected_part()
        # if nothing is selected, show a message instead of guessing.
        if selected is None:
            self.status.set("Select a finished part to remove it.")
            return
        name = self.parts.pop(selected)["name"]
        self.refresh_list()
        self.status.set(f"{name} was removed.")

    # changing the order changes which part appears in front of another.
    # direction is +1 to bring it forward and -1 to send it backward.
    def move_part(self, direction):
        selected = self.get_selected_part()
        if selected is None:
            self.status.set("Select a part to move it.")
            return

        new_place = selected + direction
        # dont move it past the very front or the very back.
        if not 0 <= new_place < len(self.parts):
            if direction > 0:
                self.status.set("That part is already at the front.")
            else:
                self.status.set("That part is already at the back.")
            return

        # swap the two parts around, no need to make a new list.
        self.parts[selected], self.parts[new_place] = (
            self.parts[new_place], self.parts[selected]
        )
        self.refresh_list(new_place)
        self.status.set("The drawing order was changed.")

    # this resets the whole drawing so the user can start again.
    def clear_all(self):
        # nothing to clear means no reason to pop up a warning.
        if not self.parts and not self.points:
            self.status.set("There is nothing to clear.")
            return
        # confirmation just in case someone clicked clear by accident.
        if not messagebox.askyesno(
            "Clear drawing", "Remove all your drawn parts?"
        ):
            return

        self.parts.clear()
        self.points.clear()
        # starting fresh means the part names start from 1 again too.
        self.parts_made = 0
        self.part_name.set(self.next_part_name())
        self.refresh_list()
        self.status.set("The drawing is empty. You can start again.")

    # before exporting i make sure theres actually a finished shape, so
    # nobody saves an empty file or forgets their last bit.
    def ready_to_export(self):
        # unfinished points dont count, they need finishing or cancelling.
        if self.points:
            messagebox.showwarning(
                "Unfinished part", "Finish or cancel your current part first."
            )
            return False
        if not self.parts:
            messagebox.showwarning(
                "Empty drawing", "Draw and finish a part first."
            )
            return False
        return True

    # grab the shape name, tidied up, and put the tidy version back in the
    # box so the user can see exactly what name gets used.
    def get_shape_name(self):
        name = clean_name(self.shape_name.get(), "my_shape")
        self.shape_name.set(name)
        return name

    # both export buttons use this, so the file writing and error handling
    # are only written once.
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

        # only the file name goes in the status bar. a full path can be
        # really long and would stretch the whole window.
        self.status.set(f"Saved your file as {os.path.basename(path)}")
        messagebox.showinfo("File saved", "Your file has been saved.")

    # this asks where to save, then writes the turtle program there.
    def export_python(self):
        if not self.ready_to_export():
            return
        shape_name = self.get_shape_name()
        path = filedialog.asksaveasfilename(
            title="Export your Turtle program",
            defaultextension=".py",
            filetypes=[("Python files", "*.py")],
            initialfile=suggested_file_name(shape_name) + ".py",
        )
        # an empty path means they cancelled the save box.
        if not path:
            return

        # stop the turtle.py problem before the file gets saved.
        file_name = os.path.basename(path)
        name, ending = os.path.splitext(file_name)
        if ending.lower() == ".py" and name.lower() in BLOCKED_FILE_NAMES:
            messagebox.showwarning(
                "Choose another name",
                f"A program called {file_name} would import itself "
                f"instead of Python's {name.lower()} module, so it "
                "would not run. Please pick a different name.",
            )
            return

        self.write_file(path, make_python(shape_name, self.parts))

    # same idea as the python export, but for the text file.
    def export_text(self):
        if not self.ready_to_export():
            return
        shape_name = self.get_shape_name()
        path = filedialog.asksaveasfilename(
            title="Save your coordinates",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=suggested_file_name(shape_name) + ".txt",
        )
        # an empty path means they cancelled the save box.
        if path:
            self.write_file(path, make_text(shape_name, self.parts))


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

import tkinter as tk
import csv
import os


# ---------------------------------------------------------------------------
# Question bank
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "type": "multiple_choice",
        "question": "Which formula correctly represents Ohm's Law?",
        "choices": ["V = I + R", "V = I x R", "V = I - R", "V = I / R"],
        "answer": "V = I x R",
        "worked_solution": "Ohm's Law states that Voltage = Current x Resistance, written as V = IR."
    },
    {
        "type": "numerical",
        "question": "A resistor has 12V across it and 3A flowing through it. What is the resistance in ohms?",
        "answer": 4.0,
        "tolerance": 0.1,
        "unit": "Ω",
        "worked_solution": "Using Ohm's Law: R = V / I\nR = 12 / 3\nR = 4Ω"
    },
    {
        "type": "multiple_choice",
        "question": "What happens to total resistance when you add a resistor in series?",
        "choices": ["It decreases", "It stays the same", "It increases", "It becomes zero"],
        "answer": "It increases",
        "worked_solution": "In a series circuit R_total = R1 + R2 + ... so adding any resistor increases total resistance."
    },
    {
        "type": "numerical",
        "question": "Two resistors of 4Ω and 6Ω are connected in series. What is the total resistance in ohms?",
        "answer": 10.0,
        "tolerance": 0.1,
        "unit": "Ω",
        "worked_solution": "For series resistors: R_total = R1 + R2\nR_total = 4 + 6\nR_total = 10Ω"
    },
    {
        "type": "multiple_choice",
        "question": "In a parallel circuit, what is true about the voltage across each resistor?",
        "choices": ["It is different for each", "It is the same for each", "It adds up", "It is zero"],
        "answer": "It is the same for each",
        "worked_solution": "In a parallel circuit all components share the same voltage across them."
    },
    {
        "type": "numerical",
        "question": "Two resistors of 6Ω and 3Ω are connected in parallel. What is the total resistance in ohms?",
        "answer": 2.0,
        "tolerance": 0.1,
        "unit": "Ω",
        "worked_solution": "For parallel resistors: 1/R_total = 1/R1 + 1/R2\n1/R_total = 1/6 + 1/3 = 3/6\nR_total = 2Ω"
    },
    {
        "type": "multiple_choice",
        "question": "What is the unit of electrical resistance?",
        "choices": ["Volt", "Ampere", "Ohm", "Watt"],
        "answer": "Ohm",
        "worked_solution": "Resistance is measured in Ohms, represented by the symbol Ω."
    },
    {
        "type": "numerical",
        "question": "A circuit has a resistance of 5Ω and a current of 2A. What is the voltage in volts?",
        "answer": 10.0,
        "tolerance": 0.1,
        "unit": "V",
        "worked_solution": "Using Ohm's Law: V = I x R\nV = 2 x 5\nV = 10V"
    },
    {
        "type": "multiple_choice",
        "question": "If resistance doubles and voltage stays the same, what happens to current?",
        "choices": ["It doubles", "It halves", "It stays the same", "It becomes zero"],
        "answer": "It halves",
        "worked_solution": "From I = V / R, if R doubles and V stays constant then I is halved."
    },
    {
        "type": "numerical",
        "question": "A circuit has a voltage of 20V and a resistance of 4Ω. What is the current in amps?",
        "answer": 5.0,
        "tolerance": 0.1,
        "unit": "A",
        "worked_solution": "Using Ohm's Law: I = V / R\nI = 20 / 4\nI = 5A"
    },
]


# ---------------------------------------------------------------------------
# CSV file handling
# ---------------------------------------------------------------------------

SCORES_FILE = "scores.csv"


def save_score(name, score, total):
    file_exists = os.path.isfile(SCORES_FILE)
    with open(SCORES_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Score", "Total"])
        writer.writerow([name, score, total])


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class QuizApp:

    def __init__(self, window):
        self.window = window
        self.window.title("Resistance Quiz")
        self.window.geometry("550x400")

        self.student_name = ""
        self.current_index = 0
        self.score = 0
        self.last_correct = False

        self.home_frame = tk.Frame(window)
        self.question_frame = tk.Frame(window)
        self.feedback_frame = tk.Frame(window)
        self.results_frame = tk.Frame(window)

        for frame in (self.home_frame, self.question_frame,
                      self.feedback_frame, self.results_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        self.build_home()
        self.build_question()
        self.build_feedback()
        self.build_results()

        self.show_frame(self.home_frame)


    def show_frame(self, frame):
        frame.tkraise()


    # -----------------------------------------------------------------------
    # Home screen
    # -----------------------------------------------------------------------

    def build_home(self):
        tk.Label(self.home_frame, text="Resistance Quiz",
                 font=("Arial", 22, "bold")).pack(pady=30)

        tk.Label(self.home_frame, text="Enter your name:",
                 font=("Arial", 12)).pack()

        self.name_entry = tk.Entry(self.home_frame, font=("Arial", 12))
        self.name_entry.pack(pady=5)

        self.name_error = tk.Label(self.home_frame, text="",
                                   font=("Arial", 10), fg="red")
        self.name_error.pack()

        tk.Button(self.home_frame, text="Start Quiz",
                  font=("Arial", 13), command=self.start_quiz).pack(pady=15)


    # -----------------------------------------------------------------------
    # Question screen
    # -----------------------------------------------------------------------

    def build_question(self):
        self.progress_label = tk.Label(self.question_frame, text="",
                                       font=("Arial", 10))
        self.progress_label.pack(pady=10)

        self.question_label = tk.Label(self.question_frame, text="",
                                       font=("Arial", 13), wraplength=480,
                                       justify="center")
        self.question_label.pack(pady=15)

        # Multiple choice buttons frame
        self.mc_frame = tk.Frame(self.question_frame)
        self.mc_frame.pack(pady=5)

        self.mc_buttons = []
        for i in range(4):
            btn = tk.Button(self.mc_frame, text="", font=("Arial", 11),
                            width=25,
                            command=lambda i=i: self.submit_mc(i))
            btn.grid(row=i, column=0, pady=3)
            self.mc_buttons.append(btn)

        # Numerical input frame
        self.num_frame = tk.Frame(self.question_frame)
        self.num_frame.pack(pady=5)

        self.unit_label = tk.Label(self.num_frame, text="", font=("Arial", 12))
        self.unit_label.grid(row=0, column=0, padx=5)

        self.num_entry = tk.Entry(self.num_frame, font=("Arial", 12), width=10)
        self.num_entry.grid(row=0, column=1, padx=5)

        self.num_error = tk.Label(self.num_frame, text="",
                                  font=("Arial", 10), fg="red")
        self.num_error.grid(row=1, column=0, columnspan=2)

        tk.Button(self.num_frame, text="Submit", font=("Arial", 12),
                  command=self.submit_numerical).grid(row=2, column=0,
                                                      columnspan=2, pady=8)


    # -----------------------------------------------------------------------
    # Feedback screen
    # -----------------------------------------------------------------------

    def build_feedback(self):
        self.feedback_label = tk.Label(self.feedback_frame, text="",
                                       font=("Arial", 16, "bold"))
        self.feedback_label.pack(pady=20)

        self.solution_label = tk.Label(self.feedback_frame, text="",
                                       font=("Arial", 11), wraplength=480,
                                       justify="center")
        self.solution_label.pack(pady=10)

        tk.Button(self.feedback_frame, text="Next",
                  font=("Arial", 13), command=self.next_question).pack(pady=20)


    # -----------------------------------------------------------------------
    # Results screen
    # -----------------------------------------------------------------------

    def build_results(self):
        tk.Label(self.results_frame, text="Quiz Complete!",
                 font=("Arial", 22, "bold")).pack(pady=30)

        self.results_score_label = tk.Label(self.results_frame, text="",
                                            font=("Arial", 14))
        self.results_score_label.pack(pady=10)

        self.saved_label = tk.Label(self.results_frame, text="",
                                    font=("Arial", 10))
        self.saved_label.pack()

        tk.Button(self.results_frame, text="Play Again",
                  font=("Arial", 13), command=self.restart).pack(pady=20)


    # -----------------------------------------------------------------------
    # Logic
    # -----------------------------------------------------------------------

    def start_quiz(self):
        name = self.name_entry.get().strip()
        if not name:
            self.name_error.config(text="Name cannot be empty.")
            return
        self.name_error.config(text="")
        self.student_name = name
        self.current_index = 0
        self.score = 0
        self.load_question()
        self.show_frame(self.question_frame)


    def load_question(self):
        q = QUESTIONS[self.current_index]

        self.progress_label.config(
            text=f"Question {self.current_index + 1} of {len(QUESTIONS)}")
        self.question_label.config(text=q["question"])

        if q["type"] == "multiple_choice":
            self.mc_frame.pack()
            self.num_frame.pack_forget()
            for i, choice in enumerate(q["choices"]):
                self.mc_buttons[i].config(text=choice)

        elif q["type"] == "numerical":
            self.mc_frame.pack_forget()
            self.num_frame.pack()
            self.unit_label.config(text=f"Answer ({q['unit']}):")
            self.num_entry.delete(0, tk.END)
            self.num_error.config(text="")


    def submit_mc(self, index):
        q = QUESTIONS[self.current_index]
        selected = q["choices"][index]
        self.last_correct = selected == q["answer"]
        if self.last_correct:
            self.score += 1
        self.show_feedback(q["worked_solution"])


    def submit_numerical(self):
        q = QUESTIONS[self.current_index]
        raw = self.num_entry.get().strip()
        try:
            value = float(raw)
        except ValueError:
            self.num_error.config(text="Please enter a valid number.")
            return
        self.num_error.config(text="")
        self.last_correct = abs(value - q["answer"]) <= q["tolerance"]
        if self.last_correct:
            self.score += 1
        self.show_feedback(q["worked_solution"])


    def show_feedback(self, solution):
        if self.last_correct:
            self.feedback_label.config(text="Correct!")
        else:
            self.feedback_label.config(text="Incorrect!")
        self.solution_label.config(text=solution)
        self.show_frame(self.feedback_frame)


    def next_question(self):
        self.current_index += 1
        if self.current_index >= len(QUESTIONS):
            self.show_results()
        else:
            self.load_question()
            self.show_frame(self.question_frame)


    def show_results(self):
        self.results_score_label.config(
            text=f"{self.student_name}, you scored {self.score} / {len(QUESTIONS)}")
        save_score(self.student_name, self.score, len(QUESTIONS))
        self.saved_label.config(text="Your score has been saved.")
        self.show_frame(self.results_frame)


    def restart(self):
        self.name_entry.delete(0, tk.END)
        self.show_frame(self.home_frame)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

window = tk.Tk()
QuizApp(window)
window.mainloop()
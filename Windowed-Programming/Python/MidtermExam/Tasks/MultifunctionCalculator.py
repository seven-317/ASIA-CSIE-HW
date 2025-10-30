import tkinter as tk
import math

SCALE = 0.85

def sin_d(x): return math.sin(math.radians(x))
def cos_d(x): return math.cos(math.radians(x))
def tan_d(x): return math.tan(math.radians(x))

SAFE_ENV = {
    "__builtins__": {},
    "sin": sin_d, "cos": cos_d, "tan": tan_d,
    "sqrt": math.sqrt, "log": math.log, "abs": abs,
    "pi": math.pi, "e": math.e
}

def last_number_span(s: str):
    if not s: return (0, 0)
    i = len(s) - 1
    valid = "0123456789."
    while i >= 0 and s[i] in valid:
        i -= 1
    if i >= 0 and s[i] == '-' and (i == 0 or s[i-1] in "+-*/%^("):
        start = i
    else:
        start = i + 1
    return (start, len(s))

def show(ch: str):
    cur = expr_var.get()
    if cur == "0" and ch not in (")", "%"):
        cur = ""
    expr_var.set(cur + ch)

def clear():
    expr_var.set("0")
    result_var.set("")

def backspace():
    cur = expr_var.get()
    if len(cur) <= 1:
        expr_var.set("0")
    else:
        expr_var.set(cur[:-1])

def make_percent():
    cur = expr_var.get()
    a, b = last_number_span(cur)
    if a == b:
        return
    try:
        val = float(cur[a:b]) / 100.0
        txt = str(val) if (val % 1) else str(int(val))
        expr_var.set(cur[:a] + txt + cur[b:])
    except Exception:
        result_var.set("Error")

def invert_1x():
    cur = expr_var.get()
    a, b = last_number_span(cur)
    if a == b:
        expr_var.set(f"1/({cur})")
    else:
        expr_var.set(cur[:a] + f"1/({cur[a:b]})" + cur[b:])

def func_insert(name):
    show(f"{name}(")

def power_insert():
    show("^")

def calculate():
    raw = expr_var.get().strip()
    if not raw: return
    expr = raw.replace("^", "**").replace("×", "*").replace("÷", "/")
    try:
        val = eval(expr, SAFE_ENV, {})
        if isinstance(val, float) and abs(val - round(val)) < 1e-12:
            val = int(round(val))
        result_var.set(str(val))
    except Exception:
        result_var.set("Error")

COLOR_BG = "#1C1C1C"
COLOR_DISP = "#000000"
COLOR_TEXT = "#FFFFFF"
COLOR_NUM = "#505050"
COLOR_FUNC = "#D4D4D2"
COLOR_OP = "#FF9F0A"

root = tk.Tk()
root.title("計算機")
root.configure(bg=COLOR_BG)
root.resizable(False, False)

PX = lambda v: int(round(v * SCALE))
FONT_BTN = ("Helvetica", PX(18))
FONT_EXPR = ("Helvetica", PX(14))
FONT_RES  = ("Helvetica", PX(28), "bold")

pad_outer = PX(10)
pad_btn   = PX(5)
btn_ipady = PX(6)
btn_width = 3

expr_var = tk.StringVar(value="0")
result_var = tk.StringVar(value="")

disp = tk.Frame(root, bg=COLOR_BG)
disp.grid(row=0, column=0, columnspan=6, sticky="nsew",
          padx=pad_outer, pady=(pad_outer, PX(6)))

tk.Label(disp, textvariable=expr_var, bg=COLOR_DISP, fg=COLOR_TEXT,
         anchor="e", justify="right", font=FONT_EXPR,
         padx=PX(10), pady=PX(4)).pack(fill="x")
tk.Label(disp, textvariable=result_var, bg=COLOR_DISP, fg=COLOR_TEXT,
         anchor="e", justify="right", font=FONT_RES,
         padx=PX(10), pady=PX(8)).pack(fill="x")

grid = tk.Frame(root, bg=COLOR_BG)
grid.grid(row=1, column=0, sticky="nsew", padx=pad_outer, pady=(PX(4), pad_outer))

for c in range(6):
    grid.grid_columnconfigure(c, weight=1, uniform="col")
for r in range(5):
    grid.grid_rowconfigure(r, weight=1, uniform="row")

def mkbtn(text, r, c, cmd=None, bg=COLOR_NUM, fg=COLOR_TEXT):
    b = tk.Button(grid, text=text, command=cmd or (lambda t=text: show(t)),
                  bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
                  bd=0, relief="flat", font=FONT_BTN, width=btn_width)
    b.grid(row=r, column=c, sticky="nsew", padx=pad_btn, pady=pad_btn, ipady=btn_ipady)
    return b

mkbtn("abs",  0, 0, cmd=lambda: func_insert("abs"),  bg=COLOR_FUNC, fg="#000")
mkbtn("sqrt", 0, 1, cmd=lambda: func_insert("sqrt"), bg=COLOR_FUNC, fg="#000")
mkbtn("C",    0, 2, cmd=clear,                        bg=COLOR_FUNC, fg="#000")
mkbtn("DEL",  0, 3, cmd=backspace,                    bg=COLOR_FUNC, fg="#000")
mkbtn("%",    0, 4, cmd=make_percent,                 bg=COLOR_FUNC, fg="#000")
mkbtn("÷",    0, 5, cmd=lambda: show("/"),            bg=COLOR_OP)

mkbtn("sin",  1, 0, cmd=lambda: func_insert("sin"),   bg=COLOR_FUNC, fg="#000")
mkbtn("1/x",  1, 1, cmd=invert_1x,                    bg=COLOR_FUNC, fg="#000")
mkbtn("7",    1, 2)
mkbtn("8",    1, 3)
mkbtn("9",    1, 4)
mkbtn("×",    1, 5, cmd=lambda: show("*"),            bg=COLOR_OP)

mkbtn("cos",  2, 0, cmd=lambda: func_insert("cos"),   bg=COLOR_FUNC, fg="#000")
mkbtn("x^y",  2, 1, cmd=power_insert,                 bg=COLOR_FUNC, fg="#000")
mkbtn("4",    2, 2)
mkbtn("5",    2, 3)
mkbtn("6",    2, 4)
mkbtn("−",    2, 5, cmd=lambda: show("-"),            bg=COLOR_OP)

mkbtn("tan",  3, 0, cmd=lambda: func_insert("tan"),   bg=COLOR_FUNC, fg="#000")
mkbtn("(",    3, 1)
mkbtn("1",    3, 2)
mkbtn("2",    3, 3)
mkbtn("3",    3, 4)
mkbtn("+",    3, 5, cmd=lambda: show("+"),            bg=COLOR_OP)

mkbtn("log",  4, 0, cmd=lambda: func_insert("log"),   bg=COLOR_FUNC, fg="#000")
mkbtn(")",    4, 1)
mkbtn("0",    4, 2)
mkbtn(".",    4, 3)

mkbtn("=",    4, 5, cmd=calculate,                    bg=COLOR_OP)

root.mainloop()

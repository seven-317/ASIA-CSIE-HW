from tkinter import *
import time

root = Tk()
root.title("動態時鐘")

t = StringVar(value="--:--:--")
clock = Label(root, textvariable=t, font=("Consolas", 40, "bold"),
              fg="#00E676", bg="#0B0F14", padx=24, pady=12, relief=RIDGE, bd=6)
clock.pack(padx=20, pady=20, fill="x")

loop = [None]
loop[0] = lambda: (t.set(time.strftime("%H:%M:%S")), root.after(1000, loop[0]))
root.after(0, loop[0])

root.mainloop()

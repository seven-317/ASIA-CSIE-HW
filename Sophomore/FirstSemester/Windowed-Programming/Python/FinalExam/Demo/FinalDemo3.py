from tkinter import *
import matplotlib.pyplot as plt
from tkinter.ttk import *
window = Tk()
window.title("loan calculator")
def fill(*args):
    Eyear.insert(0, int(lslider.get()))

rateVar = StringVar()
Erate=Entry(window, textvariable=rateVar, justify=RIGHT)
Erate.grid(row=1, column=2, padx=3)
yearVar = StringVar()
Eyear=Entry(window, textvariable=yearVar, justify=RIGHT)
Eyear.grid(row=2, column=2, padx=3)
loanVar = StringVar()
Eloan=Entry(window, textvariable=loanVar, justify=RIGHT)
Eloan.grid(row=3, column=2, padx=3)

fm=Frame(window)
fm.grid(row=0,column=0)
lslider=Scale(fm,from_=100,to=0,orient=VERTICAL, command=fill)
lslider.grid(row=1,column=0)
mslider=Scale(fm,from_=20,to=0, orient=VERTICAL, command=fill)
mslider.grid(row=1,column=1)
rslider=Scale(fm,from_=100000000,to=0,orient=VERTICAL, command=fill)
rslider.grid(row=1,column=2)
window.mainloop()
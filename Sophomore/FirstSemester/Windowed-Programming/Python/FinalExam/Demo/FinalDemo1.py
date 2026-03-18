from tkinter import *
import matplotlib.pyplot as plt
from tkinter.ttk import *
window = Tk()
window.title("loan calculator")


pw=PanedWindow(orient=HORIZONTAL)
leftframe=LabelFrame(pw,text="資料輸入區",width=300,height=200)
pw.add(leftframe,weight=1)
rightframe=LabelFrame(pw,text="滑桿選擇區",width=200,height=200)
pw.add(rightframe,weight=1)

fm=Frame(rightframe)
fm.pack()

pw.grid(row=0,column=0,padx=10,pady=10,sticky=NSEW)
window.mainloop()


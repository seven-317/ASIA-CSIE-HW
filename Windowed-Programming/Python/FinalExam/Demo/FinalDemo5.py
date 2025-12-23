from tkinter import *
import matplotlib.pyplot as plt
from tkinter.ttk import *
def cal(*args):
    term=[]
    ins=[]
    prin=[]
    for i in range(terms):
        term.append(i)
        ins.append(intst)
        prin.append(principal)
    plt.plot(term, ins,prin)
    plt.legend(['interest','principal'])
    plt.xlabel("months")
    plt.ylabel("NTD dollars")
    plt.show()


window = Tk()
window.title("loan calculator")

terms=100
intst=10000
principal=100000
cal()
window.mainloop()



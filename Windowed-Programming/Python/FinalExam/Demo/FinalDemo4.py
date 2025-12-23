from tkinter import *
import matplotlib.pyplot as plt
from tkinter.ttk import *

def cal(*args):
    clear()
    terms = 12 * int(yearVar.get())
    monthrate = float(rateVar.get()) / (12 * 100)  # 改成百分比以及月利率
    balance = float(loanVar.get())
    numerator = float(loanVar.get()) * (1 + monthrate) ** (int(yearVar.get()) * 12) * monthrate
    denominator = (1 + monthrate) ** (int(yearVar.get()) * 12) - 1
    monthlypay = float(numerator / denominator)  # 每月還款金額
    monthlypayVar.set(int(monthlypay))
    totalPay = monthlypay * int(yearVar.get()) * 12
    totalpayVar.set(int(totalPay))

    for i in range(terms):
        text.insert(INSERT, "    ")
        text.insert(INSERT,str(i+1))
        text.insert(INSERT, "\t\t\t")
        intst = (monthrate * balance)
        balance = balance - (monthlypay - intst)
        principal=monthlypay - intst
        text.insert(INSERT, str(format(principal, '.0f')))
        text.insert(INSERT, "\t\t\t")
        text.insert(INSERT, str(format(intst, '.0f')))
        text.insert(INSERT, "\t\t")
        text.insert(INSERT, str(format(balance, '.0f')))
        text.insert(END, "\n")

def cal2(*args):
    clear()
    terms = 12 * int(yearVar.get())
    monthrate = float(rateVar.get()) / (12 * 100)  # 改成百分比以及月利率
    balance = float(loanVar.get())
    principal=float(loanVar.get())/terms
    for i in range(terms):
        intst = monthrate * balance
        monthlypay =principal+intst
        balance = balance-principal
        text.insert(INSERT, "    ")
        text.insert(INSERT, str(i + 1))
        text.insert(INSERT, "\t\t\t")
        text.insert(INSERT, str(format(principal, '.0f')))
        text.insert(INSERT, "\t\t\t")
        text.insert(INSERT, str(format(intst, '.0f')))
        text.insert(INSERT, "\t\t")
        text.insert(INSERT, str(format(balance, '.0f')))
        text.insert(END, "\n")

def clear():
    text.delete('1.0',END)

def clearall():
    text.delete('1.0',END)
    Erate.delete(0,END)
    Eyear.delete(0,END)
    Eloan.delete(0,END)

window = Tk()
window.title("loan calculator")

yscrollbar = Scrollbar(window)  # y軸scrollbar物件
yscrollbar.grid(row=8,column=6,sticky=NS)
text = Text(window, height=20, width=80)  # y軸scrollbar包裝顯示
text.grid(row=8, column=1, columnspan=5, sticky=NS)
yscrollbar.config(command=text.yview)  # y軸scrollbar設定
text.config(yscrollcommand=yscrollbar.set)  # Text控件設定

Label(window, text="貸款年利率").grid(row=1, column=1, sticky=W)
Label(window, text="貸款年數").grid(row=2, column=1, sticky=W)
Label(window, text="貸款金額").grid(row=3, column=1, sticky=W)
Label(window, text="月付款金額").grid(row=4, column=1, sticky=W)
Label(window, text="總付款金額").grid(row=5, column=1, sticky=W)

rateVar = StringVar()
Erate=Entry(window, textvariable=rateVar, justify=RIGHT)
Erate.grid(row=1, column=2, padx=3)
yearVar = StringVar()
Eyear=Entry(window, textvariable=yearVar, justify=RIGHT)
Eyear.grid(row=2, column=2, padx=3)
loanVar = StringVar()
Eloan=Entry(window, textvariable=loanVar, justify=RIGHT)
Eloan.grid(row=3, column=2, padx=3)


monthlypayVar = StringVar()
lblmonthlypay = Label(window, textvariable=monthlypayVar).grid(row=4,column=2, sticky=E, pady=3)
totalpayVar = StringVar()
lbltotalpay = Label(window, textvariable=totalpayVar).grid(row=5,column=2, sticky=E, padx=3)
btn_Cal = Button(window, text="計算貸款金額", command=cal).grid(row=6, column=2, sticky=E, padx=3, pady=3)

var=IntVar()
var.set(1)
rbtn1=Radiobutton(window,text="本息平均攤還法",variable=var,value=1,command=cal)
rbtn2=Radiobutton(window,text="本金平均攤還法",variable=var,value=2,command=cal2)
rbtn1.grid(row=6,column=4, sticky=E, padx=3)
rbtn2.grid(row=6,column=5, sticky=E, padx=3)

btn_Clr = Button(window, text="清除", command=clearall ).grid(row=6, column=3, sticky=E, padx=3, pady=3)
term1 = Label(window, text="期別").grid(row=7, column=1)
term2 = Label(window, text="償還本金").grid(row=7, column=2)
term3 = Label(window, text="償還利息").grid(row=7, column=3)
term4 = Label(window, text="           剩餘本金").grid(row=7, column=4)



window.mainloop()



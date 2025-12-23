from tkinter import *
from tkinter.ttk import *
import matplotlib.pyplot as plt

# ======================
# 全域狀態
# ======================
interest_list = []
principal_list = []
updating = False
initializing = True   # ★ 初始化鎖（關鍵）

# ======================
# 工具
# ======================
def safe_float(var):
    try:
        return float(var.get())
    except:
        return None

# ======================
# 計算邏輯
# ======================
def clear_text():
    text.delete("1.0", END)

def clear_all():
    clear_text()
    rateVar.set("")
    yearVar.set("")
    loanVar.set("")
    monthlypayVar.set("")
    totalpayVar.set("")

def cal_equal_payment():
    clear_text()
    interest_list.clear()
    principal_list.clear()

    years = safe_float(yearVar)
    rate = safe_float(rateVar)
    loan = safe_float(loanVar)
    if None in (years, rate, loan):
        return

    years = int(years)
    terms = years * 12
    month_rate = rate / 1200

    monthly_pay = loan * (1 + month_rate) ** terms * month_rate / ((1 + month_rate) ** terms - 1)
    monthlypayVar.set(int(monthly_pay))
    totalpayVar.set(int(monthly_pay * terms))

    balance = loan
    for i in range(terms):
        interest = balance * month_rate
        principal = monthly_pay - interest
        balance -= principal

        interest_list.append(interest)
        principal_list.append(principal)

        text.insert(
            END,
            f"{i+1:3d}\t{int(principal):10d}\t{int(interest):10d}\t{int(balance):10d}\n"
        )

def cal_equal_principal():
    clear_text()

    years = safe_float(yearVar)
    rate = safe_float(rateVar)
    loan = safe_float(loanVar)
    if None in (years, rate, loan):
        return

    years = int(years)
    terms = years * 12
    month_rate = rate / 1200

    principal_pay = loan / terms
    balance = loan

    for i in range(terms):
        interest = balance * month_rate
        balance -= principal_pay

        text.insert(
            END,
            f"{i+1:3d}\t{int(principal_pay):10d}\t{int(interest):10d}\t{int(balance):10d}\n"
        )

def plot_curve():
    if not interest_list:
        return
    plt.plot(interest_list, label="interest")
    plt.plot(principal_list, label="principal")
    plt.xlabel("months")
    plt.ylabel("NTD dollars")
    plt.legend()
    plt.show()

def recalc():
    if modeVar.get() == 1:
        cal_equal_payment()
    else:
        cal_equal_principal()

# ======================
# 同步邏輯
# ======================
def slider_update(val=None):
    global updating, initializing
    if initializing or updating:
        return

    updating = True

    rateVar.set(int(rateSlider.get()))
    yearVar.set(int(yearSlider.get()))
    loanVar.set(int(loanSlider.get()))

    rateLabelVar.set(f"年利率：{int(rateSlider.get())} %")
    yearLabelVar.set(f"年數：{int(yearSlider.get())} 年")
    loanLabelVar.set(f"金額：{int(loanSlider.get()):,} 元")

    recalc()
    updating = False

def entry_update(event=None):
    global updating
    if updating:
        return

    updating = True
    try:
        rateSlider.set(float(rateVar.get()))
        yearSlider.set(float(yearVar.get()))
        loanSlider.set(float(loanVar.get()))
        recalc()
    except:
        pass
    updating = False

# ======================
# 主視窗
# ======================
window = Tk()
window.title("Loan Calculator")

pw = PanedWindow(window, orient=HORIZONTAL)
pw.pack(fill=BOTH, expand=True, padx=10, pady=10)

# ======================
# 左側：資料輸入 + 表格
# ======================
left = LabelFrame(pw, text="資料輸入區")
pw.add(left, weight=3)

Label(left, text="貸款年利率 (%)").grid(row=0, column=0, sticky=W)
Label(left, text="貸款年數").grid(row=1, column=0, sticky=W)
Label(left, text="貸款金額").grid(row=2, column=0, sticky=W)
Label(left, text="月付款金額").grid(row=3, column=0, sticky=W)
Label(left, text="總付款金額").grid(row=4, column=0, sticky=W)

rateVar = StringVar()
yearVar = StringVar()
loanVar = StringVar()
monthlypayVar = StringVar()
totalpayVar = StringVar()

Erate = Entry(left, textvariable=rateVar, width=12)
Eyear = Entry(left, textvariable=yearVar, width=12)
Eloan = Entry(left, textvariable=loanVar, width=12)

Erate.grid(row=0, column=1)
Eyear.grid(row=1, column=1)
Eloan.grid(row=2, column=1)

Erate.bind("<KeyRelease>", entry_update)
Eyear.bind("<KeyRelease>", entry_update)
Eloan.bind("<KeyRelease>", entry_update)

Label(left, textvariable=monthlypayVar).grid(row=3, column=1, sticky=E)
Label(left, textvariable=totalpayVar).grid(row=4, column=1, sticky=E)

Button(left, text="顯示本息關係曲線", command=plot_curve).grid(row=5, column=0, columnspan=2, pady=5)
Button(left, text="清除", command=clear_all).grid(row=6, column=0, columnspan=2)

Label(left, text="期別\t本金\t\t利息\t\t剩餘本金").grid(row=7, column=0, columnspan=2, sticky=W)

text = Text(left, width=65, height=16)
text.grid(row=8, column=0, columnspan=2)

# ======================
# 右側：滑桿 + 攤還方式
# ======================
right = LabelFrame(pw, text="滑桿選擇區")
pw.add(right, weight=1)

rateLabelVar = StringVar()
yearLabelVar = StringVar()
loanLabelVar = StringVar()

rateSlider = Scale(right, from_=0, to=10, orient=VERTICAL, command=slider_update)
yearSlider = Scale(right, from_=1, to=40, orient=VERTICAL, command=slider_update)
loanSlider = Scale(right, from_=100000, to=30000000, orient=VERTICAL, command=slider_update)

rateSlider.set(2)
yearSlider.set(20)
loanSlider.set(1000000)

Label(right, textvariable=rateLabelVar).pack(pady=(5, 0))
rateSlider.pack()

Label(right, textvariable=yearLabelVar).pack(pady=(5, 0))
yearSlider.pack()

Label(right, textvariable=loanLabelVar).pack(pady=(5, 0))
loanSlider.pack()

Separator(right).pack(fill=X, pady=10)

# ★ modeVar 在任何 callback 之前就建立
modeVar = IntVar(value=1)

Radiobutton(
    right, text="本息平均攤還法",
    variable=modeVar, value=1, command=recalc
).pack(anchor=W)

Radiobutton(
    right, text="本金平均攤還法",
    variable=modeVar, value=2, command=recalc
).pack(anchor=W)

# ======================
# 初始化完成，解除鎖定
# ======================
initializing = False
slider_update()

window.mainloop()

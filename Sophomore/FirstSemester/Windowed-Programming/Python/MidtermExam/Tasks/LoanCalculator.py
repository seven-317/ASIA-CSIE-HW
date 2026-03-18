from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox

class LoanCalculator(Tk):
    def __init__(self):
        super().__init__()
        self.title("Loan Calculator")
        self.geometry("900x600")

        self.var_rate = StringVar(value="2")
        self.var_years = StringVar(value="30")
        self.var_amount = StringVar(value="20000000")

        self.var_early = BooleanVar(value=False)
        self.var_early_month = StringVar(value="120")
        self.var_early_amount = StringVar(value="300000")

        self.var_pay_before = StringVar(value="")
        self.var_pay_after = StringVar(value="")

        frm = Frame(self)
        frm.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        frm.grid_columnconfigure(1, weight=1)
        r = 0

        Label(frm, text="貸款年利率(%)").grid(row=r, column=0, sticky="w", pady=4)
        Entry(frm, textvariable=self.var_rate, width=18, justify="right").grid(row=r, column=1, sticky="w")

        r += 1
        Label(frm, text="貸款年數").grid(row=r, column=0, sticky="w", pady=4)
        Entry(frm, textvariable=self.var_years, width=18, justify="right").grid(row=r, column=1, sticky="w")

        r += 1
        Label(frm, text="貸款金額").grid(row=r, column=0, sticky="w", pady=4)
        Entry(frm, textvariable=self.var_amount, width=18, justify="right").grid(row=r, column=1, sticky="w")

        r += 1
        Checkbutton(frm, text="提前還款", variable=self.var_early, command=self.toggle_entry).grid(row=r, column=0, sticky="w")

        r += 1
        Label(frm, text="提前還款時間（月數）").grid(row=r, column=0, sticky="w", pady=4)
        self.ent_early_month = Entry(frm, textvariable=self.var_early_month, width=18, justify="right", state=DISABLED)
        self.ent_early_month.grid(row=r, column=1, sticky="w")

        r += 1
        Label(frm, text="提前還款金額").grid(row=r, column=0, sticky="w", pady=4)
        self.ent_early_amount = Entry(frm, textvariable=self.var_early_amount, width=18, justify="right", state=DISABLED)
        self.ent_early_amount.grid(row=r, column=1, sticky="w")

        r += 1
        Label(frm, text="提前還款前月付款").grid(row=r, column=0, sticky="w", pady=4)
        Entry(frm, textvariable=self.var_pay_before, width=18, justify="right", state="readonly").grid(row=r, column=1, sticky="w")

        r += 1
        Label(frm, text="提前還款後月付款").grid(row=r, column=0, sticky="w", pady=4)
        Entry(frm, textvariable=self.var_pay_after, width=18, justify="right", state="readonly").grid(row=r, column=1, sticky="w")

        btns = Frame(frm)
        btns.grid(row=0, column=2, rowspan=8, padx=10, sticky="n")
        Button(btns, text="計算貸款金額", command=self.calculate_payment, width=16).pack(pady=4)
        Button(btns, text="清除", command=self.clear, width=16).pack(pady=4)

        table_frame = Frame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,12))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        cols = ("period", "principal", "interest", "balance")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=16)
        self.tree.heading("period", text="期數")
        self.tree.heading("principal", text="償還本金")
        self.tree.heading("interest", text="償還利息")
        self.tree.heading("balance", text="剩餘本金")

        self.tree.column("period", width=70, anchor=E, stretch=False)
        self.tree.column("principal", width=140, anchor=E)
        self.tree.column("interest", width=140, anchor=E)
        self.tree.column("balance", width=160, anchor=E)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def toggle_entry(self):
        state = NORMAL if self.var_early.get() else DISABLED
        self.ent_early_month.config(state=state)
        self.ent_early_amount.config(state=state)
        if not self.var_early.get():
            self.var_pay_after.set("")

    @staticmethod
    def monthly_payment(principal, monthly_rate, n_months):
        if n_months <= 0: return 0.0
        if monthly_rate == 0: return principal / n_months
        x = (1 + monthly_rate) ** n_months
        return principal * monthly_rate * x / (x - 1)

    def calculate_payment(self):
        try:
            annual_rate = float(self.var_rate.get())
            years = int(float(self.var_years.get()))
            amount = float(self.var_amount.get())
            if annual_rate < 0 or years <= 0 or amount <= 0:
                raise ValueError

            r = annual_rate / 100.0 / 12.0
            n = years * 12

            pay_before = self.monthly_payment(amount, r, n)
            self.var_pay_before.set(self._fmt_money(pay_before))

            for i in self.tree.get_children():
                self.tree.delete(i)

            balance = amount
            month = 0

            if self.var_early.get():
                early_month = int(float(self.var_early_month.get()))
                early_amount = float(self.var_early_amount.get())
                if not (1 <= early_month < n):
                    messagebox.showwarning("提醒", "提前還款月份需在 1 ~ (總期數-1) 之間。")
                    return
                if early_amount < 0:
                    messagebox.showwarning("提醒", "提前還款金額需為非負數。")
                    return

                while month < early_month and balance > 0:
                    month += 1
                    interest = balance * r
                    principal = min(pay_before - interest, balance)
                    balance -= principal
                    self._insert_row(month, principal, interest, balance)

                if balance > 0 and early_amount > 0:
                    balance = max(0.0, balance - early_amount)
                    self.tree.insert("", "end", values=("提前還款", "", "", self._fmt_money(balance)))

                remain_n = max(0, n - month)
                pay_after = self.monthly_payment(balance, r, remain_n)
                self.var_pay_after.set(self._fmt_money(pay_after) if pay_after > 0 else "0")

                while balance > 0 and remain_n > 0:
                    month += 1
                    remain_n -= 1
                    interest = balance * r
                    principal = min(pay_after - interest, balance)
                    balance -= principal
                    self._insert_row(month, principal, interest, balance)

            else:
                self.var_pay_after.set("")
                while month < n and balance > 0:
                    month += 1
                    interest = balance * r
                    principal = min(pay_before - interest, balance)
                    balance -= principal
                    self._insert_row(month, principal, interest, balance)

        except Exception:
            messagebox.showerror("輸入錯誤", "請確認年利率、年數與金額等輸入為有效數值。")

    def clear(self):
        self.var_rate.set("")
        self.var_years.set("")
        self.var_amount.set("")
        self.var_early.set(False)
        self.var_early_month.set("")
        self.var_early_amount.set("")
        self.var_pay_before.set("")
        self.var_pay_after.set("")
        self.toggle_entry()
        for i in self.tree.get_children():
            self.tree.delete(i)

    def _insert_row(self, period, principal, interest, balance):
        self.tree.insert(
            "", "end",
            values=(
                period,
                self._fmt_money(principal),
                self._fmt_money(interest),
                self._fmt_money(balance),
            )
        )

    @staticmethod
    def _fmt_money(x):
        return f"{x:,.0f}"

if __name__ == "__main__":
    app = LoanCalculator()
    app.mainloop()
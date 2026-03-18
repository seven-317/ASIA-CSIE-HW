import tkinter as tk
from tkinter import messagebox

def is_valid_email(s: str) -> bool:
    s = s.strip()
    if not s or "@" not in s:
        return False
    user, _, domain = s.partition("@")
    if not user or not domain:
        return False
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        return False
    return True

def submit():
    name = name_var.get().strip()
    email = email_var.get().strip()

    if not name:
        messagebox.showwarning("錯誤", "姓名不得為空白")
        return
    if not email:
        messagebox.showwarning("錯誤", "Email 不得為空白")
        return
    if not is_valid_email(email):
        messagebox.showwarning("錯誤", "Email 格式不正確")
        return

    ok = messagebox.askyesno(
        "確認",
        f"確定送出以下資料？\n\n姓名：{name}\nEmail：{email}"
    )
    if ok:
        messagebox.showinfo("完成", "資料已成功送出")
        name_var.set("")
        email_var.set("")

root = tk.Tk()
root.title("期末Q1 學生資料登錄")
root.geometry("420x220")
root.resizable(False, False)

name_var = tk.StringVar()
email_var = tk.StringVar()

tk.Label(root, text="姓名：", font=("Segoe UI", 10)).place(x=40, y=40)
tk.Entry(root, textvariable=name_var, width=30, font=("Segoe UI", 10)).place(x=110, y=40)

tk.Label(root, text="Email：", font=("Segoe UI", 10)).place(x=40, y=80)
tk.Entry(root, textvariable=email_var, width=30, font=("Segoe UI", 10)).place(x=110, y=80)

tk.Button(root, text="送出", width=12, command=submit).place(x=165, y=130)

root.mainloop()
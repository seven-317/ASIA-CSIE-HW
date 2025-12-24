import tkinter as tk
from tkinter import messagebox

def refresh_contact_ui():
    if need_var.get() == "yes":
        contact_frame.pack(fill="x", padx=20, pady=10)
    else:
        contact_frame.pack_forget()

def submit():
    if need_var.get() == "no":
        messagebox.showinfo("完成", "已選擇不提供聯絡資訊")
        return

    phone = phone_var.get().strip()
    addr = addr_var.get().strip()

    if not phone:
        messagebox.showwarning("錯誤", "請輸入電話")
        return
    if not addr:
        messagebox.showwarning("錯誤", "請輸入地址")
        return

    messagebox.showinfo("完成", f"已送出聯絡資訊：\n電話：{phone}\n地址：{addr}")

root = tk.Tk()
root.title("期末Q7 聯絡方式選擇")
root.geometry("520x300")
root.resizable(False, False)

need_var = tk.StringVar(value="no")
phone_var = tk.StringVar()
addr_var = tk.StringVar()

tk.Label(root, text="是否需要輸入聯絡資訊？", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=20, pady=(15, 6))

radio_frame = tk.Frame(root)
radio_frame.pack(anchor="w", padx=20)

tk.Radiobutton(radio_frame, text="不需要", variable=need_var, value="no", command=refresh_contact_ui).pack(side="left", padx=(0, 10))
tk.Radiobutton(radio_frame, text="需要", variable=need_var, value="yes", command=refresh_contact_ui).pack(side="left")

contact_frame = tk.LabelFrame(root, text="聯絡資訊")
tk.Label(contact_frame, text="電話：").grid(row=0, column=0, sticky="e", padx=8, pady=8)
tk.Entry(contact_frame, textvariable=phone_var, width=30).grid(row=0, column=1, padx=8, pady=8)

tk.Label(contact_frame, text="地址：").grid(row=1, column=0, sticky="e", padx=8, pady=8)
tk.Entry(contact_frame, textvariable=addr_var, width=30).grid(row=1, column=1, padx=8, pady=8)

tk.Button(root, text="送出", width=14, command=submit).pack(pady=18)

refresh_contact_ui()
root.mainloop()

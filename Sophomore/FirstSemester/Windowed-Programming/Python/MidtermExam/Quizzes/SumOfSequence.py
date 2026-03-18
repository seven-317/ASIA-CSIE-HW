import tkinter as tk

root = tk.Tk()
root.title("數列總和 (1+2+...+N)")
root.geometry("300x200")

tk.Label(root, text="輸入要計算的整數 N：").pack()
entry = tk.Entry(root)
entry.pack()

result_label = tk.Label(root, text="")
result_label.pack()

def calc():
    try:
        n = int(entry.get())
        total = n * (n + 1) // 2
        result_label.config(text=f"總和：{total}")
    except:
        tk.showerror("錯誤", "請輸入正確的整數")

tk.Button(root, text="計算", command=calc).pack()

root.mainloop()
import tkinter as tk

root = tk.Tk()
root.title("每位數的總和計算")
root.geometry("300x200")

tk.Label(root, text="輸入正整數：").pack()
entry = tk.Entry(root)
entry.pack()

result_label = tk.Label(root, text="")
result_label.pack()

def calc_sum():
    try:
        s = str(abs(int(entry.get())))
        total = sum(int(d) for d in s)
        result_label.config(text=f"每位數總和：{total}")
    except:
        tk.showerror("錯誤", "請輸入正確的整數")

tk.Button(root, text="計算", command=calc_sum).pack()

root.mainloop()
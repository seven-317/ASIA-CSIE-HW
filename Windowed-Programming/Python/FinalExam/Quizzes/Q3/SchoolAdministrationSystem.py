import tkinter as tk
from tkinter import ttk

def show_page(name: str):
    # 隱藏全部
    for p in pages.values():
        p.pack_forget()
    # 顯示指定
    pages[name].pack(fill="both", expand=True, padx=10, pady=10)

def on_menu_select(event=None):
    sel = menu_list.curselection()
    if not sel:
        return
    item = menu_list.get(sel[0])
    if item in pages:
        show_page(item)

root = tk.Tk()
root.title("期末Q3 校務系統介面（PanedWindow）")
root.geometry("820x520")

paned = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
paned.pack(fill="both", expand=True)

left = ttk.Frame(paned, width=180)
right = ttk.Frame(paned)

paned.add(left, weight=1)
paned.add(right, weight=4)

ttk.Label(left, text="功能選單", font=("Segoe UI", 11, "bold")).pack(pady=(10, 6))

menu_list = tk.Listbox(left, height=10)
menu_list.pack(fill="x", padx=10)
for item in ["最新公告", "課表查詢", "成績查詢"]:
    menu_list.insert(tk.END, item)

menu_list.bind("<<ListboxSelect>>", on_menu_select)

# 右側內容頁面
pages = {}

def make_page(title, body_lines):
    frame = ttk.Frame(right)
    ttk.Label(frame, text=f"目前頁面：{title}", font=("Segoe UI", 12, "bold")).pack(anchor="w")
    txt = tk.Text(frame, height=18, width=70)
    txt.pack(fill="both", expand=True, pady=8)
    txt.insert("1.0", "\n".join(body_lines))
    txt.config(state="disabled")
    return frame

pages["最新公告"] = make_page("最新公告", [
    "• 期末考注意事項：禁止聯網、可翻閱參考資料。",
    "• 上機考佔期末成績 60%。",
    "• 請準時繳交作業與錄影檔。",
])
pages["課表查詢"] = make_page("課表查詢", [
    "【週一】視窗程式設計 / 資料結構",
    "【週二】計算機組織 / 離散數學",
    "（示意內容，可自行更換）",
])
pages["成績查詢"] = make_page("成績查詢", [
    "平時：85",
    "期中：80",
    "期末：待公布",
    "（示意內容，可自行更換）",
])

# 預設顯示第一頁
menu_list.selection_set(0)
show_page("最新公告")

root.mainloop()

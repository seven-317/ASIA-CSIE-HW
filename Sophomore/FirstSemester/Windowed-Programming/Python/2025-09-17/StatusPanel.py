from tkinter import *

root = Tk()
root.title("狀態面板")
root.geometry("800x400")

panel = Frame(root, bg="#f4f4f5", relief=RIDGE, bd=2, padx=10, pady=10)
panel.pack(fill="both", expand=True, padx=16, pady=16)

title = Label(panel, text="系統狀態", anchor="w", bg="#f4f4f5", font=("Arial", 12, "bold"))
title.grid(row=0, column=0, sticky="we", padx=2, pady=(0, 8))

Label(panel, bitmap="info", text="  系統資訊", compound="left",
      bg="light sky blue", relief=GROOVE, bd=3, padx=10, pady=6).grid(row=1, column=0, sticky="we", pady=4)

Label(panel, bitmap="warning", text="  注意事項", compound="left",
      bg="moccasin", relief=RAISED, bd=4, padx=10, pady=6).grid(row=2, column=0, sticky="we", pady=4)

Label(panel, bitmap="error", text="  錯誤發生", compound="left",
      bg="light coral", relief=SOLID, bd=2, padx=10, pady=6).grid(row=3, column=0, sticky="we", pady=4)

Label(panel, bitmap="question", text="  需要回覆？", compound="left",
      bg="pale turquoise", relief=RIDGE, bd=3, padx=10, pady=6).grid(row=4, column=0, sticky="we", pady=4)

Label(panel, bitmap="hourglass", text="  處理中…", compound="left",
      bg="thistle", relief=SUNKEN, bd=3, padx=10, pady=6).grid(row=5, column=0, sticky="we", pady=4)

Label(panel, bitmap="gray75", text="  背景任務 (75%)", compound="left",
      bg="gainsboro", relief=FLAT, bd=1, padx=10, pady=6).grid(row=6, column=0, sticky="we", pady=4)

panel.grid_columnconfigure(0, weight=1)

root.mainloop()

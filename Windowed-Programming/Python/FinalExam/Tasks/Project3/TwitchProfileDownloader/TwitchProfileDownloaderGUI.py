import requests
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

CLIENT_ID = '9cpeh3x1xtijcq33ew3908v6o8uvqz'
CLIENT_SECRET = 'sihgy6vmaabs3m5nkownsqjw2shzpj'

TWITCH_PURPLE = "#9146FF"
TWITCH_DARK_PURPLE = "#772CE8"
BG_COLOR = "#f0f0ff"
TEXT_COLOR = "#1f1f23"

def get_oauth_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()['access_token']

def get_user_info(username, headers):
    url = 'https://api.twitch.tv/helix/users'
    params = {'login': username}
    res = requests.get(url, headers=headers, params=params)
    data = res.json()['data']
    if not data:
        raise ValueError(f"使用者 {username} 不存在")
    return data[0]

def download_image(url, path):
    res = requests.get(url)
    res.raise_for_status()
    with open(path, 'wb') as f:
        f.write(res.content)

def select_folder():
    folder = filedialog.askdirectory(title="選擇下載資料夾")
    if folder:
        save_path.set(folder)

def start_download():
    usernames = entry_usernames.get().strip()
    folder = save_path.get()

    if not usernames:
        messagebox.showwarning("請輸入使用者名稱", "請至少輸入一個 Twitch 使用者名稱")
        return
    if not folder:
        messagebox.showwarning("請選擇儲存位置", "請選擇一個資料夾來儲存圖片")
        return

    username_list = [u.strip() for u in usernames.split(',') if u.strip()]
    output_log.set("")
    progress_bar["value"] = 0
    progress_bar["maximum"] = len(username_list)
    root.update_idletasks()

    try:
        token = get_oauth_token()
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {token}'
        }

        for index, username in enumerate(username_list, 1):
            output_log.set(f"下載中：{username} ({index}/{len(username_list)})")
            info = get_user_info(username, headers)
            user_dir = os.path.join(folder, username)
            os.makedirs(user_dir, exist_ok=True)

            if info['profile_image_url']:
                download_image(info['profile_image_url'], os.path.join(user_dir, 'avatar.jpg'))
            if info['offline_image_url']:
                download_image(info['offline_image_url'], os.path.join(user_dir, 'banner.jpg'))

            progress_bar["value"] = index
            root.update_idletasks()

        output_log.set("✅ 所有使用者下載完成")
        messagebox.showinfo("完成", "所有圖片下載成功")

    except Exception as e:
        messagebox.showerror("錯誤", str(e))
        output_log.set(f"❌ 發生錯誤：{str(e)}")

root = tk.Tk()
root.title("Twitch Profile Downloader")
root.geometry("560x370")
root.configure(bg=BG_COLOR)
root.resizable(False, False)

title = tk.Label(root, text="Twitch 頭貼 & 橫幅 批量下載工具",
                 font=("Segoe UI", 16, "bold"), fg=TWITCH_PURPLE, bg=BG_COLOR)
title.pack(pady=(15, 10))

frame_input = tk.Frame(root, bg=BG_COLOR)
frame_input.pack(padx=20, fill='x')

tk.Label(frame_input, text="輸入 Twitch 使用者名稱（逗號分隔）",
         bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky='w')
entry_usernames = tk.Entry(frame_input, width=60)
entry_usernames.grid(row=1, column=0, columnspan=2, pady=5)

tk.Label(frame_input, text="選擇儲存資料夾", bg=BG_COLOR, fg=TEXT_COLOR).grid(row=2, column=0, sticky='w')
save_path = tk.StringVar()
entry_path = tk.Entry(frame_input, textvariable=save_path, width=47)
entry_path.grid(row=3, column=0, pady=5, sticky='w')
btn_browse = tk.Button(frame_input, text="選擇資料夾", command=select_folder, bg="#ddddff", relief="flat")
btn_browse.grid(row=3, column=1, padx=10)

btn_download = tk.Button(root, text="⬇ 開始下載", font=("Segoe UI", 12, "bold"),
                         width=20, bg=TWITCH_PURPLE, fg="white", activebackground=TWITCH_DARK_PURPLE,
                         command=start_download, relief="flat")
btn_download.pack(pady=10)

style = ttk.Style()
style.theme_use('default')
style.configure("Twitch.Horizontal.TProgressbar", troughcolor='white', background=TWITCH_PURPLE, thickness=12)

progress_bar = ttk.Progressbar(root, orient="horizontal", style="Twitch.Horizontal.TProgressbar",
                               mode="determinate", length=420)
progress_bar.pack(pady=10)

output_log = tk.StringVar()
label_log = tk.Label(root, textvariable=output_log, bg=BG_COLOR, fg=TEXT_COLOR)
label_log.pack(pady=(5, 10))

root.mainloop()

import os
import shutil
import subprocess
import json
import tkinter as tk
from tkinter import filedialog, messagebox

# --- Chrome User Data パス ---
user_data_dir = os.path.join(
    os.environ["LOCALAPPDATA"],
    r"Google\Chrome\User Data"
)

if not os.path.exists(user_data_dir):
    messagebox.showerror("エラー", "Chrome User Data が見つかりません")
    exit()

# --- 表示名取得 ---
local_state_path = os.path.join(user_data_dir, "Local State")
profile_names = {}

if os.path.isfile(local_state_path):
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
            info_cache = local_state.get("profile", {}).get("info_cache", {})
            for key, value in info_cache.items():
                profile_names[key] = value.get("name", key)
    except Exception:
        pass

# --- プロファイル検出 ---
profiles = []
for folder in os.listdir(user_data_dir):
    pref_path = os.path.join(user_data_dir, folder, "Preferences")
    if os.path.isfile(pref_path):
        profiles.append(folder)

profiles.sort()

if not profiles:
    messagebox.showerror("エラー", "プロファイルが見つかりません")
    exit()

# --- GUI ---
root = tk.Tk()
root.title("Chrome プロファイル選択")

selected_profile = tk.StringVar()

display_map = {}
for p in profiles:
    display = f"{profile_names.get(p, p)} ({p})"
    display_map[display] = p

tk.Label(root, text="プロファイルを選択してください").pack(pady=5)

listbox = tk.Listbox(root, width=50, height=10)
for name in display_map.keys():
    listbox.insert(tk.END, name)
listbox.pack(padx=10, pady=5)

def on_execute():
    selection = listbox.curselection()
    if not selection:
        messagebox.showerror("エラー", "プロファイルを選択してください")
        return

    display_name = listbox.get(selection[0])
    profile_name = display_map[display_name]

    root.withdraw()

    initial_dir = "C:\\"

    if not os.path.exists(initial_dir):
        initial_dir = os.path.expanduser("~")  # fallback

    target_dir = filedialog.askdirectory(
        title="設定するフォルダを選択（キャンセルで空にする）",
        initialdir=initial_dir
    )

    # パス正規化
    if target_dir:
        target_dir = os.path.normpath(target_dir)
    else:
        target_dir = ""

    # Chrome終了
    subprocess.run(
        ["taskkill", "/f", "/im", "chrome.exe"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    pref_path = os.path.join(user_data_dir, profile_name, "Preferences")
    backup_path = pref_path + ".bak"

    # バックアップ
    shutil.copyfile(pref_path, backup_path)

    # JSON安全編集
    with open(pref_path, "r", encoding="utf-8") as f:
        prefs = json.load(f)

    if "savefile" in prefs:
        prefs["savefile"]["default_directory"] = target_dir

    if "selectfile" in prefs:
        prefs["selectfile"]["last_directory"] = target_dir

    with open(pref_path, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False)

    messagebox.showinfo(
        "完了",
        f"{display_name} を更新しました。\n\n"
        f"設定フォルダ: {target_dir if target_dir else '空'}\n\n"
        "【復旧方法】\n"
        "1. Chromeを終了\n"
        "2. Preferences を削除\n"
        "3. Preferences.bak を Preferences にリネーム\n"
        "4. Chrome起動"
    )

    root.destroy()

tk.Button(root, text="実行", command=on_execute).pack(pady=10)

root.mainloop()
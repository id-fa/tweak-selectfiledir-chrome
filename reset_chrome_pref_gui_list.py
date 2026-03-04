import os
import shutil
import subprocess
import json
import locale
import tkinter as tk
from tkinter import filedialog, messagebox

# --- i18n ---
_lang = locale.getdefaultlocale()[0] or ""
_ja = _lang.startswith("ja")

MSG = {
    "err":                "エラー" if _ja else "Error",
    "no_userdata":        "Chrome User Data が見つかりません" if _ja else "Chrome User Data not found",
    "no_profiles":        "プロファイルが見つかりません" if _ja else "No profiles found",
    "window_title":       "Chrome プロファイル選択" if _ja else "Chrome Profile Selector",
    "select_label":       "プロファイルを選択してください" if _ja else "Select a profile",
    "no_selection":       "プロファイルを選択してください" if _ja else "Please select a profile",
    "folder_dialog":      "設定するフォルダを選択（キャンセルで空にする）" if _ja else "Select folder (cancel to clear)",
    "btn_execute":        "実行" if _ja else "Execute",
    "done_title":         "完了" if _ja else "Done",
    "done_body":          "{name} を更新しました。\n\n設定フォルダ: {folder}\n\n【復旧方法】\n1. Chromeを終了\n2. Preferences を削除\n3. Preferences.bak を Preferences にリネーム\n4. Chrome起動"
                          if _ja else
                          "{name} updated.\n\nFolder: {folder}\n\n[Recovery]\n1. Close Chrome\n2. Delete Preferences\n3. Rename Preferences.bak to Preferences\n4. Restart Chrome",
    "empty_folder":       "空" if _ja else "(empty)",
    "confirm_kill_title": "確認" if _ja else "Confirm",
    "confirm_kill_body":  "Chromeを強制終了します。\n書きかけのフォーム等がある場合はデータが失われます。\n\n続行しますか？"
                          if _ja else
                          "Chrome will be force-closed.\nUnsaved data (e.g. forms) will be lost.\n\nContinue?",
}

# --- Chrome User Data パス ---
user_data_dir = os.path.join(
    os.environ["LOCALAPPDATA"],
    r"Google\Chrome\User Data"
)

if not os.path.exists(user_data_dir):
    messagebox.showerror(MSG["err"], MSG["no_userdata"])
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
    messagebox.showerror(MSG["err"], MSG["no_profiles"])
    exit()

# --- GUI ---
root = tk.Tk()
root.title(MSG["window_title"])

selected_profile = tk.StringVar()

display_map = {}
for p in profiles:
    display = f"{profile_names.get(p, p)} ({p})"
    display_map[display] = p

tk.Label(root, text=MSG["select_label"]).pack(pady=5)

listbox = tk.Listbox(root, width=50, height=10)
for name in display_map.keys():
    listbox.insert(tk.END, name)
listbox.pack(padx=10, pady=5)

def on_execute():
    selection = listbox.curselection()
    if not selection:
        messagebox.showerror(MSG["err"], MSG["no_selection"])
        return

    display_name = listbox.get(selection[0])
    profile_name = display_map[display_name]

    root.withdraw()

    initial_dir = "C:\\"

    if not os.path.exists(initial_dir):
        initial_dir = os.path.expanduser("~")  # fallback

    target_dir = filedialog.askdirectory(
        title=MSG["folder_dialog"],
        initialdir=initial_dir
    )

    # パス正規化
    if target_dir:
        target_dir = os.path.normpath(target_dir)
    else:
        target_dir = ""

    # Chrome終了前の確認
    if not messagebox.askokcancel(MSG["confirm_kill_title"], MSG["confirm_kill_body"]):
        root.deiconify()
        return

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
        MSG["done_title"],
        MSG["done_body"].format(
            name=display_name,
            folder=target_dir if target_dir else MSG["empty_folder"]
        )
    )

    root.destroy()

tk.Button(root, text=MSG["btn_execute"], command=on_execute).pack(pady=10)

root.mainloop()
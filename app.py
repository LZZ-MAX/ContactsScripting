import sqlite3
import re
import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

conn = sqlite3.connect('contacts.db')
cursor = conn.cursor()

def scrape_contacts():
    """
    從指定的URL抓取聯絡人資訊。

    回傳:
    list: 包含聯絡人資訊的列表，每個聯絡人是一個包含姓名、職稱和Email的元組。
    """
    response = requests.get('https://csie.ncut.edu.tw/content.php?key=86OP82WJQO')
    try:
        response.raise_for_status()
        print("成功")
    except requests.exceptions.HTTPError as HTTPError:
        if response.status_code == 404:
            messagebox.showerror("網路錯誤", "無法取得網頁：404")
        else:
            messagebox.showerror("網路錯誤", f"HTTP 錯誤：{response.status_code}")

    HTMLContent = response.text
    contact = []

    pattern = re.compile(
        r'<div\s+class="member_name">.*?<a\s+href="content_teacher_detail\.php\?teacher_rkey=.*?">\s*(.*?)\s*</a>'
        r'.*?<div\s+class="member_info_content">\s*(.*?)\s*</div>.*?<a\s+href="mailto:(.*?)">',
        re.DOTALL
    )
    matches = pattern.findall(HTMLContent)

    for match in matches:
        name, title, email = match
        name = re.sub(r'\s+', ' ', name).strip()
        title = re.sub(r'\s+', ' ', title).strip()
        email = email.replace('//', '').strip()
        contact.append((name, title, email))
    return contact

def create_table():
    """
    建立聯絡人資料表（如果不存在）。
    """
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
        '''
    )

def insert_contact(name, title, email):
    """
    插入聯絡人資訊到資料庫。

    參數:
    name (str): 聯絡人姓名。
    title (str): 聯絡人職稱。
    email (str): 聯絡人Email。
    """
    cursor.execute(
        '''
        INSERT INTO contacts (name, title, email)
        VALUES (?, ?, ?)
        ''',
        (name, title, email)
    )
    conn.commit()
    conn.close()

def pad_string(text, width):
    """
    將字串填充到指定的寬度。

    參數:
    text (str): 要填充的字串。
    width (int): 目標寬度。

    回傳:
    str: 填充後的字串。
    """
    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    padding_length = width - len(text) - chinese_count
    return text + ' ' * max(padding_length, 0)

def display_contacts(contacts):
    """
    顯示聯絡人資訊。

    參數:
    contacts (list): 包含聯絡人資訊的列表，每個聯絡人是一個包含姓名、職稱和Email的元組。
    """
    contact_text.configure(state="normal")
    contact_text.delete(1.0, tk.END)

    headers = ['姓名', '職稱', 'Email']
    widths = [12, 30, 40]

    header_line = ''.join(pad_string(header, width) for header, width in zip(headers, widths))
    contact_text.insert(tk.END, header_line + "\n")
    separator = ''.join('-' * width for width in widths)
    contact_text.insert(tk.END, separator + "\n")

    for name, title, email in contacts:
        row = [
            pad_string(name, widths[0]),
            pad_string(title, widths[1]),
            pad_string(email, widths[2])
        ]
        contact_text.insert(tk.END, ''.join(row) + "\n")

    contact_text.configure(state="disabled")

def tkinter_window():
    """
    建立並顯示Tkinter視窗。
    """
    global contact_text
    root = tk.Tk()
    root.title("聯絡資訊爬蟲")
    root.geometry("640x480")
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)

    url_label = ttk.Label(root, text="URL:")
    url_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

    url_entry = ttk.Entry(root, width=60)
    url_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
    url_entry.insert(0, 'https://csie.ncut.edu.tw/content.php?key=86OP82WJQO')

    fetch_button = ttk.Button(root, text="抓取", command=lambda: display_contacts(scrape_contacts()))
    fetch_button.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)

    contact_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
    contact_text.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)

    root.mainloop()


create_table()
tkinter_window()
import sqlite3
import re
import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

conn = sqlite3.connect('contacts.db')
cursor = conn.cursor()

url = 'https://csie.ncut.edu.tw/content.php?key=86OP82WJQO'

def create_table():
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

def scrape_contacts(url):
    response = requests.get(url)
    try:
        response.raise_for_status()
        print("成功")
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            messagebox.showerror("網路錯誤", "無法取得網頁：404")
        else:
            messagebox.showerror("網路錯誤", f"HTTP 錯誤：{response.status_code}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("網路錯誤", f"錯誤：{e}")
        return


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

def insert_contact(name, title, email):
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
    return text.ljust(width)

def display_contacts(contacts):
    contact_text.configure(state="normal")
    contact_text.delete(1.0, tk.END)


    headers = ['姓名', '職稱', 'Email']
    widths = [12, 30, 30]

    # Create the header line with padding
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
    url_entry.insert(0, url)


    fetch_button = ttk.Button(root, text="抓取", command=lambda: display_contacts(scrape_contacts(url_entry.get())))
    fetch_button.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)


    contact_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
    contact_text.grid(row=1, column=0, columnspan=3, sticky=tk.NSEW, padx=5, pady=5)

    root.mainloop()


create_table()
tkinter_window()

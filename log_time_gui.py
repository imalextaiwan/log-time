#!/usr/bin/env python3
"""log-time 視窗版：把 LOG 檔拖進視窗，或按「選擇檔案…」，顯示開始、結束、總共時間。

用法：
  雙擊 log-time.exe                開視窗，拖入或選擇 LOG 檔
  把 LOG 檔拖到 log-time.exe 圖示上   開視窗並直接顯示結果
  log-time.exe --selftest OUT a.log   建立視窗、算 a.log，把結果寫到 OUT 後關閉（CI 用）
"""
import sys
import tkinter as tk
from tkinter import filedialog

from log_time import __version__, summarize_file

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:  # 沒有 tkinterdnd2 時只剩「選擇檔案…」
    TkinterDnD = None

HINT = '把 LOG 檔拖到這個視窗裡（可一次多個），或按「選擇檔案…」'


class App:
    def __init__(self):
        self.dnd = False
        if TkinterDnD is not None:
            try:
                self.root = TkinterDnD.Tk()
                self.dnd = True
            except Exception:
                self.root = tk.Tk()
        else:
            self.root = tk.Tk()
        root = self.root
        root.title(f'log-time {__version__}')
        root.geometry('760x460')
        root.minsize(480, 260)

        bar = tk.Frame(root)
        bar.pack(fill='x', padx=10, pady=(10, 4))
        tk.Button(bar, text='選擇檔案…', command=self.choose).pack(side='left')
        tk.Button(bar, text='複製結果', command=self.copy).pack(side='left', padx=6)
        tk.Button(bar, text='清除', command=self.clear).pack(side='left')
        hint = HINT if self.dnd else '這台電腦無法拖放，請按「選擇檔案…」'
        tk.Label(bar, text=hint, fg='#555').pack(side='left', padx=10)

        frame = tk.Frame(root)
        frame.pack(fill='both', expand=True, padx=10, pady=(4, 10))
        scroll = tk.Scrollbar(frame)
        scroll.pack(side='right', fill='y')
        self.text = tk.Text(frame, wrap='none', font=('Microsoft JhengHei UI', 11),
                            yscrollcommand=scroll.set, state='disabled')
        self.text.pack(side='left', fill='both', expand=True)
        scroll.config(command=self.text.yview)

        if self.dnd:
            for w in (root, self.text):
                w.drop_target_register(DND_FILES)
                w.dnd_bind('<<Drop>>', self.on_drop)

    def append(self, s):
        self.text.config(state='normal')
        if self.text.get('1.0', 'end-1c'):
            self.text.insert('end', '\n\n')
        self.text.insert('end', s)
        self.text.config(state='disabled')
        self.text.see('end')

    def run_files(self, paths):
        self.root.config(cursor='watch')
        self.root.update_idletasks()
        try:
            for p in paths:
                self.append(summarize_file(p))
                self.root.update_idletasks()
        finally:
            self.root.config(cursor='')

    def on_drop(self, event):
        self.run_files(self.root.tk.splitlist(event.data))
        return event.action

    def choose(self):
        paths = filedialog.askopenfilenames(
            title='選擇 LOG 檔',
            filetypes=[('LOG／文字檔', '*.log *.txt *.csv'), ('所有檔案', '*.*')])
        if paths:
            self.run_files(paths)

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.text.get('1.0', 'end-1c'))

    def clear(self):
        self.text.config(state='normal')
        self.text.delete('1.0', 'end')
        self.text.config(state='disabled')

    def result(self):
        return self.text.get('1.0', 'end-1c')


def main(argv):
    if argv[:1] == ['--selftest']:
        out, files = argv[1], argv[2:]
        app = App()
        app.root.update()
        app.run_files(files)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(f'dnd={"ok" if app.dnd else "missing"}\n{app.result()}\n')
        app.root.destroy()
        return
    app = App()
    if argv:
        app.root.after(100, app.run_files, argv)
    app.root.mainloop()


if __name__ == '__main__':
    main(sys.argv[1:])

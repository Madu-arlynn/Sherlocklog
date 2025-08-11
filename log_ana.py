import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import sqlite3
import os
from datetime import datetime
import hashlib

DB_FILE = "sherlocklog.db"

class LogAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Logs")
        self.root.geometry("900x600")

        self.logs = []
        self.filtered_logs = []
        self.filters = []
        self.usuario_id = None

        self.init_db()
        self.show_login_screen()

    # ============================
    # BANCO DE DADOS
    # ============================
    def init_db(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS filtros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                nome TEXT,
                tipo TEXT,
                valor TEXT,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
            )
        """)
        conn.commit()
        conn.close()

    def salvar_filtros_bd(self, nome):
        if not self.usuario_id:
            messagebox.showerror("Erro", "Nenhum usuário logado.")
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM filtros WHERE id_usuario=? AND nome=?", (self.usuario_id, nome))
        for f in self.filters:
            cursor.execute("""
                INSERT INTO filtros (id_usuario, nome, tipo, valor)
                VALUES (?, ?, ?, ?)
            """, (self.usuario_id, nome, f["type"], f["value"]))
        conn.commit()
        conn.close()
        messagebox.showinfo("Salvo", f"Grupo '{nome}' salvo no banco.")

    def carregar_filtros_bd(self, nome):
        if not self.usuario_id:
            messagebox.showerror("Erro", "Nenhum usuário logado.")
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tipo, valor FROM filtros
            WHERE id_usuario=? AND nome=?
        """, (self.usuario_id, nome))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            messagebox.showerror("Erro", f"Grupo '{nome}' não encontrado no banco.")
            return
        self.filters = [{"type": t, "value": v, "active": tk.BooleanVar(value=True)} for t, v in rows]
        self.refresh_filter_list()

    def excluir_filtros_bd(self, nome):
        if not self.usuario_id:
            messagebox.showerror("Erro", "Nenhum usuário logado.")
            return
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM filtros WHERE id_usuario=? AND nome=?", (self.usuario_id, nome))
        conn.commit()
        conn.close()
        messagebox.showinfo("Removido", f"Grupo '{nome}' excluído do banco.")

    # ============================
    # AUTENTICAÇÃO
    # ============================
    def show_login_screen(self):
        self.clear_window()

        login_frame = ttk.Frame(self.root, padding=20)
        login_frame.pack(expand=True)

        ttk.Label(login_frame, text="Usuário:").pack()
        username_entry = ttk.Entry(login_frame)
        username_entry.pack()

        ttk.Label(login_frame, text="Senha:").pack()
        password_entry = ttk.Entry(login_frame, show="*")
        password_entry.pack()

        def login():
            user = username_entry.get().strip()
            pwd = hashlib.sha256(password_entry.get().encode()).hexdigest()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE username=? AND password=?", (user, pwd))
            row = cursor.fetchone()
            conn.close()
            if row:
                self.usuario_id = row[0]
                self.create_widgets()
            else:
                messagebox.showerror("Erro", "Usuário ou senha inválidos.")

        def register():
            user = username_entry.get().strip()
            pwd = hashlib.sha256(password_entry.get().encode()).hexdigest()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (user, pwd))
                conn.commit()
                messagebox.showinfo("Sucesso", "Usuário registrado.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", "Usuário já existe.")
            conn.close()

        ttk.Button(login_frame, text="Entrar", command=login).pack(pady=5)
        ttk.Button(login_frame, text="Registrar", command=register).pack()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ============================
    # INTERFACE PRINCIPAL
    # ============================
    def create_widgets(self):
        self.clear_window()

        self.text_area = tk.Text(self.root, wrap="none")
        self.text_area.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        filter_frame = ttk.Frame(self.root, padding=10)
        filter_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(filter_frame, text="Palavra-chave:").pack(anchor='w')
        self.keyword_entry = ttk.Entry(filter_frame)
        self.keyword_entry.pack(fill='x')
        ttk.Button(filter_frame, text="Adicionar", command=self.add_keyword_filter).pack(pady=2)

        ttk.Label(filter_frame, text="Regex:").pack(anchor='w', pady=(10, 0))
        self.regex_entry = ttk.Entry(filter_frame)
        self.regex_entry.pack(fill='x')
        ttk.Button(filter_frame, text="Adicionar", command=self.add_regex_filter).pack(pady=2)

        ttk.Label(filter_frame, text="Salvar/Carregar Filtros:").pack(anchor='w', pady=(10, 0))
        self.preset_entry = ttk.Entry(filter_frame)
        self.preset_entry.pack(fill='x')
        ttk.Button(filter_frame, text="Salvar Grupo", command=lambda: self.salvar_filtros_bd(self.preset_entry.get().strip())).pack(pady=2)
        ttk.Button(filter_frame, text="Carregar Grupo", command=lambda: self.carregar_filtros_bd(self.preset_entry.get().strip())).pack()
        ttk.Button(filter_frame, text="Excluir Grupo", command=lambda: self.excluir_filtros_bd(self.preset_entry.get().strip())).pack(pady=2)

        ttk.Button(filter_frame, text="Abrir Arquivo Log", command=self.load_log_file).pack(pady=10)

    # ============================
    # LÓGICA DE FILTROS (MESMA DO SEU CÓDIGO)
    # ============================
    def load_log_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Log", "*.log")])
        if not file_path:
            return
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.logs = f.readlines()
        self.display_logs(self.logs)

    def display_logs(self, logs):
        self.text_area.delete('1.0', tk.END)
        for line in logs:
            self.text_area.insert(tk.END, line)

    def add_keyword_filter(self):
        word = self.keyword_entry.get().strip()
        if word:
            self.filters.append({"type": "keyword", "value": word, "active": tk.BooleanVar(value=True)})
            self.refresh_filter_list()
            self.keyword_entry.delete(0, tk.END)

    def add_regex_filter(self):
        regex = self.regex_entry.get().strip()
        if regex:
            self.filters.append({"type": "regex", "value": regex, "active": tk.BooleanVar(value=True)})
            self.refresh_filter_list()
            self.regex_entry.delete(0, tk.END)

    def refresh_filter_list(self):
        for widget in self.root.pack_slaves():
            if isinstance(widget, ttk.Frame):
                for sub in widget.pack_slaves():
                    if isinstance(sub, ttk.Frame):
                        for w in sub.winfo_children():
                            w.destroy()
        # recria lista
        for f in self.filters:
            cb = ttk.Checkbutton(self.root, text=f"{f['type']}: {f['value']}", variable=f['active'])
            cb.pack(anchor='w')

if __name__ == "__main__":
    root = tk.Tk()
    app = LogAnalyzerApp(root)
    root.mainloop()

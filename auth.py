import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
from log_analyzer import LogAnalyzerApp

USUARIOS_FILE = "usuarios.json"

def carregar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, 'r') as f:
            return json.load(f)
    return {}

def salvar_usuarios(usuarios):
    with open(USUARIOS_FILE, 'w') as f:
        json.dump(usuarios, f, indent=4)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x220")
        self.usuarios = carregar_usuarios()
        self.create_login_ui()

    def create_login_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Usuário:").pack(anchor="w")
        self.username_entry = ttk.Entry(frame)
        self.username_entry.pack(fill='x', pady=5)

        ttk.Label(frame, text="Senha:").pack(anchor="w")
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(fill='x', pady=5)

        ttk.Button(frame, text="Entrar", command=self.login).pack(pady=5)
        ttk.Button(frame, text="Criar Conta", command=self.abrir_tela_cadastro).pack(pady=5)

    def login(self):
        usuario = self.username_entry.get().strip()
        senha = self.password_entry.get()

        if not usuario or not senha:
            messagebox.showwarning("Campos vazios", "Preencha todos os campos.")
            return

        senha_cripto = hash_senha(senha)

        if usuario in self.usuarios and self.usuarios[usuario] == senha_cripto:
            messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario}!")
            self.root.destroy()
            main_app = tk.Tk()
            LogAnalyzerApp(main_app)
            main_app.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    def abrir_tela_cadastro(self):
        CadastroApp(tk.Toplevel(self.root), self.usuarios)

class CadastroApp:
    def __init__(self, root, usuarios):
        self.root = root
        self.root.title("Cadastro")
        self.root.geometry("300x220")
        self.usuarios = usuarios
        self.create_ui()

    def create_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Novo Usuário:").pack(anchor="w")
        self.username_entry = ttk.Entry(frame)
        self.username_entry.pack(fill='x', pady=5)

        ttk.Label(frame, text="Senha:").pack(anchor="w")
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.pack(fill='x', pady=5)

        ttk.Label(frame, text="Confirmar Senha:").pack(anchor="w")
        self.confirm_entry = ttk.Entry(frame, show="*")
        self.confirm_entry.pack(fill='x', pady=5)

        ttk.Button(frame, text="Cadastrar", command=self.cadastrar).pack(pady=10)

    def cadastrar(self):
        usuario = self.username_entry.get().strip()
        senha = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not usuario or not senha or not confirm:
            messagebox.showwarning("Campos vazios", "Preencha todos os campos.")
            return

        if usuario in self.usuarios:
            messagebox.showerror("Erro", "Usuário já existe.")
            return

        if senha != confirm:
            messagebox.showerror("Erro", "As senhas não coincidem.")
            return

        self.usuarios[usuario] = hash_senha(senha)
        salvar_usuarios(self.usuarios)
        messagebox.showinfo("Sucesso", "Conta criada com sucesso!")
        self.root.destroy()

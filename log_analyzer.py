import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
import json
import os
from datetime import datetime

FILTROS_SALVOS = "filtros_salvos.json"

class LogAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Logs")
        self.root.geometry("900x600")

        self.logs = []
        self.filtered_logs = []
        self.filters = []

        self.create_widgets()

    def create_widgets(self):
        self.text_area = tk.Text(self.root, wrap="none")
        self.text_area.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        filter_frame = ttk.Frame(self.root, padding=10)
        filter_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Palavras-chave
        ttk.Label(filter_frame, text="Palavra-chave:").pack(anchor='w')
        self.keyword_entry = ttk.Entry(filter_frame)
        self.keyword_entry.pack(fill='x')
        ttk.Button(filter_frame, text="Adicionar", command=self.add_keyword_filter).pack(pady=2)

        # Regex
        ttk.Label(filter_frame, text="Regex:").pack(anchor='w', pady=(10, 0))
        self.regex_entry = ttk.Entry(filter_frame)
        self.regex_entry.pack(fill='x')
        ttk.Button(filter_frame, text="Adicionar", command=self.add_regex_filter).pack(pady=2)

        # Filtro por Data
        ttk.Label(filter_frame, text="Filtro por Data (YYYY-MM-DD HH:MM:SS):").pack(anchor='w', pady=(10, 0))
        self.start_entry = ttk.Entry(filter_frame)
        self.start_entry.insert(0, "Data Inicial")
        self.start_entry.pack(fill='x')
        self.end_entry = ttk.Entry(filter_frame)
        self.end_entry.insert(0, "Data Final")
        self.end_entry.pack(fill='x')
        ttk.Button(filter_frame, text="Aplicar Filtro de Data", command=self.apply_date_filter).pack(pady=2)

        # Lista de filtros ativos
        ttk.Label(filter_frame, text="Filtros Ativos:").pack(anchor='w', pady=(10, 0))
        self.active_filters_frame = ttk.Frame(filter_frame)
        self.active_filters_frame.pack(fill='x')

        # AND / OR
        ttk.Label(filter_frame, text="Modo de Filtro:").pack(anchor='w', pady=(10, 0))
        self.filter_mode = tk.StringVar(value="AND")
        ttk.Radiobutton(filter_frame, text="Todos (AND)", variable=self.filter_mode, value="AND").pack(anchor='w')
        ttk.Radiobutton(filter_frame, text="Algum (OR)", variable=self.filter_mode, value="OR").pack(anchor='w')

        ttk.Button(filter_frame, text="Aplicar Filtros Ativos", command=self.apply_filters).pack(pady=5)
        ttk.Button(filter_frame, text="Limpar Filtros", command=self.clear_filters).pack()
        ttk.Button(filter_frame, text="Gerar Resumo", command=self.gerar_resumo).pack(pady=5)

        # Presets
        ttk.Label(filter_frame, text="Salvar/Carregar Filtros:").pack(anchor='w', pady=(10, 0))
        self.preset_entry = ttk.Entry(filter_frame)
        self.preset_entry.pack(fill='x')
        ttk.Button(filter_frame, text="Salvar Grupo", command=self.salvar_grupo).pack(pady=2)
        ttk.Button(filter_frame, text="Carregar Grupo", command=self.carregar_grupo).pack()
        ttk.Button(filter_frame, text="Excluir Grupo", command=self.excluir_grupo).pack(pady=2)

        # Abrir arquivo
        ttk.Button(filter_frame, text="Abrir Arquivo Log", command=self.load_log_file).pack(pady=10)

    def ensure_logs_loaded(self):
        """Se não tiver logs carregados, pega o que está na caixa de texto."""
        if not self.logs:
            conteudo = self.text_area.get("1.0", tk.END).splitlines()
            self.logs = [linha for linha in conteudo if linha.strip()]

    def load_log_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Arquivos de Texto", "*.log *.txt"),
                ("Todos os Arquivos", "*.*")
            ]
        )
        if not file_path:
            return
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            self.logs = f.readlines()
        self.display_logs(self.logs)

    def display_logs(self, logs):
        self.text_area.delete('1.0', tk.END)
        for line in logs:
            self.text_area.insert(tk.END, line if line.endswith("\n") else line + "\n")

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
        for widget in self.active_filters_frame.winfo_children():
            widget.destroy()
        for i, f in enumerate(self.filters):
            cb = ttk.Checkbutton(self.active_filters_frame, text=f"{f['type']}: {f['value']}", variable=f['active'])
            cb.pack(anchor='w')

    def clear_filters(self):
        self.ensure_logs_loaded()
        self.filters.clear()
        self.refresh_filter_list()
        self.filtered_logs = self.logs
        self.display_logs(self.logs)

    def apply_filters(self):
        self.ensure_logs_loaded()
        active_filters = [f for f in self.filters if f['active'].get()]
        if not active_filters:
            self.display_logs(self.logs)
            return

        filtered = []
        for line in self.logs:
            matches = []
            for f in active_filters:
                if f['type'] == "keyword":
                    matches.append(f['value'].lower() in line.lower())
                elif f['type'] == "regex":
                    try:
                        matches.append(bool(re.search(f['value'], line)))
                    except re.error:
                        messagebox.showerror("Erro de Regex", f"Regex inválida: {f['value']}")
                        return

            if self.filter_mode.get() == "AND" and all(matches):
                filtered.append(line)
            elif self.filter_mode.get() == "OR" and any(matches):
                filtered.append(line)

        self.filtered_logs = filtered
        self.display_logs(filtered)

    def apply_date_filter(self):
        self.ensure_logs_loaded()
        fmt = "%Y-%m-%d %H:%M:%S"
        try:
            start = datetime.strptime(self.start_entry.get(), fmt)
            end = datetime.strptime(self.end_entry.get(), fmt)
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido")
            return

        result = []
        for line in self.logs:
            match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line)
            if match:
                timestamp = datetime.strptime(match.group(), fmt)
                if start <= timestamp <= end:
                    result.append(line)

        self.filtered_logs = result
        self.display_logs(result)

    def gerar_resumo(self):
        self.ensure_logs_loaded()
        total = len(self.filtered_logs)
        erros = len([l for l in self.filtered_logs if "error" in l.lower()])
        avisos = len([l for l in self.filtered_logs if "warning" in l.lower()])

        resumo = f"Total de linhas: {total}\nErros: {erros}\nAvisos: {avisos}"
        messagebox.showinfo("Resumo do Log", resumo)

    def salvar_grupo(self):
        nome = self.preset_entry.get().strip()
        if not nome:
            messagebox.showwarning("Nome Inválido", "Informe um nome para o grupo de filtros.")
            return

        grupos = self.carregar_todos_os_grupos()
        grupos[nome] = [{"type": f["type"], "value": f["value"]} for f in self.filters]
        with open(FILTROS_SALVOS, 'w') as f:
            json.dump(grupos, f, indent=4)
        messagebox.showinfo("Salvo", f"Grupo '{nome}' salvo com sucesso.")

    def carregar_grupo(self):
        nome = self.preset_entry.get().strip()
        grupos = self.carregar_todos_os_grupos()
        if nome not in grupos:
            messagebox.showerror("Erro", f"Grupo '{nome}' não encontrado.")
            return

        self.filters = []
        for f in grupos[nome]:
            self.filters.append({"type": f["type"], "value": f["value"], "active": tk.BooleanVar(value=True)})
        self.refresh_filter_list()

    def excluir_grupo(self):
        nome = self.preset_entry.get().strip()
        grupos = self.carregar_todos_os_grupos()
        if nome in grupos:
            del grupos[nome]
            with open(FILTROS_SALVOS, 'w') as f:
                json.dump(grupos, f, indent=4)
            messagebox.showinfo("Removido", f"Grupo '{nome}' removido.")

    def carregar_todos_os_grupos(self):
        if os.path.exists(FILTROS_SALVOS):
            with open(FILTROS_SALVOS, 'r') as f:
                return json.load(f)
        return {}

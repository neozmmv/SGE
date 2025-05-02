import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection

class MonitorFrame(tk.Frame):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.tree = None

        tk.Label(self, text="Monitores", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Nome", "CPF", "Perfil"), show="headings")
        for col in ("ID", "Nome", "CPF", "Perfil"):
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        tk.Button(self, text="Adicionar Monitor", command=self.abrir_cadastro).pack(pady=5)
        tk.Button(self, text="Voltar", command=self.voltar).pack(side=tk.RIGHT, padx=10, pady=5)

        self.carregar_monitores()

    def carregar_monitores(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, cpf, perfil
            FROM monitores
            WHERE escola_id = %s
        """, (self.usuario["escola_id"],))
        for monitor in cursor.fetchall():
            self.tree.insert("", tk.END, values=monitor)
        conn.close()

    def abrir_cadastro(self):
        self.new_window = tk.Toplevel(self)
        self.new_window.title("Cadastro de Monitor")
        self.new_window.geometry("400x300")

        tk.Label(self.new_window, text="Nome:").pack()
        self.nome_entry = tk.Entry(self.new_window)
        self.nome_entry.pack()

        tk.Label(self.new_window, text="CPF:").pack()
        self.cpf_entry = tk.Entry(self.new_window)
        self.cpf_entry.pack()

        tk.Label(self.new_window, text="Senha:").pack()
        self.senha_entry = tk.Entry(self.new_window, show="*")
        self.senha_entry.pack()

        tk.Label(self.new_window, text="Perfil (monitor/admin):").pack()
        self.perfil_entry = tk.Entry(self.new_window)
        self.perfil_entry.pack()

        tk.Button(self.new_window, text="Salvar", command=self.salvar_monitor).pack(pady=10)

    def salvar_monitor(self):
        nome = self.nome_entry.get()
        cpf = self.cpf_entry.get()
        senha = self.senha_entry.get()
        perfil = self.perfil_entry.get()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO monitores (nome, cpf, senha, perfil, escola_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, cpf, senha, perfil, self.usuario["escola_id"]))
        conn.commit()
        conn.close()
        self.new_window.destroy()
        self.carregar_monitores()

    def voltar(self):
        from main import MainFrame
        self.destroy()
        MainFrame(self.master, self.usuario).pack()

import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection

class ObservacaoFrame(tk.Frame):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.tree = None
        self.aluno_id = None

        tk.Label(self, text="Observações dos Alunos", font=("Arial", 14)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Aluno", "Tipo", "Descrição", "Consequências", "Data"), show="headings")
        for col in ("ID", "Aluno", "Tipo", "Descrição", "Consequências", "Data"):
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        tk.Button(self, text="Adicionar Observação", command=self.abrir_cadastro).pack(pady=5)
        tk.Button(self, text="Voltar", command=self.voltar).pack(side=tk.RIGHT, padx=10, pady=5)

        self.carregar_observacoes()

    def carregar_observacoes(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, a.nome, o.tipo, o.descricao, o.consequencias, o.data
            FROM observacoes o
            JOIN alunos a ON o.aluno_id = a.id
            WHERE a.escola_id = %s
        """, (self.usuario["escola_id"],))
        for obs in cursor.fetchall():
            self.tree.insert("", tk.END, values=obs)
        conn.close()

    def abrir_cadastro(self):
        self.new_window = tk.T_

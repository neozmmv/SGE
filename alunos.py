import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection

class AlunoFrame(tk.Frame):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.tree = None


        tk.Label(self, text="Alunos da Escola", font=("Arial", 14)).pack(pady=10)

        # Criando um frame para os campos de pesquisa lado a lado
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)

        # Label e campos de busca
        tk.Label(search_frame, text="Nome:").grid(row=0, column=0, padx=5)
        self.busca_nome = tk.Entry(search_frame)
        self.busca_nome.grid(row=0, column=1, padx=5)

        tk.Label(search_frame, text="Número:").grid(row=0, column=2, padx=5)
        self.busca_numero = tk.Entry(search_frame)
        self.busca_numero.grid(row=0, column=3, padx=5)

        tk.Label(search_frame, text="Turma:").grid(row=0, column=4, padx=5)
        self.busca_turma = tk.Entry(search_frame)
        self.busca_turma.grid(row=0, column=5, padx=5)

        tk.Label(search_frame, text="Ano Letivo:").grid(row=0, column=6, padx=5)
        self.busca_ano = tk.Entry(search_frame)
        self.busca_ano.grid(row=0, column=7, padx=5)

        # Botão de busca
        tk.Button(self, text="Buscar", command=self.buscar_aluno).pack(pady=10)

        # Botão de cadastro
        tk.Button(self, text="Cadastrar Novo Aluno", command=self.abrir_cadastro).pack(pady=5)

        # Tabela de alunos
        self.tree = ttk.Treeview(self, columns=("ID", "Nome", "Número", "Turma", "Ano"), show="headings")
        for col in ("ID", "Nome", "Número", "Turma", "Ano"):
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Botões de ação
        tk.Button(self, text="Editar", command=self.editar).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(self, text="Excluir", command=self.excluir).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(self, text="Voltar", command=self.voltar).pack(side=tk.RIGHT, padx=10, pady=5)

        # Carregar alunos inicialmente
        self.carregar_alunos()

    def buscar_aluno(self):
        """Função para buscar aluno com base nos campos de pesquisa"""
        nome = self.busca_nome.get()
        numero = self.busca_numero.get()
        turma = self.busca_turma.get()
        ano = self.busca_ano.get()

        self.carregar_alunos(nome, numero, turma, ano)

    def carregar_alunos(self, nome=None, numero=None, turma=None, ano=None):
        """Carregar alunos com base nos filtros fornecidos"""
        # Limpar a tabela existente
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()

        # Criar a consulta SQL dinamicamente, dependendo dos filtros fornecidos
        query = "SELECT id, nome, numero, turma, ano_letivo FROM alunos WHERE escola_id = %s"
        params = [self.usuario["escola_id"]]

        if nome:
            query += " AND nome LIKE %s"
            params.append(f"%{nome}%")
        if numero:
            query += " AND numero LIKE %s"
            params.append(f"%{numero}%")
        if turma:
            query += " AND turma LIKE %s"
            params.append(f"%{turma}%")
        if ano:
            query += " AND ano_letivo LIKE %s"
            params.append(f"%{ano}%")

        cursor.execute(query, tuple(params))

        # Inserir os resultados na tabela
        for aluno in cursor.fetchall():
            self.tree.insert("", tk.END, values=aluno)

        conn.close()

    def abrir_cadastro(self):
        self.new_window = tk.Toplevel(self)
        self.new_window.title("Cadastro de Aluno")
        self.new_window.geometry("300x250")

        labels = ["Nome", "Número", "Turma", "Ano Letivo"]
        self.entries = {}
        for label in labels:
            tk.Label(self.new_window, text=label).pack()
            entry = tk.Entry(self.new_window)
            entry.pack()
            self.entries[label.lower().replace(" ", "_")] = entry

        tk.Button(self.new_window, text="Salvar", command=self.salvar_aluno).pack(pady=10)

    def salvar_aluno(self):
        dados = {k: v.get() for k, v in self.entries.items()}
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alunos (nome, numero, turma, ano_letivo, escola_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            dados["nome"], dados["número"], dados["turma"], dados["ano_letivo"], self.usuario["escola_id"]
        ))
        conn.commit()
        conn.close()
        self.new_window.destroy()
        self.carregar_alunos()

    def editar(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Seleção", "Selecione um aluno para editar.")
            return
        values = self.tree.item(item, "values")
        self.abrir_cadastro()
        for i, key in enumerate(["nome", "número", "turma", "ano_letivo"]):
            self.entries[key].insert(0, values[i+1])

        def salvar_edicao():
            dados = {k: v.get() for k, v in self.entries.items()}
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE alunos SET nome=%s, numero=%s, turma=%s, ano_letivo=%s WHERE id=%s
            """, (
                dados["nome"], dados["número"], dados["turma"], dados["ano_letivo"], values[0]
            ))
            conn.commit()
            conn.close()
            self.new_window.destroy()
            self.carregar_alunos()

        self.new_window.children['!button'].config(command=salvar_edicao)

    def excluir(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Seleção", "Selecione um aluno para excluir.")
            return
        aluno_id = self.tree.item(item, "values")[0]
        if messagebox.askyesno("Confirmação", "Deseja excluir este aluno?"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM alunos WHERE id=%s", (aluno_id,))
            conn.commit()
            conn.close()
            self.carregar_alunos()

    def voltar(self):
        from main import MainFrame
        self.destroy()
        MainFrame(self.master, self.usuario).pack()

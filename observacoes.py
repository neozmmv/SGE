import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_connection
from datetime import datetime

class ObservacaoFrame(tk.Frame):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.tree = None
        self.aluno_id = None
        self.escola_selecionada = None
        self.turma_selecionada = None

        # Criar notebook para separar observações gerais e disciplina
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=5)

        # Frame para observações gerais
        self.frame_geral = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_geral, text="Observações Gerais")

        # Frame para disciplina
        self.frame_disciplina = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_disciplina, text="Disciplina")

        # Configurar frame de observações gerais
        self.setup_frame_geral()
        
        # Configurar frame de disciplina
        self.setup_frame_disciplina()

    def setup_frame_geral(self):
        tk.Label(self.frame_geral, text="Observações dos Alunos", font=("Arial", 14)).pack(pady=10)

        # Frame para seleção de escola e turma
        frame_filtros = ttk.Frame(self.frame_geral)
        frame_filtros.pack(fill="x", padx=10, pady=5)

        # Escola
        ttk.Label(frame_filtros, text="Escola:").pack(side="left", padx=5)
        self.escola_var_geral = tk.StringVar()
        self.escola_combo_geral = ttk.Combobox(frame_filtros, textvariable=self.escola_var_geral, width=30)
        self.escola_combo_geral.pack(side="left", padx=5)
        self.escola_combo_geral.bind("<<ComboboxSelected>>", self.atualizar_turmas_geral)

        # Turma
        ttk.Label(frame_filtros, text="Turma:").pack(side="left", padx=5)
        self.turma_var_geral = tk.StringVar()
        self.turma_combo_geral = ttk.Combobox(frame_filtros, textvariable=self.turma_var_geral, width=20)
        self.turma_combo_geral.pack(side="left", padx=5)
        self.turma_combo_geral.bind("<<ComboboxSelected>>", self.carregar_observacoes)

        self.carregar_escolas_geral()

        self.tree = ttk.Treeview(self.frame_geral, columns=("ID", "Aluno", "Turma", "Tipo", "Disciplina", "Descrição", "Data"), show="headings")
        for col in ("ID", "Aluno", "Turma", "Tipo", "Disciplina", "Descrição", "Data"):
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        tk.Button(self.frame_geral, text="Adicionar Observação", command=self.abrir_cadastro).pack(pady=5)
        tk.Button(self.frame_geral, text="Voltar", command=self.voltar).pack(side=tk.RIGHT, padx=10, pady=5)

    def setup_frame_disciplina(self):
        tk.Label(self.frame_disciplina, text="Registro de Fato Observado", font=("Arial", 14)).pack(pady=10)

        # Frame para seleção de escola e turma
        frame_filtros = ttk.Frame(self.frame_disciplina)
        frame_filtros.pack(fill="x", padx=10, pady=5)

        # Escola
        ttk.Label(frame_filtros, text="Escola:").pack(side="left", padx=5)
        self.escola_var_disc = tk.StringVar()
        self.escola_combo_disc = ttk.Combobox(frame_filtros, textvariable=self.escola_var_disc, width=30)
        self.escola_combo_disc.pack(side="left", padx=5)
        self.escola_combo_disc.bind("<<ComboboxSelected>>", self.atualizar_turmas_disc)

        # Turma
        ttk.Label(frame_filtros, text="Turma:").pack(side="left", padx=5)
        self.turma_var_disc = tk.StringVar()
        self.turma_combo_disc = ttk.Combobox(frame_filtros, textvariable=self.turma_var_disc, width=20)
        self.turma_combo_disc.pack(side="left", padx=5)
        self.turma_combo_disc.bind("<<ComboboxSelected>>", self.carregar_fatos_observados)

        self.carregar_escolas_disc()

        # Treeview para fatos observados
        self.tree_disciplina = ttk.Treeview(self.frame_disciplina, 
            columns=("ID", "Aluno", "Turma", "Tipo", "Descrição", "Consequência", "Data"), 
            show="headings")
        
        for col in ("ID", "Aluno", "Turma", "Tipo", "Descrição", "Consequência", "Data"):
            self.tree_disciplina.heading(col, text=col)
        self.tree_disciplina.pack(expand=True, fill="both", padx=10, pady=10)

        # Botões
        tk.Button(self.frame_disciplina, text="Registrar Fato", command=self.abrir_cadastro_disciplina).pack(pady=5)
        tk.Button(self.frame_disciplina, text="Voltar", command=self.voltar).pack(side=tk.RIGHT, padx=10, pady=5)

    def carregar_escolas_geral(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM escolas ORDER BY nome")
        escolas = cursor.fetchall()
        self.escola_combo_geral["values"] = [f"{escola[0]} - {escola[1]}" for escola in escolas]
        conn.close()

    def carregar_escolas_disc(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM escolas ORDER BY nome")
        escolas = cursor.fetchall()
        self.escola_combo_disc["values"] = [f"{escola[0]} - {escola[1]}" for escola in escolas]
        conn.close()

    def atualizar_turmas_geral(self, event=None):
        escola_id = self.escola_var_geral.get().split(" - ")[0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT turma, ano_letivo 
            FROM alunos 
            WHERE escola_id = %s 
            ORDER BY ano_letivo DESC, turma
        """, (escola_id,))
        turmas = cursor.fetchall()
        self.turma_combo_geral["values"] = [f"{turma[0]} - {turma[1]}" for turma in turmas]
        conn.close()
        self.turma_var_geral.set("")
        self.carregar_observacoes()

    def atualizar_turmas_disc(self, event=None):
        escola_id = self.escola_var_disc.get().split(" - ")[0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT turma, ano_letivo 
            FROM alunos 
            WHERE escola_id = %s 
            ORDER BY ano_letivo DESC, turma
        """, (escola_id,))
        turmas = cursor.fetchall()
        self.turma_combo_disc["values"] = [f"{turma[0]} - {turma[1]}" for turma in turmas]
        conn.close()
        self.turma_var_disc.set("")
        self.carregar_fatos_observados()

    def carregar_observacoes(self, event=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not self.turma_var_geral.get():
            return

        turma, ano = self.turma_var_geral.get().split(" - ")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, a.nome, a.turma, o.tipo, o.disciplina, o.descricao, o.data
            FROM observacoes o
            JOIN alunos a ON o.aluno_id = a.id
            WHERE a.turma = %s AND a.ano_letivo = %s
            ORDER BY o.data DESC
        """, (turma, ano))
        for obs in cursor.fetchall():
            # Formatar a data para exibição
            data_formatada = obs[6].strftime("%d/%m/%Y %H:%M") if obs[6] else ""
            self.tree.insert("", tk.END, values=(obs[0], obs[1], obs[2], obs[3], obs[4], obs[5], data_formatada))
        conn.close()

    def carregar_fatos_observados(self, event=None):
        for row in self.tree_disciplina.get_children():
            self.tree_disciplina.delete(row)

        if not self.turma_var_disc.get():
            return

        turma, ano = self.turma_var_disc.get().split(" - ")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fo.id, a.nome, a.turma, fo.tipo, fo.descricao, fo.consequencia, fo.data
            FROM fatos_observados fo
            JOIN alunos a ON fo.aluno_id = a.id
            WHERE a.turma = %s AND a.ano_letivo = %s
            ORDER BY fo.data DESC
        """, (turma, ano))
        for fo in cursor.fetchall():
            # Formatar a data para exibição
            data_formatada = fo[6].strftime("%d/%m/%Y %H:%M") if fo[6] else ""
            self.tree_disciplina.insert("", tk.END, values=(fo[0], fo[1], fo[2], fo[3], fo[4], fo[5], data_formatada))
        conn.close()

    def abrir_cadastro_disciplina(self):
        if not self.turma_var_disc.get():
            messagebox.showerror("Erro", "Selecione uma escola e turma primeiro!")
            return

        self.window = tk.Toplevel(self)
        self.window.title("Registrar Fato Observado")
        self.window.geometry("500x400")

        # Frame para seleção de aluno
        frame_aluno = ttk.Frame(self.window)
        frame_aluno.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_aluno, text="Aluno:").pack(side="left")
        self.aluno_var = tk.StringVar()
        self.aluno_combo = ttk.Combobox(frame_aluno, textvariable=self.aluno_var)
        self.aluno_combo.pack(side="left", fill="x", expand=True)
        self.carregar_alunos()

        # Frame para tipo de fato
        frame_tipo = ttk.Frame(self.window)
        frame_tipo.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_tipo, text="Tipo:").pack(side="left")
        self.tipo_var = tk.StringVar()
        self.tipo_combo = ttk.Combobox(frame_tipo, textvariable=self.tipo_var, 
                                     values=["Positivo", "Negativo"])
        self.tipo_combo.pack(side="left", fill="x", expand=True)
        self.tipo_combo.bind("<<ComboboxSelected>>", self.atualizar_consequencias)

        # Frame para descrição
        frame_desc = ttk.Frame(self.window)
        frame_desc.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_desc, text="Descrição:").pack(side="left")
        self.descricao_text = tk.Text(frame_desc, height=4)
        self.descricao_text.pack(fill="x", expand=True)

        # Frame para consequência
        frame_cons = ttk.Frame(self.window)
        frame_cons.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_cons, text="Consequência:").pack(side="left")
        self.consequencia_var = tk.StringVar()
        self.consequencia_combo = ttk.Combobox(frame_cons, textvariable=self.consequencia_var)
        self.consequencia_combo.pack(side="left", fill="x", expand=True)

        # Botões
        frame_botoes = ttk.Frame(self.window)
        frame_botoes.pack(fill="x", padx=10, pady=10)
        ttk.Button(frame_botoes, text="Salvar", command=self.salvar_fato_observado).pack(side="right", padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=self.window.destroy).pack(side="right", padx=5)

    def abrir_cadastro(self):
        if not self.turma_var_geral.get():
            messagebox.showerror("Erro", "Selecione uma escola e turma primeiro!")
            return

        self.new_window = tk.Toplevel(self)
        self.new_window.title("Adicionar Observação")
        self.new_window.geometry("500x400")

        # Frame para seleção de aluno
        frame_aluno = ttk.Frame(self.new_window)
        frame_aluno.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_aluno, text="Aluno:").pack(side="left")
        self.aluno_var_obs = tk.StringVar()
        self.aluno_combo_obs = ttk.Combobox(frame_aluno, textvariable=self.aluno_var_obs)
        self.aluno_combo_obs.pack(side="left", fill="x", expand=True)
        self.carregar_alunos_obs()

        # Frame para tipo
        frame_tipo = ttk.Frame(self.new_window)
        frame_tipo.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_tipo, text="Tipo:").pack(side="left")
        self.tipo_var_obs = tk.StringVar()
        self.tipo_combo_obs = ttk.Combobox(frame_tipo, textvariable=self.tipo_var_obs,
                                         values=["Positivo", "Negativo"])
        self.tipo_combo_obs.pack(side="left", fill="x", expand=True)

        # Frame para disciplina
        frame_disc = ttk.Frame(self.new_window)
        frame_disc.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_disc, text="Disciplina:").pack(side="left")
        self.disciplina_var_obs = tk.StringVar()
        self.disciplina_combo_obs = ttk.Combobox(frame_disc, textvariable=self.disciplina_var_obs,
                                               values=["Português", "Matemática", "História", "Geografia", 
                                                      "Ciências", "Inglês", "Educação Física", "Artes", 
                                                      "Outra"])
        self.disciplina_combo_obs.pack(side="left", fill="x", expand=True)

        # Frame para descrição
        frame_desc = ttk.Frame(self.new_window)
        frame_desc.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_desc, text="Descrição:").pack(side="left")
        self.descricao_text_obs = tk.Text(frame_desc, height=4)
        self.descricao_text_obs.pack(fill="x", expand=True)

        # Botões
        frame_botoes = ttk.Frame(self.new_window)
        frame_botoes.pack(fill="x", padx=10, pady=10)
        ttk.Button(frame_botoes, text="Salvar", command=self.salvar_observacao).pack(side="right", padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=self.new_window.destroy).pack(side="right", padx=5)

    def carregar_alunos(self):
        turma, ano = self.turma_var_disc.get().split(" - ")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome FROM alunos 
            WHERE turma = %s AND ano_letivo = %s
            ORDER BY nome
        """, (turma, ano))
        alunos = cursor.fetchall()
        self.aluno_combo["values"] = [f"{aluno[0]} - {aluno[1]}" for aluno in alunos]
        conn.close()

    def carregar_alunos_obs(self):
        turma, ano = self.turma_var_geral.get().split(" - ")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome FROM alunos 
            WHERE turma = %s AND ano_letivo = %s
            ORDER BY nome
        """, (turma, ano))
        alunos = cursor.fetchall()
        self.aluno_combo_obs["values"] = [f"{aluno[0]} - {aluno[1]}" for aluno in alunos]
        conn.close()

    def atualizar_consequencias(self, event=None):
        tipo = self.tipo_var.get()
        if tipo == "Positivo":
            self.consequencia_combo["values"] = [
                "Elogio Verbal",
                "Elogio Publicado"
            ]
        else:
            self.consequencia_combo["values"] = [
                "Advertência Verbal",
                "Advertência",
                "Repreensão",
                "Estudo Obrigatório",
                "Exclusão"
            ]

    def salvar_fato_observado(self):
        aluno_id = self.aluno_var.get().split(" - ")[0]
        tipo = self.tipo_var.get()
        descricao = self.descricao_text.get("1.0", tk.END).strip()
        consequencia = self.consequencia_var.get()

        if not all([aluno_id, tipo, descricao, consequencia]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO fatos_observados (aluno_id, tipo, descricao, consequencia, data)
                VALUES (%s, %s, %s, %s, %s)
            """, (aluno_id, tipo, descricao, consequencia, datetime.now()))
            conn.commit()
            messagebox.showinfo("Sucesso", "Fato observado registrado com sucesso!")
            self.window.destroy()
            self.carregar_fatos_observados()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar fato observado: {str(e)}")
        finally:
            conn.close()

    def salvar_observacao(self):
        aluno_id = self.aluno_var_obs.get().split(" - ")[0]
        tipo = self.tipo_var_obs.get()
        disciplina = self.disciplina_var_obs.get()
        descricao = self.descricao_text_obs.get("1.0", tk.END).strip()

        if not all([aluno_id, tipo, disciplina, descricao]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO observacoes (aluno_id, tipo, descricao, disciplina, data)
                VALUES (%s, %s, %s, %s, %s)
            """, (aluno_id, tipo, descricao, disciplina, datetime.now()))
            conn.commit()
            messagebox.showinfo("Sucesso", "Observação registrada com sucesso!")
            self.new_window.destroy()
            self.carregar_observacoes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar observação: {str(e)}")
        finally:
            conn.close()

    def voltar(self):
        self.master.clear()
        self.master.iniciar_app()

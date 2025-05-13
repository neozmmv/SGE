import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_connection

class AlunoFrame(tk.Frame):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.tree = None

        tk.Label(self, text="Alunos da Escola", font=("Arial", 14)).pack(pady=10)

        # Search frame
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        # Adicionar filtro de escola para administradores
        if self.usuario.get("perfil") == "admin":
            tk.Label(search_frame, text="Escola:").pack(side=tk.LEFT, padx=5)
            self.escola_filter = ttk.Combobox(search_frame, state="readonly", width=30)
            self.escola_filter.pack(side=tk.LEFT, padx=5)
            self.carregar_escolas_filtro()
            self.escola_filter.bind("<<ComboboxSelected>>", lambda e: self.carregar_alunos())
        
        tk.Label(search_frame, text="Buscar por:").pack(side=tk.LEFT, padx=5)
        self.search_by = ttk.Combobox(search_frame, values=["ID", "Nome", "Número", "Turma", "Ano Letivo"], state="readonly", width=10)
        self.search_by.current(1)  # Default to Nome
        self.search_by.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="Buscar", command=self.buscar_aluno).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Limpar", command=self.limpar_busca).pack(side=tk.LEFT, padx=5)

        # Tabela de alunos
        self.tree = ttk.Treeview(self, columns=("ID", "Nome", "Número", "Turma", "Ano", "Escola"), show="headings")
        for col in ("ID", "Nome", "Número", "Turma", "Ano", "Escola"):
            self.tree.heading(col, text=col)
            
        # Set column widths to ensure all columns are visible
        self.tree.column("ID", width=50, minwidth=50)
        self.tree.column("Nome", width=200, minwidth=150)
        self.tree.column("Número", width=100, minwidth=80)
        self.tree.column("Turma", width=100, minwidth=80)
        self.tree.column("Ano", width=100, minwidth=80)
        self.tree.column("Escola", width=150, minwidth=100)
            
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Add right-click menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.editar_aluno)
        self.context_menu.add_command(label="Excluir", command=self.excluir_aluno)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda event: self.editar_aluno())

        # Buttons frame
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(button_frame, text="Cadastrar Novo Aluno", command=self.abrir_cadastro).pack(side=tk.LEFT, pady=5)
        tk.Button(button_frame, text="Editar", command=self.editar_aluno).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Excluir", command=self.excluir_aluno).pack(side=tk.LEFT, pady=5)
        tk.Button(button_frame, text="Voltar", command=self.voltar).pack(side=tk.RIGHT, padx=10, pady=5)

        # Carregar alunos inicialmente
        self.carregar_alunos()
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def carregar_escolas_filtro(self):
        """Carrega as escolas para o filtro"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM escolas ORDER BY nome")
        escolas = cursor.fetchall()
        conn.close()
        
        self.escolas_filtro_ids = {escola[1]: escola[0] for escola in escolas}
        self.escola_filter['values'] = ["Todas as Escolas"] + list(self.escolas_filtro_ids.keys())
        self.escola_filter.set("Todas as Escolas")

    def carregar_alunos(self):
        """Carregar todos os alunos da escola"""
        # Limpar a tabela existente
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()

        # Buscar alunos baseado no perfil do usuário
        if self.usuario.get("perfil") == "admin":
            # Verificar se há filtro de escola selecionado
            escola_selecionada = self.escola_filter.get()
            if escola_selecionada and escola_selecionada != "Todas as Escolas":
                escola_id = self.escolas_filtro_ids.get(escola_selecionada)
                query = """
                    SELECT a.id, a.nome, a.numero, a.turma, a.ano_letivo, e.nome as escola_nome 
                    FROM alunos a
                    JOIN escolas e ON a.escola_id = e.id
                    WHERE a.escola_id = %s
                    ORDER BY a.nome
                """
                cursor.execute(query, (escola_id,))
            else:
                # Admin vê todos os alunos de todas as escolas
                query = """
                    SELECT a.id, a.nome, a.numero, a.turma, a.ano_letivo, e.nome as escola_nome 
                    FROM alunos a
                    JOIN escolas e ON a.escola_id = e.id
                    ORDER BY e.nome, a.nome
                """
                cursor.execute(query)
        else:
            # Monitor vê apenas alunos da sua escola
            query = """
                SELECT a.id, a.nome, a.numero, a.turma, a.ano_letivo, e.nome as escola_nome 
                FROM alunos a
                JOIN escolas e ON a.escola_id = e.id
                WHERE a.escola_id = %s
                ORDER BY a.nome
            """
            cursor.execute(query, (self.usuario["escola_id"],))

        # Inserir os resultados na tabela
        for aluno in cursor.fetchall():
            self.tree.insert("", tk.END, values=aluno)

        conn.close()

    def buscar_aluno(self):
        """Search students based on selected criteria"""
        search_text = self.search_entry.get().strip()
        if not search_text:
            self.carregar_alunos()
            return
            
        search_by = self.search_by.get()
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        conn = get_connection()
        cursor = conn.cursor()
        
        # Map combobox selection to database column
        column_map = {
            "ID": "a.id",
            "Nome": "a.nome",
            "Número": "a.numero",
            "Turma": "a.turma",
            "Ano Letivo": "a.ano_letivo"
        }
        
        db_column = column_map[search_by]
        
        if self.usuario.get("perfil") == "admin":
            # Verificar se há filtro de escola selecionado
            escola_selecionada = self.escola_filter.get()
            if escola_selecionada and escola_selecionada != "Todas as Escolas":
                escola_id = self.escolas_filtro_ids.get(escola_selecionada)
                query = f"""
                    SELECT a.id, a.nome, a.numero, a.turma, a.ano_letivo, e.nome as escola_nome
                    FROM alunos a
                    JOIN escolas e ON a.escola_id = e.id
                    WHERE {db_column} LIKE %s AND a.escola_id = %s
                    ORDER BY a.nome
                """
                cursor.execute(query, (f"%{search_text}%", escola_id))
            else:
                query = f"""
                    SELECT a.id, a.nome, a.numero, a.turma, a.ano_letivo, e.nome as escola_nome
                    FROM alunos a
                    JOIN escolas e ON a.escola_id = e.id
                    WHERE {db_column} LIKE %s
                    ORDER BY e.nome, a.nome
                """
                cursor.execute(query, (f"%{search_text}%",))
        else:
            query = f"""
                SELECT a.id, a.nome, a.numero, a.turma, a.ano_letivo, e.nome as escola_nome
                FROM alunos a
                JOIN escolas e ON a.escola_id = e.id
                WHERE {db_column} LIKE %s AND a.escola_id = %s
                ORDER BY a.nome
            """
            cursor.execute(query, (f"%{search_text}%", self.usuario["escola_id"]))
            
        for aluno in cursor.fetchall():
            self.tree.insert("", tk.END, values=aluno)
            
        conn.close()

    def limpar_busca(self):
        """Clear search and reload all students"""
        self.search_entry.delete(0, tk.END)
        if self.usuario.get("perfil") == "admin":
            self.escola_filter.set("Todas as Escolas")
        self.carregar_alunos()

    def abrir_cadastro(self):
        self.new_window = tk.Toplevel(self)
        self.new_window.title("Cadastro de Aluno")
        self.new_window.geometry("300x300")

        labels = ["Nome", "Número", "Turma", "Ano Letivo"]
        self.entries = {}
        for label in labels:
            tk.Label(self.new_window, text=label).pack()
            entry = tk.Entry(self.new_window)
            entry.pack()
            self.entries[label.lower().replace(" ", "_")] = entry

        # Adicionar seleção de escola para administradores
        if self.usuario.get("perfil") == "admin":
            tk.Label(self.new_window, text="Escola:").pack()
            self.escola_combobox = ttk.Combobox(self.new_window, state="readonly")
            self.escola_combobox.pack()
            self.carregar_escolas_cadastro()

        tk.Button(self.new_window, text="Salvar", command=self.salvar_aluno).pack(pady=10)

    def carregar_escolas_cadastro(self):
        """Carrega as escolas para o combobox de cadastro"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM escolas ORDER BY nome")
        escolas = cursor.fetchall()
        conn.close()
        
        self.escolas_ids = {escola[1]: escola[0] for escola in escolas}
        self.escola_combobox['values'] = list(self.escolas_ids.keys())
        if escolas:
            self.escola_combobox.set(escolas[0][1])

    def salvar_aluno(self):
        dados = {k: v.get() for k, v in self.entries.items()}
        
        # Validação básica
        if not all(dados.values()):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        # Obter escola_id baseado no perfil do usuário
        if self.usuario.get("perfil") == "admin":
            escola_nome = self.escola_combobox.get()
            if not escola_nome:
                messagebox.showerror("Erro", "Selecione uma escola!")
                return
            escola_id = self.escolas_ids.get(escola_nome)
        else:
            escola_id = self.usuario["escola_id"]
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO alunos (nome, numero, turma, ano_letivo, escola_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                dados["nome"], dados["número"], dados["turma"], dados["ano_letivo"], escola_id
            ))
            conn.commit()
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            self.new_window.destroy()
            self.carregar_alunos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar aluno: {str(e)}")
        finally:
            conn.close()

    def editar_aluno(self):
        """Edit selected student"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno para editar.")
            return
            
        # Get student data
        values = self.tree.item(selected_item[0], "values")
        aluno_id = values[0]
        
        # Open edit window
        self.edit_window = tk.Toplevel(self)
        self.edit_window.title("Editar Aluno")
        self.edit_window.geometry("300x250")
        
        # Store student ID
        self.aluno_id = aluno_id
        
        labels = ["Nome", "Número", "Turma", "Ano Letivo"]
        self.edit_entries = {}
        
        for i, label in enumerate(labels):
            tk.Label(self.edit_window, text=label).pack()
            entry = tk.Entry(self.edit_window)
            entry.insert(0, values[i+1])  # +1 because first value is ID
            entry.pack()
            self.edit_entries[label.lower().replace(" ", "_")] = entry
        
        tk.Button(self.edit_window, text="Salvar", command=self.salvar_edicao).pack(pady=10)
    
    def salvar_edicao(self):
        """Save student edits"""
        dados = {k: v.get() for k, v in self.edit_entries.items()}
        
        # Validação básica
        if not all(dados.values()):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE alunos 
                SET nome=%s, numero=%s, turma=%s, ano_letivo=%s 
                WHERE id=%s
            """, (
                dados["nome"], dados["número"], dados["turma"], dados["ano_letivo"], self.aluno_id
            ))
            conn.commit()
            messagebox.showinfo("Sucesso", "Aluno atualizado com sucesso!")
            self.edit_window.destroy()
            self.carregar_alunos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar aluno: {str(e)}")
        finally:
            conn.close()
    
    def excluir_aluno(self):
        """Delete selected student"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um aluno para excluir.")
            return
            
        aluno_id = self.tree.item(selected_item[0], "values")[0]
        aluno_nome = self.tree.item(selected_item[0], "values")[1]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirmar exclusão", 
                                      f"Tem certeza que deseja excluir o aluno '{aluno_nome}'?")
        if not confirm:
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")
            self.carregar_alunos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir aluno: {str(e)}")
        finally:
            conn.close()

    def voltar(self):
        from main import MainFrame
        self.destroy()
        MainFrame(self.master, self.usuario).pack()
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from db_config import get_connection
from werkzeug.security import generate_password_hash

class MonitorFrame(tk.Frame):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.tree = None

        tk.Label(self, text="Monitores", font=("Arial", 14)).pack(pady=10)
        
        # Search frame
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(search_frame, text="Buscar por:").pack(side=tk.LEFT, padx=5)
        self.search_by = ttk.Combobox(search_frame, values=["ID", "Nome", "CPF", "Perfil", "Escola"], state="readonly", width=10)
        self.search_by.current(1)  # Default to Nome
        self.search_by.pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="Buscar", command=self.buscar_monitores).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Limpar", command=self.limpar_busca).pack(side=tk.LEFT, padx=5)

        # Add "Escola" column to the Treeview
        self.tree = ttk.Treeview(self, columns=("ID", "Nome", "CPF", "Perfil", "Escola"), show="headings")
        for col in ("ID", "Nome", "CPF", "Perfil", "Escola"):
            self.tree.heading(col, text=col)
            
        # Set column widths to ensure all columns are visible
        self.tree.column("ID", width=50, minwidth=50)
        self.tree.column("Nome", width=150, minwidth=100)
        self.tree.column("CPF", width=120, minwidth=100)
        self.tree.column("Perfil", width=100, minwidth=80)
        self.tree.column("Escola", width=150, minwidth=100)
            
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Add right-click menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.editar_monitor)
        self.context_menu.add_command(label="Excluir", command=self.excluir_monitor)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda event: self.editar_monitor())

        # Buttons frame
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(button_frame, text="Adicionar Monitor", command=self.abrir_cadastro).pack(side=tk.LEFT, pady=5)
        tk.Button(button_frame, text="Editar", command=self.editar_monitor).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Excluir", command=self.excluir_monitor).pack(side=tk.LEFT, pady=5)
        tk.Button(button_frame, text="Voltar", command=self.voltar).pack(side=tk.RIGHT, padx=10, pady=5)

        self.carregar_monitores()
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def buscar_monitores(self):
        """Search monitors based on selected criteria"""
        search_text = self.search_entry.get().strip()
        if not search_text:
            self.carregar_monitores()
            return
            
        search_by = self.search_by.get()
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        conn = get_connection()
        cursor = conn.cursor()
        
        # Map combobox selection to database column
        column_map = {
            "ID": "m.id",
            "Nome": "m.nome",
            "CPF": "m.cpf",
            "Perfil": "m.perfil",
            "Escola": "e.nome"
        }
        
        db_column = column_map[search_by]
        
        if self.usuario.get("perfil") == "admin":
            query = f"""
                SELECT m.id, m.nome, m.cpf, m.perfil, e.nome as escola_nome
                FROM monitores m
                JOIN escolas e ON m.escola_id = e.id
                WHERE {db_column} LIKE %s
            """
            cursor.execute(query, (f"%{search_text}%",))
        else:
            query = f"""
                SELECT m.id, m.nome, m.cpf, m.perfil, e.nome as escola_nome
                FROM monitores m
                JOIN escolas e ON m.escola_id = e.id
                WHERE {db_column} LIKE %s AND m.escola_id = %s
            """
            cursor.execute(query, (f"%{search_text}%", self.usuario["escola_id"]))
            
        for monitor in cursor.fetchall():
            self.tree.insert("", tk.END, values=monitor)
            
        conn.close()
    
    def limpar_busca(self):
        """Clear search and reload all monitors"""
        self.search_entry.delete(0, tk.END)
        self.carregar_monitores()

    def carregar_monitores(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor()
        
        # Different query based on user profile
        if self.usuario.get("perfil") == "admin":
            # Admin sees all monitors from all schools
            cursor.execute("""
                SELECT m.id, m.nome, m.cpf, m.perfil, e.nome as escola_nome
                FROM monitores m
                JOIN escolas e ON m.escola_id = e.id
            """)
        else:
            # Regular users only see monitors from their school
            cursor.execute("""
                SELECT m.id, m.nome, m.cpf, m.perfil, e.nome as escola_nome
                FROM monitores m
                JOIN escolas e ON m.escola_id = e.id
                WHERE m.escola_id = %s
            """, (self.usuario["escola_id"],))
            
        for monitor in cursor.fetchall():
            self.tree.insert("", tk.END, values=monitor)
        conn.close()
    
    def editar_monitor(self):
        """Edit selected monitor"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um monitor para editar.")
            return
            
        # Get monitor data
        monitor_id = self.tree.item(selected_item[0], "values")[0]
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.nome, m.cpf, m.perfil, m.escola_id, e.nome as escola_nome
            FROM monitores m
            JOIN escolas e ON m.escola_id = e.id
            WHERE m.id = %s
        """, (monitor_id,))
        
        monitor = cursor.fetchone()
        conn.close()
        
        if not monitor:
            messagebox.showerror("Erro", "Monitor não encontrado.")
            return
            
        self.abrir_edicao(monitor)
    
    def abrir_edicao(self, monitor):
        """Open edit window for monitor"""
        self.edit_window = tk.Toplevel(self)
        self.edit_window.title("Editar Monitor")
        self.edit_window.geometry("400x350")
        
        # Store monitor ID
        self.monitor_id = monitor[0]
        
        tk.Label(self.edit_window, text="Nome:").pack()
        self.nome_edit = tk.Entry(self.edit_window)
        self.nome_edit.insert(0, monitor[1])
        self.nome_edit.pack()
        
        tk.Label(self.edit_window, text="CPF:").pack()
        self.cpf_edit = tk.Entry(self.edit_window)
        self.cpf_edit.insert(0, monitor[2])
        self.cpf_edit.pack()
        
        tk.Label(self.edit_window, text="Perfil (monitor/admin):").pack()
        self.perfil_edit = tk.Entry(self.edit_window)
        self.perfil_edit.insert(0, monitor[3])
        self.perfil_edit.pack()
        
        tk.Label(self.edit_window, text="Escola:").pack()
        self.escola_edit = ttk.Combobox(self.edit_window, state="readonly")
        self.escola_edit.pack()
        
        # Load schools
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM escolas")
        escolas = cursor.fetchall()
        conn.close()
        
        self.escolas_ids = {escola[1]: escola[0] for escola in escolas}
        self.escola_edit['values'] = list(self.escolas_ids.keys())
        
        # Set current school
        for nome, id in self.escolas_ids.items():
            if id == monitor[4]:
                self.escola_edit.set(nome)
                break
        
        # Password change option
        self.change_password = tk.BooleanVar()
        self.change_password.set(False)
        tk.Checkbutton(self.edit_window, text="Alterar senha", variable=self.change_password, 
                       command=self.toggle_password_entry).pack(pady=5)
        
        # Password entry (initially hidden)
        self.password_frame = tk.Frame(self.edit_window)
        tk.Label(self.password_frame, text="Nova senha:").pack()
        self.senha_edit = tk.Entry(self.password_frame, show="*")
        self.senha_edit.pack()
        
        tk.Button(self.edit_window, text="Salvar", command=self.salvar_edicao).pack(pady=10)
    
    def toggle_password_entry(self):
        """Show/hide password entry based on checkbox"""
        if self.change_password.get():
            self.password_frame.pack(pady=5)
        else:
            self.password_frame.pack_forget()
    
    def salvar_edicao(self):
        """Save monitor edits"""
        nome = self.nome_edit.get()
        cpf = self.cpf_edit.get()
        perfil = self.perfil_edit.get()
        escola_nome = self.escola_edit.get()
        
        if not (nome and cpf and perfil and escola_nome):
            messagebox.showerror("Erro", "Nome, CPF, perfil e escola são obrigatórios!")
            return
        
        escola_id = self.escolas_ids.get(escola_nome)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            if self.change_password.get():
                senha = self.senha_edit.get()
                if not senha:
                    messagebox.showerror("Erro", "A nova senha é obrigatória!")
                    return
                
                # Gerar hash da nova senha
                senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
                    
                cursor.execute("""
                    UPDATE monitores
                    SET nome = %s, cpf = %s, perfil = %s, escola_id = %s, senha = %s
                    WHERE id = %s
                """, (nome, cpf, perfil, escola_id, senha_hash, self.monitor_id))
            else:
                cursor.execute("""
                    UPDATE monitores
                    SET nome = %s, cpf = %s, perfil = %s, escola_id = %s
                    WHERE id = %s
                """, (nome, cpf, perfil, escola_id, self.monitor_id))
                
            conn.commit()
            messagebox.showinfo("Sucesso", "Monitor atualizado com sucesso!")
            self.edit_window.destroy()
            self.carregar_monitores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar monitor: {str(e)}")
        finally:
            conn.close()
    
    def excluir_monitor(self):
        """Delete selected monitor"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Aviso", "Selecione um monitor para excluir.")
            return
            
        monitor_id = self.tree.item(selected_item[0], "values")[0]
        monitor_nome = self.tree.item(selected_item[0], "values")[1]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirmar exclusão", 
                                      f"Tem certeza que deseja excluir o monitor '{monitor_nome}'?")
        if not confirm:
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM monitores WHERE id = %s", (monitor_id,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Monitor excluído com sucesso!")
            self.carregar_monitores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir monitor: {str(e)}")
        finally:
            conn.close()

    def abrir_cadastro(self):
        self.new_window = tk.Toplevel(self)
        self.new_window.title("Cadastro de Monitor")
        self.new_window.geometry("400x350")

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
        
        tk.Label(self.new_window, text="Escola:").pack()
        self.escola_combobox = ttk.Combobox(self.new_window, state="readonly")
        self.escola_combobox.pack()
        
        self.carregar_escolas()

        tk.Button(self.new_window, text="Salvar", command=self.salvar_monitor).pack(pady=10)
    
    def carregar_escolas(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM escolas")
        escolas = cursor.fetchall()
        conn.close()
        
        self.escolas_ids = {escola[1]: escola[0] for escola in escolas}
        
        self.escola_combobox['values'] = list(self.escolas_ids.keys())
        
        if self.usuario["escola_id"]:
            for nome, id in self.escolas_ids.items():
                if id == self.usuario["escola_id"]:
                    self.escola_combobox.set(nome)
                    break

    def salvar_monitor(self):
        nome = self.nome_entry.get()
        cpf = self.cpf_entry.get()
        senha = self.senha_entry.get()
        perfil = self.perfil_entry.get()
        escola_nome = self.escola_combobox.get()
        
        if not (nome and cpf and senha and perfil and escola_nome):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return
        
        escola_id = self.escolas_ids.get(escola_nome)
        
        # Gerar hash da senha
        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO monitores (nome, cpf, senha, perfil, escola_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, cpf, senha_hash, perfil, escola_id))
            conn.commit()
            messagebox.showinfo("Sucesso", "Monitor cadastrado com sucesso!")
            self.new_window.destroy()
            self.carregar_monitores()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar monitor: {str(e)}")
        finally:
            conn.close()

    def voltar(self):
        from main import MainFrame
        self.destroy()
        MainFrame(self.master, self.usuario).pack()
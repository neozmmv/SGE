import tkinter as tk
from tkinter import ttk, messagebox
from db_config import get_connection
from werkzeug.security import generate_password_hash

class CadastroUsuarioFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Cadastro de Usuário")
        self.master.geometry("500x600")
        self.master.resizable(False, False)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Criação dos widgets para o cadastro de usuário"""
        # Title
        title_label = tk.Label(self, 
                             text="Cadastro de Usuário",
                             font=("Arial", 20, "bold"))
        title_label.pack(pady=(20, 30))

        # Main container
        main_container = tk.Frame(self)
        main_container.pack(padx=40, pady=20)

        # Nome
        tk.Label(main_container, text="Nome Completo:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        self.nome_entry = tk.Entry(main_container, width=40)
        self.nome_entry.pack(fill="x", pady=(0, 15))

        # CPF
        tk.Label(main_container, text="CPF:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        self.cpf_entry = tk.Entry(main_container, width=40)
        self.cpf_entry.pack(fill="x", pady=(0, 15))

        # Senha
        tk.Label(main_container, text="Senha:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        self.senha_entry = tk.Entry(main_container, show="*", width=40)
        self.senha_entry.pack(fill="x", pady=(0, 15))

        # Confirmar Senha
        tk.Label(main_container, text="Confirmar Senha:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        self.confirmar_senha_entry = tk.Entry(main_container, show="*", width=40)
        self.confirmar_senha_entry.pack(fill="x", pady=(0, 15))

        # Perfil
        tk.Label(main_container, text="Perfil:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        self.perfil_var = tk.StringVar(value="monitor")
        tk.Radiobutton(main_container, text="Monitor", variable=self.perfil_var, 
                      value="monitor", font=("Arial", 10),
                      command=self.toggle_escola_field).pack(anchor="w")
        tk.Radiobutton(main_container, text="Administrador", variable=self.perfil_var, 
                      value="admin", font=("Arial", 10),
                      command=self.toggle_escola_field).pack(anchor="w", pady=(0, 15))

        # Escola Frame
        self.escola_frame = tk.Frame(main_container)
        self.escola_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(self.escola_frame, text="Escola:", font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        self.escola_combobox = ttk.Combobox(self.escola_frame, width=38, state="readonly")
        self.escola_combobox.pack(fill="x")
        self.carregar_escolas()

        # Botões
        button_frame = tk.Frame(main_container)
        button_frame.pack(fill="x", pady=(20, 0))
        
        tk.Button(button_frame, 
                 text="Cadastrar",
                 command=self.cadastrar_usuario,
                 width=20).pack(side="left", padx=(0, 10))
        
        tk.Button(button_frame,
                 text="Cancelar",
                 command=self.master.destroy,
                 width=20).pack(side="left")

    def toggle_escola_field(self):
        """Mostra ou esconde o campo de escola baseado no perfil selecionado"""
        if self.perfil_var.get() == "admin":
            self.escola_frame.pack_forget()
        else:
            self.escola_frame.pack(fill="x", pady=(0, 15))

    def carregar_escolas(self):
        """Carrega as escolas do banco de dados"""
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, nome FROM escolas ORDER BY nome")
            escolas = cursor.fetchall()
            
            self.escolas_dict = {escola[1]: escola[0] for escola in escolas}
            self.escola_combobox['values'] = list(self.escolas_dict.keys())
            
            if escolas:
                self.escola_combobox.set(escolas[0][1])
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar escolas: {str(e)}")
        finally:
            conn.close()

    def cadastrar_usuario(self):
        """Cadastra o novo usuário no sistema"""
        nome = self.nome_entry.get().strip()
        cpf = self.cpf_entry.get().strip()
        senha = self.senha_entry.get()
        confirmar_senha = self.confirmar_senha_entry.get()
        perfil = self.perfil_var.get()
        escola_nome = self.escola_combobox.get() if perfil == "monitor" else None

        # Validações
        if not all([nome, cpf, senha, confirmar_senha]):
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        if senha != confirmar_senha:
            messagebox.showerror("Erro", "As senhas não coincidem!")
            return

        if not cpf.isdigit() or len(cpf) != 11:
            messagebox.showerror("Erro", "CPF inválido! Deve conter 11 dígitos numéricos.")
            return

        if perfil == "monitor" and not escola_nome:
            messagebox.showerror("Erro", "A escola é obrigatória para monitores!")
            return

        escola_id = self.escolas_dict.get(escola_nome) if perfil == "monitor" else None

        # Gerar hash da senha
        senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Verificar se CPF já existe
            cursor.execute("SELECT id FROM monitores WHERE cpf = %s", (cpf,))
            if cursor.fetchone():
                messagebox.showerror("Erro", "CPF já cadastrado no sistema!")
                return

            # Inserir novo usuário com senha hasheada
            cursor.execute("""
                INSERT INTO monitores (nome, cpf, senha, perfil, escola_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, cpf, senha_hash, perfil, escola_id))
            
            conn.commit()
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")
            #self.master.destroy() #fechar o app
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {str(e)}")
        finally:
            conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = CadastroUsuarioFrame(root)
    app.pack(expand=True, fill="both")
    root.mainloop() 
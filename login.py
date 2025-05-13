import tkinter as tk
from tkinter import messagebox
from db_config import get_connection
from werkzeug.security import check_password_hash

class LoginFrame(tk.Frame):
    def __init__(self, master, callback):
        super().__init__(master)
        self.master = master
        self.callback = callback
        self.pack(expand=True)

        self.create_widgets()

    def create_widgets(self):
        """Criação dos widgets para a tela de login"""
        # Title
        title_label = tk.Label(self, 
                             text="Sistema de Gerenciamento Escolar",
                             font=("Arial", 20, "bold"))
        title_label.pack(pady=(0, 30))

        # Login container
        login_container = tk.Frame(self)
        login_container.pack(pady=20)

        tk.Label(login_container, text="Usuário:", font=("Arial", 10)).pack(pady=5)
        self.usuario_entry = tk.Entry(login_container, width=30)
        self.usuario_entry.pack(pady=5)

        tk.Label(login_container, text="Senha:", font=("Arial", 10)).pack(pady=5)
        self.senha_entry = tk.Entry(login_container, show="*", width=30)
        self.senha_entry.pack(pady=5)

        tk.Button(login_container, 
                 text="Login",
                 command=self.realizar_login,
                 width=20).pack(pady=15)

    def realizar_login(self):
        """Função para realizar a autenticação"""
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()

        if self.autenticar(usuario, senha):
            self.callback(usuario)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    def autenticar(self, usuario, senha):
        """Função para verificar o login"""
        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Buscar usuário pelo nome
            cursor.execute("SELECT senha FROM monitores WHERE nome = %s", (usuario,))
            result = cursor.fetchone()
            
            if result and check_password_hash(result[0], senha):
                return True
            return False
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao autenticar: {str(e)}")
            return False
        finally:
            conn.close()

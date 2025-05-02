import tkinter as tk
from tkinter import messagebox
from db import get_connection

class LoginFrame(tk.Frame):
    def __init__(self, master, callback):
        super().__init__(master)
        self.master = master
        self.callback = callback
        self.pack()

        self.create_widgets()

    def create_widgets(self):
        """Criação dos widgets para a tela de login"""
        tk.Label(self, text="Usuário:").pack(pady=5)
        self.usuario_entry = tk.Entry(self)
        self.usuario_entry.pack(pady=5)

        tk.Label(self, text="Senha:").pack(pady=5)
        self.senha_entry = tk.Entry(self, show="*")
        self.senha_entry.pack(pady=5)

        tk.Button(self, text="Login", command=self.realizar_login).pack(pady=10)

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

        query = "SELECT * FROM monitores WHERE nome = %s AND senha = %s"
        cursor.execute(query, (usuario, senha))

        result = cursor.fetchone()
        conn.close()

        return result is not None

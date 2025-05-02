import tkinter as tk
from tkinter import messagebox
from login import LoginFrame
from alunos import AlunoFrame
from monitores import MonitorFrame
from observacoes import ObservacaoFrame
from db import get_connection

class MainFrame(tk.Frame):
    def __init__(self, master, usuario=None):
        super().__init__(master)
        self.master = master
        self.usuario = usuario
        self.pack()

        if not usuario:
            self.iniciar_login()
        else:
            self.iniciar_app()

    def iniciar_login(self):
        """Função para exibir a tela de login"""
        self.login_frame = LoginFrame(self.master, self.autenticar_usuario)
        self.login_frame.pack()

    def autenticar_usuario(self, usuario):
        """Função que é chamada após o login"""
        if usuario:
            # Aqui, deve retornar um dicionário com as informações do usuário
            self.usuario = {
                "nome": usuario,
                "escola_id": 1  # Aqui você deve buscar o id correto da escola do usuário
            }
            self.login_frame.destroy()
            self.iniciar_app()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")


    def iniciar_app(self):
        """Função que inicia a tela principal do aplicativo"""
        self.clear()

        # Título
        tk.Label(self, text="Sistema de Gestão de Alunos", font=("Arial", 16)).pack(pady=10)

        # Botões de navegação
        tk.Button(self, text="Gerenciar Alunos", command=self.abrir_alunos).pack(pady=5)
        tk.Button(self, text="Gerenciar Monitores", command=self.abrir_monitores).pack(pady=5)
        tk.Button(self, text="Observações", command=self.abrir_observacoes).pack(pady=5)

        # Botão de Logout
        tk.Button(self, text="Sair", command=self.sair).pack(side=tk.BOTTOM, padx=10, pady=10)

    def abrir_alunos(self):
        """Função para abrir o módulo de alunos"""
        self.clear()
        AlunoFrame(self, self.usuario).pack()

    def abrir_monitores(self):
        """Função para abrir o módulo de monitores"""
        self.clear()
        MonitorFrame(self, self.usuario).pack()

    def abrir_observacoes(self):
        """Função para abrir o módulo de observações"""
        self.clear()
        ObservacaoFrame(self, self.usuario).pack()

    def sair(self):
        """Função para sair da aplicação"""
        response = messagebox.askyesno("Sair", "Você tem certeza que deseja sair?")
        if response:
            self.master.quit()

    def clear(self):
        """Função para limpar a tela atual"""
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sistema de Gestão de Alunos")
    root.geometry("800x600")
    root.resizable(False, False)
    app = MainFrame(root)
    app.pack()
    root.mainloop()

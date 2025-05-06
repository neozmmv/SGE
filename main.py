import tkinter as tk
from tkinter import ttk, messagebox
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
            # Buscar informações completas do usuário
            self.usuario = self.obter_dados_usuario(usuario)
            self.login_frame.destroy()
            self.iniciar_app()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    def obter_dados_usuario(self, nome_usuario):
        """Obtém os dados completos do usuário logado"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, nome, cpf, perfil, escola_id FROM monitores WHERE nome = %s"
        cursor.execute(query, (nome_usuario,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "nome": result[1],
                "cpf": result[2],
                "perfil": result[3],
                "escola_id": result[4]
            }
        return None

    def iniciar_app(self):
        """Função que inicia a tela principal do aplicativo"""
        self.clear()

        # Título
        tk.Label(self, text="Sistema de Gestão de Alunos", font=("Arial", 16)).pack(pady=10)
        tk.Label(self, text=f"Bem-vindo, {self.usuario['nome']}!", font=("Arial", 12)).pack(pady=5)

        # Botões de navegação
        tk.Button(self, text="Gerenciar Alunos", command=self.abrir_alunos).pack(pady=5)
        
        # Apenas administradores podem gerenciar monitores
        if self.usuario.get("perfil") == "admin":
            tk.Button(self, text="Gerenciar Monitores", command=self.abrir_monitores).pack(pady=5)
            tk.Button(self, text="Cadastrar Escola", command=self.abrir_cadastro_escola).pack(pady=5)
        
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
        
    def abrir_cadastro_escola(self):
        """Abre a janela para cadastro de escola"""
        self.escola_window = tk.Toplevel(self)
        self.escola_window.title("Cadastro de Escola")
        self.escola_window.geometry("400x150")
        
        tk.Label(self.escola_window, text="Nome da Escola:").pack(pady=5)
        self.nome_escola_entry = tk.Entry(self.escola_window, width=40)
        self.nome_escola_entry.pack(pady=5)
        
        tk.Button(self.escola_window, text="Salvar", command=self.salvar_escola).pack(pady=10)
    
    def salvar_escola(self):
        """Salva os dados da nova escola no banco de dados"""
        nome = self.nome_escola_entry.get()
        
        if not nome:
            messagebox.showerror("Erro", "O nome da escola é obrigatório!")
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO escolas (nome)
                VALUES (%s)
            """, (nome,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Escola cadastrada com sucesso!")
            self.escola_window.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar escola: {str(e)}")
        finally:
            conn.close()

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
import requests
from tkinter import *
from tkinter import ttk, messagebox
import webbrowser
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageTk
from io import BytesIO

urlDoSistema = "https://produtocolonial.fly.dev/"
url_imagem = "https://raw.githubusercontent.com/joaovitorpichetti/produtoColonialRelatoriosTK/refs/heads/master/img/serra_e-commerce.png"

# Função para baixar a imagem da URL
def baixar_imagem(url):
    response = requests.get(url)
    response.raise_for_status() # Verifica se houve algum erro no download
    return Image.open(BytesIO(response.content))

# --- Função para autenticação com TOKEN ---
class TelaLogin:
    def __init__(self):
        self.janela = Tk()
        self.janela.title("Tela de Login")
        self.janela.geometry("400x400")
        self.janela.configure(bg="white")

        # Baixa a imagem e cria o objeto PhotoImage
        imagem_pil = baixar_imagem(url_imagem)
        self.imagem = ImageTk.PhotoImage(imagem_pil)

        #self.imagem = PhotoImage(file="img/serra_e-commerce.png")
        w = Label(self.janela, image=self.imagem, bg="white")
        w.image = self.imagem
        w.pack(pady=5)

        self.label_token = Label(self.janela, text="Insira seu TOKEN:", font=("Arial", 15, "bold", "italic"),  bg="white")
        self.label_token.pack(pady=20)

        self.entry_token = Entry(self.janela, show="*", width=45, bg="#f0f0f0", bd=2, relief="solid", highlightthickness=2, highlightcolor="blue")
        self.entry_token.pack(pady=5)

        self.botao_entrar = Button(self.janela, text="Entrar", command=self.entrar, width=20)
        self.botao_entrar.pack(pady=20)

        self.janela.mainloop()

    def validar_token(self, token):
        """Função para validar o TOKEN com a API."""
        headers = {"Authorization": f"Bearer {token}"}

        try:
            # Envia uma requisição GET para um endpoint da API (substitua "/api/validar" com o endpoint real)
            response = requests.get(urlDoSistema + "/api/validar", headers=headers)
            if response.status_code == 200:
                return True  # TOKEN válido
            else:
                messagebox.showerror("Erro de Autenticação", "TOKEN inválido ou expirado.")
                return False
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Erro de conexão com a API: {e}")
            return False

    def entrar(self):
        """Verifica o TOKEN e avança para a tela principal se for válido."""
        token = self.entry_token.get()
        if token:
            # Chama a função de validação do TOKEN
            if self.validar_token(token):
                global TOKEN, headers
                TOKEN = token
                headers = {"Authorization": f"Bearer {TOKEN}"}
                self.janela.destroy()
                Aplicacao()  # Chama a aplicação principal
            else:
                # Não faz nada se o TOKEN for inválido
                pass
        else:
            messagebox.showerror("Erro", "Por favor, insira um TOKEN válido.")

class Relatorios:
    def printProdutor(self):
        webbrowser.open("produtor.pdf")

    def geraRelarProdutor(self):
        self.c = canvas.Canvas("produtor.pdf", pagesize=letter)
        largura, altura = letter
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawString(200, altura - 50, "Relatório do Produtor")

        dados = self.listaCli.selection()
        if not dados:
            messagebox.showwarning("Seleção", "Por favor, selecione um produtor na lista para gerar o relatório.")
            return

        for item in dados:
            valores = self.listaCli.item(item, 'values')
            self.c.setFont("Helvetica", 14)
            self.c.drawString(50, altura - 100, f"Código: {valores[0]}")
            self.c.drawString(50, altura - 120, f"Nome: {valores[1]}")
            self.c.drawString(50, altura - 140, f"Cidade: {valores[2]}")

        self.c.save()
        self.printProdutor()

class Funcs:
    def buscar_dados_api(self):
        try:
            response = requests.get(urlDoSistema + "/api/produtores", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                messagebox.showerror("Erro", f"Erro ao buscar dados: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro de conexão: {e}")
            return []

    def carregar_dados(self):
        dados = self.buscar_dados_api()
        if dados:
            self.listaCli.delete(*self.listaCli.get_children())
            for item in dados:
                nomeFantasia = item.get("nomeFantasia")
                nome = item.get("nome")
                celular = item.get("celular")
                endereco = item.get("endereco")
                self.listaCli.insert("", "end", values=(nomeFantasia, nome, celular, endereco))
        else:
            messagebox.showinfo("Informação", "Nenhum dado encontrado.")

class Faturas(Funcs):
    def __init__(self):
        self.janela = Tk()
        self.janela.title("Faturas")
        self.janela.geometry("800x600")
        self.janela.resizable(False, False)
        self.frame_tela()
        self.lista_frame()
        self.carregar_faturas()
        self.janela.mainloop()

    def frame_tela(self):
        self.frame = Frame(self.janela, bg="#d3d3d3")
        self.frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.95)

        self.voltar = Button(self.frame, text="Voltar", command=self.voltar_para_tela_inicial, bg="#736660", fg="white")
        self.voltar.place(relx=0.01, rely=0.02, relwidth=0.1, relheight=0.05)

    def lista_frame(self):
        self.listaFaturas = ttk.Treeview(self.frame, height=3, columns=("col1", "col2", "col3", "col4"))
        self.listaFaturas.place(relx=0.01, rely=0.1, relwidth=0.96, relheight=0.8)
        self.scroollista = Scrollbar(self.frame, orient='vertical')
        self.listaFaturas.configure(yscrollcommand=self.scroollista.set)
        self.scroollista.place(relx=0.96, rely=0.1, relwidth=0.03, relheight=0.8)
        self.listaFaturas.heading("#0", text="")
        self.listaFaturas.heading("#1", text="Nome do Produtor")
        self.listaFaturas.heading("#2", text="Plano")
        self.listaFaturas.heading("#3", text="Valor")
        self.listaFaturas.heading("#4", text="Data de pagamento")
        self.listaFaturas.column("#0", width=1)
        self.listaFaturas.column("#1", width=150)
        self.listaFaturas.column("#3", width=100)
        self.listaFaturas.column("#4", width=100)

    def buscar_dados_faturas(self):
        try:
            response = requests.get(urlDoSistema + "/api/faturas", headers=headers)
            if response.status_code == 200:
                dados = response.json()
                print(dados)
                return dados
            else:
                messagebox.showerror("Erro", f"Erro ao buscar dados: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro de conexão: {e}")
            return []

    def carregar_faturas(self):
        dados = self.buscar_dados_faturas()
        if dados:
            self.listaFaturas.delete(*self.listaFaturas.get_children())
            for item in dados:
                dados_plano = item.get("plano", {})
                nome = item.get("nomeFantasia")
                nome_plano = dados_plano.get("nome_plano")
                valor = dados_plano.get("valor")
                data_de_pagamento = dados_plano.get("data_de_pagamento")
                self.listaFaturas.insert("", "end", values=(nome, nome_plano, valor, data_de_pagamento))
        else:
            messagebox.showinfo("Informação", "Nenhuma fatura encontrada.")

    def voltar_para_tela_inicial(self):
        self.janela.destroy()
        Aplicacao()

class CadastroProdutores(Funcs, Relatorios):
    def __init__(self):
        self.janela = Tk()
        self.tela()
        self.frame_tela()
        self.lista_frame()
        self.menus()
        self.carregar_dados()
        self.janela.mainloop()

    def tela(self):
        self.janela.title("Cadastro de Produtores")
        self.janela.configure(bg="#736660")
        self.janela.geometry("800x600")
        self.janela.resizable(True, True)
        self.janela.maxsize(width=800, height=600)
        self.janela.minsize(width=800, height=600)

    def frame_tela(self):
        self.frame = Frame(self.janela, bg="#d3d3d3")
        self.frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.95)

        self.voltar = Button(self.frame, text="Voltar", command=self.voltar_para_tela_inicial)
        self.voltar.place(relx=0.01, rely=0.02, relwidth=0.1, relheight=0.05)

    def lista_frame(self):
        self.listaCli = ttk.Treeview(self.frame, height=3, columns=("col1", "col2", "col3", "col4"))
        self.listaCli.place(relx=0.01, rely=0.1, relwidth=0.96, relheight=0.8)
        self.scroollista = Scrollbar(self.frame, orient='vertical')
        self.listaCli.configure(yscrollcommand=self.scroollista.set)
        self.scroollista.place(relx=0.96, rely=0.1, relwidth=0.03, relheight=0.8)
        self.listaCli.heading("#0", text="")
        self.listaCli.heading("#1", text="Nome Fantasia")
        self.listaCli.heading("#2", text="Nome")
        self.listaCli.heading("#3", text="Telefone")
        self.listaCli.heading("#4", text="Cidade")
        self.listaCli.column("#0", width=1)
        self.listaCli.column("#1", width=100)
        self.listaCli.column("#2", width=200)
        self.listaCli.column("#3", width=120)
        self.listaCli.column("#4", width=130)

    def menus(self):
        menubar = Menu(self.janela)
        self.janela.config(menu=menubar)

        filemenu = Menu(menubar)
        menubar.add_cascade(label="Relatório", menu=filemenu)
        filemenu.add_command(label="Gerar Relatório", command=self.geraRelarProdutor)

    def voltar_para_tela_inicial(self):
        self.janela.destroy()
        Aplicacao()


class RelatoriosProdutos:
    def mostrar_relatorio_produtos(self):
        # Criando uma nova janela pop-up para o relatório
        janela_relatorio = Toplevel(self.janela)
        janela_relatorio.title("Relatório de Produtos")
        janela_relatorio.geometry("600x400")

        # Criando o Treeview para exibir os produtos
        lista_produtos = ttk.Treeview(janela_relatorio, height=10, columns=("col1", "col2", "col3"))
        lista_produtos.place(relx=0.01, rely=0.1, relwidth=0.96, relheight=0.8)
        lista_produtos.heading("#0", text="")
        lista_produtos.heading("#1", text="Código")
        lista_produtos.heading("#2", text="Nome")
        lista_produtos.heading("#3", text="Preço")
        lista_produtos.column("#0", width=1)
        lista_produtos.column("#1", width=50)
        lista_produtos.column("#2", width=200)
        lista_produtos.column("#3", width=125)

        # Preenchendo os dados dos produtos
        dados = self.buscar_dados_produtos()
        if dados:
            for item in dados:
                codigo = item.get("codigo")
                nome = item.get("nome")
                preco = item.get("preco")
                lista_produtos.insert("", "end", values=(codigo, nome, preco))
        else:
            messagebox.showinfo("Informação", "Nenhum produto encontrado.")

        # Adicionando um botão para fechar o relatório
        botao_fechar = Button(janela_relatorio, text="Fechar", command=janela_relatorio.destroy)
        botao_fechar.place(relx=0.85, rely=0.9, relwidth=0.12, relheight=0.05)


class FuncsProdutos:
    def buscar_dados_produtos(self):
        try:
            response = requests.get(urlDoSistema + "/api/produtos", headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                messagebox.showerror("Erro", f"Erro ao buscar dados: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro", f"Erro de conexão: {e}")
            return []


class CadastroProdutos(FuncsProdutos, RelatoriosProdutos):
    def __init__(self):
        self.janela = Tk()
        self.tela()
        self.frame_tela()
        self.lista_frame()
        self.menus()
        self.carregar_dados_produtos()
        self.janela.mainloop()

    def tela(self):
        self.janela.title("Cadastro de Produtos")
        self.janela.configure(bg="#736660")
        self.janela.geometry("800x600")
        self.janela.resizable(False, False)
        self.janela.maxsize(width=800, height=600)
        self.janela.minsize(width=800, height=600)

    def frame_tela(self):
        self.frame = Frame(self.janela, bg="#d3d3d3")
        self.frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.95)

        self.voltar = Button(self.frame, text="Voltar", command=self.voltar_para_tela_inicial)
        self.voltar.place(relx=0.01, rely=0.02, relwidth=0.1, relheight=0.05)
    def lista_frame(self):
        self.listaProdutos = ttk.Treeview(self.frame, height=3, columns=("col1", "col2", "col3"))
        self.listaProdutos.place(relx=0.01, rely=0.1, relwidth=0.96, relheight=0.8)
        self.scroollista = Scrollbar(self.frame, orient='vertical')
        self.listaProdutos.configure(yscrollcommand=self.scroollista.set)
        self.scroollista.place(relx=0.96, rely=0.1, relwidth=0.03, relheight=0.8)
        self.listaProdutos.heading("#0", text="")
        self.listaProdutos.heading("#1", text="Categoria")
        self.listaProdutos.heading("#2", text="Nome")
        self.listaProdutos.heading("#3", text="Preço")
        self.listaProdutos.column("#0", width=1)
        self.listaProdutos.column("#1", width=50)
        self.listaProdutos.column("#2", width=200)
        self.listaProdutos.column("#3", width=125)

    def menus(self):
        menubar = Menu(self.janela)
        self.janela.config(menu=menubar)

    def carregar_dados_produtos(self):
        dados = self.buscar_dados_produtos()
        if dados:
            self.listaProdutos.delete(*self.listaProdutos.get_children())
            for item in dados:
                categoria = item.get("categoria")
                nome = item.get("nome")
                preco = item.get("preco")
                self.listaProdutos.insert("", "end", values=(categoria, nome, preco))
        else:
            messagebox.showinfo("Informação", "Nenhum produto encontrado.")

    def voltar_para_tela_inicial(self):
        self.janela.destroy()
        Aplicacao()

class Aplicacao:
    def __init__(self):
        self.janela = Tk()
        self.configurar_janela()
        self.img()
        self.botoes_frame()
        self.janela.mainloop()

    def configurar_janela(self):
        self.janela.title("Sistema de Produtores")
        self.janela.configure(bg="white")
        self.janela.geometry("450x300")
        self.janela.resizable(False, False)

    def img(self):
        try:
            # Baixa a imagem e cria o objeto PhotoImage
            imagem_pil = baixar_imagem(url_imagem)
            self.imagem = ImageTk.PhotoImage(imagem_pil)
            #self.imagem = PhotoImage(file="img/serra_e-commerce.png")
            w = Label(self.janela, image=self.imagem, bg="white")
            w.image = self.imagem
            w.pack(pady=15)
        except TclError:
            print("Erro: Imagem não encontrada.")

    def botoes_frame(self):
        button_color = "#736660"  # Cor do fundo dos botões
        hover_color = "#ae9f98"  # Cor quando pressionado
        button_text_color = "white"  # Cor do texto dos botões

        # Criando botões com eventos de mouse para mudar a cor ao pressionar
        self.produtores = Button(self.janela, text="Produtores", bg=button_color, fg=button_text_color, command=self.abrir_cadastro_produtores)
        self.produtores.place(relx=0.05, rely=0.7, relwidth=0.2, relheight=0.1)
        self.produtores.bind("<ButtonPress-1>", lambda e: e.widget.config(bg=hover_color))
        self.produtores.bind("<ButtonRelease-1>", lambda e: e.widget.config(bg=button_color))

        self.produtos = Button(self.janela, text="Produtos", bg=button_color, fg=button_text_color, command=self.abrir_cadastro_produtos)
        self.produtos.place(relx=0.28, rely=0.7, relwidth=0.2, relheight=0.1)
        self.produtos.bind("<ButtonPress-1>", lambda e: e.widget.config(bg=hover_color))
        self.produtos.bind("<ButtonRelease-1>", lambda e: e.widget.config(bg=button_color))

        self.relatorio = Button(self.janela, text="Relatórios", bg=button_color, fg=button_text_color)
        self.relatorio.place(relx=0.52, rely=0.7, relwidth=0.2, relheight=0.1)
        self.relatorio.bind("<ButtonPress-1>", lambda e: e.widget.config(bg=hover_color))
        self.relatorio.bind("<ButtonRelease-1>", lambda e: [e.widget.config(bg=button_color), emDesenvolvimento()])

        def emDesenvolvimento():
            messagebox.showinfo("Aviso", "Em desenvolvimento")

        self.fatura = Button(self.janela, text="Faturas", bg=button_color, fg=button_text_color, command=self.abrir_fatura)
        self.fatura.place(relx=0.75, rely=0.7, relwidth=0.2, relheight=0.1)
        self.fatura.bind("<ButtonPress-1>", lambda e: e.widget.config(bg=hover_color))
        self.fatura.bind("<ButtonRelease-1>", lambda e: e.widget.config(bg=button_color))


    def abrir_cadastro_produtores(self):
            self.janela.destroy()
            CadastroProdutores()

    def abrir_cadastro_produtos(self):
        self.janela.destroy()
        CadastroProdutos()

    def abrir_fatura(self):
        self.janela.destroy()
        Faturas()

    def emDesenvolvimento(self):
        messagebox.showinfo("Aviso", "Em desenvolvimento!")


# --- Execução da Tela de Login ---
if __name__ == "__main__":
    TelaLogin()

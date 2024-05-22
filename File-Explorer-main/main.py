import os
from tkinter import ttk, Tk, Entry, StringVar, Menu, simpledialog, messagebox, Toplevel
from PIL import ImageTk, Image
import zipfile

from git import Repo

janela = Tk()
janela.title('Indiana Arquives')
janela.config(background='black')
favoritos = [{'text': 'C', 'caminho': "C:\\"},
             {'text': 'Users', 'caminho': "C:\\Users\\"},
             {'text': 'Área de trabalho jose', 'caminho': "C:\\Users\\josev\\OneDrive\\Área de Trabalho\\"},
             {'text': 'area de trabalho','caminho': 'C:\\Users\\jose_ghisleire\\Desktop\\'}
             ]

imagem_pasta = ImageTk.PhotoImage(
    Image.open('./pasta.jpeg').resize((16, 16)))

imagem_arquivo = ImageTk.PhotoImage(
    Image.open('./arquivo.jpg').resize((16, 16)))

historico = ["C:\\"]
indice = 0
pasta = "C:\\"

style = ttk.Style()
style.configure("Treeview", background="black", foreground="white", fieldbackground="black")
frame_botoes = ttk.Treeview(janela, height=20)
frame_botoes.grid(row=1, column=1)

# Cria um frame para conter o Treeview e a Scrollbar
frame_favoritos = ttk.Frame(janela)
frame_favoritos.grid(row=2, column=1)

favoritos_tree = ttk.Treeview(frame_favoritos, height=10, show='tree')
favoritos_tree.pack(side='left')

tree = ttk.Treeview(janela, style="Treeview")
tree["show"] = "tree"

entrada = StringVar()


def get_texto_pesquisa():
    return entrada.get()


def listar_arquivos(diretorio, filtro=""):
    for n in tree.get_children():
        tree.delete(n)
    for nome in os.listdir(diretorio):
        if filtro.lower() in nome.lower():
            caminho_completo = os.path.join(diretorio, nome)
            caminho_completo = caminho_completo.replace("\\", "/")
            if os.path.isdir(caminho_completo):
                tree.insert('', 'end', text=nome, image=imagem_pasta, values=[caminho_completo])
            else:
                tree.insert('', 'end', text=nome, image=imagem_arquivo, values=[caminho_completo])


def atualizar_tree():
    listar_arquivos(historico[indice])
    campo_pesquisa.delete(0, 'end')


def adicionar_ao_historico(caminho_completo):
    global indice
    if os.path.isdir(caminho_completo):
        try:
            os.listdir(caminho_completo)
        except PermissionError:
            print(f"Permissão negada: {caminho_completo}")
            return
        indice += 1
        if len(historico) > indice:
            historico[indice] = caminho_completo
            del historico[indice + 1:]
        else:
            historico.append(caminho_completo)
        listar_arquivos(caminho_completo)
    elif os.path.isfile(caminho_completo):
        try:
            os.startfile(caminho_completo)
        except Exception as e:
            print(f"Erro ao abrir o arquivo {caminho_completo}: {e}")


def abrir_arquivo_com_permissao():
    global indice
    item_selecionado = tree.selection()[0]
    caminho_completo = os.path.join(historico[indice], tree.item(item_selecionado)['text'])
    adicionar_ao_historico(caminho_completo)


def abrir_diretorio(event):
    global indice
    item_selecionado = tree.selection()[0]
    caminho_completo = tree.item(item_selecionado)['values'][0]
    print(caminho_completo)
    if os.path.isdir(caminho_completo):
        adicionar_ao_historico(caminho_completo)
        listar_arquivos(caminho_completo)
    elif os.path.isfile(caminho_completo):
        try:
            os.startfile(caminho_completo)
        except Exception as e:
            print(f"Erro ao abrir o arquivo {caminho_completo}: {e}")


def voltar():
    global indice
    if indice > 0:
        indice -= 1
        listar_arquivos(historico[indice])


def avancar():
    global indice
    if indice < len(historico) - 1:
        indice += 1
        listar_arquivos(historico[indice])


def listar_arquivos_favoritos(event):
    global historico, indice
    item_selecionado = favoritos_tree.selection()[0]
    caminho_completo = favoritos_tree.item(item_selecionado)['values'][0]
    adicionar_ao_historico(caminho_completo)


def pesquisar(*args):
    listar_arquivos(historico[indice], entrada.get())


def criar_novo_item():
    def confirmar():
        nome = nome_var.get()
        tipo = tipo_var.get()
        if nome:
            caminho_completo = os.path.join(historico[indice], nome)
            if tipo == "Pasta":
                try:
                    os.mkdir(caminho_completo)
                    adicionar_ao_historico(historico[indice])
                    messagebox.showinfo("Sucesso", f"Pasta '{nome}' criada com sucesso!")
                except FileExistsError:
                    messagebox.showerror("Erro", f"A pasta '{nome}' já existe.")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao criar a pasta: {e}")
            elif tipo == "Arquivo":
                if not os.path.splitext(nome)[1]:
                    messagebox.showerror("Erro", "Por favor, inclua uma extensão no nome do arquivo.")
                else:
                    try:
                        with open(caminho_completo, 'w') as arquivo:
                            pass
                        adicionar_ao_historico(historico[indice])
                        messagebox.showinfo("Sucesso", f"Arquivo '{nome}' criado com sucesso!")
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao criar o arquivo: {e}")
            novo_item_window.destroy()
        else:
            messagebox.showwarning("Aviso", "Por favor, digite um nome válido.")

    novo_item_window = Toplevel(janela)
    novo_item_window.title("Criar Novo Item")
    novo_item_window.geometry("300x150")

    nome_var = StringVar()
    tipo_var = StringVar(value="Pasta")

    ttk.Label(novo_item_window, text="Nome:").pack(pady=5)
    Entry(novo_item_window, textvariable=nome_var).pack(pady=5)

    ttk.Label(novo_item_window, text="Tipo:").pack(pady=5)
    tipo_frame = ttk.Frame(novo_item_window)
    tipo_frame.pack(pady=5)

    ttk.Radiobutton(tipo_frame, text="Pasta", variable=tipo_var, value="Pasta").pack(side='left', padx=5)
    ttk.Radiobutton(tipo_frame, text="Arquivo", variable=tipo_var, value="Arquivo").pack(side='left', padx=5)

    ttk.Button(novo_item_window, text="Confirmar", command=confirmar).pack(pady=10)

def enviar_para_github():
    try:
        caminho_repo = r"C://Users//jose_ghisleire//Desktop//File-Explorer-main"
        
        if os.path.isdir(caminho_repo):
            if not os.path.exists(os.path.join(caminho_repo, '.git')):
                messagebox.showerror("Erro", "O diretório especificado não é um repositório Git.")
                return

            mensagem_commit = simpledialog.askstring("Mensagem de Commit", "Digite a mensagem do commit:")

            if not mensagem_commit:
                messagebox.showwarning("Aviso", "Por favor, forneça uma mensagem de commit.")
                return

            repo = Repo(caminho_repo)
            repo.git.add(all=True)
            repo.index.commit(mensagem_commit)

            origin = repo.remote(name='origin')
            origin.push()

            messagebox.showinfo("Sucesso", "Arquivos enviados para o GitHub com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao enviar para o GitHub: {e}")
        print(e)


def adicionar_aos_favoritos(caminho_completo):
    global favoritos
    if not any(fav['caminho'] == caminho_completo for fav in favoritos):
        favoritos.append({'text': os.path.basename(caminho_completo), 'caminho': caminho_completo})
        for n in favoritos_tree.get_children():
            favoritos_tree.delete(n)
        for i in favoritos:
            favoritos_tree.insert('', 'end', text=i['text'], values=[i['caminho']])


def zipar_arquivo(arquivo_origem, arquivo_destino_zip):
    with zipfile.ZipFile(arquivo_destino_zip, 'w') as zipf:
        zipf.write(str(arquivo_origem), arcname=os.path.basename(arquivo_origem))


def zipar_diretorio(diretorio_origem, arquivo_destino_zip):
    with zipfile.ZipFile(arquivo_destino_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(diretorio_origem):
            for file in files:
                caminho_completo = os.path.join(root, file)
                arcname = os.path.relpath(str(caminho_completo), diretorio_origem)
                zipf.write(str(caminho_completo), arcname=arcname)


def zipar_selecionado():
    if tree.selection():
        item_selecionado = tree.selection()[0]
        caminho_completo = tree.item(item_selecionado)['values'][0]

        if os.path.isdir(caminho_completo):
            destino_zip = os.path.join(os.path.dirname(caminho_completo), os.path.basename(caminho_completo) + ".zip")
            zipar_diretorio(caminho_completo, destino_zip)
        elif os.path.isfile(caminho_completo):
            destino_zip = os.path.join(os.path.dirname(caminho_completo), os.path.basename(caminho_completo) + ".zip")
            zipar_diretorio(caminho_completo, destino_zip)

        listar_arquivos(historico[indice])
    else:
        messagebox.showerror("Erro", "Por favor, selecione um item para zipar.")


def extrair_zip(arquivo_zip):
    diretorio_destino = historico[indice]

    if not diretorio_destino:
        return

    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        for file in zip_ref.namelist():
            file_path = os.path.join(diretorio_destino, file)
            if os.path.exists(file_path):
                # Cria uma janela de diálogo para lidar com o conflito
                janela_conflito = Toplevel(janela)
                janela_conflito.title("Conflito de Arquivo")
                janela_conflito.geometry("300x150")

                label = ttk.Label(janela_conflito, text=f"O arquivo '{file}' já existe. O que você deseja fazer?")
                label.pack(pady=10)

                def substituir():
                    zip_ref.extract(file, diretorio_destino)
                    listar_arquivos(os.path.dirname(arquivo_zip))  # Atualizar a visualização após a extração
                    janela_conflito.destroy()

                def renomear_zip():
                    novo_nome = simpledialog.askstring("Novo Nome", "Digite um novo nome para a pasta:")
                    if novo_nome:
                        novo_caminho = os.path.join(diretorio_destino, novo_nome)
                        with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
                            zip_ref.extractall(novo_caminho)
                        listar_arquivos(diretorio_destino)
                    janela_conflito.destroy()

                def manter_ambos():
                    novo_nome = file
                    i = 1
                    while os.path.exists(os.path.join(diretorio_destino, novo_nome)):
                        novo_nome = f"{os.path.splitext(file)[0]}_{i}{os.path.splitext(file)[1]}"
                        i += 1
                    zip_ref.extract(file, os.path.dirname(os.path.join(diretorio_destino, novo_nome)))
                    listar_arquivos(os.path.dirname(arquivo_zip))  # Atualizar a visualização após a extração
                    janela_conflito.destroy()

                def cancelar():
                    janela_conflito.destroy()

                botao_substituir = ttk.Button(janela_conflito, text="Substituir", command=substituir)
                botao_substituir.pack(side='left', padx=10, pady=10)

                botao_renomear = ttk.Button(janela_conflito, text="Renomear", command=renomear_zip)
                botao_renomear.pack(side='left', padx=10, pady=10)

                botao_manter_ambos = ttk.Button(janela_conflito, text="Manter Ambos", command=manter_ambos)
                botao_manter_ambos.pack(side='left', padx=10, pady=10)

                botao_cancelar = ttk.Button(janela_conflito, text="Cancelar", command=cancelar)
                botao_cancelar.pack(side='left', padx=10, pady=10)

                janela_conflito.transient(janela)
                janela_conflito.grab_set()
                janela_conflito.wait_window(janela_conflito)
                listar_arquivos(os.path.dirname(arquivo_zip))
            else:
                zip_ref.extract(file, diretorio_destino)
                listar_arquivos(os.path.dirname(arquivo_zip))


def verificar_tipo_arquivo(caminho_completo):
    if os.path.isfile(caminho_completo):
        print(f"'{caminho_completo}' é um arquivo.")
    elif os.path.isdir(caminho_completo):
        print(f"'{caminho_completo}' é um diretório.")
    elif os.path.islink(caminho_completo):
        print(f"'{caminho_completo}' é um link simbólico.")
    else:
        print(f"'{caminho_completo}' não é um arquivo, diretório ou link simbólico reconhecido.")


def deletar_selecionado(caminho_completo):
    if os.path.isfile(caminho_completo) or os.path.isdir(caminho_completo):
        confirmar = messagebox.askyesno("Confirmar Deleção", f"Tem certeza que deseja deletar '{caminho_completo}'?")
        if confirmar:
            try:
                if os.path.isfile(caminho_completo):
                    os.remove(caminho_completo)
                elif os.path.isdir(caminho_completo):
                    os.rmdir(caminho_completo)
                listar_arquivos(historico[indice])
                return True
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deletar '{caminho_completo}': {e}")
                return False


def on_delete(event):
    item = tree.focus()
    if item:
        caminho_completo = tree.item(item)['values'][0]
        if deletar_selecionado(caminho_completo):
            messagebox.showinfo("Sucesso", f"'{caminho_completo}' foi deletado com sucesso.")
            listar_arquivos(historico[indice])


def renomear():
    item_selecionado = tree.selection()[0]
    caminho_completo = tree.item(item_selecionado)['values'][0]
    nome_atual = os.path.basename(caminho_completo)

    novo_nome = simpledialog.askstring("Renomear", f"Digite um novo nome para '{nome_atual}':")
    if novo_nome:
        diretorio_atual = os.path.dirname(caminho_completo)
        novo_caminho = os.path.join(diretorio_atual, novo_nome)

        try:
            os.rename(caminho_completo, novo_caminho)
            listar_arquivos(diretorio_atual)  # Atualizar a lista de arquivos
            messagebox.showinfo("Sucesso", f"'{nome_atual}' foi renomeado para '{novo_nome}'.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao renomear: {e}")


def criar_menu(event):
    # Identifica o item na Treeview baseado na posição do clique
    item = tree.identify('item', event.x, event.y)

    # Verifica se um item foi clicado
    if not item:
        # Se não houver item clicado, criar um menu simples para criar nova pasta
        print("Nenhum item foi clicado")
        menu = Menu(janela, tearoff=0)
        menu.add_command(label="Criar Pasta", command=criar_novo_item)
    else:
        # Selecione o item clicado
        tree.selection_set(item)

        # Obtém o caminho completo do item selecionado
        caminho_completo = tree.item(item)['values'][0]
        print(f"Item clicado: {caminho_completo}")
        menu = Menu(janela, tearoff=0)

        if caminho_completo.endswith('.zip'):
            menu.add_command(label="Extrair", command=lambda: extrair_zip(caminho_completo))
        else:
            menu.add_command(label="Zipar", command=lambda: zipar_selecionado())

        menu.add_command(label="Adicionar aos Favoritos", command=lambda: adicionar_aos_favoritos(caminho_completo))
        menu.add_command(label="Criar Pasta", command=criar_novo_item)
        menu.add_command(label="Renomear", command=renomear)
        menu.add_command(label="Enviar para github", command=enviar_para_github)
        menu.add_command(label="Deletar", command=lambda: deletar_selecionado(caminho_completo))

    # Exibe o menu de contexto na posição do clique
    menu.post(event.x_root, event.y_root)


# Vincule o evento de clique com o botão direito à função criar_menu
tree.bind("<Button-3>", criar_menu)

botao_voltar = ttk.Button(frame_botoes, text='Voltar', command=voltar)
botao_voltar.pack(side='left')

botao_avancar = ttk.Button(frame_botoes, text='Avançar', command=avancar)
botao_avancar.pack(side='left')

for i in favoritos:
    favoritos_tree.insert('', 'end', text=i['text'], values=[i['caminho']])

campo_pesquisa = Entry(janela, textvariable=entrada, width=100)
campo_pesquisa.grid(row=1, column=3)

tree.image = imagem_pasta
tree.grid_configure(column=3, row=2)
tree.grid(sticky="NSEW")

tree.bind('<Double-Button-1>', abrir_diretorio)
favoritos_tree.bind('<Double-Button-1>', listar_arquivos_favoritos)
tree.bind("<Button-3>", criar_menu)
janela.bind("<Delete>", on_delete)

entrada.trace("w", pesquisar)

listar_arquivos(historico[indice])
janela.mainloop()

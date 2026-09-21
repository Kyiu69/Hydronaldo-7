import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import pygame
import pystray

from PIL import Image, ImageTk
from pystray import MenuItem as item


# ============================================================
# CONFIGURAÇÕES INICIAIS
# ============================================================

pygame.mixer.init()

janela = tk.Tk()
janela.title("HYDRONALDO 7!")
janela.geometry("700x500")
janela.resizable(True, True)

icone_bandeja = None


# ============================================================
# SISTEMA DE ÁUDIO
# ============================================================

def tocar_som(nome_arquivo):
    """
    Carrega e toca um arquivo de áudio.
    """

    print("Tentando tocar:", nome_arquivo)
    print("Arquivo existe?", os.path.exists(nome_arquivo))

    try:
        pygame.mixer.music.load(nome_arquivo)

        print("Arquivo carregado com sucesso!")

        pygame.mixer.music.play()

        print("Comando PLAY executado!")

    except Exception as erro:
        print(f"Erro ao tocar o áudio: {erro}")


def tocar_prowler_e_fechar():
    """
    Toca o áudio do Prowler.
    Quando o áudio terminar, fecha o aplicativo.
    """

    tocar_som("Prowler.mp3")

    verificar_fim_audio()


def verificar_fim_audio():
    """
    Verifica se o áudio ainda está tocando.
    Enquanto estiver tocando, verifica novamente depois de 100 ms.
    Quando terminar, fecha o aplicativo.
    """

    if pygame.mixer.music.get_busy():
        janela.after(100, verificar_fim_audio)

    else:
        janela.destroy()


# ============================================================
# SISTEMA DE IMAGENS
# ============================================================

image_definitions = {
    "cmc": "CR7cmc.jpg",
    "puto": "CRputo.jpg",
    "orgulho": "orgulho.jpg",
    "vc": "vc.jpg",
    "pensano": "pensano.jpg",
}


original_pil_images = {}


# Carrega todas as imagens
for chave, caminho in image_definitions.items():

    try:
        original_pil_images[chave] = Image.open(caminho)

    except FileNotFoundError:

        messagebox.showerror(
            "Erro de Arquivo",
            f"Não foi possível encontrar a imagem: {caminho}"
        )

        original_pil_images[chave] = Image.new(
            "RGB",
            (100, 100)
        )


# Imagem inicial
current_bg_key = "cmc"


# ============================================================
# FUNDO DA JANELA
# ============================================================

fundo1 = tk.Label(janela)

fundo1.place(
    x=0,
    y=0,
    relwidth=1,
    relheight=1
)


def update_background_image(event=None):
    """
    Redimensiona a imagem de fundo de acordo
    com o tamanho atual da janela.
    """

    pil_image = original_pil_images.get(current_bg_key)

    if not pil_image:
        return

    try:

        largura = janela.winfo_width()
        altura = janela.winfo_height()

    except tk.TclError:

        return

    if largura < 50 or altura < 50:
        return

    imagem_redimensionada = pil_image.resize(
        (largura, altura),
        Image.Resampling.LANCZOS
    )

    imagem_tk = ImageTk.PhotoImage(
        imagem_redimensionada
    )

    fundo1.config(
        image=imagem_tk
    )

    fundo1.image = imagem_tk


def set_and_update_background(chave):
    """
    Troca a imagem de fundo e atualiza a janela.
    """

    global current_bg_key

    if chave in original_pil_images:

        current_bg_key = chave

        update_background_image()


# Sempre que a janela mudar de tamanho,
# atualiza o fundo.
janela.bind(
    "<Configure>",
    update_background_image
)


# ============================================================
# MENSAGEM PRINCIPAL
# ============================================================

mensagem = tk.Label(
    janela,
    text="Olá Campeão",
    font=("Verdana", 12),
    bg="#370",
    fg="white"
)

mensagem.pack(
    side="top",
    pady=25
)


# ============================================================
# VARIÁVEIS DO APLICATIVO
# ============================================================

botao_sim = None
botao_nao = None
botao_ok = None

entrada_intervalo = None
botao_confirmar_intervalo = None

vezes_clicou_nao = 0

intervalo_minutos = 0

lembrete_thread_ativa = False


# ============================================================
# EFEITOS DOS BOTÕES
# ============================================================

button_effects = {}


def start_breathing(widget):
    """
    Faz o botão alternar entre duas tonalidades de verde.
    """

    def breath():

        if (
            widget not in button_effects
            or not widget.winfo_exists()
        ):
            return

        try:

            cor_atual = widget.cget("background")

        except tk.TclError:

            button_effects.pop(widget, None)

            return

        if cor_atual == "#00FF00":

            nova_cor = "#00DD00"

        else:

            nova_cor = "#00FF00"

        try:

            widget.config(
                background=nova_cor
            )

        except tk.TclError:

            button_effects.pop(widget, None)

            return

        job_id = widget.after(
            300,
            breath
        )

        if widget in button_effects:

            button_effects[widget]["job"] = job_id

    breath()


def on_enter(event):
    """
    Executada quando o mouse entra no botão.
    """

    widget = event.widget

    if not widget.winfo_exists():
        return

    if widget not in button_effects:

        button_effects[widget] = {
            "original_bg": widget.cget("background"),
            "job": None
        }

    if button_effects[widget]["job"]:

        widget.after_cancel(
            button_effects[widget]["job"]
        )

    widget.config(
        background="#00FF00"
    )

    start_breathing(widget)


def on_leave(event):
    """
    Executada quando o mouse sai do botão.
    """

    widget = event.widget

    if not widget.winfo_exists():
        return

    if widget in button_effects:

        if button_effects[widget]["job"]:

            widget.after_cancel(
                button_effects[widget]["job"]
            )

        try:

            widget.config(
                background=button_effects[widget]["original_bg"]
            )

        except tk.TclError:

            pass

        del button_effects[widget]


# ============================================================
# PRIMEIRA TELA
# ============================================================

def clicar():

    global botao_sim
    global botao_nao

    mensagem.config(
        text="Você trouxe sua garrafa, campeão?"
    )

    botao.pack_forget()

    if botao_sim is None:

        botao_sim = tk.Button(
            janela,
            text="Sim",
            font=("Verdana", 15),
            command=botao_sim_clicado
        )

        botao_sim.bind(
            "<Enter>",
            on_enter
        )

        botao_sim.bind(
            "<Leave>",
            on_leave
        )

        botao_sim.pack(
            side="left",
            padx=50,
            pady=20
        )

    if botao_nao is None:

        botao_nao = tk.Button(
            janela,
            text="Não",
            font=("Verdana", 15),
            command=botao_nao_clicado
        )

        botao_nao.bind(
            "<Enter>",
            on_enter
        )

        botao_nao.bind(
            "<Leave>",
            on_leave
        )

        botao_nao.pack(
            side="right",
            padx=50,
            pady=20
        )


# ============================================================
# BOTÃO SIM
# ============================================================

def botao_sim_clicado():

    set_and_update_background(
        "orgulho"
    )

    mensagem.config(
        text="Boa, meu nobre! Vamo nessa então!",
        wraplength=500
    )

    mensagem.pack(
        side="top",
        pady=20
    )

    tocar_som(
        "EPA.mp3"
    )

    janela.after(
        2500,
        mostrar_pergunta
    )

    botao_sim.pack_forget()
    botao_nao.pack_forget()


# ============================================================
# PERGUNTA DO INTERVALO
# ============================================================

def mostrar_pergunta():

    global entrada_intervalo
    global botao_confirmar_intervalo

    mensagem.config(
        text=(
            "De quantos em quantos minutos "
            "você quer ser lembrado de se hidratar?\n"
            "(Não pode passar de 120 minutos)"
        ),
        wraplength=500
    )

    if entrada_intervalo is None:

        entrada_intervalo = tk.Entry(
            janela,
            font=("Verdana", 15),
            justify="center"
        )

    entrada_intervalo.pack(
        pady=5
    )

    if botao_confirmar_intervalo is None:

        botao_confirmar_intervalo = tk.Button(
            janela,
            text="Bora!",
            font=("Verdana", 15),
            command=confirmar_intervalo
        )

        botao_confirmar_intervalo.bind(
            "<Enter>",
            on_enter
        )

        botao_confirmar_intervalo.bind(
            "<Leave>",
            on_leave
        )

    botao_confirmar_intervalo.config(
        text="Bora!"
    )

    botao_confirmar_intervalo.pack(
        side="bottom",
        pady=10
    )


# ============================================================
# BOTÃO NÃO
# ============================================================

def botao_nao_clicado():

    global botao_ok
    global vezes_clicou_nao

    vezes_clicou_nao += 1

    print(
        "Quantidade de NÃO:",
        vezes_clicou_nao
    )

    # PRIMEIRO NÃO
    if vezes_clicou_nao == 1:

        set_and_update_background(
            "puto"
        )

        mensagem.config(
            text="VAI PEGAR ESSA POHA DE GARRAFA!"
        )

        botao_sim.pack_forget()
        botao_nao.pack_forget()

        if botao_ok is None:

            botao_ok = tk.Button(
                janela,
                text="Ok, Papai Cris",
                font=("Verdana", 15),
                command=botao_ok_clicado
            )

            botao_ok.bind(
                "<Enter>",
                on_enter
            )

            botao_ok.bind(
                "<Leave>",
                on_leave
            )

        botao_ok.pack(
            side="bottom",
            pady=20
        )

    # SEGUNDO NÃO
    elif vezes_clicou_nao == 2:

        print(
            "SEGUNDO NÃO DETECTADO!"
        )

        messagebox.showerror(
            "CR7 Ficou puto!",
            "Cansei de você, mlk!"
        )

        tocar_prowler_e_fechar()


# ============================================================
# BOTÃO OK
# ============================================================

def botao_ok_clicado():

    global botao_ok

    botao_ok.pack_forget()

    set_and_update_background(
        "cmc"
    )

    mensagem.config(
        text="Pegou essa garrafa?",
        wraplength=400
    )

    botao_sim.pack(
        side="left",
        padx=50,
        pady=20
    )

    botao_nao.pack(
        side="right",
        padx=50,
        pady=20
    )


# ============================================================
# INTERVALO
# ============================================================

def confirmar_intervalo():

    global intervalo_minutos
    global lembrete_thread_ativa

    try:

        intervalo = entrada_intervalo.get()

        if not intervalo:

            messagebox.showwarning(
                "Atenção",
                "O campo de intervalo não pode estar vazio."
            )

            return

        intervalo_minutos = int(
            intervalo
        )

        if (
            intervalo_minutos <= 1
            or intervalo_minutos > 120
        ):

            messagebox.showwarning(
                "Porra man.",
                "O intervalo deve ser maior que 1 e menor ou igual a 120 minutos."
            )

            return

        entrada_intervalo.pack_forget()

        botao_confirmar_intervalo.pack_forget()

        set_and_update_background(
            "orgulho"
        )

        mensagem.config(
            text=(
                f"Valeu! Te vejo a cada "
                f"{intervalo_minutos} minuto(s). "
                f"Beba água!"
            )
        )

        if not lembrete_thread_ativa:

            thread = threading.Thread(
                target=lembrete_auto,
                daemon=True
            )

            thread.start()

            lembrete_thread_ativa = True

    except ValueError:

        messagebox.showerror(
            "Bixo Burro",
            "Digita só números, mula!"
        )


# ============================================================
# ALTERAR INTERVALO PELA BANDEJA
# ============================================================

def alterar_intervalo(
    icon=None,
    item=None
):

    global entrada_intervalo
    global botao_confirmar_intervalo

    janela.deiconify()

    set_and_update_background(
        "pensano"
    )

    mensagem.config(
        text=(
            "Mudou de ideia, Gajo? "
            "Me atualiza do seu novo intervalo "
            "de minutos aí"
        ),
        wraplength=500
    )

    if entrada_intervalo is None:

        entrada_intervalo = tk.Entry(
            janela,
            font=("Verdana", 15),
            justify="center"
        )

    entrada_intervalo.delete(
        0,
        tk.END
    )

    entrada_intervalo.pack(
        pady=5
    )

    if botao_confirmar_intervalo is None:

        botao_confirmar_intervalo = tk.Button(
            janela,
            text="Atualizar! SIUU",
            font=("Verdana", 15),
            command=confirmar_intervalo
        )

        botao_confirmar_intervalo.bind(
            "<Enter>",
            on_enter
        )

        botao_confirmar_intervalo.bind(
            "<Leave>",
            on_leave
        )

    botao_confirmar_intervalo.config(
        text="Atualizar! SIUU"
    )

    botao_confirmar_intervalo.pack(
        side="bottom",
        pady=10
    )


# ============================================================
# SISTEMA DE LEMBRETES
# ============================================================

def lembrete_auto():

    while True:

        time.sleep(
            intervalo_minutos * 60
        )

        if not janela.winfo_exists():
            break

        janela.deiconify()

        set_and_update_background(
            "vc"
        )

        mensagem.config(
            text="BEBA ÁGUA, CAMPEÃO, SIUUUU!!",
            wraplength=500
        )

        tocar_som(
            "SIUU.mp3"
        )


# ============================================================
# BANDEJA DO WINDOWS
# ============================================================

def esconder_janela():

    janela.withdraw()


def mostrar_janela(
    icon,
    item
):

    global icone_bandeja

    janela.deiconify()

    if icone_bandeja:

        icone_bandeja.stop()

        icone_bandeja = None


def sair_do_app(
    icon,
    item
):

    global icone_bandeja

    if icone_bandeja:

        icone_bandeja.stop()

    janela.destroy()


def criar_bandeja():

    global icone_bandeja

    if (
        icone_bandeja is not None
        and icone_bandeja.visible
    ):

        return

    try:

        imagem_icone = Image.open(
            "cristiano1.ico"
        )

    except FileNotFoundError:

        imagem_icone = Image.open(
            "cristiano.jpg"
        ).resize(
            (64, 64)
        )

    menu = (

        item(
            "Exibir",
            mostrar_janela
        ),

        item(
            "Alterar Intervalo",
            alterar_intervalo
        ),
        item(
            "Sair",
            sair_do_app
        )
    )

    icone_bandeja = pystray.Icon(
        "CR7hidrata",
        imagem_icone,
        "CR7 Hidrata!",
        menu
    )

    icone_bandeja.run()


def iniciar_bandeja():

    thread = threading.Thread(
        target=criar_bandeja,
        daemon=True
    )

    thread.start()


# ============================================================
# BOTÃO INICIAL
# ============================================================

botao = tk.Button(
    janela,
    text="Olá CR7",
    font=("Verdana", 14),
    command=clicar
)

botao.bind(
    "<Enter>",
    on_enter
)

botao.bind(
    "<Leave>",
    on_leave
)

botao.pack(
    side="bottom",
    pady=20
)


# ============================================================
# MINIMIZAR / FECHAR
# ============================================================

def ao_fechar():

    esconder_janela()

    iniciar_bandeja()


def ao_minimizar(event):

    if janela.state() == "iconic":

        esconder_janela()

        iniciar_bandeja()


janela.protocol(
    "WM_DELETE_WINDOW",
    ao_fechar
)

janela.bind(
    "<Unmap>",
    ao_minimizar
)


# ============================================================
# INICIA O APLICATIVO
# ============================================================

janela.mainloop()
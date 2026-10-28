#!/usr/bin/env python3
"""Modelo do build.py: monta os slides do carrossel pelo Chrome, sem Paper. Grátis e sem limite.

Copie pra pasta do carrossel como build.py, troque SLUG, FONTES, as cores e o SLIDES, e rode:
    python3 build.py          -> slides/<SLUG>-01.png, -02.png ...
    python3 build.py 2 5      -> só os slides 2 e 5

Cada slide é um HTML do tamanho do slide (1080x1440 por padrão) com os elementos em posição
absoluta. O Chrome headless abre o HTML e tira o print em PNG. Imagens (fotos, recortes do
original feitos com recortes.py, fundo de papel) ficam em _assets/ ao lado deste arquivo.
Precisa só do Google Chrome instalado (Mac, Windows ou Linux).
"""
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
A = ROOT / "_assets"
OUT = ROOT / "slides"
PERFIL = Path.home() / ".claude" / "carrossel" / "perfil"

SLUG = "meu-carrossel"
W, H = 1080, 1440
FUNDO = "#FFFFFF"            # cor lisa; pra fundo de imagem use FUNDO_IMG
FUNDO_IMG = None             # ex.: "papel.png" (arquivo em _assets/)
TINTA = "#111111"            # cor do texto
DESTAQUE = "#E2343A"         # cor de destaque (palavra colorida, risco)
# Fontes do Google Fonts, no formato da URL css2 (separadas por &)
FONTES = "family=Inter:wght@400;600;800"
FONTE_PADRAO = "Inter"

# Selo do último slide (lido do perfil quando existir)
SELO_NOME = "Seu Nome"
SELO_ARROBA = "@seuperfil"
SELO_VERIFICADO = False
AVATAR = PERFIL / "avatar.jpg"


def uri(p):
    return Path(p).resolve().as_uri()


def asset(nome):
    return uri(A / nome)


def head():
    fundo = f"{FUNDO} url('{asset(FUNDO_IMG)}')" if FUNDO_IMG else FUNDO
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?{FONTES}&display=block" rel="stylesheet">
<style>
html,body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:{fundo};background-size:cover;
  font-family:'{FONTE_PADRAO}',sans-serif;color:{TINTA};-webkit-font-smoothing:antialiased}}
.abs{{position:absolute}}
.sub{{background-repeat:no-repeat;background-position:0 100%;white-space:nowrap}}
</style></head><body>"""


VERIF = ('<svg width="{s}" height="{s}" viewBox="0 0 24 24" style="flex-shrink:0"><path fill="#1D9BF0" '
         'd="M12 1.5l2.4 1.8 3-.2 1 2.8 2.6 1.5-.6 2.9 1.5 2.6-1.9 2.3.2 3-2.8.9-1.4 2.7-2.9-.5-2.6 1.5-2.4-1.8-3 .2-1-2.8'
         '-2.6-1.5.6-2.9L.9 12.1l1.9-2.3-.2-3 2.8-.9L6.8 3.2l2.9.5z"/><path d="M7.5 12.3l3 3 6-6.2" stroke="#fff" '
         'stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def img(nome, x, y, w, extra=""):
    """Imagem de _assets/ na posição (x, y) com largura w."""
    return f'<img src="{asset(nome)}" class="abs" style="left:{x}px;top:{y}px;width:{w}px;{extra}">'


def texto(conteudo, x, y, tamanho, largura=None, peso=700, altura_linha=1.12, cor=None, fonte=None,
          alinhar="left", extra=""):
    """Bloco de texto. Use <br> pra quebrar linha onde a referência quebra."""
    larg = f"width:{largura}px;" if largura else "white-space:nowrap;"
    cor = f"color:{cor};" if cor else ""
    fonte = f"font-family:'{fonte}';" if fonte else ""
    return (f'<div class="abs" style="left:{x}px;top:{y}px;{larg}font-size:{tamanho}px;font-weight:{peso};'
            f'line-height:{altura_linha};text-align:{alinhar};{cor}{fonte}{extra}">{conteudo}</div>')


def sub(palavra, risco, altura, desce=0):
    """Palavra sublinhada com um risco (PNG de _assets/, ex. recortado do original) esticado na largura dela."""
    return (f'<span class="sub" style="background-image:url({asset(risco)});background-size:104% {altura}px;'
            f'padding-bottom:{desce}px">{palavra}</span>')


def selo(y, tamanho=96):
    """Foto de perfil + nome (+ selo azul) + @, centralizado. Vai no último slide."""
    foto = (f'<img src="{uri(AVATAR)}" style="width:{tamanho}px;height:{tamanho}px;border-radius:50%;'
            f'object-fit:cover">') if AVATAR.exists() else ""
    verif = VERIF.format(s=int(tamanho * 0.4)) if SELO_VERIFICADO else ""
    return (f'<div class="abs" style="left:0;top:{y}px;width:{W}px;display:flex;justify-content:center;'
            f'align-items:center;gap:20px">{foto}<div style="display:flex;flex-direction:column;gap:2px;'
            f'font-family:Inter,sans-serif"><div style="display:flex;align-items:center;gap:8px;font-weight:700;'
            f'font-size:{int(tamanho * 0.4)}px;color:#14171A">{SELO_NOME}{verif}</div>'
            f'<span style="font-weight:500;font-size:{int(tamanho * 0.31)}px;color:#6B6660">{SELO_ARROBA}</span>'
            f'</div></div>')


# Um item por slide. Margem de 60px dos lados; nada pra ler no canto superior direito.
SLIDES = {
    1: texto("MANCHETE DA CAPA<br>EM DUAS LINHAS", 60, 520, 84, peso=800)
    + texto("Subtítulo da capa", 60, 780, 54, largura=960, peso=400),

    2: texto("Título do slide", 60, 180, 80, peso=800)
    + texto(f"Texto do slide com uma palavra em {sub('destaque', 'risco.png', 18, 6)} sublinhada.",
            60, 340, 56, largura=960, peso=400, altura_linha=1.3),

    3: texto("Comenta <span style='color:%s'>PALAVRA</span>" % DESTAQUE, 0, 520, 92, largura=W, peso=800,
             alinhar="center")
    + texto("que eu te mando na DM.", 0, 680, 64, largura=W, peso=400, alinhar="center")
    + selo(1180),
}


def chrome():
    """Acha o Google Chrome (ou Edge/Chromium) no Mac, no Windows e no Linux."""
    candidatos = []
    sistema = platform.system()
    if sistema == "Darwin":
        candidatos += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                       "/Applications/Chromium.app/Contents/MacOS/Chromium",
                       "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    elif sistema == "Windows":
        for base in [os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                     os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                     os.environ.get("LOCALAPPDATA", "")]:
            candidatos += [os.path.join(base, r"Google\Chrome\Application\chrome.exe"),
                           os.path.join(base, r"Microsoft\Edge\Application\msedge.exe")]
    for nome in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"]:
        achado = shutil.which(nome)
        if achado:
            candidatos.append(achado)
    for c in candidatos:
        if c and os.path.exists(c):
            return c
    sys.exit("Não achei o Google Chrome. Instale em https://www.google.com/chrome e rode de novo.")


def render(n, navegador):
    OUT.mkdir(exist_ok=True)
    png = OUT / f"{SLUG}-{n:02d}.png"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(head() + SLIDES[n] + "</body></html>")
        tmp = Path(f.name)
    png.unlink(missing_ok=True)
    subprocess.run([navegador, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={W},{H}", "--virtual-time-budget=8000", "--allow-file-access-from-files",
                    f"--screenshot={png}", tmp.as_uri()], capture_output=True)
    tmp.unlink(missing_ok=True)
    if not png.exists():
        sys.exit(f"Falhou no slide {n}")
    print(png)


if __name__ == "__main__":
    navegador = chrome()
    for n in ([int(a) for a in sys.argv[1:]] or sorted(SLIDES)):
        render(n, navegador)

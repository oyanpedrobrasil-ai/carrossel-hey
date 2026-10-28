#!/usr/bin/env python3
"""Recorta desenhos, ícones, molduras e riscos de um slide da referência com fundo transparente.

A tinta é separada do papel (a cor do fundo é medida sozinha na borda do recorte), então o PNG
assenta em qualquer fundo sem caixa em volta e com o mesmo traço do original.

Uso:
    python3 recortes.py <imagem> <x0> <y0> <x1> <y1> <saida.png> [--modo tinta|preto|colorido] [--apagar x0,y0,x1,y1 ...]

- x0 y0 x1 y1: a caixa do desenho, em pixels da imagem da referência.
- --modo tinta (padrão): qualquer cor sobre fundo liso (preto, vermelho, azul...).
- --modo preto: só o traço escuro; ignora o que é colorido (ex.: letra vermelha encostada no desenho).
- --modo colorido: só o traço colorido (sublinhado vermelho, marca-texto, faísca); ignora letra preta
  por cima. Em risco comprido, também tapa o buraco que a letra deixava.
- --apagar: retângulo pra limpar (coordenadas dentro da caixa). Pode repetir.
- --corte-seco: corta exatamente na caixa (pra moldura grande); sem ele, o script dá uma folga e
  fica só com os traços cujo centro cai dentro da caixa, então nada sai cortado na borda.

Precisa de: pip3 install pillow numpy opencv-python-headless
"""
import argparse

import cv2
import numpy as np
from PIL import Image


def cor_do_fundo(p):
    """Mediana da borda do recorte: na borda quase tudo é papel."""
    borda = np.concatenate([p[:4].reshape(-1, 3), p[-4:].reshape(-1, 3), p[:, :4].reshape(-1, 3), p[:, -4:].reshape(-1, 3)])
    claros = borda[borda.sum(axis=1) > np.percentile(borda.sum(axis=1), 40)]
    return np.median(claros, axis=0)


def recorte(img, caixa, modo="tinta", apagar=(), folga=34, corte_seco=False):
    x0, y0, x1, y1 = caixa
    X0, Y0 = max(x0 - folga, 0), max(y0 - folga, 0)
    X1, Y1 = min(x1 + folga, img.shape[1]), min(y1 + folga, img.shape[0])
    p = img[Y0:Y1, X0:X1]
    papel = np.maximum(cor_do_fundo(p), 1)

    croma = p.max(axis=2) - p.min(axis=2)
    if modo == "colorido":
        # só a tinta colorida (risco vermelho, marca-texto): letra preta por cima fica de fora
        a = ((croma - 16) / 150).clip(0, 1)
        forte = a > 0.6
        cor = np.broadcast_to(np.median(p[forte], axis=0) if forte.any() else papel, p.shape)
    else:
        # alpha = quanto o pixel escureceu em relação ao papel; cor = tinta "desmisturada" do papel
        a = ((papel - p) / papel).max(axis=2)
        a = ((a - 0.07) / 0.86).clip(0, 1)
        if modo == "preto":
            a = np.where(croma > 60, 0, a)
        cor = (p - papel * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3)
    a = a.astype(np.float32)

    if modo == "colorido" and x1 - x0 > 3 * (y1 - y0):
        # risco comprido: tapa o buraco onde uma letra preta do original cruzava o traço
        a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((3, 25), np.uint8))
    for ex0, ey0, ex1, ey1 in apagar:
        a[ey0 + y0 - Y0:ey1 + y0 - Y0, ex0 + x0 - X0:ex1 + x0 - X0] = 0

    if corte_seco:
        a[: y0 - Y0], a[y1 - Y0:], a[:, : x0 - X0], a[:, x1 - X0:] = 0, 0, 0, 0
    else:
        traco = cv2.dilate((a > 0.15).astype(np.uint8), np.ones((5, 5), np.uint8))
        qtd, rotulo, _, centros = cv2.connectedComponentsWithStats(traco)
        manter = np.zeros(qtd, bool)
        for i in range(1, qtd):
            cx, cy = centros[i][0] + X0, centros[i][1] + Y0
            manter[i] = x0 <= cx <= x1 and y0 <= cy <= y1
        a = np.where(manter[rotulo], a, 0)

    ys, xs = np.nonzero(a > 0.02)
    if not len(ys):
        raise SystemExit("Nada de tinta nessa caixa. Confira as coordenadas.")
    t0, t1, l0, l1 = max(ys.min() - 3, 0), ys.max() + 4, max(xs.min() - 3, 0), xs.max() + 4
    rgba = np.dstack([cor.clip(0, 255), a * 255]).astype(np.uint8)[t0:t1, l0:l1]
    return Image.fromarray(rgba)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("imagem")
    ap.add_argument("x0", type=int)
    ap.add_argument("y0", type=int)
    ap.add_argument("x1", type=int)
    ap.add_argument("y1", type=int)
    ap.add_argument("saida")
    ap.add_argument("--modo", choices=["tinta", "preto", "colorido"], default="tinta")
    ap.add_argument("--apagar", action="append", default=[], help="x0,y0,x1,y1 dentro da caixa")
    ap.add_argument("--corte-seco", action="store_true")
    args = ap.parse_args()

    img = np.array(Image.open(args.imagem).convert("RGB")).astype(float)
    apagar = [tuple(int(v) for v in r.split(",")) for r in args.apagar]
    out = recorte(img, (args.x0, args.y0, args.x1, args.y1), args.modo, apagar, corte_seco=args.corte_seco)
    out.save(args.saida)
    print(f"{args.saida} ({out.width}x{out.height})")


if __name__ == "__main__":
    main()

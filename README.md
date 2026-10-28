# Carrossel Hey

Plugin do Claude Code que recria carrossel viral do Instagram com a **sua** marca. Feito por Yan Pedro ([@heyinvestidor](https://www.instagram.com/heyinvestidor/)) pros mentorados.

Você manda o link de um carrossel que bombou e o tema que quer. O Claude baixa os slides, transcreve, adapta o texto no seu tom de voz, te mostra pra aprovar e monta os slides prontos pra postar (1080×1440), com a legenda e uma sugestão de música.

## O que vem no plugin

| Skill | Como monta | Custo |
|---|---|---|
| `recriar-carrossel` | Slides em HTML com o print do Chrome (ou no Paper, se você usar). Texto 100% certo, reaproveita os desenhos do original. | Grátis |
| `recriar-carrossel-image-gen` | Cada slide gerado inteiro por IA (Gemini ou GPT Image). Bom pra carrossel com foto forte. | ~US$ 0,05 a 0,50 por slide |

Na dúvida, é a primeira. O Claude escolhe sozinho pelo seu pedido.

## Do que você precisa

- **Claude Code** (plano Pro ou Max do Claude): no app desktop do Claude (aba Code) ou no terminal.
- **Google Chrome** instalado.
- **Python 3** (o Mac já tem; no Windows, instale em [python.org](https://www.python.org/downloads/) marcando "Add to PATH").
- **Modelo:** pra montar os slides, use o modelo mais forte que o seu plano tiver (o Opus, se tiver). É trabalho visual fino: conferir posição, margem e acento slide a slide.

Opcionais (o Claude pede só quando precisar):
- **Apify** pra baixar o post pelo link. Sem ela, você manda os prints dos slides. Custa centavos por post, e o plano grátis da Apify cobre centenas por mês: [apify.com](https://apify.com).
- **OpenRouter** pra gerar foto com o seu rosto: [openrouter.ai](https://openrouter.ai).
- **Paper** pra editar os slides à mão depois: [paper.design](https://paper.design).

## Instalação (uma vez só)

Não precisa de conta no GitHub.

**1. Instale o plugin.** Dentro do Claude Code no terminal, digite um comando de cada vez:

```
/plugin marketplace add oyanpedrobrasil-ai/carrossel-hey
/plugin install carrossel-hey@hey-investidor
```

Ou direto no terminal, sem abrir o Claude Code:

```bash
claude plugin marketplace add oyanpedrobrasil-ai/carrossel-hey
```

```bash
claude plugin install carrossel-hey@hey-investidor
```

Usa só o app desktop e não tem o comando `claude` no terminal? Instale o Claude Code de terminal ([guia oficial](https://code.claude.com/docs/en/setup)), rode os dois comandos acima e pronto: o plugin aparece também na aba Code do app.

**2. Feche e abra o Claude Code** pra ele carregar o plugin.

## Como usar

Abra o Claude Code na pasta onde quer guardar os carrosséis e peça do seu jeito. Exemplos:

```
Recria esse carrossel pra mim: https://www.instagram.com/p/CODIGO/
Tema: os 5 erros de quem começa a vender pelo Instagram.
```

```
Recria esse carrossel das imagens que eu anexei, trocando o conteúdo por: [seu tema]
```

```
Recria esse carrossel e coloca uma foto minha na capa.
```

**Na primeira vez** o Claude monta o seu perfil: pergunta o seu @, o nome que vai no selo do último slide e o seu tom de voz, e pede a sua foto de perfil. Se você tiver um documento de tom de voz (de um Project do Claude ou do ChatGPT), mande junto: o texto sai muito mais com a sua cara.

**Em todo carrossel** ele vai:
1. Te perguntar o CTA (comentar uma palavra, seguir, link na bio...).
2. Te mostrar o texto novo slide a slide e perguntar "Aprovado?".
3. Montar os slides, te mostrar e perguntar "Aprovado?" de novo.

Tudo fica em `carrosseis/AAAA-MM-DD-nome/slides/`: os PNGs, a `legenda.txt` e a `musica.txt`.

## Onde ficam os seus dados

Em `~/.claude/carrossel/`, fora da pasta do plugin (assim nada some quando ele atualizar):
- `.env`: as suas chaves de API. **Nunca mande esse arquivo pra ninguém.**
- `perfil/`: o seu @, foto, fotos do rosto e tom de voz.

## Atualizar

Quando eu avisar que tem versão nova:

```bash
claude plugin marketplace update hey-investidor
```

```bash
claude plugin update carrossel-hey@hey-investidor
```

(Ou, dentro do Claude Code: `/plugin marketplace update hey-investidor`.)

## Deu problema?

- **Erro ao adicionar o marketplace:** confira se digitou `oyanpedrobrasil-ai/carrossel-hey` certinho e se o computador tem o `git` (no Mac, o terminal oferece instalar na primeira vez; no Windows, [git-scm.com](https://git-scm.com)).
- **"Não achei o Google Chrome":** instale o Chrome e peça de novo.
- **Falta biblioteca do Python:** o Claude instala sozinho. Se ele não conseguir: `pip3 install httpx python-dotenv pillow numpy opencv-python-headless`.
- **O texto saiu com cara de tradução:** mande pro Claude 2 ou 3 legendas suas e peça pra ele atualizar o seu `tom-de-voz.md`.

Qualquer outra coisa, me chama.

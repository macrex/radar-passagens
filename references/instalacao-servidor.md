# Instalação em servidor de agente (cron, headless)

Para quando a skill não roda na máquina de quem pergunta, e sim num agente hospedado que dispara
buscas sozinho — o caso do Hermes (pod Kubernetes), medido em 31/07/2026.

Na estação de trabalho nada disso é necessário: `pip install -r requirements.txt` e pronto.

## O que quebra num servidor e não quebra no desktop

| Sintoma | Causa |
|---|---|
| `ModuleNotFoundError: fast_flights` chamando `python3` | o interpretador do sistema não é o do venv; o agente não herda `VIRTUAL_ENV` |
| `BrowserType.launch: Executable doesn't exist at .../chrome-headless-shell` | job de cron roda em **sessão limpa**: sem `PLAYWRIGHT_BROWSERS_PATH`, o playwright procura o navegador no caminho do processo pai |
| funciona no teste, falha no cron | o teste foi feito com login shell, que popula `PATH`/`HOME`. Valide com `env -i` (abaixo) |

Os três somem usando `scripts/radar.sh` como única porta de entrada.

## Passos

```bash
# 1. venv com as dependências (uv, pip ou o que houver)
uv venv /opt/data/venv-radar --python 3.13
VIRTUAL_ENV=/opt/data/venv-radar uv pip install -r requirements.txt

# 2. metabusca (opcional, mas é ela que aproxima do preço real — ver "Divergência" abaixo)
VIRTUAL_ENV=/opt/data/venv-radar uv pip install playwright
PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/ms-playwright \
  /opt/data/venv-radar/bin/python -m playwright install chromium

# 3. skill no servidor (SKILL.md + scripts/ + references/)
#    e o wrapper onde o agente consegue chamar
cp scripts/radar.sh /opt/data/scripts/radar.sh && chmod 755 /opt/data/scripts/radar.sh

# 4. conferir
/opt/data/scripts/radar.sh checar_ambiente.py
```

`modo_recomendado: "completa"` ou `"completa-sem-metabusca"` = pronto para uso.

## Validação honesta (a que pega o bug do cron)

Testar com `su usuario -c` **não serve**: o login shell popula o ambiente e o erro desaparece.
Reproduza a sessão limpa do cron:

```bash
env -i PATH=/usr/local/bin:/usr/bin:/bin HOME=<home-do-agente> \
  /opt/data/scripts/radar.sh fonte_navegador.py BSB CGH 2026-09-28 --volta 2026-10-01 --site kayak
```

Voltou JSON com `preco_minimo`, a instalação está de pé. Voltou traceback, falta env — e é
exatamente o que aconteceria às 3h da manhã, sem ninguém olhando.

## Divergência entre fontes: por que a metabusca importa no servidor

Medido em 31/07/2026, BSB→CGH, ida 28/09, volta 01/10, tudo no mesmo dia:

| Fonte | Menor preço |
|---|---|
| Google Flights (requisição HTTP, sem sessão de navegador) | R$ 1.079 |
| Kayak via `fonte_navegador.py` | R$ 680 |
| Google Flights aberto no navegador do titular | R$ 639 |

O HTML devolvido à requisição do script continha apenas 1.079, 1.092, 1.186 e 1.189 — **o 639 não
estava lá**. Não é falha de parse: o Google entrega conteúdo diferente para requisição sem sessão,
e a tela do titular agrega ofertas de OTA (123Milhas, Decolar, maxmilhas, Kiwi.com...).

E não é um viés constante que dê para corrigir com fator: na janela 28/08→01/09 as duas bateram
(Google R$ 1.245 × Kayak R$ 1.248). **Por isso o servidor deve consultar as duas fontes e reportar
as duas, com o nome de cada uma ao lado do valor** — nunca fundir num número só.

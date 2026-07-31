#!/usr/bin/env bash
# radar.sh — roda os scripts desta skill em servidor de agente (cron, headless).
#
#   radar.sh <script.py> [args...]
#   radar.sh buscar_voos.py BSB CGH 2026-08-28 --volta 2026-09-01
#   radar.sh fonte_navegador.py BSB CGH 2026-08-28 --volta 2026-09-01 --site kayak
#
# Existe por dois motivos, ambos medidos em producao (Hermes, 31/07/2026):
#   - o `python3` do sistema costuma NAO ter as dependencias (elas vivem num venv);
#   - job de cron roda em sessao limpa, sem PLAYWRIGHT_BROWSERS_PATH — sem ele o
#     playwright procura o navegador no caminho do processo pai e a metabusca morre
#     com "Executable doesn't exist", mesmo com o chromium baixado.
#
# Ajuste por ambiente (defaults do servidor Hermes):
#   RADAR_VENV     python do venv com as dependencias
#   RADAR_SCRIPTS  pasta scripts/ desta skill
#   RADAR_BROWSERS cache de navegadores do playwright
#
# Instalacao passo a passo: references/instalacao-servidor.md

set -uo pipefail

VENV="${RADAR_VENV:-/opt/data/venv-radar/bin/python}"
SCRIPTS="${RADAR_SCRIPTS:-/opt/data/skills/radar-passagens/scripts}"
export PLAYWRIGHT_BROWSERS_PATH="${RADAR_BROWSERS:-$HOME/.cache/ms-playwright}"

[ -x "$VENV" ] || {
  echo "ERRO: python do venv nao encontrado em $VENV" >&2
  echo "      crie com: uv venv <venv> && VIRTUAL_ENV=<venv> uv pip install -r requirements.txt" >&2
  echo "      ou aponte outro caminho em RADAR_VENV" >&2
  exit 1
}

SCRIPT="${1:-}"
[ -n "$SCRIPT" ] || {
  echo "uso: radar.sh <script.py> [args...]" >&2
  ls "$SCRIPTS" 2>/dev/null >&2
  exit 2
}
shift

[ -f "$SCRIPTS/$SCRIPT" ] || {
  echo "ERRO: $SCRIPT nao existe em $SCRIPTS (ajuste RADAR_SCRIPTS)" >&2
  ls "$SCRIPTS" 2>/dev/null >&2
  exit 2
}

exec "$VENV" "$SCRIPTS/$SCRIPT" "$@"

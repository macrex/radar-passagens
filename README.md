# Radar de Passagens

Assistente de busca e comparação de passagens aéreas: preços **reais** do Google Flights e de metabusca, links de compra prontos (1 clique) e estratégia de preço mínimo — melhores dias pra voar, aeroportos alternativos e o momento certo de comprar.

Vem em **duas versões da mesma coisa**. O agente escolhe sozinho pela regra abaixo.

| | Versão **completa** | Versão **lite** |
|---|---|---|
| Onde roda | Agentes que executam código (Claude Code, Cursor, CLIs com shell) | Qualquer chat: Gemini (Gems), ChatGPT (GPTs), Claude Projects, Copilot |
| Arquivos | `SKILL.md` + `scripts/` + `references/` | `lite/INSTRUCOES.md` + `lite/conhecimento.md` |
| Preços | Scripts consultam Google Flights, Kayak/Skyscanner e cache Aviasales | Busca da própria plataforma + links do Google Flights |
| Validação | 8 regras automáticas (`validar_voos.py`), exit 1 se falhar | Checklist de sanidade aplicado pelo agente |
| Requisitos | Python 3, `fast-flights`, Playwright + Chrome | Nenhum |

### Regra de seleção

1. O agente consegue executar código? → **versão completa**. Teste: `python3 scripts/buscar_voos.py --help`.
2. Não consegue, ou os scripts falham (dependência/rede)? → **versão lite**, avisando o usuário que está em modo lite.

Nunca misturar: ou o relatório sai dos scripts, ou sai pelo protocolo da lite.

## Instalação

**Completa** — clone dentro da pasta de skills do seu agente (ex.: `~/.claude/skills/radar-passagens`) e instale as dependências:

```bash
pip install fast-flights typing_extensions requests playwright
python -m playwright install chromium   # e tenha o Google Chrome instalado
```

### Token opcional (fonte extra Aviasales)

A 4ª fonte (cache de preços da Aviasales) é **opcional** — sem ela tudo funciona, o agente só avisa que a fonte está desativada. Para habilitar:

1. Crie conta grátis em [travelpayouts.com](https://www.travelpayouts.com) → **Profile** → **API token**.
2. Guarde o token como **variável de ambiente** `TRAVELPAYOUTS_TOKEN` (nunca dentro de arquivo do repositório):

```bash
# Windows (PowerShell) — permanente, reabra o terminal depois
setx TRAVELPAYOUTS_TOKEN "seu_token_aqui"

# Linux / macOS — permanente
echo 'export TRAVELPAYOUTS_TOKEN="seu_token_aqui"' >> ~/.bashrc && source ~/.bashrc

# só na sessão atual
export TRAVELPAYOUTS_TOKEN="seu_token_aqui"    # bash/zsh
$env:TRAVELPAYOUTS_TOKEN = "seu_token_aqui"     # PowerShell
```

3. Confira: `python3 scripts/fonte_aviasales.py BSB CGH 2026-08-28` — se responder "TRAVELPAYOUTS_TOKEN ausente", o terminal ainda não enxerga a variável (reabra-o).

Opcional: `TRAVELPAYOUTS_MARKER` (id de afiliado) pelo mesmo caminho. Nunca coloque o token em `SKILL.md`, nos scripts ou em commit.

**Lite** — no Gemini: Gems → novo Gem → cole `lite/INSTRUCOES.md` nas instruções e anexe `lite/conhecimento.md` como conhecimento. Em GPTs/Projects o processo é análogo.

Teste: `passagem BSB para CGH, ida 28/08 volta 01/09`.

## O que ele faz

- **Busca pontual**: ida ou ida+volta, tabela enxuta com horários, escalas (espera por conexão), duração total, preço e link por companhia.
- **Melhor período**: amostragem de datas reais (mínimo 5 por mês) e ranking do período; ano inteiro tem protocolo próprio (1 consulta por mês → +5 no melhor mês).
- **Estratégia de economia**: dias da semana que fogem do caro, comparação dos aeroportos da região e quando comprar (com alerta de preço).
- **Multi-fonte** (completa): Google Flights ao vivo, metabusca Kayak/Skyscanner (tarifas de OTA, costumam ficar abaixo) e cache Aviasales; divergência alta vira alerta.
- **Dados reais sempre**: proibido estimar, extrapolar ou reaproveitar consulta antiga; prévia de calendário é triagem, nunca preço.

## Limitações

- Preços são "a partir de" e mudam a toda hora — a confirmação é no checkout da companhia ou do vendedor.
- Tarifa de metabusca é de OTA: regras de bagagem e cancelamento podem diferir da tarifa da companhia.
- Não compra nem automatiza checkout; só pesquisa, compara e entrega links.
- Calibrado para pt-BR e BRL por padrão (ajustável a pedido).

## Licença

[MIT](LICENSE).

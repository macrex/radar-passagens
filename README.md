# Radar de Passagens

Assistente de busca e comparação de passagens aéreas para agentes de IA. Preços **reais**, links de compra a 1 clique e estratégia de preço mínimo: melhores dias pra voar, aeroportos alternativos e o momento certo de comprar.

Duas versões da mesma coisa no mesmo repositório — o agente escolhe sozinho pela regra abaixo.

| | **Completa** | **Lite** |
|---|---|---|
| Onde roda | Agentes que executam código (Claude Code, Cursor, CLIs com shell) | Qualquer chat: Gemini (Gems), ChatGPT (GPTs), Claude Projects, Copilot |
| Arquivos | `SKILL.md` + `scripts/` + `references/` | `lite/INSTRUCOES.md` + `lite/conhecimento.md` |
| Preços | Scripts consultam Google Flights, Kayak/Skyscanner e cache Aviasales | Busca da própria plataforma + links do Google Flights |
| Validação | 8 regras automáticas (`validar_voos.py`), sai com erro se falhar | Checklist de sanidade aplicado pelo agente |
| Requisitos | Python 3 + dependências abaixo | Nenhum |

### Regra de seleção

1. O agente consegue executar código? Teste: `python3 scripts/buscar_voos.py --help` → **versão completa**.
2. Não consegue, ou os scripts falham por dependência/rede → **versão lite**, avisando o usuário que está em modo lite.

Nunca misturar as duas no mesmo relatório: ou os números vêm dos scripts, ou vêm do protocolo da lite.

## Instalação — versão completa

```bash
git clone https://github.com/macrex/radar-passagens.git
cd radar-passagens
pip install fast-flights typing_extensions requests playwright
python -m playwright install chromium
```

A metabusca (Kayak/Skyscanner) exige **Google Chrome instalado**: o anti-bot desses sites barra o Chromium empacotado do Playwright, mas aceita o Chrome real — inclusive em modo headless.

Para expor como skill do seu agente, aponte a pasta de skills para o clone (ex.: symlink em `~/.claude/skills/radar-passagens`) ou passe o caminho do repo ao agente.

## Instalação — versão lite

No Gemini: **Gems** → novo Gem → cole `lite/INSTRUCOES.md` no campo de instruções e anexe `lite/conhecimento.md` como arquivo de conhecimento. Em GPTs (Instructions + Knowledge) e Claude Projects o processo é análogo.

Teste em qualquer versão: `passagem BSB para CGH, ida 28/08 volta 01/09`.

## Token opcional (fonte Aviasales)

A fonte de cache da Aviasales é **opcional** — sem ela tudo funciona e o agente apenas avisa que está desativada.

1. Conta grátis em [travelpayouts.com](https://www.travelpayouts.com) → **Profile** → **API token**.
2. Guarde o token numa **variável de ambiente** (nunca em arquivo do repositório):

```bash
# Windows (PowerShell) — permanente; reabra o terminal depois
setx TRAVELPAYOUTS_TOKEN "seu_token_aqui"

# Linux / macOS — permanente
echo 'export TRAVELPAYOUTS_TOKEN="seu_token_aqui"' >> ~/.bashrc && source ~/.bashrc

# só na sessão atual
export TRAVELPAYOUTS_TOKEN="seu_token_aqui"    # bash/zsh
$env:TRAVELPAYOUTS_TOKEN = "seu_token_aqui"     # PowerShell
```

3. Confira: `python3 scripts/fonte_aviasales.py BSB CGH 2026-08-28`. Se responder `TRAVELPAYOUTS_TOKEN ausente`, o terminal ainda não enxerga a variável — reabra-o.

Opcional: `TRAVELPAYOUTS_MARKER` (id de afiliado) pelo mesmo caminho.

## O que ele faz

- **Busca pontual** — ida ou ida+volta: tabela enxuta com horários, escalas (espera de cada conexão), duração total, preço e link por companhia.
- **Melhor período** — amostragem de datas **reais**: mínimo 5 por mês do período pedido, com ranking e oferta de ampliar a amostra.
- **Ano inteiro** — protocolo próprio: ≥1 consulta real por mês (12) → ranqueia os meses pelos valores reais → +5 consultas no mês vencedor.
- **Estratégia de economia** — o mapa: dias da semana que fogem do caro, comparação dos aeroportos da região e quando comprar (com alerta de preço).
- **Multi-fonte** (completa) — Google Flights ao vivo, metabusca Kayak/Skyscanner e cache Aviasales, com a fonte de cada valor e alerta quando divergem.
- **Dados reais sempre** — proibido estimar, extrapolar ou reaproveitar consulta antiga; prévia de calendário é triagem, nunca preço.

## Scripts (versão completa)

| Script | Faz |
|---|---|
| `buscar_voos.py` | Voos + preço mínimo geral e por companhia, duração total e espera por escala (JSON) |
| `melhor_periodo.py` | Varre uma janela de datas e ranqueia os períodos; `--amostra N` consulta só N datas espalhadas |
| `validar_voos.py` | 8 regras de sanidade (rota, datas, companhias, faixa de preço, anti-stale, consistência) |
| `fonte_navegador.py` | Metabusca Kayak/Skyscanner via Chrome real (Playwright) — preços de OTA, costumam ficar abaixo do Google |
| `fonte_aviasales.py` | Cache de preços da Aviasales (requer token) |
| `aeroportos.py` | Resolve cidade → aeroportos, marcando as cidades que exigem escolha |
| `spike_aviasales.py` | Mede a cobertura do cache Aviasales em rotas BR (rodar uma vez após obter o token) |

Todas as fontes extras são **fail-open**: se falharem, a busca principal segue e o agente avisa.

## Limitações

- Preços são "a partir de" e mudam a toda hora — a confirmação é sempre no checkout da companhia ou do vendedor.
- Tarifa de metabusca é de OTA: regras de bagagem e cancelamento podem diferir da tarifa vendida pela companhia.
- Skyscanner costuma bloquear a automação mesmo com Chrome real; Kayak responde normalmente.
- Não compra nem automatiza checkout — só pesquisa, compara e entrega links.
- Calibrado para pt-BR e BRL por padrão (ajustável a pedido do usuário).

## Licença

[MIT](LICENSE).

---
name: radar-passagens
description: >
  Busca e compara passagens aéreas com preços reais do Google Flights e acha
  o melhor período para voar. Use quando mencionar: passagem aérea, voo,
  preço de voo, melhor data para viajar, ida e volta, LATAM, GOL, Azul,
  Google Flights, ou rotas por código de aeroporto (BSB, CGH, GRU...).
metadata:
  version: "7"
---

# Radar de Passagens — busca, comparação e melhor período

## Qual versão usar (checar ANTES de tudo)

Duas versões no repo. A escolha é simples: **com shell + Python → completa; sem → lite**.

1. Rode `python3 <PASTA_DESTA_SKILL>/scripts/checar_ambiente.py` — use o caminho
   ABSOLUTO da pasta da skill (o cwd é o projeto do usuário, não a pasta da skill).
2. `modo_recomendado: "completa"` ou `"completa-sem-metabusca"` → siga esta versão.
   Metabusca/playwright ausente NÃO é motivo de lite — a 3ª fonte é opcional e fail-open.
3. `"instalar-dependencias"` → tente UMA vez o `comando_install` do JSON (se der
   "externally-managed-environment", acrescente `--break-system-packages` ou use venv)
   e recheque.
4. Só use a **versão LITE** (`lite/INSTRUCOES.md` + `lite/conhecimento.md`) se não houver
   como executar código, ou se a instalação falhar — avisando o usuário que está no modo
   lite (preços de busca, não de script) e entregando o `comando_install` para ele
   habilitar a completa depois.

Nunca misture: ou reporta com dados dos scripts, ou reporta pelo protocolo da lite.
Nesta versão, NÃO leia os arquivos de `lite/` — eles são o empacotamento para
plataformas sem código (Gems/GPTs), não material desta versão.

Fonte: Google Flights via lib `fast-flights` (sem chave de API). Dependências:
`pip install -r <pasta-da-skill>/requirements.txt`; metabusca (3ª fonte): o mesmo com
`-r requirements-extra.txt`, mais `python -m playwright install chromium` e **Google
Chrome instalado** (o Chromium do Playwright é barrado pelo anti-bot). **Token opcional**
(2ª fonte): se `TRAVELPAYOUTS_TOKEN` existir no ambiente, a fonte Aviasales ativa; senão
avise que está desativada — setup completo no README §Token opcional.

## Scripts (sempre por caminho absoluto: `<pasta-da-skill>/scripts/<nome>.py`)

| Script | Faz | Exemplo |
|---|---|---|
| `checar_ambiente.py` | Diagnóstico do ambiente / teste de seleção da skill: deps, token, `modo_recomendado`, `comando_install` (JSON; exit 0 sempre) | `checar_ambiente.py` |
| `aeroportos.py` | Resolve cidade → aeroportos (cidade antes de IATA: "rio" → SDU/GIG); cidade multi devolve `candidatas` e exige escolha | `aeroportos.py "são paulo"` |
| `buscar_voos.py` | Voos + preço mínimo geral e por cia, tempo total, espera por escala, `consultado_em` (JSON) | `buscar_voos.py BSB CGH 2026-08-28 --volta 2026-09-01 [--max-paradas 1] [--ordenar preco\|tempo\|escalas]` |
| `melhor_periodo.py` | Varre janela de datas e ranqueia os períodos mais baratos; `--amostra N` = só N datas espalhadas (períodos grandes/ano); `--paralelo N` = consultas simultâneas (default 6) | `melhor_periodo.py BSB CGH --inicio 2026-08-20 --fim 2026-09-10 --duracao 4 [--amostra 5] [--paralelo 6]` |
| `validar_voos.py` | 8 regras de sanidade sobre um JSON já salvo (`--json`), sem nova consulta | `validar_voos.py BSB CGH 2026-08-28 --volta 2026-09-01 --json /tmp/rp_voos.json --cias-esperadas LATAM,Gol,Azul --preco-min 150 --preco-max 5000` |
| `fonte_aviasales.py` | 2ª fonte: cache Aviasales (Travelpayouts) — ESTIMATIVAS com tarifas de OTAs; mesma interface do buscar_voos | `fonte_aviasales.py BSB CGH 2026-08-28 --volta 2026-09-01` |
| `fonte_navegador.py` | 3ª fonte: Kayak/Skyscanner via Chrome real (Playwright) — preços REAIS de metabusca (tarifas de OTAs), costumam ficar abaixo do Google; ~30s | `fonte_navegador.py BSB CGH 2026-08-28 --volta 2026-09-01 [--site kayak\|skyscanner\|todos]` |
| `spike_aviasales.py` | Gate go/no-go: mede cobertura do cache em rotas BR (rodar 1x após obter o token) | `spike_aviasales.py [--mes 2026-09]` |

Exit codes: 0 ok · 1 regra reprovada · 2 erro de uso · 3 falha de consulta · 4 sem resultados.

## Fluxo padrão

0. **Cidade com vários aeroportos** (São Paulo, Rio, BH, NY, Londres...): antes de
   pesquisar, rode `aeroportos.py "<cidade>"` e apresente as `candidatas` (cada uma com a
   observação de distância/perfil + a opção **"todos"**) via AskUserQuestion (ou pergunta
   em texto, se a ferramenta não existir). Só pesquise depois da escolha. "Todos" =
   códigos separados por vírgula (ex.: `CGH,GRU,VCP`).
1. Busca pontual → `buscar_voos.py` (ida ou ida+volta; aceita destino múltiplo com vírgulas).
   **Comparador multi-fonte EM PARALELO** (fail-open — nenhuma fonte quebra a principal).
   Os sites são independentes: dispare as 3 fontes juntas em background no MESMO comando
   e a espera total vira a da mais lenta (~30s), não a soma:
   ```bash
   S=<pasta-da-skill>/scripts; A="BSB CGH 2026-08-28 --volta 2026-09-01"
   python3 $S/buscar_voos.py $A     > /tmp/rp_google.json 2>/tmp/rp_google.err &
   python3 $S/fonte_navegador.py $A > /tmp/rp_kayak.json  2>/tmp/rp_kayak.err &
   [ -n "$TRAVELPAYOUTS_TOKEN" ] && python3 $S/fonte_aviasales.py $A > /tmp/rp_avia.json 2>/tmp/rp_avia.err &
   wait
   ```
   Sem token, avise que a 2ª fonte está desativada. 3ª fonte: Kayak (`--site todos` inclui
   Skyscanner, que costuma bloquear) — tarifas de OTA, frequentemente **abaixo** do Google;
   pule-a em varredura de período. Em host com subagentes paralelos, cada fonte pode ir em
   um subagente disparado na mesma rodada — mas o `&`+`wait` acima resolve com custo zero.
2. Datas flexíveis → `melhor_periodo.py`, que já consulta **6 datas em paralelo**
   (`--paralelo N` ajusta; medido: 12 datas em 8s contra 63s no modo sequencial). Delegue
   ao subagente `passagens-buscador` para não poluir o contexto. **Período (mês ou meses)**:
   mínimo **5 datas reais POR MÊS** — `--amostra 5` uma vez por mês (janela = o mês);
   meses diferentes também podem rodar simultâneos (`&`+`wait`). Resposta vazia sob carga é
   rate limit e o `buscar_voos.py` já repete com backoff — paralelismo alto custa tempo, não
   qualidade do dado. Ao entregar, SEMPRE ofereça ampliar a amostra. **Ano inteiro**: (1) `--amostra 12` na janela do ano (≥1 consulta real/mês);
   (2) ranquear os meses pelos valores REAIS (sazonalidade só desempata); (3) no melhor mês,
   `--amostra 5`; (4) reportar mês vencedor + amostra. Nunca reportar mês "bom" sem consulta
   real nele.
3. **Sempre validar** antes de reportar preços — sobre exatamente o JSON que vira o
   relatório, sem nova consulta:
   ```bash
   python3 <pasta-da-skill>/scripts/buscar_voos.py BSB CGH 2026-08-28 --volta 2026-09-01 > /tmp/rp_voos.json
   python3 <pasta-da-skill>/scripts/validar_voos.py BSB CGH 2026-08-28 --volta 2026-09-01 --json /tmp/rp_voos.json --cias-esperadas LATAM,Gol,Azul --preco-min 150 --preco-max 5000
   ```
   `--cias-esperadas` é o conjunto **FIXO** da rota (doméstico BR: `LATAM,Gol,Azul`) —
   NUNCA as cias que a própria busca retornou (torna R4 tautológico). `--preco-min/-max`
   vêm da faixa da rota em `references/fontes.md`. Em varredura, valide a data VENCEDORA.
   Triagem: **R1/R2/R5 reprovados = NÃO reportar preços**; **R3/R4/R6/R7/R8 reprovados =
   reportar com alerta explícito** (R7/R8 só rodam com `--anti-stale`).
4. Reporte **bem resumido, só o essencial**: cabeçalho de 1 linha (rota, datas, hora da
   consulta = `consultado_em`), melhor preço em destaque, tabela enxuta (3–6 linhas: a mais
   barata + competitivas até ~15%) com ⭐ na recomendação — sem prosa, sem explicar processo.
   Colunas: cia, horário, escalas com a espera de CADA conexão (`escalas`: aeroporto +
   `espera_min`), **tempo total** (`duracao_total_min`), preço e o **`link_compra` de cada
   voo listado** (1 clique da compra); além do mínimo por cia e por aeroporto (se "todos").
   **Ida e volta**: pequena tabela de VOLTA (`voos_volta`: horários, tempo, esperas) — o
   preço total do RT já está na lista de ida (`nota_volta` explica) e o de `voos_volta` é
   ida avulsa, só referência. **Priorização**: menos escalas e, no empate, menor espera
   total (`--ordenar escalas` já ranqueia) entre os competitivos — mas sempre mostre o
   mais barato, mesmo que perca no critério.
5. **Comparação entre fontes** (quando 2ª/3ª rodarem): tabela com coluna **Fonte** — Google
   (ao vivo) · Kayak/Skyscanner (ao vivo, tarifa de OTA) · Aviasales ("estimativa, vista em
   `visto_em`"). Cache nunca é a recomendação sozinho; metabusca abaixo do Google =
   oportunidade real, mas rotule "tarifa de OTA — confirmar no site do vendedor"
   (bagagem/cancelamento podem diferir). **Divergência entre fontes ou entre duas leituras
   da mesma rota >30% = alerta; >50% = alerta destacado** (dado provavelmente stale). A
   validação R1–R8 cobre só a fonte Google.

## Estratégia de preço mínimo

Gatilhos: pedido de estratégia/economia ("pagar o mínimo", "quando comprar", "melhores
dias"), mês sem data fechada. Passos: (a) região multi-aeroporto → usar "todos" direto
(comparar é parte da estratégia; só informe); (b) `melhor_periodo.py` na janela do período
(delegar se for grande); (c) ler `estatisticas` + `por_dia_semana` e montar o mapa;
(d) sinal ≤p25 = comprar, p25–mediana = bom preço, >mediana = esperar; (e) recomendar o
alerta de preço ("Acompanhar preços") no link da rota. Formato do mapa e heurísticas:
`references/estrategia-compra.md`.

## Regra dura (dados reais) e gotchas

- Todo preço reportado vem de execução dos scripts AGORA. PROIBIDO estimar, extrapolar, reaproveitar consulta antiga ou completar lacuna com valor "típico". Script falhou/sem dado → dizer isso e entregar o link da rota.
- Prévia de calendário/meses do Google Flights (site) é estimativa em cache — serve só de triagem; o valor reportado vem sempre da consulta direta da data (os scripts já fazem isso).
- **Ida e volta**: o Google lista opções de IDA com o preço TOTAL do round-trip; a volta é escolhida no site. O JSON reflete isso.
- Preços são "a partir de" (tarifa mais barata do dia) e mudam com frequência — **sempre dizer a data/hora da consulta** (`consultado_em`); o valor final se confirma no checkout.
- Preço igual em todos os voos do dia é comum em rotas-ponte (ex.: BSB↔CGH) — não é bug; o validador R7 confirma variação entre datas.
- Com proxy TLS o cliente nativo (primp) falha; os scripts caem para `requests` (respeita `HTTPS_PROXY`/CA bundle).
- Não automatize compra/checkout — a skill só pesquisa e compara.
- Fallbacks (se o parse do Google quebrar) e faixas de sanidade por rota: `references/fontes.md`.

## Delegação

Varredura de período, ano inteiro, múltiplas rotas ou múltiplos aeroportos: delegue
ao subagente `passagens-buscador` (definição em `.claude/agents/passagens-buscador.md`;
instale com `cp` para `~/.claude/agents/` — ver README). Passe rota(s) por IATA já
resolvidas, datas/janela, flexibilidade e o CAMINHO ABSOLUTO deste repo. Ele roda os
scripts, valida e devolve só o resumo ranqueado com links — os JSONs brutos ficam fora
do contexto principal.

Se o subagente não estiver instalado no ambiente, delegue a um subagente de uso geral
com as mesmas instruções (o arquivo do agente serve de prompt). Busca de UMA data e UMA
rota: rode direto, sem delegar — a tabela detalhada vale mais que o resumo.

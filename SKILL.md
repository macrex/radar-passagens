---
name: radar-passagens
description: >
  Busca e compara passagens aéreas com preços reais do Google Flights e acha
  o melhor período para voar. Use quando mencionar: passagem aérea, voo,
  preço de voo, melhor data para viajar, ida e volta, LATAM, GOL, Azul,
  Google Flights, ou rotas por código de aeroporto (BSB, CGH, GRU...).
---

# Radar de Passagens — busca, comparação e melhor período

# Versao: 6

## Qual versão usar (checar ANTES de tudo)

Este repo tem duas versões do mesmo assistente. Escolha assim:

1. **Consegue executar código?** (tem ferramenta de shell/Bash, Python 3 disponível
   e permissão para rodar script) → use **esta versão COMPLETA**: os scripts abaixo
   trazem preço real do Google Flights e de metabusca, com validação automática.
2. **Não consegue** (Gems, GPTs, chat sem execução de código) ou os scripts falham
   por falta de dependência/rede → use a **versão LITE**: `lite/INSTRUCOES.md` +
   `lite/conhecimento.md`, que fazem o mesmo trabalho só com busca e links.

Teste rápido antes de decidir: rode `python3 scripts/buscar_voos.py --help`. Funcionou
→ versão completa. Erro de execução/import → siga a lite e avise o usuário que está
no modo lite (preços de busca, não de script).

Nunca misture: ou reporta com dados dos scripts, ou reporta pelo protocolo da lite.

Fonte: Google Flights via lib `fast-flights` (sem chave de API).
Dependências: `pip install fast-flights typing_extensions requests`.
3ª fonte (metabusca): `pip install playwright && python -m playwright install chromium`
— exige **Google Chrome instalado** (o Chromium do Playwright é barrado pelo anti-bot).

**Token opcional** (fonte Aviasales): variável de ambiente `TRAVELPAYOUTS_TOKEN`
(token grátis em travelpayouts.com → Profile → API token). Windows:
`setx TRAVELPAYOUTS_TOKEN "<token>"`; Linux/macOS: `export TRAVELPAYOUTS_TOKEN="<token>"`
no `~/.bashrc`. Sem token a fonte fica desativada e o resto funciona normal — avise o
usuário desse caminho quando ele perguntar como habilitar. NUNCA escreva o token em
arquivo do repo.

## Scripts (rodar da pasta da skill ou por caminho absoluto)

| Script | Faz | Exemplo |
|---|---|---|
| `scripts/buscar_voos.py` | Lista voos + preço mínimo geral e por cia, tempo total e espera por escala (JSON) | `buscar_voos.py BSB CGH 2026-08-28 --volta 2026-09-01 [--max-paradas 1] [--ordenar preco\|tempo\|escalas]` |
| `scripts/melhor_periodo.py` | Varre janela de datas e ranqueia os períodos mais baratos; `--amostra N` = só N datas espalhadas (períodos grandes/ano) | `melhor_periodo.py BSB CGH --inicio 2026-08-20 --fim 2026-09-10 --duracao 4 [--amostra 5]` |
| `scripts/validar_voos.py` | 8 regras de sanidade (rota, datas, cias, faixa de preço, anti-stale, consistência); exit 1 se falhar | `validar_voos.py BSB CGH 2026-08-28 --volta 2026-09-01 --cias-esperadas LATAM,Gol,Azul` |
| `scripts/fonte_aviasales.py` | 2ª fonte: cache Aviasales (Travelpayouts) — ESTIMATIVAS com tarifas de OTAs; mesma interface do buscar_voos | `fonte_aviasales.py BSB CGH 2026-08-28 --volta 2026-09-01` |
| `scripts/fonte_navegador.py` | 3ª fonte: Kayak/Skyscanner via Chrome real (Playwright) — preços REAIS de metabusca (tarifas de OTAs), costumam ficar abaixo do Google; ~30s | `fonte_navegador.py BSB CGH 2026-08-28 --volta 2026-09-01 [--site kayak\|skyscanner\|todos]` |
| `scripts/spike_aviasales.py` | Gate go/no-go: mede cobertura do cache em rotas BR (rodar 1x após obter o token) | `spike_aviasales.py [--mes 2026-09]` |

## Fluxo padrão

0. **Cidade com vários aeroportos** (São Paulo, Rio, BH, NY, Londres...): antes de
   pesquisar, rode `scripts/aeroportos.py "<cidade>"` e apresente as opções ao
   usuário (cada aeroporto com a observação de distância/perfil + a opção
   **"todos"**) via AskUserQuestion. Só pesquise depois da escolha. "Todos" =
   passar os códigos separados por vírgula (ex.: `CGH,GRU,VCP`).
1. Busca pontual → `buscar_voos.py` (ida ou ida+volta; aceita destino múltiplo com vírgulas).
   **Comparador multi-fonte** (todas fail-open — nunca quebram a busca principal):
   - 2ª fonte: se `TRAVELPAYOUTS_TOKEN` existir no ambiente, rode `fonte_aviasales.py`
     com os mesmos argumentos. Sem token, avise que está desativada.
   - 3ª fonte: rode `fonte_navegador.py` (Kayak; `--site todos` inclui Skyscanner,
     que costuma bloquear). Preços REAIS de metabusca com tarifas de OTAs —
     frequentemente **abaixo** do Google. Pule em varredura de período (~30s/consulta).
2. Usuário flexível de datas → `melhor_periodo.py` (janelas grandes demoram ~2s/dia; delegue ao agent `passagens-buscador` para não poluir o contexto).
   - **Período (mês ou meses)**: amostragem mínima de **5 datas reais POR MÊS** —
     rodar `melhor_periodo.py --amostra 5` uma vez por mês do período (janela =
     o mês). Ao entregar, SEMPRE perguntar se o usuário quer ampliar a amostra.
   - **Ano inteiro**: (1) `--amostra 12` na janela do ano (≥1 consulta real/mês);
     (2) ranquear os meses pelos valores REAIS (sazonalidade só desempata);
     (3) no melhor mês, `--amostra 5`; (4) reportar mês vencedor + amostra
     detalhada. Nunca reportar mês "bom" sem consulta real nele.
3. **Sempre validar** antes de reportar preços: `validar_voos.py` com as cias esperadas da rota. Só apresente valores se as regras passarem.
4. Reporte **bem resumido, só o essencial**: cabeçalho de 1 linha (rota, datas,
   data/hora da consulta), melhor preço em destaque, tabela enxuta (3–6 linhas:
   mais barata + competitivas até ~15%) com ⭐ na recomendação, links — sem
   prosa longa, sem explicar processo. Conteúdo: preço mínimo geral, mínimo por cia (e por aeroporto se "todos"),
   melhores horários, **coluna de tempo total de viagem** (`duracao_total_min`),
   e **o `link_compra` de cada voo listado** (URL do Google Flights já filtrada
   pela cia — 1 clique da compra). O preço final se confirma no checkout da
   companhia.
   - **Voo com escala**: mostrar a espera de CADA conexão na própria linha/
     célula (campo `escalas`: aeroporto + `espera_min`), não só o total.
   - **Ida e volta**: incluir uma **pequena tabela com as opções de VOLTA**
     (campo `voos_volta`: horários, tempo total, esperas por conexão). O preço
     total do RT já está na lista de ida (`nota_volta` explica); o preço em
     `voos_volta` é de ida avulsa — cite como referência, não como valor do RT.
5. **Voos com escala — priorização**: prefira sempre menos escalas e, entre
   voos com o mesmo nº de escalas, a menor espera total (`--ordenar escalas`
   já ranqueia assim). Ao recomendar, aplique essa ordem entre os voos de
   preço competitivo (até ~15% acima do mínimo) — e sempre mostre o mais
   barato, mesmo que perca no critério de escalas.
6. **Comparação entre fontes** (quando 2ª/3ª rodarem): tabela com coluna
   **Fonte** — Google (ao vivo) · Kayak/Skyscanner (ao vivo, tarifa de OTA) ·
   Aviasales ("estimativa, vista em `visto_em`"). Preço de cache nunca é a
   recomendação sozinho. Metabusca mais barata que o Google = oportunidade real,
   mas rotule "tarifa de OTA — confirmar no site do vendedor" (regras de bagagem/
   cancelamento podem diferir). Divergência >40% entre fontes = alerta destacado.
   A validação R1–R8 do `validar_voos.py` cobre só a fonte Google.

## Estratégia de preço mínimo

Gatilhos: pedido de estratégia/economia ("pagar o mínimo", "quando comprar",
"melhores dias"), mês sem data fechada.

Passos:
a. Região com vários aeroportos → usar "todos" direto (comparação é parte da
   estratégia — não perguntar aeroporto a um a um; só informar que vai comparar).
b. `melhor_periodo.py` na janela do mês/período (delegar ao agent
   `passagens-buscador` se a janela for grande).
c. Ler `estatisticas` + `por_dia_semana` do JSON e montar o mapa.
d. Sinal de compra pelo p25/mediana (heurísticas canônicas).
e. Recomendar ativar o alerta de preço ("Acompanhar preços") no link da rota.

Heurísticas e formato do mapa: `references/estrategia-compra.md`.

## Dados reais (regra dura)

- Todo preço reportado vem de execução dos scripts AGORA. PROIBIDO: estimar,
  extrapolar, reaproveitar consulta antiga, completar lacuna com valor "típico".
- Script falhou/sem dado → dizer explicitamente e entregar o link da rota;
  nunca preencher com estimativa.
- Prévia de calendário/meses do Google Flights (site) é estimativa/cache — os
  valores mudam na pesquisa de fato. Serve só de triagem; preço reportado é
  sempre o da consulta direta da data (os scripts já fazem isso).

## Semântica e gotchas

- **Ida e volta**: o Google lista opções de IDA com o preço TOTAL do round-trip; a volta é escolhida no site. O JSON reflete isso.
- Preços são "a partir de" (tarifa mais barata do dia) e mudam com frequência — **sempre dizer a data/hora da consulta** e que o valor final se confirma no checkout da companhia.
- Preço igual em todos os voos do dia é comum em rotas-ponte (ex.: BSB↔CGH) — não é bug; o validador R7 confirma variação entre datas.
- Em ambiente com proxy TLS o cliente nativo (primp) falha; os scripts caem automaticamente para `requests` (respeita `HTTPS_PROXY`/CA bundle).
- Não automatize compra/checkout — a skill só pesquisa e compara.
- Fallbacks (se o parse do Google quebrar) e faixas de sanidade por rota: `references/fontes.md`.

## Delegação

Buscas com varredura de período ou múltiplas rotas: delegue ao agent
`passagens-buscador` (definição em `agents/passagens-buscador.md` — copie para a
pasta de agents do seu ambiente, ex.: `~/.claude/agents/`) passando rota(s),
datas/janela, flexibilidade e o caminho do repo; ele roda os scripts, valida e
devolve só o resumo ranqueado, mantendo as consultas brutas fora do contexto.

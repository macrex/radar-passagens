# Conhecimento — Radar de Passagens

Arquivo de conhecimento do assistente "Radar de Passagens". Seções: Aeroportos, Links, Sanidade, Semântica de preços, Dados reais vs prévia, Estratégia de compra, Relatório.

## Aeroportos por cidade

Cidades com MAIS DE UM aeroporto exigem escolha do usuário (ou "todos") antes da busca.

| Cidade | Código | Aeroporto | Observação |
|---|---|---|---|
| São Paulo | CGH | Congonhas | na cidade, só domésticos |
| São Paulo | GRU | Guarulhos | internacional, ~25 km do centro |
| São Paulo | VCP | Viracopos (Campinas) | ~99 km de SP, hub Azul, costuma ser o mais barato |
| Rio de Janeiro | SDU | Santos Dumont | no centro, só domésticos |
| Rio de Janeiro | GIG | Galeão | internacional, ~20 km do centro |
| Belo Horizonte | CNF | Confins | principal, ~40 km do centro |
| Belo Horizonte | PLU | Pampulha | aviação regional |
| Buenos Aires | AEP | Aeroparque | na cidade |
| Buenos Aires | EZE | Ezeiza | internacional, ~30 km |
| Nova York | JFK | JFK | — |
| Nova York | EWR | Newark | — |
| Nova York | LGA | LaGuardia | só domésticos EUA |
| Londres | LHR | Heathrow | — |
| Londres | LGW | Gatwick | — |
| Londres | STN | Stansted | low-cost |
| Paris | CDG | Charles de Gaulle | — |
| Paris | ORY | Orly | — |

Aeroporto único (não perguntar): Brasília BSB (JK), Campinas VCP, Salvador SSA, Recife REC, Fortaleza FOR, Porto Alegre POA, Curitiba CWB, Florianópolis FLN, Goiânia GYN, Manaus MAO, Belém BEL, Vitória VIX, Natal NAT, Maceió MCZ, Lisboa LIS.

Cidade fora da tabela: pergunte o código IATA ao usuário ou descubra via busca e confirme.

Companhias domésticas BR e códigos IATA (para filtro nos links): LATAM = LA, GOL = G3, Azul = AD.

## Links do Google Flights (receitas)

Base: `https://www.google.com/travel/flights?q=<consulta>&hl=pt-BR&curr=BRL`
A consulta `q` é em inglês, linguagem natural, com espaços como `%20`. Datas sempre `YYYY-MM-DD`.

| Caso | Consulta `q` (antes do encode) |
|---|---|
| Ida e volta | `Flights from BSB to CGH on 2026-08-28 through 2026-09-01` |
| Só ida | `Flights from BSB to CGH on 2026-08-28 one way` |
| Só voos diretos | `Nonstop flights from BSB to CGH on 2026-08-28 through 2026-09-01` |
| Filtrado por companhia | `Flights from BSB to CGH on 2026-08-28 through 2026-09-01 with LATAM` |
| Explorar mês/período | `Flights from BSB to CGH in September` |

Exemplo pronto (ida e volta filtrado por GOL):
`https://www.google.com/travel/flights?q=Flights%20from%20BSB%20to%20CGH%20on%202026-08-28%20through%202026-09-01%20with%20GOL&hl=pt-BR&curr=BRL`

Calendário de preços (datas flexíveis): entregue o link da rota e instrua: abrir → tocar no campo de datas → alternar para a visão de calendário/grade, que mostra o preço mínimo por dia do mês inteiro. Não existe URL estável direta para o calendário — o caminho é via link da rota.

Regras dos links:
- 1 link geral da rota + 1 link por companhia listada no relatório (coluna Link).
- Sempre incluir `hl=pt-BR&curr=BRL` (ou a moeda pedida).
- Nunca inventar parâmetros além de `q`, `hl`, `curr` — o formato `?tfs=` do Google é binário e não deve ser montado à mão.

## Sanidade (checklist antes de reportar)

| # | Regra | Ação se falhar |
|---|---|---|
| S1 | Rota dos resultados = rota pedida (origem→destino) | refazer a busca |
| S2 | Data de partida = data pedida | refazer a busca |
| S3 | Rota de grande fluxo (ex.: ponte aérea) com ≥3 opções de voo | suspeitar do dado; entregar link para conferência ao vivo |
| S4 | Rota doméstica tronco BR: pelo menos 2 entre LATAM/GOL/Azul presentes | idem S3 |
| S5 | Preços dentro da faixa plausível da rota (tabela abaixo) | alerta explícito + confirmar no link |
| S6 | Duração do trecho plausível (ex.: BSB↔CGH direto ≈ 1h20–2h30) | alerta explícito |
| S7 | Preço não parece congelado: se TODOS os dias de uma janela grande têm o MESMO preço, dado provavelmente stale | refazer busca / alertar |
| S8 | Consistência: duas leituras da mesma rota não divergem >30% (acima de 50%, dado provavelmente stale) | alerta "dado volátil/esgotando"; confirmar no link |

## Faixas de sanidade e calibração (BRL, econômica)

- BSB↔CGH (ida direta): promocional ~R$ 230–300; normal/última hora R$ 800–1.500. Abaixo de ~R$ 150 ou acima de ~R$ 5.000 = suspeito.
- Regra geral doméstico BR direto: abaixo de R$ 100 ou acima de R$ 8.000 = quase certamente erro de leitura.
- Pontos reais coletados em 2026-07-23 (referência): BSB→CGH ida 28/08 R$ 810 (todas as diretas no mesmo preço); RT 28/08→01/09 R$ 1.493–2.047; RT 14/09→21/09 R$ 1.172.

## Semântica de preços (Google Flights)

- **Ida e volta**: a lista de IDA já mostra o preço TOTAL do round-trip a partir daquela ida; a volta é escolhida depois, no site. Nunca some ida + volta avulsas para estimar o RT.
- Preços são "**a partir de**" (tarifa mais barata do dia naquela opção) e mudam com frequência. Sempre datar a consulta.
- Preço idêntico em vários horários do mesmo dia = comum em rota de grande fluxo (classe mais barata do dia). Não é erro.
- Preço de ida avulsa NÃO é metade do RT — cite como referência apenas.
- **O preço do Google não é o piso do mercado.** Medido em 31/07/2026, BSB→CGH 28/09→01/10, tudo no mesmo dia: R$ 1.079 numa consulta automatizada do Google, R$ 639 na tela do titular e R$ 680 no Kayak — a diferença são as ofertas de agências (123Milhas, Decolar, maxmilhas, Kiwi.com...) que a tela agrega. Em outra janela (28/08→01/09) os valores bateram, então não existe desconto fixo a aplicar. Ao reportar: diga que o valor é do Google e recomende conferir uma metabusca (Kayak/Skyscanner) antes de comprar. Tarifa de agência exige checar bagagem e cancelamento no vendedor.

## Dados reais vs prévia do calendário

- O Google Flights tem dois tipos de número: a **pesquisa real** de uma data (fonte de verdade, refeita a cada consulta) e a **prévia** do calendário/visão de meses (estimativa em cache). É comum a prévia mostrar um valor e a pesquisa de fato retornar outro (às vezes menor). Por isso: prévia serve só de triagem de datas candidatas; TODO valor reportado deve vir da pesquisa real da data.
- Protocolo de período (mês ou meses): amostrar no mínimo **5 datas reais POR MÊS** do período, espalhadas dentro de cada mês → ranquear pelos valores reais → perguntar se o usuário quer ampliar a amostra.
- Protocolo de ano inteiro: triagem dos meses (sazonalidade + prévia) → ≥1 pesquisa real por mês (12) → ranquear meses pelo valor real → +5 pesquisas reais no melhor mês → reportar mês vencedor + amostra.
- Sazonalidade BR para triagem de meses (tendência): **caros** — julho, dezembro–janeiro, feriados prolongados, alta de eventos locais (ex.: Carnaval no Rio/Salvador); **baratos** — março–maio e agosto–setembro fora de feriado. Sazonalidade nunca substitui a pesquisa real — só ordena o que pesquisar primeiro.

## Estratégia de compra

Heurísticas canônicas:

- Antecedência doméstico BR: comprar ~1–3 meses antes; última semana quase sempre cara.
- Antecedência internacional: ~2–6 meses.
- Dias de VOAR tipicamente mais baratos (tendência, não lei): terça, quarta e sábado; sexta e domingo tendem a ser os mais caros.
- Dia de COMPRAR: "comprar terça-feira é mais barato" = mito, sem evidência robusta. O que funciona é monitorar com alerta de preço.
- Alta temporada BR (julho, dezembro–janeiro, feriados prolongados) encarece; setembro é baixa temporada doméstica.
- Alerta de preço do Google Flights: abrir o link da rota → "Acompanhar preços" — o Google avisa quedas por e-mail/notificação.
- Sinal objetivo (quando houver varredura de janela): preço atual ≤ p25 da janela = **comprar**; entre p25 e mediana = **bom preço**; acima da mediana = **esperar/monitorar** (com alerta ativo).
- Aeroportos alternativos: sempre comparar TODOS os aeroportos da região metropolitana (VCP costuma bater CGH/GRU em SP; SDU×GIG no Rio muda por horário/companhia).

Sem script de varredura (ambiente prompt-only), o sinal p25/mediana é **qualitativo**: compare o preço visto com a faixa de preços do mês inteiro no calendário do Google Flights (grade de preços por dia) — dias entre os mais baratos do calendário = comprar; próximos da média visual do mês = bom preço; visivelmente acima da maioria = esperar/monitorar com alerta ativo.

Formato do mapa (resposta a pedido de estratégia/economia) — 3 blocos:

1. **Dias mais baratos**: dias da semana favoráveis pra VOAR na rota, cruzando a heurística acima com o que a busca/calendário GF mostrar; cite também os dias mais caros a evitar.
2. **Aeroportos alternativos**: tabela comparando cada aeroporto da região metropolitana (mínimo por aeroporto), quando a cidade tiver mais de um.
3. **Momento de compra**: janela de antecedência recomendada (doméstico/internacional), sinal qualitativo de comprar/esperar (comparado à faixa do mês no calendário GF) e instrução de ativar "Acompanhar preços" no link da rota.

## Relatório (formato padrão)

Regra: **bem resumido, só o essencial** — cabeçalho de 1 linha, destaque do melhor preço, tabela enxuta (3–6 linhas: a mais barata + competitivas até ~15% acima), links. Sem parágrafos longos, sem repetir o pedido, sem explicar o processo.

Modelo:

> ✈️ **BSB → CGH** · ida 28/08 · volta 01/09 · consulta 25/07 21h
> 💰 **A partir de R$ 1.083** — Azul, direto · preços "a partir de", confirmam no checkout
>
> | | Cia | Horário | Escalas | Tempo | Preço RT | Link |
> |---|---|---|---|---|---|---|
> | ⭐ | Azul | 20:05 → 21:50 | direto | 1h45 | **R$ 1.083** | [abrir](...) |
> | | Azul | 12:00 → 13:45 | direto | 1h45 | R$ 1.166 | [abrir](...) |
> | | GOL | 07:30 → 09:15 | direto | 1h45 | R$ 1.284 | [abrir](...) |
>
> ↩️ **Volta 01/09** (diretas, 1h45): Azul 07:15 · GOL 06:00 / 06:30 / 08:00
> 📅 Acompanhar preços: [link da rota](...)

- ⭐ marca a recomendação (equilíbrio preço × escalas × horário).
- Escalas: cada conexão com aeroporto e espera na própria célula (ex.: "1 (VCP, 55 min)"; "2 (CNF 1h10, GRU 45 min)").
- Volta com escala: mini-tabela em vez da linha única.
- Multi-aeroporto ("todos"): uma linha de mínimo por aeroporto antes da tabela.
- Período/ano: lista ranqueada das datas pesquisadas (⭐ na melhor, preço real em negrito), 1 linha de estatística (mín/mediana do período) e fechar perguntando: "Quero amostrar mais dias?".

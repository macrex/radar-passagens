# Estratégia de preço mínimo

Heurísticas canônicas — idênticas à seção "Estratégia de compra" de
`lite/conhecimento.md` (as duas versões devem dizer a mesma coisa).

## Heurísticas canônicas

- Antecedência doméstico BR: comprar ~1–3 meses antes; última semana quase
  sempre cara.
- Antecedência internacional: ~2–6 meses.
- Dias de VOAR tipicamente mais baratos (tendência, não lei): terça, quarta e
  sábado; sexta e domingo tendem a ser os mais caros.
- Dia de COMPRAR: "comprar terça-feira é mais barato" = mito, sem evidência
  robusta. O que funciona é monitorar com alerta de preço.
- Alta temporada BR (julho, dezembro–janeiro, feriados prolongados) encarece;
  setembro é baixa temporada doméstica.
- Alerta de preço do Google Flights: abrir o link da rota → "Acompanhar
  preços" — o Google avisa quedas por e-mail/notificação.
- Sinal objetivo (quando houver varredura de janela): preço atual ≤ p25 da
  janela = **comprar**; entre p25 e mediana = **bom preço**; acima da mediana
  = **esperar/monitorar** (com alerta ativo).
- Aeroportos alternativos: sempre comparar TODOS os aeroportos da região
  metropolitana (VCP costuma bater CGH/GRU em SP; SDU×GIG no Rio muda por
  horário/companhia).

## Formato do mapa (resposta ao usuário)

Montar com `estatisticas` + `por_dia_semana` de `melhor_periodo.py`. 3 blocos:

1. **Dias mais baratos** — `por_dia_semana` ordenado por `min`/`mediana`;
   destacar os dias com menor mediana e citar a tendência ter/qua/sáb.
2. **Aeroportos alternativos** — tabela comparando mínimo por aeroporto
   (quando a busca rodou com "todos"); apontar o mais barato.
3. **Momento de compra** — sinal comprar/bom preço/esperar via p25/mediana de
   `estatisticas`; se "esperar", recomendar ativar alerta de preço no link.

Sempre citar a data/hora da consulta e que o preço final confirma no
checkout da companhia (mesma nota da seção "Semântica e gotchas").

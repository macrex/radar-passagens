# Estratégia de preço mínimo (versão completa)

Como transformar a saída dos scripts no mapa de economia. As heurísticas de fundo
não moram aqui — este arquivo cobre só o que é específico da versão com scripts.

Heurísticas canônicas (antecedência, dias de voar, sazonalidade, mito da terça, alerta
de preço): `lite/conhecimento.md` §Estratégia de compra — fonte única; não duplicar aqui.
(Exceção consciente à regra de não ler `lite/` na versão completa: aquele arquivo é a
fonte canônica das heurísticas para as DUAS versões.)

## Do JSON para o mapa

Montar com `estatisticas` + `por_dia_semana` de `melhor_periodo.py`. 3 blocos:

1. **Dias mais baratos** — `por_dia_semana` ordenado por `min`/`mediana`; destacar os
   dias com menor mediana e citar a tendência ter/qua/sáb.
2. **Aeroportos alternativos** — tabela comparando o mínimo por aeroporto (quando a
   busca rodou com "todos"); apontar o mais barato.
3. **Momento de compra** — sinal via `estatisticas`: preço atual **≤ p25 = comprar**;
   **entre p25 e mediana = bom preço**; **acima da mediana = esperar/monitorar**. Se
   "esperar", recomendar ativar "Acompanhar preços" no link da rota.

Sempre citar a data/hora da consulta (campo `consultado_em`) e que o preço final se
confirma no checkout da companhia.

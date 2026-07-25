# Fontes de dados de voos — alternativas e fallbacks (pesquisa 2026-07)

## Fonte primária (implementada nos scripts)

Google Flights via `fast-flights` (github.com/AWeirdDev/flights, v3.x, ativa):
protobuf `?tfs=` em Base64 + parse do HTML. `BRL` e `pt-BR` suportados nativamente.
Gotcha confirmado em 2 testes independentes: o fetcher nativo (`primp`) falha atrás
de proxy TLS/MITM (não confia na CA); o contorno é buscar `query.params()` com
`requests` e usar `fast_flights.parser.parse(html)` — é o que `buscar_voos.py` faz.

## 2ª fonte implementada (comparador)

Aviasales cache via Travelpayouts Data API v3 (`scripts/fonte_aviasales.py`):
preços cacheados ~48h vistos por usuários (incluem OTAs), grátis com
`TRAVELPAYOUTS_TOKEN`. São ESTIMATIVAS — rotular "vista em <found_at>" e
confirmar no link. Gate de cobertura BR: `scripts/spike_aviasales.py`
(spec: docs/superpowers/specs/2026-07-23-fontes-voos-design.md). Pesquisa
jul/2026: Amadeus self-service desligada, Kiwi/Skyscanner só parceiros,
Decolar sem API pública — Aviasales é a única fonte grátis complementar.

## 3ª fonte implementada (metabusca ao vivo)

Kayak + Skyscanner via Playwright (`scripts/fonte_navegador.py`), validado 2026-07-25:
- **Chrome instalado (`channel="chrome"`) passa no anti-bot, headless inclusive**; o
  Chromium empacotado do Playwright é barrado ("O que é um bot?" / "Are you a person
  or a robot?"), assim como HTTP puro. UA realista + `navigator.webdriver` mascarado.
- Kayak: cards `div[class*="nrc6-wrapper"]` trazem horários ida/volta, escalas, duração,
  cias e preço. Skyscanner segue bloqueando mesmo com Chrome real — best-effort.
- Preços são REAIS e incluem tarifas de OTAs: BSB↔CGH RT 28/08→01/09 deu **R$ 870 no
  Kayak vs R$ 1.083 no Google** (mesma consulta, 2026-07-25). Rotular "tarifa de OTA —
  confirmar no site do vendedor" (bagagem/cancelamento podem diferir).
- Parse por regex sobre o texto do card: resiste a troca de classe interna, mas se o
  seletor do card mudar o script devolve "nenhum resultado legivel" (fail-open).

## Fallbacks (se o parse do Google quebrar)

1. **`fli`** (github.com/punitarani/fli, ~3k stars): mesma engenharia reversa, mas com
   matriz de datas nativa (`fli dates`) e servidor MCP pronto — candidato a substituir
   `melhor_periodo.py` se a varredura por N consultas ficar lenta demais.
2. **SerpApi `google_flights`**: plano gratuito de 250 buscas/mês sem cartão; retorna
   `price_insights` e date-grid estruturados sem parsing próprio. Bom cross-check.
3. **Playwright + Chrome** em flights.google.com: navegador real; sobrevive a bloqueio
   de TLS-fingerprint e proxy. Plano B lento (a infra já está em `fonte_navegador.py`).

## Não usar

- **Amadeus Self-Service (test tier)**: dataset ESTÁTICO — serve para testar schema,
  nunca para preço real; cobertura de GOL/Azul doméstico incerta (NDC não aderido).
- **Kiwi/Tequila e Skyscanner oficial**: não são mais self-service abertos (só parceiros).
- **Scraping direto de LATAM/GOL/Azul**: anti-bot (Cloudflare/fingerprint) — instável e
  caro de manter.

## Interpretação de preços (validado com dados reais)

- Preço idêntico em vários horários do mesmo dia = preço "a partir de" da classe mais
  barata do dia (comum em rota-ponte). Reportar como "a partir de", nunca como tarifa
  exata do voo específico.
- Faixa de sanidade BSB↔CGH econômica: ida promocional ~R$230–300; ida normal/última
  hora R$800–1500; abaixo de ~R$150 ou acima de ~R$5000 (ida direta) = suspeito.
- Divergência >30–40% entre fontes ou entre repetições = dado stale/tarifa esgotada.

Pontos de dado reais coletados em 2026-07-23 (referência de calibração):
ida 28/08 R$810 (todas as diretas); RT 28/08→01/09 R$1493–2047; RT 14/09→21/09 R$1172.

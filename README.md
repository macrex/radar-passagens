# Radar de Passagens

Assistente de busca e comparação de passagens aéreas, 100% prompt-only: preços do Google Flights, links de compra prontos (1 clique) e estratégia de preço mínimo — melhores dias pra voar, aeroportos alternativos e o momento certo de comprar.

Funciona em qualquer plataforma de agentes que aceite **instruções + arquivo de conhecimento**: Gemini (Gems), ChatGPT (GPTs), Claude (Projects), Copilot e afins. Sem código, sem API, sem chave — o assistente usa a própria busca da plataforma e entrega links diretos do Google Flights.

## Arquivos

| Arquivo | Uso |
|---|---|
| `INSTRUCOES.md` | Campo de instruções / system prompt do agente |
| `conhecimento.md` | Arquivo de conhecimento (upload/anexo) |

## Como montar

Exemplo no Gemini (Gems):

1. gemini.google.com → **Gems** → criar novo Gem.
2. Nome: `Radar de Passagens`.
3. Cole o conteúdo de `INSTRUCOES.md` no campo de instruções.
4. Anexe `conhecimento.md` como arquivo de conhecimento.
5. Salve e teste: `passagem BSB para CGH, ida 28/08 volta 01/09`.

Nas demais plataformas o processo é análogo (GPTs: Instructions + Knowledge; Claude Projects: instruções do projeto + arquivo no projeto).

Teste de aceitação: o assistente deve perguntar o aeroporto quando a cidade tiver mais de um (ex.: "São Paulo"), reportar em tabela com escalas/esperas e entregar links do Google Flights clicáveis (geral + por companhia).

## O que ele faz

- **Busca pontual**: ida ou ida+volta, tabela com horários, escalas (espera por conexão), duração total, preço "a partir de" e link por companhia.
- **Melhor período**: dias mais baratos da janela + orientação do calendário de preços do Google Flights.
- **Estratégia de economia**: o mapa — dias da semana que fogem do caro, comparação dos aeroportos da região e quando comprar (com alerta de preço).
- **Sanidade**: checklist de 8 regras antes de reportar (rota, datas, companhias, faixa de preço, duração, dado desatualizado).

## Limitações

- Preços vêm da busca do agente, não de API: são estimativas "a partir de" — a confirmação é sempre no link do Google Flights / checkout da companhia.
- Não compra nem automatiza checkout; só pesquisa, compara e entrega links.
- Calibrado para pt-BR e BRL por padrão (ajustável a pedido do usuário).

## Licença

[MIT](LICENSE).

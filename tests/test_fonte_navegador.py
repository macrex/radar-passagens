"""Testes do parse dos cards de metabusca (sem abrir navegador)."""
from fonte_navegador import SITES, parse_card, preco_de

CARD_KAYAK = (
    "Melhor opção | Mais barato | 9:30 – 11:15 | BSBBrasília | - | CGHCongonhas | direto | "
    "1h 45min | 17:05 – 18:50 | CGHCongonhas | - | BSBBrasília | direto | 1h 45min | "
    "GOL, Azul | R$\xa0870 | Promo + Econômica | Selecionar"
)
CARD_ANUNCIO = "20:05 – 21:50 | direto | 1h 45min | Azul | Anúncio | R$\xa01.335 | Econômica | Ver oferta"


# -------------------------------------------------------------------- precos

def test_le_preco_com_espaco_nao_quebravel_e_separador_de_milhar():
    assert preco_de("R$\xa01.335") == 1335.0


def test_ignora_valor_abaixo_da_faixa_plausivel():
    assert preco_de("R$ 12") is None


def test_ignora_valor_acima_da_faixa_plausivel():
    assert preco_de("R$ 90.000") is None


def test_sem_preco_no_texto():
    assert preco_de("nenhum valor aqui") is None


def test_pega_o_primeiro_preco_plausivel():
    assert preco_de("R$ 10 | R$ 870 | R$ 1.200") == 870.0


# --------------------------------------------------------------------- cards

def test_card_kayak_extrai_preco_cias_e_horarios():
    v = parse_card(CARD_KAYAK)
    assert v["preco"] == 870.0
    assert set(v["cias"]) == {"GOL", "Azul"}
    assert v["horarios"] == ["9:30-11:15", "17:05-18:50"]
    assert v["paradas"] == "direto"


def test_card_kayak_extrai_duracoes_de_ida_e_volta():
    assert parse_card(CARD_KAYAK)["duracoes"] == ["1h 45min", "1h 45min"]


def test_card_sem_preco_e_descartado():
    assert parse_card("BSB - CGH | direto | 1h 45min | GOL") is None


def test_card_de_anuncio_e_marcado():
    assert parse_card(CARD_ANUNCIO)["anuncio"] is True


def test_card_organico_nao_e_marcado_como_anuncio():
    assert parse_card(CARD_KAYAK)["anuncio"] is False


def test_anuncio_sem_acento_tambem_e_detectado():
    """Regressao: a deteccao testava a mesma string acentuada duas vezes."""
    assert parse_card("Anuncio | Azul | R$ 1.335")["anuncio"] is True


def test_card_com_escala_marca_paradas():
    v = parse_card("7:30 – 12:10 | 1 escala | 4h 40min | LATAM | R$ 1.190")
    assert v["paradas"] == "com escala"


# ---------------------------------------------------------------------- urls

def test_url_kayak_ida_e_volta():
    url = SITES["kayak"]["url"]("BSB", "CGH", "2026-08-28", "2026-09-01")
    assert url.startswith("https://www.kayak.com.br/flights/BSB-CGH/2026-08-28/2026-09-01")


def test_url_kayak_so_ida_nao_tem_segunda_data():
    url = SITES["kayak"]["url"]("BSB", "CGH", "2026-08-28", None)
    assert "/2026-08-28?" in url


def test_url_skyscanner_usa_formato_aammdd():
    url = SITES["skyscanner"]["url"]("BSB", "CGH", "2026-08-28", "2026-09-01")
    assert url.endswith("/bsb/cgh/260828/260901/")

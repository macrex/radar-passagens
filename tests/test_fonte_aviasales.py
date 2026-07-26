"""Testes dos filtros de sanidade do cache Aviasales (sem rede)."""
import datetime as dtmod

from fonte_aviasales import PRECO_MAX, PRECO_MIN, idade_dias, link_compra, transformar

AGORA = dtmod.datetime(2026, 7, 25, 12, 0, tzinfo=dtmod.timezone.utc)


def item(preco=900, found_at="2026-07-24T10:00:00Z", **extra):
    base = {"price": preco, "found_at": found_at, "airline": "G3", "transfers": 0,
            "origin": "BSB", "destination": "CGH", "link": "/flights/BSBCGH"}
    base.update(extra)
    return base


# ------------------------------------------------------------------- idade

def test_idade_em_dias_com_sufixo_z():
    assert round(idade_dias("2026-07-23T12:00:00Z", AGORA)) == 2


def test_idade_de_valor_invalido_e_none():
    assert idade_dias("nao e data", AGORA) is None
    assert idade_dias(None, AGORA) is None


# ------------------------------------------------------------------- filtros

def test_mantem_item_recente_e_dentro_da_faixa():
    voos, descartados = transformar([item()], "BSB", "CGH", None, AGORA)
    assert descartados == 0
    assert voos[0]["preco"] == 900
    assert voos[0]["cias"] == ["Gol"]


def test_descarta_cache_mais_velho_que_sete_dias():
    voos, descartados = transformar([item(found_at="2026-07-01T10:00:00Z")], "BSB", "CGH", None, AGORA)
    assert (voos, descartados) == ([], 1)


def test_mantem_item_sem_found_at():
    """Sem carimbo de tempo nao da para julgar idade — nao descarta."""
    voos, descartados = transformar([item(found_at=None)], "BSB", "CGH", None, AGORA)
    assert len(voos) == 1 and descartados == 0


def test_descarta_preco_fora_da_faixa_de_sanidade():
    itens = [item(preco=PRECO_MIN - 1), item(preco=PRECO_MAX + 1)]
    voos, descartados = transformar(itens, "BSB", "CGH", None, AGORA)
    assert (voos, descartados) == ([], 2)


def test_descarta_preco_ausente_ou_nao_numerico():
    voos, descartados = transformar([item(preco=None), item(preco="900")], "BSB", "CGH", None, AGORA)
    assert (voos, descartados) == ([], 2)


def test_usa_origem_destino_do_item_quando_presente():
    voos, _ = transformar([item(origin="GRU", destination="SSA")], "BSB", "CGH", None, AGORA)
    assert (voos[0]["origem"], voos[0]["destino"]) == ("GRU", "SSA")


def test_cai_para_argumentos_quando_item_nao_traz_rota():
    voos, _ = transformar([item(origin=None, destination=None)], "BSB", "CGH", None, AGORA)
    assert (voos[0]["origem"], voos[0]["destino"]) == ("BSB", "CGH")


def test_cia_desconhecida_mantem_o_codigo():
    voos, _ = transformar([item(airline="ZZ")], "BSB", "CGH", None, AGORA)
    assert voos[0]["cias"] == ["ZZ"]


def test_cache_nao_expoe_escalas():
    voos, _ = transformar([item()], "BSB", "CGH", None, AGORA)
    assert voos[0]["escalas"] is None and voos[0]["espera_total_min"] is None


def test_lista_vazia():
    assert transformar([], "BSB", "CGH", None, AGORA) == ([], 0)


# --------------------------------------------------------------------- link

def test_link_recebe_marker_de_afiliado():
    assert link_compra("/voo", "755330").endswith("?marker=755330")


def test_link_com_query_existente_usa_e_comercial():
    assert link_compra("/voo?a=1", "999").endswith("&marker=999")


def test_link_sem_marker_fica_limpo():
    assert link_compra("/voo", None) == "https://www.aviasales.com/voo"


def test_link_sem_fragmento_e_none():
    assert link_compra(None, "755330") is None

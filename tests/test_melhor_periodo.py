"""Testes de agregacao e amostragem do melhor_periodo."""
import datetime as dtmod

import pytest

from melhor_periodo import calcula_estatisticas, calcula_por_dia_semana, datas_amostradas


def linha(ida, preco):
    return {"ida": ida, "volta": None, "preco_minimo": preco, "n_voos": 5, "erro": None}


# ---------------------------------------------------------------- estatisticas

def test_estatisticas_sem_dados():
    assert calcula_estatisticas([]) == {"n": 0, "min": None, "p25": None, "mediana": None, "max": None}


def test_estatisticas_um_valor_p25_igual_mediana():
    e = calcula_estatisticas([800])
    assert (e["n"], e["min"], e["max"]) == (1, 800, 800)
    assert e["p25"] == e["mediana"] == 800


def test_estatisticas_dois_valores():
    e = calcula_estatisticas([400, 800])
    assert e["n"] == 2 and e["min"] == 400 and e["max"] == 800
    assert e["p25"] <= e["mediana"] <= e["max"]


def test_estatisticas_ordem_invariante():
    assert calcula_estatisticas([900, 300, 600]) == calcula_estatisticas([300, 600, 900])


def test_p25_nunca_ultrapassa_mediana():
    for precos in ([100, 200, 300, 400], [100, 100, 100, 900], [500, 501]):
        e = calcula_estatisticas(precos)
        assert e["min"] <= e["p25"] <= e["mediana"] <= e["max"]


# ------------------------------------------------------------- por dia semana

def test_por_dia_semana_agrupa_pelo_weekday_da_ida():
    # 2026-09-01 = terca, 2026-09-02 = quarta
    r = calcula_por_dia_semana([linha("2026-09-01", 500), linha("2026-09-02", 300)])
    assert set(r) == {"ter", "qua"}
    assert r["ter"]["min"] == 500 and r["qua"]["min"] == 300


def test_por_dia_semana_so_inclui_dias_com_amostra():
    r = calcula_por_dia_semana([linha("2026-09-01", 500)])
    assert list(r) == ["ter"]


def test_por_dia_semana_respeita_ordem_da_semana():
    # domingo (06/09) inserido antes de segunda (07/09): saida deve sair ordenada
    r = calcula_por_dia_semana([linha("2026-09-06", 100), linha("2026-09-07", 200)])
    assert list(r) == ["seg", "dom"]


def test_por_dia_semana_agrega_varios_no_mesmo_dia():
    r = calcula_por_dia_semana([linha("2026-09-01", 500), linha("2026-09-08", 300)])
    assert r["ter"] == {"min": 300, "mediana": 400, "n": 2}


def test_por_dia_semana_vazio():
    assert calcula_por_dia_semana([]) == {}


# ------------------------------------------------------------------ amostragem

def d(s):
    return dtmod.date.fromisoformat(s)


def test_amostra_none_devolve_todas_as_datas():
    todas = datas_amostradas(d("2026-09-01"), d("2026-09-10"), None)
    assert len(todas) == 10
    assert todas[0] == d("2026-09-01") and todas[-1] == d("2026-09-10")


def test_amostra_maior_que_janela_devolve_todas():
    assert len(datas_amostradas(d("2026-09-01"), d("2026-09-03"), 10)) == 3


def test_amostra_inclui_as_pontas():
    a = datas_amostradas(d("2026-09-01"), d("2026-09-30"), 5)
    assert a[0] == d("2026-09-01") and a[-1] == d("2026-09-30")


def test_amostra_devolve_a_quantidade_pedida():
    for n in (2, 3, 5, 12):
        a = datas_amostradas(d("2026-01-01"), d("2026-12-31"), n)
        assert len(a) == n, f"amostra {n} devolveu {len(a)}"


def test_amostra_espalha_uniformemente():
    a = datas_amostradas(d("2026-09-01"), d("2026-09-29"), 5)
    gaps = {(a[i + 1] - a[i]).days for i in range(len(a) - 1)}
    assert gaps == {7}


def test_amostra_sem_datas_repetidas():
    a = datas_amostradas(d("2026-09-01"), d("2026-09-30"), 12)
    assert len(set(a)) == len(a)


def test_amostra_um_dia_pega_o_inicio():
    assert datas_amostradas(d("2026-09-01"), d("2026-09-30"), 1) == [d("2026-09-01")]


def test_janela_invertida_devolve_vazio():
    assert datas_amostradas(d("2026-09-30"), d("2026-09-01"), 5) == []


def test_janela_de_um_dia():
    assert datas_amostradas(d("2026-09-01"), d("2026-09-01"), 5) == [d("2026-09-01")]


@pytest.mark.parametrize("n", [0, -3])
def test_amostra_invalida_cai_para_todas(n):
    assert len(datas_amostradas(d("2026-09-01"), d("2026-09-05"), n)) == 5

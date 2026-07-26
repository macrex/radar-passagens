"""Testes de aeroportos.resolve — cidade/IATA -> aeroportos."""
import pytest

from aeroportos import resolve


def test_cidade_multi_aeroporto_marca_multi():
    r = resolve("sao paulo")
    assert r["multi"] is True
    assert {a["code"] for a in r["aeroportos"]} == {"CGH", "GRU", "VCP"}


def test_cidade_com_acento_e_maiuscula_normaliza():
    assert resolve("São Paulo")["cidade"] == "sao paulo"
    assert resolve("BRASÍLIA")["aeroportos"][0]["code"] == "BSB"


def test_cidade_unico_aeroporto_nao_e_multi():
    r = resolve("salvador")
    assert r["multi"] is False
    assert r["aeroportos"][0]["code"] == "SSA"


def test_codigo_iata_catalogado_resolve_cidade():
    r = resolve("GRU")
    assert r["cidade"] == "sao paulo"
    assert r["multi"] is False
    assert r["aeroportos"] == [a for a in r["aeroportos"] if a["code"] == "GRU"]


def test_codigo_iata_desconhecido_nao_quebra():
    r = resolve("XYZ")
    assert r["aeroportos"][0]["code"] == "XYZ"
    assert "nao catalogado" in r["aeroportos"][0]["obs"]


def test_cidade_desconhecida_devolve_erro_orientando_iata():
    r = resolve("cidade que nao existe")
    assert r["aeroportos"] == []
    assert "erro" in r


def test_rio_de_tres_letras_resolve_a_cidade_nao_iata():
    """Regressao: "rio" tem 3 letras e caia no ramo de codigo IATA,
    devolvendo "codigo nao catalogado" em vez de SDU/GIG."""
    r = resolve("rio")
    assert r["cidade"] == "rio de janeiro"
    assert {a["code"] for a in r["aeroportos"]} == {"SDU", "GIG"}
    assert r["multi"] is True


def test_iata_tem_precedencia_quando_e_codigo_real():
    """"BSB" continua sendo lido como codigo, nao como prefixo de cidade."""
    r = resolve("BSB")
    assert r["aeroportos"][0]["code"] == "BSB"
    assert r["multi"] is False


@pytest.mark.parametrize("entrada", ["", "   "])
def test_entrada_vazia_nao_explode(entrada):
    r = resolve(entrada)
    assert isinstance(r, dict)
    assert r["aeroportos"] == [] or r["multi"] is False

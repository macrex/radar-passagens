"""Testes das funcoes puras do buscar_voos (escalas, ordenacao)."""
from buscar_voos import CHAVES_ORDENACAO, escalas_de


def leg(de, para, partida, chegada, duracao=100):
    return {"de": de, "para": para, "partida": partida, "chegada": chegada,
            "duracao_min": duracao, "aeronave": None}


def voo(preco=1000, paradas=0, duracao=105, espera=0, partida="2026-08-28T07:00"):
    return {"preco": preco, "paradas": paradas, "duracao_total_min": duracao,
            "espera_total_min": espera, "trechos": [leg("BSB", "CGH", partida, partida)]}


# ------------------------------------------------------------------- escalas

def test_voo_direto_nao_tem_escala():
    assert escalas_de([leg("BSB", "CGH", "2026-08-28T07:00", "2026-08-28T08:45")]) == []


def test_uma_conexao_calcula_espera_em_minutos():
    legs = [leg("BSB", "VCP", "2026-08-28T07:00", "2026-08-28T08:30"),
            leg("VCP", "CGH", "2026-08-28T09:25", "2026-08-28T10:00")]
    assert escalas_de(legs) == [{"aeroporto": "VCP", "espera_min": 55}]


def test_duas_conexoes_devolvem_uma_entrada_por_escala():
    legs = [leg("BSB", "CNF", "2026-08-28T07:00", "2026-08-28T08:00"),
            leg("CNF", "GRU", "2026-08-28T09:10", "2026-08-28T10:10"),
            leg("GRU", "CGH", "2026-08-28T10:55", "2026-08-28T11:30")]
    assert [e["aeroporto"] for e in escalas_de(legs)] == ["CNF", "GRU"]
    assert [e["espera_min"] for e in escalas_de(legs)] == [70, 45]


def test_espera_que_atravessa_a_meia_noite():
    legs = [leg("BSB", "GRU", "2026-08-28T22:00", "2026-08-28T23:30"),
            leg("GRU", "LIS", "2026-08-29T01:00", "2026-08-29T11:00")]
    assert escalas_de(legs)[0]["espera_min"] == 90


def test_horario_invalido_vira_espera_nula_sem_quebrar():
    legs = [leg("BSB", "VCP", "2026-08-28T07:00", "hora ruim"),
            leg("VCP", "CGH", "2026-08-28T09:25", "2026-08-28T10:00")]
    assert escalas_de(legs) == [{"aeroporto": "VCP", "espera_min": None}]


# ----------------------------------------------------------------- ordenacao

def test_ordena_por_preco():
    voos = [voo(preco=1200), voo(preco=800), voo(preco=1000)]
    assert [v["preco"] for v in sorted(voos, key=CHAVES_ORDENACAO["preco"])] == [800, 1000, 1200]


def test_ordena_por_tempo_total():
    voos = [voo(duracao=300), voo(duracao=105), voo(duracao=200)]
    assert [v["duracao_total_min"] for v in sorted(voos, key=CHAVES_ORDENACAO["tempo"])] == [105, 200, 300]


def test_ordena_por_escalas_prioriza_menos_paradas():
    voos = [voo(paradas=1, preco=700), voo(paradas=0, preco=900)]
    assert [v["paradas"] for v in sorted(voos, key=CHAVES_ORDENACAO["escalas"])] == [0, 1]


def test_empate_de_escalas_desempata_por_menor_espera():
    voos = [voo(paradas=1, espera=300), voo(paradas=1, espera=60)]
    assert [v["espera_total_min"] for v in sorted(voos, key=CHAVES_ORDENACAO["escalas"])] == [60, 300]


def test_preco_nulo_vai_para_o_fim():
    voos = [voo(preco=None), voo(preco=1000)]
    assert sorted(voos, key=CHAVES_ORDENACAO["preco"])[0]["preco"] == 1000


def test_duracao_nula_vai_para_o_fim_na_ordem_por_tempo():
    voos = [voo(duracao=None), voo(duracao=105)]
    assert sorted(voos, key=CHAVES_ORDENACAO["tempo"])[0]["duracao_total_min"] == 105

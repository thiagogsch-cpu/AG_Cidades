import numpy as np
import pandas as pd


def calcular_soma_ponderada(df, pesos, considerar_custo=False):
    df_calc = df.copy()

    # Normalização Min-Max para trazer todas as variáveis para a escala 0 a 10
    def normalizar_min_max(coluna, inverter=False):
        v_min, v_max = df_calc[coluna].min(), df_calc[coluna].max()
        if v_max == v_min:
            return 5.0
        if inverter:
            return 10 * (1 - (df_calc[coluna] - v_min) / (v_max - v_min))
        return 10 * ((df_calc[coluna] - v_min) / (v_max - v_min))

    # Indicadores Normalizados
    df_calc["norm_tourist_vol"] = normalizar_min_max("tourist_volume_millions")
    df_calc["norm_traveler_rating"] = normalizar_min_max(
        "traveler_rating_score"
    )
    df_calc["norm_beauty"] = normalizar_min_max("city_beauty_score")

    if considerar_custo:
        df_calc["norm_hotel_cost"] = normalizar_min_max(
            "hotel_cost_eur", inverter=True
        )
        df_calc["norm_food_cost"] = normalizar_min_max(
            "food_cost_eur", inverter=True
        )
        df_calc["norm_attractions_cost"] = normalizar_min_max(
            "attractions_cost_eur", inverter=True
        )
        df_calc["norm_transit_cost"] = normalizar_min_max(
            "transit_cost_eur", inverter=True
        )

    pesos_ativos = {k: v for k, v in pesos.items() if v > 0}
    soma_pesos = sum(pesos_ativos.values())

    if soma_pesos == 0:
        df_calc["score_final"] = 0.0
        return df_calc

    # Cálculo da Pontuação Ponderada
    score_acumulado = (
        (df_calc["norm_beauty"] * pesos_ativos.get("city_beauty", 0))
        + (
            df_calc["norm_traveler_rating"]
            * pesos_ativos.get("traveler_rating", 0)
        )
        + (df_calc["norm_tourist_vol"] * pesos_ativos.get("tourist_volume", 0))
        + (df_calc["unesco_sites"] * pesos_ativos.get("unesco", 0))
        + (df_calc["museums_score"] * pesos_ativos.get("museums", 0))
        + (df_calc["architecture_score"] * pesos_ativos.get("architecture", 0))
        + (df_calc["cultural_events"] * pesos_ativos.get("events", 0))
        + (df_calc["gastronomy_score"] * pesos_ativos.get("gastronomy", 0))
        + (df_calc["nightlife_vibe"] * pesos_ativos.get("nightlife", 0))
        + (df_calc["nature_green_score"] * pesos_ativos.get("nature", 0))
        + (df_calc["hospitality_score"] * pesos_ativos.get("hospitality", 0))
        + (df_calc["safety_index"] * pesos_ativos.get("safety", 0))
        + (df_calc["transit_connectivity"] * pesos_ativos.get("transit", 0))
        + (df_calc["cleanliness_eco"] * pesos_ativos.get("cleanliness", 0))
        + (df_calc["hub_access"] * pesos_ativos.get("hub", 0))
    )

    if considerar_custo:
        score_acumulado += (
            (df_calc["norm_hotel_cost"] * pesos_ativos.get("hotel_cost", 0))
            + (df_calc["norm_food_cost"] * pesos_ativos.get("food_cost", 0))
            + (
                df_calc["norm_attractions_cost"]
                * pesos_ativos.get("attractions_cost", 0)
            )
            + (
                df_calc["norm_transit_cost"]
                * pesos_ativos.get("transit_cost", 0)
            )
        )

    df_calc["score_final"] = score_acumulado / soma_pesos
    return df_calc.sort_values(by="score_final", ascending=False)
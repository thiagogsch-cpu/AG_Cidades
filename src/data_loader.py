import os
import numpy as np
import pandas as pd

# Mapeamento com Amostra Expandida para França, Itália e Espanha + Restante da Europa
DADOS_PAISES_EUROPA = {
    "França": {
        "regiao": "Europa Ocidental",
        "custo": (75, 140),
        "qualidade": (7, 10),
        "cidades": [
            ("Paris", 10, 9.5, 19.4),
            ("Nice", 9, 8.9, 5.2),
            ("Lyon", 8, 8.6, 3.1),
            ("Marseille", 8, 8.2, 2.8),
            ("Bordeaux", 9, 8.8, 2.5),
            ("Strasbourg", 9, 8.7, 2.1),
            ("Toulouse", 8, 8.3, 1.8),
            ("Lille", 7, 8.1, 1.5),
            ("Nantes", 7, 8.2, 1.2),
            ("Montpellier", 8, 8.3, 1.1),
            ("Cannes", 9, 8.7, 2.4),
            ("Aix-en-Provence", 9, 8.8, 1.3),
            ("Avignon", 9, 8.9, 1.6),
            ("Rouen", 8, 8.4, 0.9),
            ("Colmar", 9, 9.0, 1.5),
        ],
    },
    "Itália": {
        "regiao": "Europa do Sul",
        "custo": (70, 130),
        "qualidade": (7, 10),
        "cidades": [
            ("Roma", 10, 9.4, 10.3),
            ("Florença", 10, 9.6, 5.2),
            ("Veneza", 10, 9.5, 5.5),
            ("Milão", 8, 8.9, 6.8),
            ("Nápoles", 8, 8.4, 3.2),
            ("Turim", 8, 8.5, 2.1),
            ("Bolonha", 8, 8.7, 2.0),
            ("Verona", 9, 8.9, 2.8),
            ("Palermo", 8, 8.3, 1.8),
            ("Gênova", 7, 8.1, 1.5),
            ("Pisa", 8, 8.5, 2.9),
            ("Siena", 9, 9.1, 1.7),
            ("Bari", 7, 8.2, 1.2),
            ("Cagliari", 8, 8.4, 0.9),
            ("Catânia", 7, 8.1, 1.1),
            ("Verona", 9, 8.9, 2.8),
            ("Padua", 8, 8.5, 1.0),
            ("Trieste", 8, 8.4, 0.8),
        ],
    },
    "Espanha": {
        "regiao": "Europa do Sul",
        "custo": (60, 115),
        "qualidade": (7, 10),
        "cidades": [
            ("Barcelona", 10, 9.3, 11.2),
            ("Madrid", 9, 9.0, 7.6),
            ("Sevilla", 9, 9.1, 3.5),
            ("Málaga", 8, 8.7, 3.2),
            ("Valência", 8, 8.8, 2.8),
            ("Granada", 9, 9.2, 2.3),
            ("Bilbao", 8, 8.6, 1.9),
            ("San Sebastián", 9, 9.1, 1.8),
            ("Palma de Maiorca", 8, 8.5, 4.8),
            ("Alicante", 7, 8.2, 2.1),
            ("Córdoba", 9, 9.0, 1.6),
            ("Toledo", 9, 9.1, 1.5),
            ("Salamanca", 8, 8.7, 1.1),
            ("Saragoça", 7, 8.2, 1.0),
            ("Cádiz", 8, 8.6, 0.9),
        ],
    },
    "Portugal": {
        "regiao": "Europa do Sul",
        "custo": (50, 95),
        "qualidade": (7, 9),
        "cidades": [
            ("Lisboa", 9, 9.2, 5.4),
            ("Porto", 9, 9.1, 3.2),
            ("Faro", 7, 8.1, 2.1),
            ("Coimbra", 8, 8.4, 1.1),
            ("Braga", 8, 8.3, 1.0),
            ("Sintra", 9, 9.3, 2.5),
            ("Évora", 8, 8.5, 0.9),
            ("Funchal", 8, 8.7, 1.5),
            ("Ponta Delgada", 8, 8.6, 0.8),
            ("Aveiro", 7, 8.2, 0.9),
        ],
    },
    "Reino Unido": {
        "regiao": "Europa Ocidental",
        "custo": (85, 150),
        "qualidade": (7, 10),
        "cidades": [
            ("Londres", 9, 9.2, 19.8),
            ("Edimburgo", 9, 9.1, 3.8),
            ("Manchester", 7, 8.3, 2.7),
            ("Liverpool", 7, 8.4, 2.1),
            ("Oxford", 8, 8.8, 2.0),
            ("Cambridge", 8, 8.7, 1.8),
            ("Belfast", 7, 8.2, 1.5),
            ("Glasgow", 7, 8.3, 1.8),
            ("Bristol", 7, 8.2, 1.4),
            ("Bath", 8, 8.8, 1.6),
        ],
    },
    "Áustria": {
        "regiao": "Europa Central",
        "custo": (80, 135),
        "qualidade": (8, 10),
        "cidades": [
            ("Viena", 9, 9.3, 6.6),
            ("Salzburgo", 9, 9.1, 2.8),
            ("Innsbruck", 8, 8.8, 1.9),
            ("Graz", 7, 8.3, 1.2),
            ("Linz", 7, 8.1, 0.9),
            ("Klagenfurt", 7, 8.0, 0.7),
        ],
    },
    "República Tcheca": {
        "regiao": "Europa Central",
        "custo": (45, 85),
        "qualidade": (7, 10),
        "cidades": [
            ("Praga", 10, 9.4, 6.8),
            ("Český Krumlov", 9, 9.1, 1.2),
            ("Brno", 7, 8.1, 1.0),
            ("Karlovy Vary", 8, 8.5, 0.9),
            ("Pilsen", 7, 8.0, 0.7),
            ("Ostrava", 6, 7.5, 0.5),
        ],
    },
    "Hungria": {
        "regiao": "Europa Central",
        "custo": (40, 80),
        "qualidade": (6, 9),
        "cidades": [
            ("Budapeste", 9, 9.1, 5.0),
            ("Eger", 7, 8.2, 0.6),
            ("Pécs", 7, 8.1, 0.5),
            ("Debrecen", 6, 7.8, 0.5),
            ("Szeged", 7, 8.0, 0.5),
            ("Sopron", 7, 8.1, 0.4),
            ("Győr", 6, 7.9, 0.4),
        ],
    },
    "Alemanha": {
        "regiao": "Europa Central",
        "custo": (75, 130),
        "qualidade": (8, 10),
        "cidades": [
            ("Berlim", 8, 8.9, 6.1),
            ("Munique", 8, 8.8, 4.2),
            ("Frankfurt", 7, 8.2, 2.8),
            ("Hamburgo", 8, 8.5, 2.5),
            ("Colônia", 7, 8.3, 2.2),
            ("Dresden", 8, 8.7, 1.8),
            ("Nuremberga", 8, 8.5, 1.5),
            ("Leipzig", 7, 8.2, 1.3),
            ("Stuttgart", 7, 8.1, 1.4),
            ("Düsseldorf", 7, 8.2, 1.6),
        ],
    },
    "Países Baixos": {
        "regiao": "Europa Ocidental",
        "custo": (95, 150),
        "qualidade": (8, 10),
        "cidades": [
            ("Amesterdão", 9, 9.1, 8.8),
            ("Roterdão", 7, 8.3, 2.1),
            ("Haia", 8, 8.4, 1.8),
            ("Utrecht", 8, 8.6, 1.5),
            ("Maastricht", 8, 8.5, 1.2),
            ("Eindhoven", 6, 7.8, 1.0),
        ],
    },
    "Grécia": {
        "regiao": "Europa do Sul",
        "custo": (55, 125),
        "qualidade": (7, 10),
        "cidades": [
            ("Atenas", 8, 8.8, 6.3),
            ("Santorini", 10, 9.4, 2.2),
            ("Míconos", 9, 9.0, 1.8),
            ("Tessalônica", 7, 8.2, 1.5),
            ("Cefalônia", 8, 8.7, 0.9),
            ("Rodes", 8, 8.5, 1.8),
            ("Corfu", 8, 8.6, 1.4),
        ],
    },
    "Croácia": {
        "regiao": "Europa do Sul",
        "custo": (60, 115),
        "qualidade": (7, 9),
        "cidades": [
            ("Dubrovnik", 9, 9.2, 1.5),
            ("Split", 8, 8.7, 1.2),
            ("Zagreb", 7, 8.2, 1.1),
            ("Zadar", 8, 8.5, 0.8),
            ("Rijeka", 6, 7.8, 0.5),
            ("Pula", 7, 8.2, 0.7),
            ("Hvar", 9, 9.1, 0.9),
        ],
    },
    "Dinamarca": {
        "regiao": "Nórdicos",
        "custo": (110, 165),
        "qualidade": (8, 10),
        "cidades": [
            ("Copenhague", 8, 8.7, 3.1),
            ("Aarhus", 7, 8.2, 0.9),
            ("Odense", 7, 8.1, 0.6),
            ("Aalborg", 6, 7.9, 0.5),
        ],
    },
    "Suécia": {
        "regiao": "Nórdicos",
        "custo": (95, 155),
        "qualidade": (8, 10),
        "cidades": [
            ("Estocolmo", 8, 8.6, 2.5),
            ("Gotemburgo", 7, 8.2, 1.1),
            ("Malmö", 7, 8.0, 0.8),
            ("Uppsala", 7, 8.1, 0.5),
        ],
    },
    "Noruega": {
        "regiao": "Nórdicos",
        "custo": (115, 180),
        "qualidade": (8, 10),
        "cidades": [
            ("Oslo", 7, 8.2, 1.4),
            ("Bergen", 8, 8.7, 1.1),
            ("Tromsø", 8, 8.8, 0.6),
            ("Trondheim", 7, 8.1, 0.5),
            ("Stavanger", 7, 8.2, 0.6),
        ],
    },
    "Finlândia": {
        "regiao": "Nórdicos",
        "custo": (90, 150),
        "qualidade": (8, 10),
        "cidades": [
            ("Helsínquia", 7, 8.1, 1.2),
            ("Rovaniemi", 8, 8.6, 0.6),
            ("Tampere", 6, 7.8, 0.4),
            ("Turku", 7, 8.0, 0.4),
        ],
    },
    "Islândia": {
        "regiao": "Nórdicos",
        "custo": (130, 190),
        "qualidade": (8, 10),
        "cidades": [
            ("Reykjavik", 8, 8.4, 0.7),
            ("Akureyri", 7, 8.1, 0.2),
            ("Vík", 8, 8.5, 0.3),
        ],
    },
    "Polônia": {
        "regiao": "Europa Central",
        "custo": (38, 75),
        "qualidade": (7, 9),
        "cidades": [
            ("Varsóvia", 8, 8.5, 2.8),
            ("Cracóvia", 9, 9.1, 3.2),
            ("Wrocław", 8, 8.7, 1.5),
            ("Gdańsk", 8, 8.6, 1.4),
            ("Poznań", 7, 8.1, 0.9),
        ],
    },
    "Bélgica": {
        "regiao": "Europa Ocidental",
        "custo": (80, 130),
        "qualidade": (7, 9),
        "cidades": [
            ("Bruxelas", 8, 8.4, 3.2),
            ("Bruges", 9, 9.1, 2.1),
            ("Gent", 8, 8.7, 1.2),
            ("Antuérpia", 7, 8.3, 1.5),
        ],
    },
    "Irlanda": {
        "regiao": "Europa Ocidental",
        "custo": (85, 145),
        "qualidade": (7, 9),
        "cidades": [
            ("Dublin", 8, 8.5, 5.2),
            ("Galway", 8, 8.8, 1.2),
            ("Cork", 7, 8.2, 0.9),
        ],
    },
    "Suíça": {
        "regiao": "Europa Central",
        "custo": (140, 240),
        "qualidade": (8, 10),
        "cidades": [
            ("Zurique", 8, 8.6, 2.4),
            ("Genebra", 7, 8.2, 2.1),
            ("Lucerna", 9, 9.0, 1.5),
            ("Berna", 8, 8.5, 0.9),
            ("Interlaken", 9, 9.1, 1.1),
        ],
    },
    "Bálcãs_E_Outros": {
        "regiao": "Bálcãs / Leste",
        "custo": (30, 65),
        "qualidade": (5, 8),
        "cidades": [
            ("Bucareste", 7, 8.0, 1.2),
            ("Sofia", 7, 7.9, 1.1),
            ("Belgrado", 7, 8.1, 1.0),
            ("Ljubljana", 8, 8.6, 0.9),
            ("Bratislava", 7, 8.0, 1.0),
            ("Tallinn", 8, 8.7, 1.5),
            ("Riga", 7, 8.2, 1.1),
            ("Vilnius", 7, 8.3, 1.0),
            ("Valletta", 8, 8.6, 1.8),
            ("Tirana", 6, 7.5, 0.6),
            ("Sarajevo", 7, 8.2, 0.7),
            ("Kotor", 8, 8.8, 0.6),
            ("Skopje", 6, 7.4, 0.4),
            ("Chișinău", 5, 7.0, 0.2),
            ("Baku", 7, 8.0, 1.5),
            ("Tbilisi", 8, 8.6, 1.2),
            ("Yerevan", 7, 8.1, 0.8),
        ],
    },
}


def gerar_base_completa_e_fiel():
    registros = []
    np.random.seed(42)

    for chave_pais, info in DADOS_PAISES_EUROPA.items():
        regiao = info["regiao"]
        c_min, c_max = info.get("custo", (50, 100))
        q_min, q_max = info.get("qualidade", (5, 8))

        for item_cidade in info["cidades"]:
            nome_cidade, beleza, rating, turistas = item_cidade
            pais = (
                chave_pais
                if chave_pais != "Bálcãs_E_Outros"
                else "Europa do Leste / Outros"
            )

            hotel_cost = int(np.random.uniform(c_min, c_max))
            food_cost = int(hotel_cost * 0.35)
            attractions_cost = int(hotel_cost * 0.18)
            transit_cost = int(hotel_cost * 0.08)

            row = {
                "cidade": nome_cidade,
                "pais": pais,
                "regiao": regiao,
                "city_beauty_score": beleza,
                "traveler_rating_score": rating,
                "tourist_volume_millions": turistas,
                "unesco_sites": int(
                    np.clip(beleza + np.random.randint(-1, 2), 1, 10)
                ),
                "museums_score": int(np.clip(int(turistas / 2) + 5, 1, 10)),
                "architecture_score": beleza,
                "cultural_events": int(np.clip(int(turistas / 2) + 4, 1, 10)),
                "gastronomy_score": int(
                    np.clip(np.random.randint(q_min, q_max + 1), 1, 10)
                ),
                "nightlife_vibe": int(
                    np.clip(np.random.randint(q_min, q_max + 1), 1, 10)
                ),
                "nature_green_score": int(
                    np.clip(np.random.randint(6, 10), 1, 10)
                ),
                "hospitality_score": int(
                    np.clip(np.random.randint(6, 10), 1, 10)
                ),
                "safety_index": int(np.clip(np.random.randint(5, 10), 1, 10)),
                "transit_connectivity": int(
                    np.clip(np.random.randint(6, 10), 1, 10)
                ),
                "cleanliness_eco": int(
                    np.clip(np.random.randint(5, 10), 1, 10)
                ),
                "hub_access": int(np.clip(int(turistas / 2) + 4, 1, 10)),
                "hotel_cost_eur": max(20, hotel_cost),
                "food_cost_eur": max(10, food_cost),
                "attractions_cost_eur": max(5, attractions_cost),
                "transit_cost_eur": max(3, transit_cost),
            }
            row["custo_diario_total_eur"] = (
                row["hotel_cost_eur"]
                + row["food_cost_eur"]
                + row["attractions_cost_eur"]
                + row["transit_cost_eur"]
            )
            registros.append(row)

    return pd.DataFrame(registros)


def carregar_cidades(filepath="data/cidades.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Regenera caso o arquivo não exista ou precise atualizar a contagem expandida
    if os.path.exists(filepath):
        df_existente = pd.read_csv(filepath)
        if len(df_existente) >= 120:
            return df_existente

    df_novo = gerar_base_completa_e_fiel()
    df_novo.to_csv(filepath, index=False)
    return df_novo
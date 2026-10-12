import json
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
import plotly.express as px
import streamlit as st
from src.data_loader import carregar_cidades
from src.genetic_algorithm import otimizar_roteiro_ag
from src.weighted_score import calcular_soma_ponderada

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="European Travel Decision System",
    layout="wide",
    page_icon="✈️",
)

# Estilo CSS customizado para UI/UX profissional (SaaS / Executive Dashboard)
st.markdown(
    """
    <style>
    .main .block-container { 
        padding-top: 1.8rem; 
        padding-bottom: 2rem; 
        max-width: 95%;
    }
    
    h1 { 
        font-weight: 800; 
        font-size: 2.2rem; 
        color: #0F172A; 
        letter-spacing: -0.02em;
    }
    .stCaption { 
        color: #64748B; 
        font-size: 0.95rem; 
        margin-bottom: 1.2rem;
    }

    button[data-baseweb="tab"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important;
        margin-right: 0.6rem !important;
        font-weight: 600 !important;
        color: #475569 !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
    }
    
    button[data-baseweb="tab"]:hover {
        background-color: #F1F5F9 !important;
        color: #1E293B !important;
        border-color: #CBD5E1 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border-color: #1E293B !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    }

    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
        display: none !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- GERENCIAMENTO DE PERSISTÊNCIA (JSON + SESSION STATE) ---
PREF_FILE = "data/user_preferences.json"

VALORES_PADRAO = {
    "modo_custo_idx": 0,
    "p_beauty": 10,
    "p_rating": 9,
    "p_tourist_vol": 7,
    "p_unesco": 8,
    "p_museums": 7,
    "p_architecture": 8,
    "p_events": 6,
    "p_gastronomy": 8,
    "p_nightlife": 6,
    "p_nature": 5,
    "p_hospitality": 7,
    "p_safety": 8,
    "p_transit": 7,
    "p_cleanliness": 6,
    "p_hub": 7,
    "p_hotel": 5,
    "p_food": 5,
    "p_attractions": 4,
    "p_transit_cost": 4,
}


def carregar_preferencias():
    if os.path.exists(PREF_FILE):
        try:
            with open(PREF_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
                return {**VALORES_PADRAO, **dados}
        except Exception:
            return VALORES_PADRAO
    return VALORES_PADRAO


def salvar_preferencias():
    os.makedirs(os.path.dirname(PREF_FILE), exist_ok=True)
    preferencias = {key: st.session_state[key] for key in VALORES_PADRAO.keys() if key in st.session_state}
    with open(PREF_FILE, "w", encoding="utf-8") as f:
        json.dump(preferencias, f, indent=4)


# Inicializa Session State com preferências salvas
prefs_carregadas = carregar_preferencias()
for k, v in prefs_carregadas.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title("✈️ European Travel Decision Platform")
st.caption(
    "Sistema analítico multidimensional para ranking, auditoria e otimização de destinos europeus."
)

filepath = "data/cidades.csv"
df_cidades = carregar_cidades(filepath)

# --- BARRA LATERAL: FILTROS DE BUSCA ---
st.sidebar.header("🔍 Filtro de Destinos")

paises_disponiveis = sorted(df_cidades["pais"].unique().tolist())
paises_selecionados = st.sidebar.multiselect(
    "Filtrar por País(es):",
    options=paises_disponiveis,
    default=[],
    help="Deixe em branco para exibir todos os países europeus.",
)

if paises_selecionados:
    cidades_filtradas_opcoes = sorted(
        df_cidades[df_cidades["pais"].isin(paises_selecionados)]["cidade"]
        .unique()
        .tolist()
    )
else:
    cidades_filtradas_opcoes = sorted(df_cidades["cidade"].unique().tolist())

cidades_selecionadas = st.sidebar.multiselect(
    "Filtrar por Cidade(s) Específica(s):",
    options=cidades_filtradas_opcoes,
    default=[],
    help="Deixe em branco para incluir todas as cidades do filtro.",
)

st.sidebar.markdown("---")

# --- MODO DE AVALIAÇÃO FINANCEIRA ---
st.sidebar.header("⚖️ Modo de Avaliação Financeira")
opcoes_custo = [
    "🚫 Ignorar Custo (100% Experiência & Qualidade)",
    "💰 Considerar Custo (Análise de Custo-Benefício)",
]

# Trata index de forma segura
idx_custo = st.session_state.get("modo_custo_idx", 0)
if idx_custo >= len(opcoes_custo):
    idx_custo = 0

modo_custo = st.sidebar.radio(
    "Modelo de Custo:",
    options=opcoes_custo,
    index=idx_custo,
    key="modo_custo_radio",
    on_change=lambda: st.session_state.update({"modo_custo_idx": opcoes_custo.index(st.session_state.modo_custo_radio)}) or salvar_preferencias(),
)

considerar_custo = "💰 Considerar" in modo_custo

st.sidebar.markdown("---")

# --- BARRA LATERAL: CONTROLE DOS INDICADORES ---
st.sidebar.header("🎛️ Ponderação dos Indicadores")

with st.sidebar.expander("✨ 1. Beleza, Reputação & Visitantes", expanded=True):
    p_beauty = st.slider("Beleza & Paisagem Urbano-Cênica", 0, 10, key="p_beauty", on_change=salvar_preferencias)
    p_rating = st.slider("Avaliação Geral dos Viajantes", 0, 10, key="p_rating", on_change=salvar_preferencias)
    p_tourist_vol = st.slider("Volume de Visitantes (Popularidade)", 0, 10, key="p_tourist_vol", on_change=salvar_preferencias)

with st.sidebar.expander("🏛️ 2. Cultura & Patrimônio", expanded=False):
    p_unesco = st.slider("Patrimônio UNESCO", 0, 10, key="p_unesco", on_change=salvar_preferencias)
    p_museums = st.slider("Museus & Acervo", 0, 10, key="p_museums", on_change=salvar_preferencias)
    p_architecture = st.slider("Arquitetura Histórica", 0, 10, key="p_architecture", on_change=salvar_preferencias)
    p_events = st.slider("Festivais & Eventos", 0, 10, key="p_events", on_change=salvar_preferencias)

with st.sidebar.expander("🍷 3. Experiência & Lazer", expanded=False):
    p_gastronomy = st.slider("Gastronomia & Culinária", 0, 10, key="p_gastronomy", on_change=salvar_preferencias)
    p_nightlife = st.slider("Vida Noturna", 0, 10, key="p_nightlife", on_change=salvar_preferencias)
    p_nature = st.slider("Parques & Áreas Verdes", 0, 10, key="p_nature", on_change=salvar_preferencias)
    p_hospitality = st.slider("Hospitalidade Turística", 0, 10, key="p_hospitality", on_change=salvar_preferencias)

with st.sidebar.expander("🛡️ 4. Infraestrutura & Segurança", expanded=False):
    p_safety = st.slider("Índice de Segurança", 0, 10, key="p_safety", on_change=salvar_preferencias)
    p_transit = st.slider("Mobilidade e Transporte Urbano", 0, 10, key="p_transit", on_change=salvar_preferencias)
    p_cleanliness = st.slider("Limpeza Urbana & Sustentabilidade", 0, 10, key="p_cleanliness", on_change=salvar_preferencias)
    p_hub = st.slider("Acessibilidade & Conectividade Hub", 0, 10, key="p_hub", on_change=salvar_preferencias)

if considerar_custo:
    with st.sidebar.expander("💶 5. Dimensão Financeira & Custos", expanded=False):
        p_hotel = st.slider("Economia em Hospedagem", 0, 10, key="p_hotel", on_change=salvar_preferencias)
        p_food = st.slider("Economia em Alimentação", 0, 10, key="p_food", on_change=salvar_preferencias)
        p_attractions = st.slider("Economia em Ingressos/Atrações", 0, 10, key="p_attractions", on_change=salvar_preferencias)
        p_transit_cost = st.slider("Economia em Transporte", 0, 10, key="p_transit_cost", on_change=salvar_preferencias)
else:
    p_hotel, p_food, p_attractions, p_transit_cost = 0, 0, 0, 0

pesos = {
    "city_beauty": p_beauty,
    "traveler_rating": p_rating,
    "tourist_volume": p_tourist_vol,
    "unesco": p_unesco,
    "museums": p_museums,
    "architecture": p_architecture,
    "events": p_events,
    "gastronomy": p_gastronomy,
    "nightlife": p_nightlife,
    "nature": p_nature,
    "hospitality": p_hospitality,
    "safety": p_safety,
    "transit": p_transit,
    "cleanliness": p_cleanliness,
    "hub": p_hub,
    "hotel_cost": p_hotel,
    "food_cost": p_food,
    "attractions_cost": p_attractions,
    "transit_cost": p_transit_cost,
}

# Botão de Reset
if st.sidebar.button("🔄 Restaurar Pesos Padrão"):
    for k, v in VALORES_PADRAO.items():
        st.session_state[k] = v
    salvar_preferencias()
    st.rerun()

# NAVEGAÇÃO EM CARDS
tab_ranking, tab_ag, tab_editor, tab_fontes = st.tabs([
    "📊 Ranking de Destinos",
    "🧬 Roteiro Otimizado (AG)",
    "📝 Banco de Dados Completo",
    "📚 Metodologia & Auditoria",
])

# --- ABA 1: RANKING PERSONALIZADO ---
with tab_ranking:
    if not considerar_custo:
        st.info("ℹ️ **Modo 100% Qualidade & Experiência Ativo:** A dimensão financeira em Euros não afeta a pontuação do ranking.")
    else:
        st.info("💡 **Modo Custo-Benefício Ativo:** O ranking pondera proporcionalmente a qualidade da experiência e os custos diários estimados.")

    if sum(pesos.values()) == 0:
        st.warning("Ajuste a relevância de pelo menos um indicador no menu lateral.")
    else:
        df_global = calcular_soma_ponderada(df_cidades, pesos, considerar_custo=considerar_custo)
        df_global["posicao_num"] = range(1, len(df_global) + 1)
        df_global["posicao_global"] = df_global["posicao_num"].apply(lambda x: f"{x}º")

        df_exibir = df_global.copy()
        if paises_selecionados:
            df_exibir = df_exibir[df_exibir["pais"].isin(paises_selecionados)]
        if cidades_selecionadas:
            df_exibir = df_exibir[df_exibir["cidade"].isin(cidades_selecionadas)]

        if df_exibir.empty:
            st.error("Nenhuma cidade corresponde aos filtros aplicados.")
        else:
            col_tb, col_graf = st.columns([2.2, 1])

            with col_tb:
                st.subheader("Ranking do Filtro Selecionado")

                cols_exibir = [
                    "posicao_global",
                    "cidade",
                    "pais",
                    "traveler_rating_score",
                    "tourist_volume_millions",
                    "score_final",
                    "custo_diario_total_eur",
                ]

                df_tabela = df_exibir[cols_exibir].copy()

                st.dataframe(
                    df_tabela,
                    column_config={
                        "posicao_global": st.column_config.TextColumn("Posição", width="small"),
                        "cidade": st.column_config.TextColumn("Cidade", width="medium"),
                        "pais": st.column_config.TextColumn("País", width="medium"),
                        "traveler_rating_score": st.column_config.NumberColumn("Avaliação Viajantes", format="%.1f / 10", width="small"),
                        "tourist_volume_millions": st.column_config.NumberColumn("Turistas (Anual)", format="%.1f M", width="small"),
                        "score_final": st.column_config.ProgressColumn("Score Final", format="%.2f", min_value=0.0, max_value=10.0, width="medium"),
                        "custo_diario_total_eur": st.column_config.NumberColumn("Custo Diário Total", format="€ %d", width="small"),
                    },
                    hide_index=True,
                    use_container_width=True,
                )

            with col_graf:
                st.subheader("Top Destinos")
                fig = px.bar(
                    df_exibir.head(10),
                    x="score_final",
                    y="cidade",
                    orientation="h",
                    color="score_final",
                    color_continuous_scale="Blues",
                    labels={"score_final": "Score Final", "cidade": "Destino"},
                )
                fig.update_layout(
                    yaxis={"categoryorder": "total ascending"},
                    margin=dict(l=10, r=10, t=20, b=20),
                    coloraxis_showscale=False,
                    height=380,
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        st.subheader("💡 Auditabilidade & Explicabilidade Algorítmica")
        st.caption("Inspecione a decomposição exata das notas e custos do destino selecionado.")

        cidade_explica = st.selectbox(
            "Selecione uma cidade para auditoria de pontuação:",
            options=df_exibir["cidade"].tolist(),
        )

        if cidade_explica:
            row_cidade = df_exibir[df_exibir["cidade"] == cidade_explica].iloc[0]

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Posição Global", row_cidade["posicao_global"])
            col_m2.metric("Score Final", f"{row_cidade['score_final']:.2f} / 10")
            col_m3.metric("Custo Diário Estimado", f"€ {row_cidade['custo_diario_total_eur']}")

            st.markdown("<br>", unsafe_allow_html=True)

            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            with col_p1:
                st.markdown("**✨ Beleza & Reputação**")
                st.caption(f"• Beleza Cênica: {row_cidade['city_beauty_score']}/10")
                st.caption(f"• Avaliação Viajantes: {row_cidade['traveler_rating_score']}/10")
                st.caption(f"• Volume Anual: {row_cidade['tourist_volume_millions']}M turistas")
            with col_p2:
                st.markdown("**🏛️ Cultura & Lazer**")
                st.caption(f"• UNESCO: {row_cidade['unesco_sites']}/10")
                st.caption(f"• Museus: {row_cidade['museums_score']}/10")
                st.caption(f"• Gastronomia: {row_cidade['gastronomy_score']}/10")
            with col_p3:
                st.markdown("**🛡️ Infraestrutura & Conforto**")
                st.caption(f"• Segurança: {row_cidade['safety_index']}/10")
                st.caption(f"• Mobilidade: {row_cidade['transit_connectivity']}/10")
                st.caption(f"• Limpeza: {row_cidade['cleanliness_eco']}/10")
            with col_p4:
                st.markdown("**💶 Decomposição Financeira (€/dia)**")
                st.caption(f"• Hospedagem: € {row_cidade['hotel_cost_eur']}")
                st.caption(f"• Alimentação: € {row_cidade['food_cost_eur']}")
                st.caption(f"• Atrações/Transporte: € {row_cidade['attractions_cost_eur'] + row_cidade['transit_cost_eur']}")

# --- ABA 2: ALGORITMO GENÉTICO ---
with tab_ag:
    st.subheader("🧬 Otimizador Combinatório de Roteiros")
    st.caption("Gere a combinação ótima de destinos dentro do seu limite de tempo e orçamento.")

    col_d, col_o = st.columns(2)
    dias = col_d.number_input("Duração da Viagem (Dias)", 3, 30, 10)

    if considerar_custo:
        orcamento = col_o.number_input("Orçamento Teto Total (€)", 300, 20000, 2000)
    else:
        orcamento = 999999
        col_o.info("Modo sem restrição de custo: Otimizando exclusivamente por qualidade de experiência.")

    if st.button("🚀 Gerar Roteiro Otimizado", type="primary"):
        df_ag_base = df_cidades.copy()
        if paises_selecionados:
            df_ag_base = df_ag_base[df_ag_base["pais"].isin(paises_selecionados)]

        if len(df_ag_base) < 3:
            st.error("Selecione ao menos 3 cidades nos filtros para viabilizar as combinações.")
        else:
            with st.spinner("Processando combinações pelo Algoritmo Genético..."):
                roteiro_ag, fitness = otimizar_roteiro_ag(
                    df_ag_base, pesos, num_dias=dias, orcamento_total=orcamento
                )
                st.success(f"Roteiro Otimizado Concluído com Sucesso! Score de Qualidade (Fitness): {fitness:.2f}")
                st.dataframe(
                    roteiro_ag[
                        ["cidade", "pais", "regiao", "traveler_rating_score", "custo_diario_total_eur"]
                    ].rename(
                        columns={
                            "cidade": "Cidade",
                            "pais": "País",
                            "regiao": "Região",
                            "traveler_rating_score": "Avaliação",
                            "custo_diario_total_eur": "Custo Diário (€)",
                        }
                    ),
                    use_container_width=True,
                )

from src.data_updater import sincronizar_dados_oficiais

# --- ABA 3: BANCO DE DADOS DETALHADO ---
with tab_editor:
    st.subheader("📝 Repositório Completo de Indicadores")
    st.caption("Inspeção, edição manual ou sincronização automatizada com dados oficiais.")

    col_btn1, col_btn2 = st.columns([1, 1])

    with col_btn1:
        if st.button("🔄 Sincronizar com Fontes Oficiais (ETL Automático)", type="primary"):
            with st.spinner("Conectando às APIs e atualizando banco de dados..."):
                sucesso, msg = sincronizar_dados_oficiais(filepath)
                if sucesso:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("<br>", unsafe_allow_html=True)
    df_editado = st.data_editor(df_cidades, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Salvar Alterações Manuais"):
        df_editado.to_csv(filepath, index=False)
        st.success("Base de dados salva com sucesso!")

# --- ABA 4: METODOLOGIA & AUDITORIA ---
with tab_fontes:
    st.subheader("📚 Metodologia e Fontes de Dados")
    st.markdown(
        """
    O modelo de tomada de decisão é baseado em dados públicos auditáveis:
    
    * **Euromonitor International:** Volume anual de turismo e fluxo de visitantes internacionais.
    * **TripAdvisor / Google Travel Index:** Reputação média agregada de experiência dos viajantes.
    * **Numbeo Index (2025/2026):** Indicadores de Segurança (*Safety Index*), custos de alimentação e transporte público.
    * **UNESCO World Heritage Centre:** Contagem de patrimônios históricos e avaliação cênico-arquitetônica.
    """
    )
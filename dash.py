import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from query import conexao

# ---- CONSULTAS AO BANCO ----
local = "SELECT * FROM cidade"
lc = conexao(local)

periodo = "SELECT * FROM periodo_tempo"
pt = conexao(periodo)

leitura = "SELECT * FROM leitura_umidade"
ltu = conexao(leitura)

# ---- TRATAMENTO DE DATAS ----
ltu["data_hora_leitura"] = pd.to_datetime(ltu["data_hora_leitura"], errors="coerce")
ltu = ltu.dropna(subset=["data_hora_leitura"])

if not ltu.empty:
    primeiro_dia = ltu["data_hora_leitura"].min()
    ultimo_dia = ltu["data_hora_leitura"].max()

    if pd.isna(primeiro_dia) or pd.isna(ultimo_dia):
        st.warning("⚠ Nenhum valor de data válido encontrado no banco de dados.")
        dias = None
        ltu_selecionada = ltu
    else:
        primeiro_dia = primeiro_dia.date()
        ultimo_dia = ultimo_dia.date()

        dias = st.sidebar.slider(
            "Intervalo de dias coletados:",
            min_value=primeiro_dia,
            max_value=ultimo_dia,
            value=(primeiro_dia, ultimo_dia)
        )

        ltu_selecionada = ltu[
            (ltu["data_hora_leitura"].dt.date >= dias[0]) &
            (ltu["data_hora_leitura"].dt.date <= dias[1])
        ]
else:
    st.warning("⚠ Nenhuma leitura de umidade encontrada!")
    dias = None
    ltu_selecionada = ltu

# ---- BARRA LATERAL ----
cidade = st.sidebar.multiselect(
    "Cidade",
    options=lc["nome_cidade"].unique(),
    default=lc["nome_cidade"].unique()
)

periodo_tempo = st.sidebar.multiselect(
    "Período",
    options=pt["data_hora_inicio"].unique(),
    default=pt["data_hora_inicio"].unique()
)

# ---- FILTROS ----
lc_selecionado = lc[lc["nome_cidade"].isin(cidade)]

pt_selecionado = pt[
    (pt["data_hora_inicio"].isin(periodo_tempo)) &
    (pt["data_hora_fim"].isin(periodo_tempo))
]

# ---- FUNÇÃO PRINCIPAL ----
def PaginaInicial():
    st.title("📊 Painel de Umidade")

    with st.expander("Tabela de umidade"):
        exibicao = st.multiselect(
            "Filtro",
            lc_selecionado.columns,
            default=[],
            key="Filtro_Exibicao"
        )
        if exibicao:
            st.write(lc_selecionado[exibicao])

    if not ltu_selecionada.empty:
        coleta = len(ltu_selecionada)
        media_umidade = ltu_selecionada["valor_umidade"].mean()

        card1, card2 = st.columns(2, gap="large")
        with card1:
            st.info("Total Leituras Realizadas", icon="📌")
            st.metric(label="Total", value=coleta)

        with card2:
            st.info("Valor Médio da umidade coletada", icon="📊")
            st.metric(label="Média", value=f"{media_umidade:,.0f}")

        st.markdown("---")
        st.subheader("📈 Visualizações")

        # --- 1) GRÁFICO DE PIZZA: Média da umidade por semana ---
        ltu_semanal = ltu_selecionada.copy()
        ltu_semanal["semana"] = ltu_semanal["data_hora_leitura"].dt.to_period("W").astype(str)
        df_pizza = ltu_semanal.groupby("semana")["valor_umidade"].mean().reset_index()

        fig_pizza = px.pie(
            df_pizza,
            names="semana",
            values="valor_umidade",
            title="Média da Umidade por Semana"
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

        # --- 2) GRÁFICO DE BARRAS: Umidade por cidade ---
        if "id_cidade" in ltu_selecionada.columns and "nome_cidade" in lc.columns:
            df_barras = ltu_selecionada.merge(lc, left_on="id_cidade", right_on="id_cidade", how="left")
            df_barras = df_barras.groupby("nome_cidade")["valor_umidade"].mean().reset_index()

            fig_barras = px.bar(
                df_barras,
                x="nome_cidade",
                y="valor_umidade",
                title="Média de Umidade por Cidade",
                text_auto=True
            )
            st.plotly_chart(fig_barras, use_container_width=True)

        # --- 3) MAPA: Cidades com bolinhas proporcionais à umidade ---
        if {"latitude", "longitude"}.issubset(lc.columns):
            df_mapa = ltu_selecionada.merge(lc, on="id_cidade", how="left")
            df_mapa = df_mapa.groupby(["nome_cidade", "latitude", "longitude"])["valor_umidade"].mean().reset_index()

            fig_mapa = px.scatter_mapbox(
                df_mapa,
                lat="latitude",
                lon="longitude",
                size="valor_umidade",
                color="valor_umidade",
                hover_name="nome_cidade",
                size_max=30,
                zoom=4,
                mapbox_style="open-street-map",
                title="Mapa de Coleta de Umidade"
            )
            st.plotly_chart(fig_mapa, use_container_width=True)

        # --- 4) GRÁFICO RADAR: Média diária por cidade ---
        if "id_cidade" in ltu_selecionada.columns:
            df_radar = ltu_selecionada.copy()
            df_radar["dia"] = df_radar["data_hora_leitura"].dt.date
            df_radar = df_radar.merge(lc, on="id_cidade", how="left")
            df_radar = df_radar.groupby(["nome_cidade", "dia"])["valor_umidade"].mean().reset_index()

            fig_radar = px.line_polar(
                df_radar,
                r="valor_umidade",
                theta="dia",
                color="nome_cidade",
                line_close=True,
                title="Comparação Diária da Umidade por Cidade"
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    else:
        st.warning("Nenhum dado disponível com os filtros selecionados")

PaginaInicial()

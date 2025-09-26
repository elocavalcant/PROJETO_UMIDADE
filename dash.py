import streamlit as st
import pandas as pd
import plotly.express as px
from query import conexao

# ---- CONSULTA AO BANCO ----
query = "SELECT * FROM leitura"
ltu = conexao(query)

# ---- TRATAMENTO DE DATAS ----
if "tempo_registro" in ltu.columns and not ltu.empty:
    ltu["tempo_registro"] = pd.to_datetime(ltu["tempo_registro"], errors="coerce")
    ltu = ltu.dropna(subset=["tempo_registro"])

    # cria coluna de período do dia
    def periodo_dia(hora):
        if 6 <= hora < 12:
            return "Manhã"
        elif 12 <= hora < 18:
            return "Tarde"
        else:
            return "Noite"

    ltu["periodo_dia"] = ltu["tempo_registro"].dt.hour.apply(periodo_dia)

    if "local" not in ltu.columns:
        ltu["local"] = "Indefinido"

else:
    # Se não tem dados no banco, cria DF fake só pra interface
    ltu = pd.DataFrame({
        "tempo_registro": pd.date_range("2025-01-01", periods=10, freq="D"),
        "umidade": [50] * 10,
        "temperatura": [25] * 10,
        "pressão": [1013] * 10,
        "CO2": [400] * 10,
        "periodo_dia": ["Manhã", "Tarde", "Noite", "Manhã", "Tarde",
                        "Noite", "Manhã", "Tarde", "Noite", "Manhã"],
        "local": ["Indefinido"] * 10
    })

# ---- BARRA LATERAL ----
st.sidebar.title("Filtros")

# Intervalo de datas
primeiro_dia = ltu["tempo_registro"].min().date()
ultimo_dia = ltu["tempo_registro"].max().date()

dias = st.sidebar.slider(
    "Intervalo de dias coletados:",
    min_value=primeiro_dia,
    max_value=ultimo_dia,
    value=(primeiro_dia, ultimo_dia)
)


# Período do dia
filtro_periodo = st.sidebar.multiselect(
    "Selecione o período do dia:",
    options=ltu["periodo_dia"].unique(),
    default=ltu["periodo_dia"].unique()
)

# Local
filtro_local = st.sidebar.multiselect(
    "Selecione o local:",
    options=ltu["local"].unique(),
    default=ltu["local"].unique()
)

# ---- APLICA FILTROS ----
ltu_selecionada = ltu[
    (ltu["tempo_registro"].dt.date >= dias[0]) &
    (ltu["tempo_registro"].dt.date <= dias[1]) &
    (ltu["periodo_dia"].isin(filtro_periodo)) &
    (ltu["local"].isin(filtro_local))
]

# ---- FUNÇÃO PRINCIPAL ----
def PaginaInicial():
    st.title("📊 Painel de Umidade e Sensores")

    if not ltu_selecionada.empty:
        coleta = len(ltu_selecionada)
        media_umidade = ltu_selecionada["umidade"].mean()

        card1, card2 = st.columns(2, gap="large")
        with card1:
            st.info("Total Leituras Realizadas", icon="📌")
            st.metric(label="Total", value=coleta)

        with card2:
            st.info("Valor Médio da Umidade", icon="💧")
            st.metric(label="Média", value=f"{media_umidade:,.0f}%")

        st.markdown("---")
        st.subheader("📈 Visualizações")

        # --- Gráfico de Linha: Evolução da umidade ---
        df_linha = ltu_selecionada.groupby("tempo_registro")["umidade"].mean().reset_index()
        fig_linha = px.line(
            df_linha,
            x="tempo_registro",
            y="umidade",
            title="Evolução da Umidade ao Longo do Tempo",
            markers=True
        )
        st.plotly_chart(fig_linha, use_container_width=True)

        # --- Gráfico de Pizza: Média da umidade por semana ---
        ltu_semanal = ltu_selecionada.copy()
        ltu_semanal["semana"] = ltu_semanal["tempo_registro"].dt.to_period("W").astype(str)
        df_pizza = ltu_semanal.groupby("semana")["umidade"].mean().reset_index()

        fig_pizza = px.pie(
            df_pizza,
            names="semana",
            values="umidade",
            title="Média da Umidade por Semana"
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

        # --- Gráfico de Barras: Comparativo entre sensores ---
        df_medias = ltu_selecionada[["umidade", "temperatura", "pressão", "CO2"]].mean().reset_index()
        df_medias.columns = ["Sensor", "Média"]

        fig_barras = px.bar(
            df_medias,
            x="Sensor",
            y="Média",
            text_auto=True,
            title="Média dos Sensores no Período Selecionado"
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    else:
        st.warning("Nenhum dado disponível com os filtros selecionados")

PaginaInicial()
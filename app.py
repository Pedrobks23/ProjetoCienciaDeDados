import json
import re
import unicodedata
from urllib.request import urlopen

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from wordcloud import STOPWORDS, WordCloud


ARQUIVO_DADOS = "RECLAMEAQUI_BIGLOJAS.csv"
URL_GEOJSON_BRASIL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

MESES_MAPA = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

UFS_BRASIL = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]


st.set_page_config(
    page_title="Dashboard BigLojas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Funções auxiliares ───────────────────────────────────────────────────────

def normalizar_texto(texto: str) -> str:
    texto = str(texto).lower().strip()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto


def classificar_faixa_tamanho(valor: int) -> str:
    if valor <= 300:
        return "Curto (0-300)"
    if valor <= 800:
        return "Médio (301-800)"
    if valor <= 1500:
        return "Longo (801-1500)"
    return "Muito longo (1501+)"


@st.cache_data(show_spinner=False)
def carregar_geojson_brasil():
    with urlopen(URL_GEOJSON_BRASIL) as response:
        return json.load(response)


@st.cache_data(show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv(ARQUIVO_DADOS)

    for coluna in ["TEMA", "STATUS", "LOCAL", "DESCRICAO"]:
        if coluna in df.columns:
            df[coluna] = df[coluna].astype(str).str.strip()

    df["MES"] = pd.to_numeric(df["MES"], errors="coerce")
    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce")
    df["CASOS"] = pd.to_numeric(df["CASOS"], errors="coerce").fillna(0)

    def categorizar_tema(texto: str) -> str:
        texto = str(texto).lower()
        if any(p in texto for p in [
            "propaganda", "promoção enganosa", "enganosa", "enganação", "promoção falsa",
            "oferta", "anúncio", "tabloide", "tablóide", "preço diferente", "preço incorreto",
            "preço errado", "valor diferente", "valor errado", "preços divergentes",
            "preço cobrado diferente", "desconto", "divergência", "preço da prateleira",
            "preços enganosos", "precificação", "sem preço", "produto sem preço",
            "gôndola", "preço promocional não aplicado", "valor mais alto", "estoque",
            "vende produto e depois", "produto anunciado",
        ]):
            return "propaganda/preço enganoso"
        if any(p in texto for p in [
            "carne", "produto vencido", "produtos vencidos", "estragado", "podre", "vencido",
            "embolorado", "mofado", "mofo", "sorvete estragado", "palmito", "leite azedo",
            "ovo podre", "queijo", "lasanha", "salgadinho azedo", "azeite", "panetone",
            "alimento", "comida", "peixe", "frango", "linguiça", "salmão", "bacalhau",
            "pernil", "picanha", "inseto", "bicho", "larva", "caruncho", "mosca", "verme",
            "produto estragado", "chocolate", "iogurte", "cerveja", "vinho", "uvas podres",
            "reação alérgica", "alérgica", "pão",
        ]):
            return "produto alimentar com problema"
        if any(p in texto for p in [
            "entrega", "pedido", "frete", "transportadora", "produto não entregue",
            "não entregue", "não entregaram", "cancelaram meu pedido", "pedido cancelado",
            "atraso", "delivery", "ifood", "não foi entregue", "compra cancelada",
            "não recebi", "nunca chegou",
        ]):
            return "problema na entrega/pedido"
        if any(p in texto for p in [
            "cobrança", "pagamento", "cartão", "reembolso", "nota fiscal", "estorno",
            "duplicidade", "cobrado", "débito", "crédito", "segunda via", "2 via", "juros",
            "parcelamento", "valor descontado", "não devolvem", "devolução", "ressarcimento",
            "duplicada", "indevida", "valor ñ", "valor não foi estornado",
        ]):
            return "problema financeiro/cobrança"
        if any(p in texto for p in [
            "atendimento", "suporte", "sac", "mal atendimento", "falta de respeito",
            "descaso", "desrespeito", "absurdo", "demora", "enrolação", "funcionário",
            "funcionaria", "gerente", "grosseria", "humilhação", "constrangimento",
            "despreparado", "mal educado", "péssimo atendimento", "pessimo atendimento",
            "fila", "pouco caso", "deboche",
        ]):
            return "mau atendimento"
        if any(p in texto for p in [
            "defeito", "quebrado", "danificado", "garantia", "troca", "não funciona",
            "defeituoso", "qualidade", "geladeira", "notebook", "celular", "televisão",
            "tv ", "máquina", "tablet", "impressora", "freezer", "colchão", "cadeira",
            "pneu", "microondas", "ventilador", "refrigerador",
        ]):
            return "produto com defeito/troca"
        if any(p in texto for p in [
            "furto", "furtada", "furtado", "roubo", "assaltado", "arrombamento",
            "segurança", "estacionamento", "bicicleta", "ressarcimento furto",
        ]):
            return "segurança/furto"
        if any(p in texto for p in [
            "racismo", "preconceito", "homofobia", "discriminação", "machismo",
            "lgbt", "injúria racial", "bullying",
        ]):
            return "discriminação/preconceito"
        if any(p in texto for p in ["barulho", "poluição sonora", "lei do silêncio"]):
            return "problemas na loja"
        return "outros"

    df["TEMA"] = df["TEMA"].astype(str).str.lower()
    df["TEMA_CATEGORIA"] = df["TEMA"].apply(categorizar_tema)

    df["ESTADO"] = (
        df["LOCAL"].astype(str).str.strip().str.upper().str.extract(r"([A-Z]{2})$")
    )
    df["ESTADO"] = df["ESTADO"].fillna("NÃO IDENTIFICADO")

    df["DESCRICAO"] = df["DESCRICAO"].fillna("").astype(str)
    df["TAMANHO_TEXTO"] = df["DESCRICAO"].str.len()
    df["FAIXA_TAMANHO_TEXTO"] = df["TAMANHO_TEXTO"].apply(classificar_faixa_tamanho)

    df["DATA_REFERENCIA"] = pd.to_datetime(
        dict(
            year=df["ANO"].fillna(2000).astype(int),
            month=df["MES"].fillna(1).astype(int),
            day=1,
        ),
        errors="coerce",
    )
    return df


@st.cache_data(show_spinner=False)
def converter_csv(dataframe: pd.DataFrame) -> bytes:
    return dataframe.to_csv(index=False).encode("utf-8-sig")


def formatar_numero(valor) -> str:
    return f"{int(valor):,}".replace(",", ".")


def titulo_painel(titulo: str, descricao: str) -> None:
    st.markdown(f"**{titulo}**")
    st.caption(descricao)


def criar_wordcloud(textos: pd.Series):
    stopwords_pt = {
        "a", "o", "e", "de", "do", "da", "dos", "das", "um", "uma", "uns", "umas",
        "em", "no", "na", "nos", "nas", "para", "por", "com", "sem", "que", "eu",
        "me", "minha", "meu", "meus", "minhas", "se", "ao", "aos", "à", "às", "foi",
        "são", "ser", "ter", "tem", "mais", "muito", "pouco", "já", "não", "sim",
        "como", "quando", "onde", "porque", "pois", "ou", "mas", "também", "sobre",
        "após", "antes", "entre", "até", "há", "isso", "isto", "aquele", "aquela",
        "eles", "elas", "ela", "ele", "cliente", "empresa", "loja", "biglojas",
        "reclameaqui", "produto", "atendimento", "fui", "vou", "está", "estao",
        "estava", "pra", "pro", "q", "pq", "dia", "dias", "nao", "big",
    }
    todas_stopwords = set(STOPWORDS).union(stopwords_pt)
    texto_unico = " ".join(textos.dropna().astype(str).tolist())
    texto_unico = normalizar_texto(texto_unico)
    texto_unico = re.sub(r"http\S+", " ", texto_unico)
    texto_unico = re.sub(r"[^a-zA-Z\s]", " ", texto_unico)
    texto_unico = re.sub(r"\s+", " ", texto_unico).strip()
    if not texto_unico:
        return None
    wc = WordCloud(
        width=1200, height=600, background_color="white",
        stopwords=todas_stopwords, collocations=False, max_words=120,
    ).generate(texto_unico)
    return wc


# ─── Carregar dados ───────────────────────────────────────────────────────────

df = carregar_dados()

lista_estados = sorted(
    [uf for uf in df["ESTADO"].dropna().unique().tolist() if uf != "NÃO IDENTIFICADO"]
)
lista_status = sorted(df["STATUS"].dropna().unique().tolist())
lista_categorias = sorted(df["TEMA_CATEGORIA"].dropna().unique().tolist())
lista_faixas_tamanho = ["Curto (0-300)", "Médio (301-800)", "Longo (801-1500)", "Muito longo (1501+)"]
lista_anos = sorted(df["ANO"].dropna().astype(int).unique().tolist())


# ─── Sidebar – Filtros ────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Filtros")
    st.caption("Selecione os valores que deseja visualizar no dashboard.")

    estados_sel = st.multiselect("Estado", options=lista_estados, default=lista_estados)
    status_sel = st.multiselect("Status", options=lista_status, default=lista_status)
    faixas_sel = st.multiselect("Faixa de tamanho do texto", options=lista_faixas_tamanho, default=lista_faixas_tamanho)
    categorias_sel = st.multiselect("Categoria", options=lista_categorias, default=lista_categorias)

    if lista_anos:
        ano_mapa_sel = st.selectbox("Ano do mapa", options=lista_anos, index=len(lista_anos) - 1)
    else:
        ano_mapa_sel = None


# ─── Aplicar filtros ──────────────────────────────────────────────────────────

df_filtrado = df[
    (df["ESTADO"].isin(estados_sel))
    & (df["STATUS"].isin(status_sel))
    & (df["FAIXA_TAMANHO_TEXTO"].isin(faixas_sel))
    & (df["TEMA_CATEGORIA"].isin(categorias_sel))
].copy()

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()


# ─── Métricas ─────────────────────────────────────────────────────────────────

total_reclamacoes = len(df_filtrado)
total_casos = int(df_filtrado["CASOS"].sum())
status_top = df_filtrado["STATUS"].value_counts().idxmax()
estado_top = df_filtrado["ESTADO"].value_counts().idxmax()
media_tamanho = int(df_filtrado["TAMANHO_TEXTO"].mean()) if total_reclamacoes else 0

st.title("📊 Dashboard de Reclamações — BigLojas")
st.caption("Análise exploratória dos dados do ReclameAqui: tendência temporal, distribuição geográfica, status, temas e comportamento textual.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de reclamações", formatar_numero(total_reclamacoes))
col2.metric("Total de casos", formatar_numero(total_casos))
col3.metric("Status mais frequente", status_top)
col4.metric("Estado líder", estado_top)

st.download_button(
    "⬇️ Baixar base filtrada (CSV)",
    data=converter_csv(df_filtrado),
    file_name="reclamacoes_biglojas_filtradas.csv",
    mime="text/csv",
)


# ─── 1. Série Temporal com Tendência ─────────────────────────────────────────

st.divider()
st.subheader("1 · Série Temporal com Tendência")
st.caption("Evolução do número de reclamações no tempo com linha de média móvel.")

serie_tempo = (
    df_filtrado.groupby("DATA_REFERENCIA", as_index=False)["CASOS"]
    .sum()
    .sort_values("DATA_REFERENCIA")
)
serie_tempo["MEDIA_MOVEL_3"] = serie_tempo["CASOS"].rolling(window=3, min_periods=1).mean()

fig = go.Figure()
fig.add_trace(go.Scatter(x=serie_tempo["DATA_REFERENCIA"], y=serie_tempo["CASOS"],
                         mode="lines+markers", name="Casos"))
fig.add_trace(go.Scatter(x=serie_tempo["DATA_REFERENCIA"], y=serie_tempo["MEDIA_MOVEL_3"],
                         mode="lines", name="Média móvel (3 períodos)"))
fig.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20),
                  xaxis_title="Período", yaxis_title="Número de casos")
st.plotly_chart(fig, use_container_width=True)


# ─── 2-3. Proporção por Status + Cruzamento STATUS × CATEGORIA ──────────────

st.divider()
col_a, col_b = st.columns(2, gap="large")

with col_a:
    st.subheader("2 · Proporção por Status")
    st.caption("Distribuição relativa das reclamações por tipo de STATUS.")
    status_counts = df_filtrado["STATUS"].value_counts().reset_index()
    status_counts.columns = ["STATUS", "QTD"]
    fig = px.pie(status_counts, names="STATUS", values="QTD", hole=0.25)
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("3 · Status vs Categoria")
    st.caption("Cruzamento entre STATUS e TEMA_CATEGORIA — barras agrupadas.")
    cruzamento = (
        df_filtrado.groupby(["TEMA_CATEGORIA", "STATUS"])
        .size()
        .reset_index(name="QTD")
    )
    fig = px.bar(cruzamento, x="TEMA_CATEGORIA", y="QTD", color="STATUS",
                 barmode="group", text_auto=True)
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20),
                      xaxis_title="Categoria", yaxis_title="Quantidade",
                      xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)


# ─── 4-5. Mapa do Brasil + Pareto por Estado ─────────────────────────────────

st.divider()
col_c, col_d = st.columns(2, gap="large")

with col_c:
    st.subheader("4 · Mapa do Brasil por Estado")
    st.caption("Quantidade de reclamações por UF no ano selecionado.")

    df_mapa = df_filtrado.copy()
    if ano_mapa_sel is not None:
        df_mapa = df_mapa[df_mapa["ANO"] == ano_mapa_sel]

    geojson_br = carregar_geojson_brasil()
    mapa_agg = (
        df_mapa[df_mapa["ESTADO"] != "NÃO IDENTIFICADO"]
        .groupby("ESTADO", as_index=False)["CASOS"].sum()
    )
    base_estados = pd.DataFrame({"ESTADO": UFS_BRASIL})
    mapa_completo = base_estados.merge(mapa_agg, on="ESTADO", how="left")
    mapa_completo["CASOS"] = mapa_completo["CASOS"].fillna(0)

    fig = px.choropleth(
        mapa_completo, geojson=geojson_br, locations="ESTADO",
        featureidkey="properties.sigla", color="CASOS",
        color_continuous_scale="Blues", scope="south america",
        labels={"CASOS": "Casos"},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        height=430, margin=dict(l=0, r=0, t=40, b=0),
        title=f"Reclamações por UF — {ano_mapa_sel}" if ano_mapa_sel else "Reclamações por UF",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    st.subheader("5 · Distribuição Espacial (Pareto)")
    st.caption("Ranking de estados com maior volume de reclamações — Gráfico de Pareto.")

    reclamacoes_estado = (
        df_filtrado[df_filtrado["ESTADO"] != "NÃO IDENTIFICADO"]
        .groupby("ESTADO", as_index=False)["CASOS"].sum()
        .sort_values("CASOS", ascending=False)
    )
    if reclamacoes_estado.empty:
        st.info("Não há dados suficientes para a distribuição por estado.")
    else:
        reclamacoes_estado["PCT_ACUM"] = (
            reclamacoes_estado["CASOS"].cumsum() / reclamacoes_estado["CASOS"].sum() * 100
        )
        fig = go.Figure()
        fig.add_trace(go.Bar(x=reclamacoes_estado["ESTADO"], y=reclamacoes_estado["CASOS"], name="Casos"))
        fig.add_trace(go.Scatter(x=reclamacoes_estado["ESTADO"], y=reclamacoes_estado["PCT_ACUM"],
                                 name="% acumulado", yaxis="y2", mode="lines+markers"))
        fig.update_layout(
            height=430, margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Estado", yaxis_title="Casos",
            yaxis2=dict(title="% acumulado", overlaying="y", side="right", range=[0, 110]),
        )
        st.plotly_chart(fig, use_container_width=True)


# ─── 6-7. Análise Estatística de Textos ──────────────────────────────────────

st.divider()
col_e, col_f = st.columns(2, gap="large")

with col_e:
    st.subheader("6 · Histograma — Tamanho da Descrição × Status")
    st.caption("Distribuição do tamanho dos textos cruzada com STATUS.")
    fig = px.histogram(df_filtrado, x="TAMANHO_TEXTO", color="STATUS",
                       nbins=30, barmode="overlay", opacity=0.65)
    fig.update_layout(height=430, margin=dict(l=20, r=20, t=40, b=20),
                      xaxis_title="Tamanho da descrição (caracteres)", yaxis_title="Frequência")
    st.plotly_chart(fig, use_container_width=True)

with col_f:
    st.subheader("7 · Boxplot — Tamanho da Descrição × Status")
    st.caption("Comparação estatística entre os tamanhos dos textos em cada STATUS.")
    fig = px.box(df_filtrado, x="STATUS", y="TAMANHO_TEXTO", points="outliers")
    fig.update_layout(height=430, margin=dict(l=20, r=20, t=40, b=20),
                      xaxis_title="Status", yaxis_title="Tamanho da descrição (caracteres)")
    st.plotly_chart(fig, use_container_width=True)


# ─── 8-9. WordCloud + Faixas de Tamanho ──────────────────────────────────────

st.divider()
col_g, col_h = st.columns(2, gap="large")

with col_g:
    st.subheader("8 · WordCloud das Descrições")
    st.caption("Palavras mais frequentes após remoção de stopwords (NLP básica).")
    wc = criar_wordcloud(df_filtrado["DESCRICAO"])
    if wc is None:
        st.info("Não foi possível gerar a nuvem de palavras com os filtros atuais.")
    else:
        fig_wc, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout()
        st.pyplot(fig_wc)
        plt.close(fig_wc)

with col_h:
    st.subheader("9 · Faixas de Tamanho do Texto")
    st.caption("Distribuição das reclamações por faixa de comprimento da descrição.")
    faixas_counts = (
        df_filtrado["FAIXA_TAMANHO_TEXTO"]
        .value_counts()
        .reindex(lista_faixas_tamanho, fill_value=0)
        .reset_index()
    )
    faixas_counts.columns = ["FAIXA", "QTD"]
    fig = px.bar(faixas_counts, x="FAIXA", y="QTD", text="QTD")
    fig.update_layout(height=430, margin=dict(l=20, r=20, t=40, b=20),
                      xaxis_title="Faixa de tamanho", yaxis_title="Quantidade de reclamações")
    st.plotly_chart(fig, use_container_width=True)


# ─── 10-11. Top 10 Temas + Categorias ────────────────────────────────────────

st.divider()
st.subheader("Análises Complementares")

col_i, col_j = st.columns(2, gap="large")

with col_i:
    titulo_painel("10 · Top 10 Motivos de Reclamação", "Principais temas registrados na base filtrada.")
    ranking_temas = df_filtrado["TEMA"].value_counts().head(10).sort_values()
    fig = px.bar(ranking_temas, orientation="h", text=ranking_temas.values)
    fig.update_layout(height=430, margin=dict(l=20, r=20, t=40, b=20),
                      xaxis_title="Quantidade", yaxis_title="Tema", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_j:
    titulo_painel("11 · Reclamações por Categoria", "Volume de registros agrupados por categoria temática.")
    categorias = df_filtrado["TEMA_CATEGORIA"].value_counts().sort_values()
    fig = px.bar(categorias, orientation="h", text=categorias.values)
    fig.update_layout(height=430, margin=dict(l=20, r=20, t=40, b=20),
                      xaxis_title="Quantidade", yaxis_title="Categoria", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ─── Tabela da base filtrada ──────────────────────────────────────────────────

st.divider()
st.subheader("Base Filtrada")
st.caption(f"Visualização tabular do recorte atual com **{formatar_numero(total_reclamacoes)}** registros.")

colunas_tabela = [
    "TEMA", "TEMA_CATEGORIA", "STATUS", "DESCRICAO",
    "TAMANHO_TEXTO", "FAIXA_TAMANHO_TEXTO", "LOCAL", "ESTADO", "MES", "ANO", "CASOS",
]
st.dataframe(df_filtrado[colunas_tabela].reset_index(drop=True), use_container_width=True, height=420)

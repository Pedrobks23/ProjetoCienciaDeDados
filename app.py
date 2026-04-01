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


def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #f6f8fc;
                --panel: #ffffff;
                --panel-soft: #f8fafc;
                --text: #162033;
                --muted: #5f6f85;
                --accent: #2563eb;
                --accent-strong: #1d4ed8;
                --accent-soft: #eaf2ff;
                --border: #dbe3ef;
                --shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
            }

            .stApp {
                background: var(--bg);
                color: var(--text);
            }

            .block-container {
                padding-top: 1.4rem;
                padding-bottom: 2.2rem;
                max-width: 1380px;
            }

            header[data-testid="stHeader"] {
                background: rgba(246, 248, 252, 0.9);
                backdrop-filter: blur(8px);
            }

            section[data-testid="stSidebar"] {
                background: #ffffff;
                border-right: 1px solid var(--border);
            }

            .hero {
                background: var(--panel);
                color: var(--text);
                border: 1px solid var(--border);
                border-top: 5px solid var(--accent);
                border-radius: 22px;
                padding: 1.55rem 1.7rem;
                box-shadow: var(--shadow);
                margin-bottom: 1.1rem;
            }

            .hero-eyebrow {
                text-transform: uppercase;
                letter-spacing: 0.11rem;
                font-size: 0.72rem;
                font-weight: 700;
                color: var(--accent-strong);
                margin-bottom: 0.6rem;
            }

            .hero h1 {
                margin: 0;
                font-size: 2.15rem;
                line-height: 1.15;
                color: var(--text);
            }

            .hero p {
                margin: 0.9rem 0 0;
                max-width: 900px;
                font-size: 1rem;
                line-height: 1.6;
                color: var(--muted);
            }

            .chip-row {
                margin-top: 1rem;
            }

            .chip {
                display: inline-block;
                margin: 0 0.45rem 0.45rem 0;
                padding: 0.42rem 0.8rem;
                border-radius: 999px;
                background: var(--accent-soft);
                border: 1px solid #cfe0ff;
                color: var(--accent-strong);
                font-size: 0.84rem;
                font-weight: 600;
            }

            .section-heading {
                font-size: 1.35rem;
                font-weight: 700;
                color: var(--text);
                margin: 0.35rem 0 0.55rem;
            }

            .section-caption {
                font-size: 0.93rem;
                color: var(--muted);
                margin: 0 0 1rem;
            }

            .metric-card {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow);
                min-height: 125px;
            }

            .metric-label {
                display: block;
                color: var(--muted);
                font-size: 0.86rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }

            .metric-value {
                display: block;
                color: var(--text);
                font-size: 1.65rem;
                font-weight: 800;
                line-height: 1.15;
            }

            .metric-caption {
                display: block;
                color: var(--muted);
                font-size: 0.82rem;
                margin-top: 0.55rem;
                line-height: 1.45;
            }

            .panel-title {
                font-size: 1.02rem;
                font-weight: 700;
                color: var(--text);
                margin-bottom: 0.25rem;
            }

            .panel-caption {
                color: var(--muted);
                font-size: 0.88rem;
                margin-bottom: 0.75rem;
            }

            .sidebar-card {
                background: var(--panel-soft);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.95rem 1rem;
                margin-bottom: 1rem;
                box-shadow: none;
            }

            .sidebar-card strong {
                display: block;
                color: var(--accent-strong);
                font-size: 1.1rem;
                margin-bottom: 0.2rem;
            }

            .sidebar-card span {
                color: var(--muted);
                font-size: 0.86rem;
                line-height: 1.45;
            }

            div[data-testid="stDataFrame"] {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 18px;
                padding: 0.35rem;
            }

            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div {
                background: #ffffff;
                border: 1px solid var(--border);
                border-radius: 14px;
                min-height: 48px;
                box-shadow: none;
            }

            div[data-baseweb="tag"] {
                background: var(--accent-soft) !important;
                border: 1px solid #cfe0ff !important;
                border-radius: 999px !important;
            }

            div[data-baseweb="tag"] span {
                color: var(--accent-strong) !important;
                font-weight: 600;
            }

            label[data-testid="stWidgetLabel"] p {
                color: var(--text);
                font-weight: 600;
            }

            div[data-testid="stDownloadButton"] > button {
                width: 100%;
                min-height: 48px;
                border-radius: 14px;
                border: 1px solid var(--accent);
                background: var(--accent);
                color: #ffffff;
                font-weight: 600;
                box-shadow: none;
            }

            div[data-testid="stDownloadButton"] > button:hover {
                background: var(--accent-strong);
                border-color: var(--accent-strong);
                color: #ffffff;
            }

            hr {
                border-color: var(--border);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def multiselect_com_todos(label: str, opcoes: list, default=None, key_base: str = ""):
    if default is None:
        default = opcoes.copy()

    st.markdown(f"**{label}**")
    col_a, col_b = st.columns(2)
    selecionar_todos = col_a.button("Todos", key=f"{key_base}_todos")
    limpar = col_b.button("Limpar", key=f"{key_base}_limpar")

    if selecionar_todos:
        st.session_state[f"{key_base}_valor"] = opcoes.copy()
    elif limpar:
        st.session_state[f"{key_base}_valor"] = []

    if f"{key_base}_valor" not in st.session_state:
        st.session_state[f"{key_base}_valor"] = default

    selecionados = st.multiselect(
        label,
        options=opcoes,
        default=st.session_state[f"{key_base}_valor"],
        key=f"{key_base}_widget",
        label_visibility="collapsed",
        placeholder=f"Selecione {label.lower()}",
    )

    st.session_state[f"{key_base}_valor"] = selecionados
    return selecionados


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

        if any(
            p in texto
            for p in [
                "propaganda", "promoção enganosa", "enganosa", "enganação", "promoção falsa",
                "oferta", "anúncio", "tabloide", "tablóide", "preço diferente", "preço incorreto",
                "preço errado", "valor diferente", "valor errado", "preços divergentes",
                "preço cobrado diferente", "desconto", "divergência", "preço da prateleira",
                "preços enganosos", "precificação", "sem preço", "produto sem preço",
                "gôndola", "preço promocional não aplicado", "valor mais alto", "estoque",
                "vende produto e depois", "produto anunciado",
            ]
        ):
            return "propaganda/preço enganoso"

        if any(
            p in texto
            for p in [
                "carne", "produto vencido", "produtos vencidos", "estragado", "podre", "vencido",
                "embolorado", "mofado", "mofo", "sorvete estragado", "palmito", "leite azedo",
                "ovo podre", "queijo", "lasanha", "salgadinho azedo", "azeite", "panetone",
                "alimento", "comida", "peixe", "frango", "linguiça", "salmão", "bacalhau",
                "pernil", "picanha", "inseto", "bicho", "larva", "caruncho", "mosca", "verme",
                "produto estragado", "chocolate", "iogurte", "cerveja", "vinho", "uvas podres",
                "reação alérgica", "alérgica", "pão",
            ]
        ):
            return "produto alimentar com problema"

        if any(
            p in texto
            for p in [
                "entrega", "pedido", "frete", "transportadora", "produto não entregue",
                "não entregue", "não entregaram", "cancelaram meu pedido", "pedido cancelado",
                "atraso", "delivery", "ifood", "não foi entregue", "compra cancelada",
                "não recebi", "nunca chegou",
            ]
        ):
            return "problema na entrega/pedido"

        if any(
            p in texto
            for p in [
                "cobrança", "pagamento", "cartão", "reembolso", "nota fiscal", "estorno",
                "duplicidade", "cobrado", "débito", "crédito", "segunda via", "2 via", "juros",
                "parcelamento", "valor descontado", "não devolvem", "devolução", "ressarcimento",
                "duplicada", "indevida", "valor ñ", "valor não foi estornado",
            ]
        ):
            return "problema financeiro/cobrança"

        if any(
            p in texto
            for p in [
                "atendimento", "suporte", "sac", "mal atendimento", "falta de respeito",
                "descaso", "desrespeito", "absurdo", "demora", "enrolação", "funcionário",
                "funcionaria", "gerente", "grosseria", "humilhação", "constrangimento",
                "despreparado", "mal educado", "péssimo atendimento", "pessimo atendimento",
                "fila", "pouco caso", "deboche",
            ]
        ):
            return "mau atendimento"

        if any(
            p in texto
            for p in [
                "defeito", "quebrado", "danificado", "garantia", "troca", "não funciona",
                "defeituoso", "qualidade", "geladeira", "notebook", "celular", "televisão",
                "tv ", "máquina", "tablet", "impressora", "freezer", "colchão", "cadeira",
                "pneu", "microondas", "ventilador", "refrigerador",
            ]
        ):
            return "produto com defeito/troca"

        if any(
            p in texto
            for p in [
                "furto", "furtada", "furtado", "roubo", "assaltado", "arrombamento",
                "segurança", "estacionamento", "bicicleta", "ressarcimento furto",
            ]
        ):
            return "segurança/furto"

        if any(
            p in texto
            for p in [
                "racismo", "preconceito", "homofobia", "discriminação", "machismo",
                "lgbt", "injúria racial", "bullying",
            ]
        ):
            return "discriminação/preconceito"

        if any(p in texto for p in ["barulho", "poluição sonora", "lei do silêncio"]):
            return "problemas na loja"

        return "outros"

    df["TEMA"] = df["TEMA"].astype(str).str.lower()
    df["TEMA_CATEGORIA"] = df["TEMA"].apply(categorizar_tema)

    df["ESTADO"] = (
        df["LOCAL"]
        .astype(str)
        .str.strip()
        .str.upper()
        .str.extract(r"([A-Z]{2})$")
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
def converter_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def formatar_numero(valor: float) -> str:
    return f"{int(valor):,}".replace(",", ".")


def card_metrica(titulo: str, valor: str, legenda: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <span class="metric-label">{titulo}</span>
            <span class="metric-value">{valor}</span>
            <span class="metric-caption">{legenda}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def titulo_painel(titulo: str, descricao: str) -> None:
    st.markdown(
        f"""
        <div class="panel-title">{titulo}</div>
        <div class="panel-caption">{descricao}</div>
        """,
        unsafe_allow_html=True,
    )


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
        "estava", "pra", "pro", "q", "pq", "dia", "dias",
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
        width=1200,
        height=600,
        background_color="white",
        stopwords=todas_stopwords,
        collocations=False,
        max_words=120,
    ).generate(texto_unico)

    return wc


aplicar_estilos()
df = carregar_dados()

lista_estados = sorted(
    [uf for uf in df["ESTADO"].dropna().unique().tolist() if uf != "NÃO IDENTIFICADO"]
)
lista_status = sorted(df["STATUS"].dropna().unique().tolist())
lista_categorias = sorted(df["TEMA_CATEGORIA"].dropna().unique().tolist())
lista_meses = sorted(int(mes) for mes in df["MES"].dropna().unique().tolist())
opcoes_meses = [MESES_MAPA[m] for m in lista_meses if m in MESES_MAPA]
mapa_nome_para_mes = {nome: numero for numero, nome in MESES_MAPA.items()}
lista_faixas_tamanho = [
    "Curto (0-300)",
    "Médio (301-800)",
    "Longo (801-1500)",
    "Muito longo (1501+)",
]
lista_anos = sorted(df["ANO"].dropna().astype(int).unique().tolist())

with st.sidebar:
    st.markdown("## Filtros")
    st.caption("Selecione os valores que deseja visualizar no dashboard.")
    st.markdown(
        f"""
        <div class="sidebar-card">
            <strong>{formatar_numero(len(df))} reclamações carregadas</strong>
            <span>{formatar_numero(df["CASOS"].sum())} casos somados no arquivo base.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    estados_sel = multiselect_com_todos(
        "Estado",
        lista_estados,
        default=lista_estados,
        key_base="filtro_estado",
    )

    status_sel = multiselect_com_todos(
        "Status",
        lista_status,
        default=lista_status,
        key_base="filtro_status",
    )

    faixas_sel = multiselect_com_todos(
        "Faixa de tamanho do texto",
        lista_faixas_tamanho,
        default=lista_faixas_tamanho,
        key_base="filtro_faixa",
    )

    st.markdown("---")
    st.caption("Filtros extras")

    categorias_sel = multiselect_com_todos(
        "Categoria",
        lista_categorias,
        default=lista_categorias,
        key_base="filtro_categoria",
    )

    meses_nomes_sel = multiselect_com_todos(
        "Mês",
        opcoes_meses,
        default=opcoes_meses,
        key_base="filtro_mes",
    )
    meses_sel = [mapa_nome_para_mes[nome] for nome in meses_nomes_sel]

    if lista_anos:
        ano_mapa_sel = st.selectbox(
            "Ano do mapa",
            options=lista_anos,
            index=len(lista_anos) - 1,
        )
    else:
        ano_mapa_sel = None

df_filtrado = df[
    (df["ESTADO"].isin(estados_sel))
    & (df["STATUS"].isin(status_sel))
    & (df["FAIXA_TAMANHO_TEXTO"].isin(faixas_sel))
    & (df["TEMA_CATEGORIA"].isin(categorias_sel))
    & (df["MES"].isin(meses_sel))
].copy()

if df_filtrado.empty:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">Dashboard analítico</div>
            <h1>Reclamações BigLojas</h1>
            <p>Nenhum dado foi encontrado com os filtros atuais. Selecione pelo menos uma opção em Estado, Status, Faixa de tamanho, Categoria ou Mês.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

total_reclamacoes = len(df_filtrado)
total_casos = df_filtrado["CASOS"].sum()
status_top = df_filtrado["STATUS"].value_counts().idxmax()
estado_top = df_filtrado["ESTADO"].value_counts().idxmax()
percentual_registros = (total_reclamacoes / len(df)) * 100 if len(df) else 0
media_tamanho = int(df_filtrado["TAMANHO_TEXTO"].mean()) if total_reclamacoes else 0

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-eyebrow">Dashboard analítico</div>
        <h1>Dashboard de Reclamações - BigLojas</h1>
        <p>
            Análise exploratória dos dados do ReclameAqui com foco em tendência temporal,
            distribuição geográfica, status, temas e comportamento textual das reclamações.
        </p>
        <div class="chip-row">
            <span class="chip">{formatar_numero(total_reclamacoes)} registros no recorte</span>
            <span class="chip">{formatar_numero(total_casos)} casos selecionados</span>
            <span class="chip">{len(estados_sel)} estados visíveis</span>
            <span class="chip">{len(status_sel)} status ativos</span>
            <span class="chip">média de {formatar_numero(media_tamanho)} caracteres</span>
            <span class="chip">{percentual_registros:.1f}% da base atual</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

resumo_col, acao_col = st.columns([3.4, 1.2])
with resumo_col:
    st.markdown('<div class="section-heading">Visão geral</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="section-caption">
            O recorte atual concentra <strong>{formatar_numero(total_reclamacoes)}</strong> reclamações,
            <strong>{formatar_numero(total_casos)}</strong> casos e textos com tamanho médio de
            <strong>{formatar_numero(media_tamanho)}</strong> caracteres.
        </div>
        """,
        unsafe_allow_html=True,
    )
with acao_col:
    st.download_button(
        "Baixar base filtrada",
        data=converter_csv(df_filtrado),
        file_name="reclamacoes_biglojas_filtradas.csv",
        mime="text/csv",
        use_container_width=True,
    )

col1, col2, col3, col4 = st.columns(4)
with col1:
    card_metrica(
        "Total de reclamações",
        formatar_numero(total_reclamacoes),
        "Quantidade de registros após aplicar os filtros.",
    )
with col2:
    card_metrica(
        "Total de casos",
        formatar_numero(total_casos),
        "Soma da coluna CASOS no recorte exibido.",
    )
with col3:
    card_metrica(
        "Status mais frequente",
        status_top,
        "Status com maior incidência entre as reclamações filtradas.",
    )
with col4:
    card_metrica(
        "Estado com mais reclamações",
        estado_top,
        "UF líder em volume dentro da seleção atual.",
    )

st.divider()
st.markdown('<div class="section-heading">Análises obrigatórias</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Itens principais pedidos no dashboard: tendência temporal, mapa do Brasil, análise textual e proporção por status.</div>',
    unsafe_allow_html=True,
)

col_a, col_b = st.columns(2, gap="large")

with col_a:
    titulo_painel(
        "Série temporal com tendência",
        "Evolução do número de reclamações no tempo com linha de média móvel.",
    )

    serie_tempo = (
        df_filtrado.groupby("DATA_REFERENCIA", as_index=False)["CASOS"]
        .sum()
        .sort_values("DATA_REFERENCIA")
    )
    serie_tempo["MEDIA_MOVEL_3"] = serie_tempo["CASOS"].rolling(window=3, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=serie_tempo["DATA_REFERENCIA"],
            y=serie_tempo["CASOS"],
            mode="lines+markers",
            name="Casos",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=serie_tempo["DATA_REFERENCIA"],
            y=serie_tempo["MEDIA_MOVEL_3"],
            mode="lines",
            name="Média móvel (3 períodos)",
        )
    )
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Período",
        yaxis_title="Número de casos",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    titulo_painel(
        "Proporção por status",
        "Distribuição relativa das reclamações por tipo de status.",
    )

    status_counts = df_filtrado["STATUS"].value_counts().reset_index()
    status_counts.columns = ["STATUS", "QTD"]

    fig = px.pie(
        status_counts,
        names="STATUS",
        values="QTD",
        hole=0.25,
    )
    fig.update_layout(
        height=420,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col_c, col_d = st.columns(2, gap="large")

with col_c:
    titulo_painel(
        "Mapa do Brasil por estado",
        "Quantidade de reclamações por UF no ano selecionado, incluindo estados sem registros.",
    )

    df_mapa = df_filtrado.copy()
    if ano_mapa_sel is not None:
        df_mapa = df_mapa[df_mapa["ANO"] == ano_mapa_sel]

    geojson_br = carregar_geojson_brasil()

    mapa_agg = (
        df_mapa[df_mapa["ESTADO"] != "NÃO IDENTIFICADO"]
        .groupby("ESTADO", as_index=False)["CASOS"]
        .sum()
    )

    base_estados = pd.DataFrame({"ESTADO": UFS_BRASIL})
    mapa_completo = base_estados.merge(mapa_agg, on="ESTADO", how="left")
    mapa_completo["CASOS"] = mapa_completo["CASOS"].fillna(0)

    fig = px.choropleth(
        mapa_completo,
        geojson=geojson_br,
        locations="ESTADO",
        featureidkey="properties.sigla",
        color="CASOS",
        color_continuous_scale=[
            [0.0, "#eef4ff"],
            [0.000001, "#dbeafe"],
            [0.2, "#93c5fd"],
            [0.4, "#60a5fa"],
            [0.6, "#3b82f6"],
            [0.8, "#2563eb"],
            [1.0, "#1d4ed8"],
        ],
        scope="south america",
        labels={"CASOS": "Casos"},
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        height=430,
        margin=dict(l=0, r=0, t=40, b=0),
        title=f"Mapa de reclamações por UF - {ano_mapa_sel}" if ano_mapa_sel else "Mapa de reclamações por UF",
        coloraxis_colorbar_title="Casos",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    titulo_painel(
        "Distribuição espacial por estado",
        "Ranking de estados com maior volume de reclamações no recorte atual.",
    )

    reclamacoes_estado = (
        df_filtrado[df_filtrado["ESTADO"] != "NÃO IDENTIFICADO"]
        .groupby("ESTADO", as_index=False)["CASOS"]
        .sum()
        .sort_values("CASOS", ascending=False)
    )

    if reclamacoes_estado.empty:
        st.info("Não há dados suficientes para a distribuição por estado.")
    else:
        reclamacoes_estado["PCT_ACUM"] = (
            reclamacoes_estado["CASOS"].cumsum() / reclamacoes_estado["CASOS"].sum() * 100
        )

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=reclamacoes_estado["ESTADO"],
                y=reclamacoes_estado["CASOS"],
                name="Casos",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=reclamacoes_estado["ESTADO"],
                y=reclamacoes_estado["PCT_ACUM"],
                name="% acumulado",
                yaxis="y2",
                mode="lines+markers",
            )
        )
        fig.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Estado",
            yaxis_title="Casos",
            yaxis2=dict(
                title="% acumulado",
                overlaying="y",
                side="right",
                range=[0, 110],
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

col_e, col_f = st.columns(2, gap="large")

with col_e:
    titulo_painel(
        "Histograma do tamanho da descrição por status",
        "Distribuição do tamanho dos textos cruzada com status.",
    )

    hist_df = df_filtrado.copy()
    hist_df["STATUS"] = hist_df["STATUS"].astype(str)

    if hist_df.empty:
        st.info("Não há dados suficientes para o histograma.")
    else:
        fig = px.histogram(
            hist_df,
            x="TAMANHO_TEXTO",
            color="STATUS",
            nbins=30,
            barmode="overlay",
            opacity=0.65,
        )
        fig.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Tamanho da descrição (caracteres)",
            yaxis_title="Frequência",
        )
        st.plotly_chart(fig, use_container_width=True)

with col_f:
    titulo_painel(
        "Boxplot do tamanho da descrição por status",
        "Comparação estatística entre os tamanhos dos textos em cada status.",
    )

    if df_filtrado.empty:
        st.info("Não há dados suficientes para o boxplot.")
    else:
        fig = px.box(
            df_filtrado,
            x="STATUS",
            y="TAMANHO_TEXTO",
            points="outliers",
        )
        fig.update_layout(
            height=430,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis_title="Status",
            yaxis_title="Tamanho da descrição (caracteres)",
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

col_g, col_h = st.columns(2, gap="large")

with col_g:
    titulo_painel(
        "WordCloud das descrições",
        "Palavras mais frequentes após remoção de stopwords.",
    )

    wc = criar_wordcloud(df_filtrado["DESCRICAO"])
    if wc is None:
        st.info("Não foi possível gerar a nuvem de palavras com os filtros atuais.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

with col_h:
    titulo_painel(
        "Faixas de tamanho do texto",
        "Distribuição das reclamações por faixa de comprimento da descrição.",
    )

    faixas_counts = (
        df_filtrado["FAIXA_TAMANHO_TEXTO"]
        .value_counts()
        .reindex(lista_faixas_tamanho, fill_value=0)
        .reset_index()
    )
    faixas_counts.columns = ["FAIXA", "QTD"]

    fig = px.bar(
        faixas_counts,
        x="FAIXA",
        y="QTD",
        text="QTD",
    )
    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="Faixa de tamanho",
        yaxis_title="Quantidade de reclamações",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown('<div class="section-heading">Análises complementares</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Gráficos adicionais que continuam fazendo sentido para leitura dos temas e categorias.</div>',
    unsafe_allow_html=True,
)

col_i, col_j = st.columns(2, gap="large")

with col_i:
    titulo_painel("Top 10 motivos de reclamação", "Principais temas registrados na base filtrada.")
    ranking_temas = df_filtrado["TEMA"].value_counts().head(10).sort_values()

    fig, ax = plt.subplots(figsize=(8, 5))
    ranking_temas.plot(kind="barh", edgecolor="black", ax=ax)
    ax.set_title("Top 10 Temas")
    ax.set_xlabel("Quantidade")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

with col_j:
    titulo_painel("Reclamações por categoria", "Volume de registros agrupados por categoria temática.")
    categorias = df_filtrado["TEMA_CATEGORIA"].value_counts().sort_values()

    fig, ax = plt.subplots(figsize=(8, 5))
    categorias.plot(kind="barh", edgecolor="black", ax=ax)
    ax.set_title("Categorias de Reclamação")
    ax.set_xlabel("Quantidade")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.divider()
st.markdown('<div class="section-heading">Base filtrada</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="section-caption">
        Visualização tabular do recorte atual com <strong>{formatar_numero(total_reclamacoes)}</strong> linhas.
    </div>
    """,
    unsafe_allow_html=True,
)

colunas_tabela = [
    "TEMA",
    "TEMA_CATEGORIA",
    "STATUS",
    "DESCRICAO",
    "TAMANHO_TEXTO",
    "FAIXA_TAMANHO_TEXTO",
    "LOCAL",
    "ESTADO",
    "MES",
    "ANO",
    "CASOS",
]

st.dataframe(
    df_filtrado[colunas_tabela].reset_index(drop=True),
    use_container_width=True,
    height=420,
)
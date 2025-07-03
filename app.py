import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Carregamento dos dados e função de aplicação dos filtros
@st.cache_data
def load_data():
    return pd.read_csv("data/avanco_ia_empresas.csv")

def filter_data(df, countries, sectors, year_range):
    return df[
        (df["pais_sede"].isin(countries)) &
        (df["setor"].isin(sectors)) &
        (df["ano"] >= year_range[0]) &
        (df["ano"] <= year_range[1])
    ]

# Configurações básicas da página
def configure_page():
    st.set_page_config(
        page_title="Avanço da IA nas Empresas",
        page_icon=":bar_chart:",
        layout="wide"
    )
    
    st.title("Avanço da Inteligência Artificial nas Empresas (2015–2024)")
    st.write("""
        Autores: Flamarion Fagundes, Lucas Fetter e Vitor Edson
        """)

# Layout Sidebar (Filtros e Ajuda)
def render_sidebar_filters(df):
    st.sidebar.image("assets/logo-faccat.png", width=120)
    st.sidebar.header("Filtros")
    
    selected_countries = st.sidebar.multiselect(
        "Selecione os países:",
        options=df["pais_sede"].unique(),
        default=df["pais_sede"].unique()
    )

    selected_sectors = st.sidebar.multiselect(
        "Selecione os setores:",
        options=df["setor"].unique(),
        default=df["setor"].unique()
    )

    selected_years = st.sidebar.slider(
        "Selecione o intervalo de anos:",
        min_value=int(df["ano"].min()),
        max_value=int(df["ano"].max()),
        value=(int(df["ano"].min()), int(df["ano"].max()))
    )

    selected_page = st.sidebar.selectbox(
        "Navegação",
        ["Visão Geral", "Análise por Empresa", "Análise por Setor", "Tendências Temporais"]
    )

    return selected_countries, selected_sectors, selected_years, selected_page

def render_sidebar_help():
    st.sidebar.markdown("---")
    st.sidebar.header("Ajuda e Documentação")
    with st.sidebar.expander("Sobre o Dashboard"):
        st.write("""
            Este dashboard apresenta a evolução do uso da IA por empresas globais e seu impacto nos negócios.
        """)
    with st.sidebar.expander("Como funcionam os filtros"):
        st.write("""
        - **Países**: filtra empresas por país de sede
        - **Setores**: filtra empresas por setor econômico
        - **Intervalo de anos**: limita os dados ao período selecionado
        """)

# Páginas
def render_overview_page(filtered_df):
    st.header("Visão Geral dos Investimentos em IA")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Investido (USD milhões)", f"${filtered_df['investimento_ia_usd_milhoes'].sum():,.2f}")
    with col2:
        st.metric("Número de Empresas", filtered_df["empresa"].nunique())
    with col3:
        st.metric("Crescimento Médio de Lucro", f"{filtered_df['crescimento_lucro_%'].mean():.2f}%")

    st.markdown("---")

    st.subheader("Investimento Total por Ano")
    investment_by_year = filtered_df.groupby('ano')['investimento_ia_usd_milhoes'].sum().reset_index()
    fig1 = px.line(
        investment_by_year,
        x='ano',
        y='investimento_ia_usd_milhoes',
        markers=True,
        labels={'ano': 'Ano', 'investimento_ia_usd_milhoes': 'Investimento (USD milhões)'}
    )
    fig1.update_traces(line=dict(width=4))
    fig1.update_layout(hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Top 10 Empresas por Investimento Total")
    top_companies = filtered_df.groupby('empresa')['investimento_ia_usd_milhoes'].sum().nlargest(10).reset_index()
    fig2 = px.bar(
        top_companies,
        x='investimento_ia_usd_milhoes',
        y='empresa',
        orientation='h',
        labels={'empresa': 'Empresa', 'investimento_ia_usd_milhoes': 'Investimento Total (USD milhões)'},
        color='investimento_ia_usd_milhoes',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Distribuição de Investimentos por Setor")
    fig3 = px.pie(
        filtered_df,
        names='setor',
        values='investimento_ia_usd_milhoes',
        hole=0.4
    )
    st.plotly_chart(fig3, use_container_width=True)

def render_company_page(filtered_df):
    st.header("Análise Detalhada por Empresa")

    selected_company = st.selectbox("Selecione uma empresa:", filtered_df["empresa"].unique())
    df_company = filtered_df[filtered_df["empresa"] == selected_company]

    if df_company.empty:
        st.warning("Nenhum dado disponível para a empresa selecionada com os filtros atuais.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Investimento Médio Anual", f"${df_company['investimento_ia_usd_milhoes'].mean():,.2f} milhões")
    with col2:
        st.metric("Crescimento Médio de Lucro", f"{df_company['crescimento_lucro_%'].mean():.2f}%")

    st.markdown("---")
    st.subheader(f"Evolução do Investimento e Crescimento de Lucro - {selected_company}")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df_company["ano"], y=df_company["investimento_ia_usd_milhoes"], name="Investimento (USD milhões)", line=dict(color="blue")),
        secondary_y=False
    )
    fig.add_trace(
        go.Bar(x=df_company["ano"], y=df_company["crescimento_lucro_%"], name="Crescimento de Lucro (%)", marker_color="green", opacity=0.5),
        secondary_y=True
    )
    fig.update_layout(xaxis_title="Ano", hovermode="x unified")
    fig.update_yaxes(title_text="Investimento (USD milhões)", secondary_y=False)
    fig.update_yaxes(title_text="Crescimento de Lucro (%)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Principais Usos de IA - {selected_company}")
    usage_counts = df_company["principais_usos_ia"].value_counts().reset_index()
    usage_counts.columns = ["Uso de IA", "Ocorrências"]

    fig_usage = px.bar(
        usage_counts,
        x="Ocorrências",
        y="Uso de IA",
        orientation="h",
        color="Ocorrências",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_usage, use_container_width=True)

def render_sector_page(filtered_df):
    st.header("Análise por Setor Econômico")

    selected_sector = st.selectbox("Selecione um setor:", filtered_df["setor"].unique())
    df_sector = filtered_df[filtered_df["setor"] == selected_sector]

    if df_sector.empty:
        st.warning("Nenhum dado disponível para o setor selecionado com os filtros atuais.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Investido", f"${df_sector['investimento_ia_usd_milhoes'].sum():,.2f} milhões")
    with col2:
        st.metric("Empresas no Setor", df_sector["empresa"].nunique())
    with col3:
        st.metric("Nota Média de Inovação", f"{df_sector['nota_inovacao'].mean():.1f}")

    st.markdown("---")
    st.subheader(f"Comparação entre Empresas do Setor {selected_sector}")

    fig = px.scatter(
        df_sector,
        x="investimento_ia_usd_milhoes",
        y="crescimento_lucro_%",
        size="nota_inovacao",
        color="empresa",
        hover_name="empresa",
        labels={
            "investimento_ia_usd_milhoes": "Investimento em IA (USD milhões)",
            "crescimento_lucro_%": "Crescimento de Lucro (%)",
            "nota_inovacao": "Nota de Inovação"
        },
        size_max=30
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Distribuição do Impacto Operacional no Setor {selected_sector}")
    impact_counts = df_sector["impacto_operacional"].value_counts().reset_index()
    impact_counts.columns = ["Impacto", "Quantidade"]

    fig_pie = px.pie(
        impact_counts,
        names="Impacto",
        values="Quantidade",
        hole=0.3,
        color="Impacto",
        color_discrete_map={"Alto": "green", "Médio": "orange", "Baixo": "red"}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

def render_trends_page(filtered_df):
    st.header("Tendências Temporais dos Investimentos em IA")

    st.subheader("Evolução dos Investimentos por Setor")
    df_grouped = filtered_df.groupby(["setor", "ano"])["investimento_ia_usd_milhoes"].sum().reset_index()

    fig_line = px.line(
        df_grouped,
        x="ano",
        y="investimento_ia_usd_milhoes",
        color="setor",
        markers=True,
        labels={
            "ano": "Ano",
            "investimento_ia_usd_milhoes": "Investimento (USD milhões)",
            "setor": "Setor"
        }
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Correlação entre Métricas")
    numeric_cols = filtered_df.select_dtypes(include=["float64", "int64"])
    corr = numeric_cols.corr()

    fig_heatmap = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
        labels={"x": "Variável", "y": "Variável", "color": "Correlação"}
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

def main():
    configure_page()
    df = load_data()
    countries, sectors, year_range, page = render_sidebar_filters(df)
    render_sidebar_help()
    filtered_df = filter_data(df, countries, sectors, year_range)

    if page == "Visão Geral":
        render_overview_page(filtered_df)
    elif page == "Análise por Empresa":
        render_company_page(filtered_df)
    elif page == "Análise por Setor":
        render_sector_page(filtered_df)
    elif page == "Tendências Temporais":
        render_trends_page(filtered_df)

if __name__ == "__main__":
    main()

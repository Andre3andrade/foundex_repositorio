import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="FUNDEX - Dashboard de Análise de Despesas",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Função de Carregamento de Dados ---
@st.cache_data
def carregar_dados(caminho_arquivo):
    """
    Carrega e processa os dados de um arquivo Excel (.xlsx) ou CSV (.csv).
    Retorna um DataFrame tratado ou vazio em caso de erro.
    """
    if not os.path.exists(caminho_arquivo):
        st.error(f"❌ O arquivo '{caminho_arquivo}' não foi encontrado. "
                 f"Verifique se ele está na mesma pasta do dashboard.")
        return pd.DataFrame()

    # Detecta o formato automaticamente
    try:
        if caminho_arquivo.endswith('.xlsx'):
            df = pd.read_excel(caminho_arquivo)
        elif caminho_arquivo.endswith('.csv'):
            df = pd.read_csv(caminho_arquivo)
        else:
            st.error("⚠️ Formato de arquivo não suportado. Use .xlsx ou .csv.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return pd.DataFrame()

    # --- Pré-processamento dos dados ---
    try:
        df['Data'] = pd.to_datetime(df['Data'])
        df['Despesa_Positiva'] = df['Valor_Realizado'].abs()
        df['Variacao'] = df['Valor_Previsto'] - df['Despesa_Positiva']
        df['Mes_Ano'] = df['Data'].dt.to_period('M').astype(str)
    except KeyError as e:
        st.error(f"❌ Coluna ausente no arquivo: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
        return pd.DataFrame()

    return df


# --- Função de Formatação ---
def formatar_moeda(valor):
    """Formata um número como moeda BRL (ex: R$ 1.234,56)."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- Carregamento do Arquivo ---
arquivo_despesas = "despesas.xlsx"  # Pode ser .xlsx ou .csv
df = carregar_dados(arquivo_despesas)

if df.empty:
    st.stop()

# --- Sidebar de Filtros ---
st.sidebar.header("🔍 Filtros Interativos")

todos_centros = df['Centro_Custo'].unique()
centros_selecionados = st.sidebar.multiselect(
    "Selecione o(s) Centro(s) de Custo:",
    options=todos_centros,
    default=todos_centros
)

todas_contas = df['Descricao_Conta'].unique()
contas_selecionadas = st.sidebar.multiselect(
    "Selecione a(s) Conta(s):",
    options=todas_contas,
    default=todas_contas
)

data_min = df['Data'].min().date()
data_max = df['Data'].max().date()

data_inicio, data_fim = st.sidebar.date_input(
    "Selecione o Período:",
    value=[data_min, data_max],
    min_value=data_min,
    max_value=data_max
)

# --- Aplicação dos Filtros ---
df_filtrado = df[
    (df['Centro_Custo'].isin(centros_selecionados)) &
    (df['Descricao_Conta'].isin(contas_selecionadas)) &
    (df['Data'].dt.date >= data_inicio) &
    (df['Data'].dt.date <= data_fim)
]

# --- Título e Separador ---
st.title("🏗️ FUNDEX - Análise de Despesas")
st.markdown("---")

# --- KPIs ---
total_realizado = df_filtrado['Despesa_Positiva'].sum()
total_previsto = df_filtrado['Valor_Previsto'].sum()
variacao_total = total_previsto - total_realizado

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Total Gasto (Realizado)", formatar_moeda(total_realizado))
with col2:
    st.metric("📋 Total Previsto (Orçado)", formatar_moeda(total_previsto))
with col3:
    delta_color = "normal" if variacao_total >= 0 else "inverse"
    st.metric(
        "💸 Diferença (Previsto - Gasto)",
        formatar_moeda(variacao_total),
        delta="Economia" if variacao_total >= 0 else "Estouro",
        delta_color=delta_color
    )

st.markdown("---")

# --- Gráficos ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📈 Evolução Mensal das Despesas")
    df_tempo = df_filtrado.groupby('Mes_Ano')['Despesa_Positiva'].sum().reset_index()
    fig_tempo = px.bar(
        df_tempo, x='Mes_Ano', y='Despesa_Positiva',
        title="Total Gasto por Mês",
        labels={'Mes_Ano': 'Mês/Ano', 'Despesa_Positiva': 'Total Gasto (R$)'},
        template='plotly_white',
        color_discrete_sequence=['#E60000']
    )
    fig_tempo.update_layout(xaxis={'type': 'category'})
    st.plotly_chart(fig_tempo, use_container_width=True)

with col_graf2:
    st.subheader("🏢 Top 10 Centros de Custo")
    df_centro_custo = df_filtrado.groupby('Centro_Custo')['Despesa_Positiva'].sum().nlargest(10).sort_values(ascending=True).reset_index()
    fig_centro = px.bar(
        df_centro_custo, y='Centro_Custo', x='Despesa_Positiva',
        title="Top 10 Centros de Custo",
        orientation='h',
        labels={'Centro_Custo': 'Centro de Custo', 'Despesa_Positiva': 'Total Gasto (R$)'},
        template='plotly_white',
        color_discrete_sequence=['#E60000']
    )
    st.plotly_chart(fig_centro, use_container_width=True)

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.subheader("📝 Top 10 Contas de Despesa")
    df_conta = df_filtrado.groupby('Descricao_Conta')['Despesa_Positiva'].sum().nlargest(10).sort_values(ascending=True).reset_index()
    fig_conta = px.bar(
        df_conta, y='Descricao_Conta', x='Despesa_Positiva',
        title="Top 10 Contas por Gasto",
        orientation='h',
        labels={'Descricao_Conta': 'Descrição da Conta', 'Despesa_Positiva': 'Total Gasto (R$)'},
        template='plotly_white',
        color_discrete_sequence=['#E60000']
    )
    st.plotly_chart(fig_conta, use_container_width=True)

with col_graf4:
    st.subheader("🎯 Previsto vs. Realizado (Top 10 Centros)")
    df_prev_real = df_filtrado.groupby('Centro_Custo')[['Valor_Previsto', 'Despesa_Positiva']].sum().reset_index()
    top_10 = df_prev_real.nlargest(10, 'Despesa_Positiva')['Centro_Custo']
    df_prev_real_top10 = df_prev_real[df_prev_real['Centro_Custo'].isin(top_10)]
    df_melted = df_prev_real_top10.melt(
        id_vars='Centro_Custo',
        value_vars=['Valor_Previsto', 'Despesa_Positiva'],
        var_name='Tipo_Valor', value_name='Valor'
    )
    fig_prev_real = px.bar(
        df_melted, x='Centro_Custo', y='Valor', color='Tipo_Valor',
        barmode='group',
        title="Comparativo: Previsto vs. Gasto",
        labels={'Centro_Custo': 'Centro de Custo', 'Valor': 'Valor (R$)'},
        template='plotly_white',
        color_discrete_map={'Valor_Previsto': '#4169E1', 'Despesa_Positiva': '#E60000'}
    )
    st.plotly_chart(fig_prev_real, use_container_width=True)

# --- Tabela Final ---
st.markdown("---")
st.subheader("🧾 Detalhes dos Lançamentos (Filtrados)")

df_display = df_filtrado.copy()
colunas_moeda = ['Valor_Realizado', 'Valor_Previsto', 'Despesa_Positiva', 'Variacao']
for col in colunas_moeda:
    if col in df_display.columns:
        df_display[col] = df_display[col].apply(formatar_moeda)

st.dataframe(df_display, use_container_width=True)

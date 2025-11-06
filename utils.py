import streamlit as st
import pandas as pd
import os

@st.cache_data
def carregar_dados(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        st.error(f"❌ O arquivo '{caminho_arquivo}' não foi encontrado.")
        return pd.DataFrame()

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

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def criar_filtros_sidebar(df_completo):
    st.sidebar.header("🔍 Filtros Interativos")

    todos_centros = df_completo['Centro_Custo'].unique()
    centros_selecionados = st.sidebar.multiselect(
        "Selecione o(s) Centro(s) de Custo:",
        options=todos_centros,
        default=todos_centros
    )

    todas_contas = df_completo['Descricao_Conta'].unique()
    contas_selecionadas = st.sidebar.multiselect(
        "Selecione a(s) Conta(s):",
        options=todas_contas,
        default=todas_contas
    )

    data_min = df_completo['Data'].min().date()
    data_max = df_completo['Data'].max().date()

    data_inicio, data_fim = st.sidebar.date_input(
        "Selecione o Período:",
        value=[data_min, data_max],
        min_value=data_min,
        max_value=data_max
    )

    df_filtrado = df_completo[
        (df_completo['Centro_Custo'].isin(centros_selecionados)) &
        (df_completo['Descricao_Conta'].isin(contas_selecionadas)) &
        (df_completo['Data'].dt.date >= data_inicio) &
        (df_completo['Data'].dt.date <= data_fim)
    ]
    
    return df_filtrado
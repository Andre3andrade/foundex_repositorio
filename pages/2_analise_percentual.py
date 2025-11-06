import streamlit as st
import pandas as pd
import plotly.express as px
import utils

st.set_page_config(
    page_title="FUNDEX - Análise Percentual",
    page_icon="📊",
    layout="wide"
)

df_completo = utils.carregar_dados("despesas.xlsx")

if df_completo.empty:
    st.stop()

df_filtrado = utils.criar_filtros_sidebar(df_completo)

st.title("📊 Análise Percentual de Despesas")
st.markdown("---")

st.write("Esta página mostra a distribuição percentual dos gastos para os filtros selecionados.")

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

total_gasto_filtrado = df_filtrado['Despesa_Positiva'].sum()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Divisão por Centro de Custo")
    df_pie_centro = df_filtrado.groupby('Centro_Custo')['Despesa_Positiva'].sum().reset_index()
    
    df_pie_centro['Percentual'] = (df_pie_centro['Despesa_Positiva'] / total_gasto_filtrado)
    
    fig_pie_centro = px.pie(
        df_pie_centro,
        names='Centro_Custo',
        values='Percentual',
        title="Gastos por Centro de Custo (%)",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig_pie_centro.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{percent:.1%}')
    st.plotly_chart(fig_pie_centro, use_container_width=True)

with col2:
    st.subheader("Divisão por Conta de Despesa (Top 10)")
    df_bar_conta = df_filtrado.groupby('Descricao_Conta')['Despesa_Positiva'].sum().nlargest(10).reset_index()
    
    df_bar_conta['Percentual'] = (df_bar_conta['Despesa_Positiva'] / total_gasto_filtrado)
    
    fig_bar_conta = px.bar(
        df_bar_conta, 
        y='Descricao_Conta', 
        x='Percentual',
        title="Participação das Top 10 Contas no Gasto Total",
        orientation='h',
        labels={'Descricao_Conta': 'Conta de Despesa', 'Percentual': 'Participação no Total (%)'},
        template='plotly_white',
        color_discrete_sequence=['#E60000']
    )
    fig_bar_conta.update_xaxes(tickformat=".1%")
    st.plotly_chart(fig_bar_conta, use_container_width=True)
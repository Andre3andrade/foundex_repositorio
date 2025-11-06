import streamlit as st
import pandas as pd
import plotly.express as px
import utils

st.set_page_config(
    page_title="FUNDEX - Visão Geral",
    page_icon="🏗️",
    layout="wide"
)

df_completo = utils.carregar_dados("despesas.xlsx")

if df_completo.empty:
    st.stop()

df_filtrado = utils.criar_filtros_sidebar(df_completo)

st.title("🏗️ FUNDEX - Análise de Despesas (Visão Geral)")
st.markdown("---")

total_realizado = df_filtrado['Despesa_Positiva'].sum()
total_previsto = df_filtrado['Valor_Previsto'].sum()
variacao_total = total_previsto - total_realizado

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Total Gasto (Realizado)", utils.formatar_moeda(total_realizado))
with col2:
    st.metric("📋 Total Previsto (Orçado)", utils.formatar_moeda(total_previsto))
with col3:
    delta_color = "normal" if variacao_total >= 0 else "inverse"
    st.metric(
        "💸 Diferença (Previsto - Gasto)",
        utils.formatar_moeda(variacao_total),
        delta="Economia" if variacao_total >= 0 else "Estouro",
        delta_color=delta_color
    )

st.markdown("---")

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

st.markdown("---")
st.subheader("🧾 Detalhes dos Lançamentos (Filtrados)")

df_display = df_filtrado.copy()
colunas_moeda = ['Valor_Realizado', 'Valor_Previsto', 'Despesa_Positiva', 'Variacao']
for col in colunas_moeda:
    if col in df_display.columns:
        df_display[col] = df_display[col].apply(utils.formatar_moeda)

st.dataframe(df_display, use_container_width=True)
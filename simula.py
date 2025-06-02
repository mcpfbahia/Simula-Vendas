import streamlit as st
import pandas as pd
from pathlib import Path

# === CONFIGURACOES ===
st.set_page_config(page_title="🏠 MCPF - BAHA SIMULADOR DE VENDAS", layout="centered")
st.markdown("""
    <style>
    .main {background-color: #f7f9fb;}
    .stApp {padding: 2rem; border-radius: 15px; border: 1px solid #d3d3d3; background-color: #ffffff; box-shadow: 0px 0px 12px rgba(0,0,0,0.07);}
    .title-box {padding: 1rem; border-radius: 10px; background: linear-gradient(90deg, #6e8efb, #a777e3); color: white; margin-bottom: 2rem; text-align: center;}
    .result-box {padding: 1.5rem; background-color: #f0f4ff; border-left: 5px solid #6e8efb; border-radius: 10px; margin-top: 2rem;}
    .highlight {font-weight: bold; color: #3b3b3b; font-size: 1.1rem;}
    </style>
""", unsafe_allow_html=True)

# === TÍTULO ===
st.markdown("""
<div class="title-box">
    <h1>🏠 MCPF - BAHA SIMULADOR DE VENDAS</h1>
    <p>Simule descontos, margens e preços de forma inteligente</p>
</div>
""", unsafe_allow_html=True)

# === CARREGAR PLANILHA ===
file_path = "precos.xlsx"
if not Path(file_path).exists():
    st.error("❌ Planilha de preços não encontrada.")
    st.stop()

planilha = pd.read_excel(file_path)

# === FORMULÁRIO ===
st.markdown("### 📋 Formulário de Simulação")
st.markdown("<hr>", unsafe_allow_html=True)

modelos = planilha['DESCRICAO'].unique()
modelo = st.selectbox("🧱 Selecione o modelo do kit:", modelos)
desconto = st.slider("💸 Percentual de Desconto:", 0.0, 15.0, 0.0, step=0.5)
tipo_pagamento = st.radio("💳 Forma de Pagamento:", ["À Vista", "Cartão de Crédito"])

# === FILTRAR DADOS DO KIT ===
kit = planilha[planilha['DESCRICAO'] == modelo].iloc[0]
preco_venda = kit['A VISTA']
preco_custo = kit['PRECO_CUSTO']
peso = kit['PESO UND']
link = kit['LINK_KIT']
codigo = kit['CODIGO']

# === CÁLCULOS ===
preco_com_desconto = preco_venda * (1 - desconto / 100)

# Custos indiretos
custo_indireto_pct = 0.27 if tipo_pagamento == "À Vista" else 0.32
custo_indireto_valor = preco_com_desconto * custo_indireto_pct
lucro_liquido = preco_com_desconto - preco_custo - custo_indireto_valor
margem_liquida_pct = (lucro_liquido / preco_com_desconto) * 100 if preco_com_desconto else 0

# Frete
frete_estimado = peso * 1150

# === RESULTADO ===
st.markdown("""
<div class="result-box">
    <p class="highlight">🔹 <strong>Código do Kit:</strong> {codigo}</p>
    <p class="highlight">🔹 <strong>Modelo:</strong> {modelo}</p>
    <p class="highlight">💰 <strong>Preço de Custo:</strong> R$ {preco_custo:,.2f}</p>
    <p class="highlight">🏷️ <strong>Preço de Venda:</strong> R$ {preco_venda:,.2f}</p>
    <p class="highlight">🔻 <strong>Preço com {desconto:.1f}% de Desconto:</strong> R$ {preco_com_desconto:,.2f}</p>
    <hr>
    <p class="highlight">📉 <strong>Lucro Líquido ({tipo_pagamento}):</strong> R$ {lucro_liquido:,.2f} ({margem_liquida_pct:.2f}%)</p>
    <p class="highlight">🚚 <strong>Frete Estimado:</strong> R$ {frete_estimado:,.2f} (Cliente paga diretamente à transportadora)</p>
    <p class="highlight">🔗 <a href="{link}" target="_blank">Acessar Kit</a></p>
</div>
""".format(
    codigo=codigo,
    modelo=modelo,
    preco_custo=preco_custo,
    preco_venda=preco_venda,
    desconto=desconto,
    preco_com_desconto=preco_com_desconto,
    tipo_pagamento=tipo_pagamento,
    lucro_liquido=lucro_liquido,
    margem_liquida_pct=margem_liquida_pct,
    frete_estimado=frete_estimado,
    link=link
), unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center;'>© 2025 Minha Casa Pré-Fabricada - Todos os direitos reservados</p>", unsafe_allow_html=True)

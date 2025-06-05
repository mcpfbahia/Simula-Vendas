import streamlit as st
import pandas as pd
from pathlib import Path

# CONFIGURAÇÃO DO APP
st.set_page_config(page_title="🏷️ Calculadora Inteligente de Descontos", layout="centered")

# CSS Personalizado
st.markdown("""
<style>
    .result-box {padding: 1.5rem; background-color: #f0f4ff; border-radius: 10px;}
    .title-box {
        padding: 1rem;
        border-radius: 10px;
        background: linear-gradient(90deg, #6e8efb, #a777e3);
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Função de formatação de moeda
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Carregar planilha com caching
@st.cache_data
def carregar_dados(filepath):
    if Path(filepath).exists():
        return pd.read_excel(filepath)
    else:
        st.error("❌ Arquivo Excel não encontrado.")
        st.stop()

dados_kits = carregar_dados("precos.xlsx")

# Cabeçalho visual
st.markdown("""
<div class="title-box">
    <h1>🏷️ Calculadora Inteligente de Descontos</h1>
    <p>Encontre rapidamente o preço ideal para sua negociação!</p>
</div>
""", unsafe_allow_html=True)

# Busca e seleção
busca = st.text_input("🔍 Buscar kit (ex: a-frame, pop):").lower().strip()
kits_filtrados = dados_kits[dados_kits['DESCRICAO'].str.lower().str.contains(busca, na=False)] if busca else dados_kits

if kits_filtrados.empty:
    st.warning("Nenhum kit encontrado.")
    st.stop()

modelo = st.selectbox("🧱 Escolha um Kit:", kits_filtrados['DESCRICAO'].unique())

# Entradas
col1, col2 = st.columns(2)
with col1:
    desconto = st.slider("💸 Desconto (%)", 0.0, 15.0, step=0.5)
with col2:
    opcoes_pagamento = {
        "À Vista": "avista",
        "Cartão de Crédito": "cartao"
    }
    forma_pagamento_exibida = st.selectbox("💳 Forma de Pagamento:", list(opcoes_pagamento.keys()))
    tipo_pagamento = opcoes_pagamento[forma_pagamento_exibida]

# Dados do kit
kit = kits_filtrados[kits_filtrados['DESCRICAO'] == modelo].iloc[0]
preco_venda = float(kit.get('A VISTA', 0))
preco_custo = float(kit.get('PRECO_CUSTO', 0))
peso = float(kit.get('PESO UND', 0))
link = kit.get('LINK_KIT', '#')
codigo = kit.get('CODIGO', 'N/A')

# Cálculos
frete_estimado = (peso / 1000) * 1129.00
preco_custo_ajustado = preco_custo - frete_estimado
preco_final = preco_venda * (1 - desconto / 100)
custo_indireto_pct = 0.27 if tipo_pagamento == "avista" else 0.32
custo_indireto_valor = preco_final * custo_indireto_pct
lucro = preco_final - preco_custo_ajustado - custo_indireto_valor
margem = (lucro / preco_final) * 100 if preco_final else 0

# Barra de desconto (semáforo)
if desconto <= 7:
    cor = "#d4edda"
    texto = "🟢 Desconto seguro: margem preservada."
    cor_texto = "#155724"
elif 7 < desconto <= 12:
    cor = "#fff3cd"
    texto = "🟡 Atenção: zona de risco operacional."
    cor_texto = "#856404"
else:
    cor = "#f8d7da"
    texto = "🔴 Alerta: desconto acima de 12%, risco elevado de prejuízo."
    cor_texto = "#721c24"

st.markdown(f"""
<div style='background-color:{cor}; padding:15px; border-radius:8px; color:{cor_texto}; font-weight: bold; text-align: center; margin-bottom:30px;'>
    {texto}
</div>
""", unsafe_allow_html=True)

# Resultado formatado
st.markdown(f"""
<div class="result-box">
    🔹 <strong>Código do Kit:</strong> {codigo}<br>
    🔹 <strong>Modelo:</strong> {modelo}<br>
    💰 <strong>Preço de Custo (sem frete):</strong> {formatar_moeda(preco_custo_ajustado)}<br>
    🏷️ <strong>Preço com Desconto ({desconto}%):</strong> {formatar_moeda(preco_final)}<br>
    📉 <strong>Lucro Líquido:</strong> {formatar_moeda(lucro)} ({margem:.2f}%)<br>
    🚚 <strong>Frete Estimado:</strong> {formatar_moeda(frete_estimado)} <em>(pago diretamente pelo cliente)</em><br>
    🔗 <a href="{link}" target="_blank">Acessar Kit</a>
</div>
""", unsafe_allow_html=True)

# Margem destacada
st.markdown(f"""
### 📈 Margem Calculada:
<span style='font-size:22px; font-weight:bold; color:#336699'>{margem:.2f}%</span>
""", unsafe_allow_html=True)

# Avaliação da margem por forma de pagamento
if tipo_pagamento == "avista":
    if margem <= 7:
        st.markdown("<div style='background-color:#d4edda; padding:15px; border-radius:8px; color:#155724; margin-bottom:30px;'>✅ Margem saudável e segura para <strong>pagamento à vista</strong>.</div>", unsafe_allow_html=True)
    elif 7 < margem <= 10:
        st.markdown("<div style='background-color:#fff3cd; padding:15px; border-radius:8px; color:#856404; margin-bottom:30px;'>⚠️ Atenção: margem no <strong>limite operacional</strong> para pagamento à vista.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color:#f8d7da; padding:15px; border-radius:8px; color:#721c24; margin-bottom:30px;'>❌ Margem crítica: risco de <strong>prejuízo</strong> para pagamento à vista.</div>", unsafe_allow_html=True)

elif tipo_pagamento == "cartao":
    if margem <= 2:
        st.markdown("<div style='background-color:#d4edda; padding:15px; border-radius:8px; color:#155724; margin-bottom:30px;'>✅ Margem saudável e segura para <strong>pagamento no cartão</strong>.</div>", unsafe_allow_html=True)
    elif 2 < margem <= 5:
        st.markdown("<div style='background-color:#fff3cd; padding:15px; border-radius:8px; color:#856404; margin-bottom:30px;'>⚠️ Atenção: margem no <strong>limite operacional</strong> para pagamento no cartão.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background-color:#f8d7da; padding:15px; border-radius:8px; color:#721c24; margin-bottom:30px;'>❌ Margem crítica: risco de <strong>prejuízo</strong> para pagamento no cartão.</div>", unsafe_allow_html=True)

# Rodapé final
st.markdown("<hr style='margin-top:40px;'><p style='text-align:center; margin-top:10px;'>© 2025 Minha Casa Pré-Fabricada - Todos os direitos reservados</p>", unsafe_allow_html=True)

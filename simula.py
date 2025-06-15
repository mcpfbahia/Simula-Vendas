import streamlit as st
import pandas as pd
from pathlib import Path
from urllib.parse import quote

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
    <p>Descubra o limite seguro de desconto conforme a forma de pagamento!</p>
</div>
""", unsafe_allow_html=True)

# Busca e seleção
busca = st.text_input("🔍 Buscar kit (ex: a-frame, pop):").lower().strip()
kits_filtrados = dados_kits[dados_kits['DESCRICAO'].str.lower().str.contains(busca, na=False)] if busca else dados_kits

if kits_filtrados.empty:
    st.warning("Nenhum kit encontrado.")
    st.stop()

modelo = st.selectbox("🧱 Escolha um Kit:", kits_filtrados['DESCRICAO'].unique())

# Entradas com tooltips
col1, col2 = st.columns(2)
with col1:
    desconto = st.slider("💸 Desconto (%)", 0.0, 15.0, step=0.5,
                         help="Defina o percentual de desconto aplicado ao cliente.")
with col2:
    opcoes_pagamento = {
        "À Vista": "avista",
        "Cartão de Crédito": "cartao"
    }
    forma_pagamento_exibida = st.selectbox("💳 Forma de Pagamento:", list(opcoes_pagamento.keys()),
                                           help="Escolha se o pagamento será à vista ou via cartão de crédito.")
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

# 🔒 Bloqueio de descontos perigosos
if tipo_pagamento == "cartao" and desconto > 10:
    st.error("❌ Desconto acima de 10% não é permitido para pagamento no cartão.")
    st.stop()
elif tipo_pagamento == "avista" and desconto > 15:
    st.error("❌ Desconto acima de 15% não é permitido para pagamento à vista.")
    st.stop()

# Alerta visual de segurança
if tipo_pagamento == "avista":
    if desconto <= 7:
        cor_seg, texto_seg, cor_texto_seg = "#d4edda", "✅ Desconto dentro do limite seguro para pagamento à vista. Margem saudável.", "#155724"
    elif 7 < desconto <= 10:
        cor_seg, texto_seg, cor_texto_seg = "#fff3cd", "⚠️ Atenção: desconto entre 7% e 10% exige análise.", "#856404"
    else:
        cor_seg, texto_seg, cor_texto_seg = "#f8d7da", "❗ Desconto elevado pode comprometer a margem.", "#721c24"
else:
    if desconto <= 2:
        cor_seg, texto_seg, cor_texto_seg = "#d4edda", "✅ Desconto dentro do limite seguro para cartão. Margem saudável.", "#155724"
    elif 2 < desconto <= 5:
        cor_seg, texto_seg, cor_texto_seg = "#fff3cd", "⚠️ Atenção: desconto entre 2% e 5% exige análise.", "#856404"
    else:
        cor_seg, texto_seg, cor_texto_seg = "#f8d7da", "❗ Desconto elevado pode comprometer a margem no cartão.", "#721c24"

st.markdown(f"""
<div style='background-color:{cor_seg}; padding:15px; border-radius:8px; color:{cor_texto_seg}; font-weight: bold; text-align: center; margin-bottom:20px;'>
    {texto_seg}
</div>
""", unsafe_allow_html=True)

# Resultado detalhado
st.markdown(f"""
<div class="result-box">
    🔹 <strong>Código do Kit:</strong> {codigo}<br>
    🔹 <strong>Modelo:</strong> {modelo}<br>
    💰 <strong>Preço de Custo (sem frete):</strong> {formatar_moeda(preco_custo_ajustado)}<br>
    💼 <strong>Valor Padrão de Venda:</strong> <span style='color:#555'>{formatar_moeda(preco_venda)}</span><br>
    ⬇️<br>
    🏷️ <strong>Preço com Desconto ({desconto}%):</strong> <strong style='color:#006400'>{formatar_moeda(preco_final)}</strong><br>
    📉 <strong>Lucro Líquido:</strong> {formatar_moeda(lucro)} ({margem:.2f}%)<br>
    🚚 <strong>Frete Estimado:</strong> {formatar_moeda(frete_estimado)} <em>(pago diretamente pelo cliente)</em><br>
    🔗 <a href="{link}" target="_blank">Acessar Kit</a>
</div>
""", unsafe_allow_html=True)

# 🎯 Barra de semáforo de margem
if margem >= 20:
    cor_barra = "green"
elif 10 <= margem < 20:
    cor_barra = "orange"
else:
    cor_barra = "red"

st.markdown(f"""
<div style="margin-top: 20px;">
    <strong>🔦 Indicador de Margem:</strong>
    <div style="width: 100%; height: 20px; background-color: #e0e0e0; border-radius: 10px; margin-top: 5px;">
        <div style="width: {margem:.2f}%; height: 100%; background-color: {cor_barra}; border-radius: 10px;"></div>
    </div>
    <p style="font-size: 16px; color: {cor_barra}; margin-top: 5px;"><strong>{margem:.2f}% de margem</strong></p>
</div>
""", unsafe_allow_html=True)

# 📱 Geração de mensagem para WhatsApp
msg = f"""Olá! Segue a simulação para o kit selecionado:

🔹 Modelo: {modelo}
🏷️ Desconto aplicado: {desconto}%
💰 Preço com desconto: {formatar_moeda(preco_final)}
📉 Lucro estimado: {formatar_moeda(lucro)} ({margem:.2f}%)
🚚 Frete estimado: {formatar_moeda(frete_estimado)} (cliente paga direto)

Link do kit: {link}

Essa simulação foi gerada automaticamente pela Calculadora Inteligente de Descontos.
"""
url_whatsapp = f"https://api.whatsapp.com/send?text={quote(msg)}"
st.markdown(f"[📲 Enviar simulação via WhatsApp]({url_whatsapp})", unsafe_allow_html=True)

# Rodapé
st.markdown("<hr style='margin-top:40px;'><p style='text-align:center; margin-top:10px;'>© 2025 Minha Casa Pré-Fabricada - Todos os direitos reservados</p>", unsafe_allow_html=True)

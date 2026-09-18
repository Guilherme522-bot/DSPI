import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Nome do arquivo de histórico
ARQUIVO_LOG = "historico_uso.csv"

# Configuração visual da página no navegador
st.set_page_config(page_title="Controle do Protótipo", page_icon="⚡", layout="centered")

# --- ESTILIZAÇÃO VISUAL (CSS) ---
st.markdown("""
    <style>
    /* Botão INICIAR em Verde */
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #16a34a !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 18px !important;
        height: 3.5em !important;
    }
    div.stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #15803d !important;
    }

    /* Botão PARAR em Vermelho */
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: #dc2626 !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 18px !important;
        height: 3.5em !important;
    }
    div.stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: #b91c1c !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa o estado de execução na sessão
if "em_execucao" not in st.session_state:
    st.session_state.em_execucao = False

# --- CABEÇALHO ---
st.title("⚡ Controle e Registro de Operação")
st.caption("Protótipo de Limpeza de Grelhas para Corte a Laser")

st.divider()

# --- IDENTIFICAÇÃO DO OPERADOR ---
st.subheader("👤 Identificação do Operador")
operador = st.text_input("Nome Completo:", placeholder="Digite seu nome completo")

st.divider()

# --- BOTÕES DE AÇÃO (INICIAR / PARAR) ---
st.subheader("🕹️ Painel de Controle")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🟢 INICIAR", type="primary", use_container_width=True):
        if not operador.strip():
            st.error("⚠️ Por favor, informe o nome do operador antes de iniciar!")
        else:
            st.session_state.em_execucao = True
            st.success("🚀 Processo iniciado! Digite a quantidade de grelhas limpas abaixo.")

with col_btn2:
    if st.button("🔴 PARAR", type="secondary", use_container_width=True):
        st.session_state.em_execucao = False
        st.warning("⏹️ Processo interrompido/parado.")

st.divider()

# --- REGISTRO DE GRELHAS (LIBERADO APENAS APÓS INICIAR) ---
st.subheader("📊 Produção e Registro de Grelhas")

if not st.session_state.em_execucao:
    st.info("🔒 O campo abaixo está **bloqueado**. Clique no botão **🟢 INICIAR** acima para liberar a digitação.")

grelhas_limpas = st.number_input(
    "Quantidade de Grelhas Limpas nesta sessão:", 
    min_value=0, 
    step=1, 
    value=0,
    disabled=not st.session_state.em_execucao,
    help="Bloqueado até clicar em INICIAR."
)

if st.session_state.em_execucao:
    if st.button("💾 GRAVAR REGISTRO DE LIMPEZA", use_container_width=True):
        if grelhas_limpas <= 0:
            st.warning("⚠️ Informe uma quantidade maior que 0 para gravar.")
        else:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            novo_registro = {
                "Data/Hora": agora,
                "Operador": operador,
                "Grelhas Limpas": grelhas_limpas,
                "Status / Ação": "Sucesso / Concluído"
            }
            
            file_exists = os.path.exists(ARQUIVO_LOG)
            df_novo = pd.DataFrame([novo_registro])
            df_novo.to_csv(ARQUIVO_LOG, mode='a', index=False, header=not file_exists)
            
            st.success(f"✅ Registrado com sucesso: {grelhas_limpas} grelha(s) por {operador}!")
            st.rerun()

st.divider()

# --- HISTÓRICO E CONTADOR DIÁRIO ---
st.subheader("📋 Histórico de Operações")

if os.path.exists(ARQUIVO_LOG):
    try:
        df_log = pd.read_csv(ARQUIVO_LOG)
    except Exception:
        df_log = pd.DataFrame(columns=["Data/Hora", "Operador", "Grelhas Limpas", "Status / Ação"])
else:
    df_log = pd.DataFrame(columns=["Data/Hora", "Operador", "Grelhas Limpas", "Status / Ação"])

grelhas_hoje = 0

if not df_log.empty and "Data/Hora" in df_log.columns:
    if "Grelhas Limpas" in df_log.columns:
        df_log["Grelhas Limpas"] = pd.to_numeric(df_log["Grelhas Limpas"], errors='coerce').fillna(0).astype(int)
    else:
        df_log["Grelhas Limpas"] = 0

    hoje_str = datetime.now().strftime("%Y-%m-%d")
    df_log['Data_Apenas'] = df_log['Data/Hora'].astype(str).str.slice(0, 10)
    
    df_hoje = df_log[df_log['Data_Apenas'] == hoje_str]
    grelhas_hoje = df_hoje["Grelhas Limpas"].sum()
    
    df_exibicao = df_log.drop(columns=['Data_Apenas'], errors='ignore')
else:
    df_exibicao = df_log

st.metric(label="📅 Grelhas Limpas HOJE", value=int(grelhas_hoje))
st.write("")

st.dataframe(df_exibicao.iloc[::-1], use_container_width=True)

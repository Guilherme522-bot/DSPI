import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Tecno Grill - Controle de Operação",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Descobre o diretório exato onde o script DSPI.py está localizado
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_PAI = os.path.dirname(DIRETORIO_ATUAL)

# Nomes possíveis do arquivo de imagem
POSSIVEIS_NOMES = [
    "Tecno Grill_27923a.jpg.jpg",
    "Tecno Grill_27923a.jpg",
    "Tecno Grill_27923a.JPG"
]

# Procura a imagem no diretório do script, no diretório pai e no diretório de execução
caminho_logo = None
for nome in POSSIVEIS_NOMES:
    locais = [
        os.path.join(DIRETORIO_ATUAL, nome),
        os.path.join(DIRETORIO_PAI, nome),
        nome
    ]
    for loc in locais:
        if os.path.exists(loc):
            caminho_logo = loc
            break
    if caminho_logo:
        break

ARQUIVO_LOG = os.path.join(DIRETORIO_ATUAL, "historico_uso.csv")

# --- ESTILIZAÇÃO VISUAL (CSS) ---
st.markdown("""
    <style>
    .stApp {
        margin-top: -20px;
    }
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

# --- CABEÇALHO COM LOGÓTIPO ---
if caminho_logo:
    try:
        with open(caminho_logo, "rb") as f:
            data_imagem = f.read()
        col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
        with col_logo2:
            st.image(data_imagem, use_container_width=True)
    except Exception:
        pass

st.title("⚡ Tecno Grill - Controle de Operação")
st.caption("Limpeza de Grelhas para Corte a Laser")

st.divider()

# --- INICIALIZAÇÃO DE ESTADOS ---
if "em_execucao" not in st.session_state:
    st.session_state.em_execucao = False
if "hora_inicio" not in st.session_state:
    st.session_state.hora_inicio = None

# --- OPERADOR ---
st.subheader("👤 Identificação do Operador")
operador = st.text_input("Nome Completo:", placeholder="Digite seu nome completo")

st.divider()

# --- PAINEL DE CONTROLE ---
st.subheader("🕹️ Painel de Controle")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🟢 INICIAR", type="primary", use_container_width=True):
        if not operador.strip():
            st.error("⚠️ Por favor, informe o nome do operador antes de iniciar!")
        else:
            st.session_state.em_execucao = True
            st.session_state.hora_inicio = datetime.now()
            st.success(f"🚀 Processo iniciado às {st.session_state.hora_inicio.strftime('%H:%M:%S')}!")

with col_btn2:
    if st.button("🔴 PARAR", type="secondary", use_container_width=True):
        if st.session_state.em_execucao:
            st.session_state.em_execucao = False
            hora_fim = datetime.now()
            st.warning(f"⏹️ Processo interrompido às {hora_fim.strftime('%H:%M:%S')}.")
        else:
            st.info("A máquina já está parada.")

st.divider()

# --- REGISTRO DE GRELHAS ---
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
            agora = datetime.now()
            hora_inicio_str = st.session_state.hora_inicio.strftime("%H:%M:%S") if st.session_state.hora_inicio else agora.strftime("%H:%M:%S")
            hora_fim_str = agora.strftime("%H:%M:%S")
            data_str = agora.strftime("%Y-%m-%d")
            
            novo_registro = pd.DataFrame([{
                "Data": data_str,
                "Hora Início": hora_inicio_str,
                "Hora Fim": hora_fim_str,
                "Operador": operador,
                "Grelhas Limpas": grelhas_limpas
            }])
            
            if not os.path.exists(ARQUIVO_LOG):
                novo_registro.to_csv(ARQUIVO_LOG, index=False)
            else:
                try:
                    df_existente = pd.read_csv(ARQUIVO_LOG)
                    if "Hora Início" not in df_existente.columns:
                        novo_registro.to_csv(ARQUIVO_LOG, index=False)
                    else:
                        novo_registro.to_csv(ARQUIVO_LOG, mode='a', index=False, header=False)
                except Exception:
                    novo_registro.to_csv(ARQUIVO_LOG, index=False)
            
            st.session_state.hora_inicio = datetime.now()
            st.success(f"✅ Registrado: {grelhas_limpas} grelha(s) por {operador} (Início: {hora_inicio_str} | Fim: {hora_fim_str})")
            st.rerun()

st.divider()

# --- HISTÓRICO E CONTADOR DIÁRIO ---
st.subheader("📋 Histórico de Operações")

colunas_desejadas = ["Data", "Hora Início", "Hora Fim", "Operador", "Grelhas Limpas"]

if os.path.exists(ARQUIVO_LOG):
    try:
        df_log = pd.read_csv(ARQUIVO_LOG)
        df_log = df_log.reindex(columns=colunas_desejadas).fillna("-")
    except Exception:
        df_log = pd.DataFrame(columns=colunas_desejadas)
else:
    df_log = pd.DataFrame(columns=colunas_desejadas)

grelhas_hoje = 0

if not df_log.empty and "Data" in df_log.columns:
    if "Grelhas Limpas" in df_log.columns:
        df_log["Grelhas Limpas"] = pd.to_numeric(df_log["Grelhas Limpas"], errors='coerce').fillna(0).astype(int)
    else:
        df_log["Grelhas Limpas"] = 0

    hoje_str = datetime.now().strftime("%Y-%m-%d")
    df_hoje = df_log[df_log['Data'].astype(str) == hoje_str]
    grelhas_hoje = df_hoje["Grelhas Limpas"].sum()

st.metric(label="📅 Grelhas Limpas HOJE", value=int(grelhas_hoje))
st.write("")

st.dataframe(df_log.iloc[::-1], use_container_width=True)

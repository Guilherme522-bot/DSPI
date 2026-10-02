import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import time

# Tenta importar pyserial de forma segura (evita quebrar no Streamlit Cloud)
try:
    import serial
    SERIAL_DISPONIVEL = True
except ImportError:
    SERIAL_DISPONIVEL = False

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Tecno Grill - Controle de Operação",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURAÇÃO DA COMUNICAÇÃO SERIAL / ARDUINO ---
PORTA_SERIAL = "COM3"
BAUD_RATE = 9600

def enviar_comando_arduino(comando):
    """Envia 'L' ou 'D' via Serial quando executado localmente no PC com o Arduino."""
    if not SERIAL_DISPONIVEL:
        st.warning("⚠️ Módulo PySerial não instalado no servidor. Modo simulação ativo.")
        return True
        
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
        time.sleep(0.2)
        ser.write(comando.encode('utf-8'))
        ser.close()
        return True
    except Exception as e:
        st.warning(f"⚠️ Não foi possível comunicar com o Arduino na porta {PORTA_SERIAL}: {e}")
        return True

# Função auxiliar para capturar a hora exata no fuso de Brasília
def obter_hora_brasilia():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))

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

# URL da logo no GitHub
URL_LOGO_GITHUB_1 = "https://raw.githubusercontent.com/Guilherme522-bot/DSPI/main/Tecno%20Grill_27923a.jpg.jpg"
URL_LOGO_GITHUB_2 = "https://raw.githubusercontent.com/Guilherme522-bot/DSPI/main/Tecno%20Grill_27923a.jpg"

# --- CABEÇALHO COM LOGÓTIPO ---
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    try:
        st.image(URL_LOGO_GITHUB_1, use_container_width=True)
    except Exception:
        st.image(URL_LOGO_GITHUB_2, use_container_width=True)

st.title("⚡ Tecno Grill - Controle de Operação")
st.caption("Sistema de Controle e Liberação de Máquina")

st.divider()

# --- INICIALIZAÇÃO DE ESTADOS ---
if "em_execucao" not in st.session_state:
    st.session_state.em_execucao = False
if "hora_inicio" not in st.session_state:
    st.session_state.hora_inicio = None

# --- STATUS DA MÁQUINA (BLOQUEADO / LIBERADO) ---
if st.session_state.em_execucao:
    st.success("🟢 **MÁQUINA LIBERADA E EM OPERAÇÃO**")
else:
    st.error("🔴 **MÁQUINA BLOQUEADA** — Preencha a identificação abaixo para liberar o uso.")

st.divider()

# --- OPERADOR E PARÂMETROS ---
st.subheader("👤 Identificação do Operador")
operador = st.text_input(
    "Nome do Operador:", 
    placeholder="Digite seu nome completo", 
    disabled=st.session_state.em_execucao
)

grelhas_limpas = st.number_input(
    "Quantidade de Grelhas a Limpar nesta sessão:", 
    min_value=1, 
    step=1, 
    value=1,
    disabled=st.session_state.em_execucao,
    help="Informe quantas grelhas serão limpas durante este ciclo."
)

st.divider()

# --- PAINEL DE COMANDO ---
st.subheader("🕹️ Painel de Comando")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🟢 INICIAR & LIBERAR MÁQUINA", type="primary", use_container_width=True, disabled=st.session_state.em_execucao):
        if not operador.strip():
            st.error("⚠️ Preenchimento obrigatório: Digite o nome do operador para liberar a máquina.")
        else:
            if enviar_comando_arduino("L"):
                st.session_state.em_execucao = True
                st.session_state.hora_inicio = obter_hora_brasilia()
                st.success(f"🚀 Máquina liberada com sucesso às {st.session_state.hora_inicio.strftime('%H:%M:%S')}!")
                st.rerun()

with col_btn2:
    if st.button("🔴 PARAR & BLOQUEAR MÁQUINA", type="secondary", use_container_width=True, disabled=not st.session_state.em_execucao):
        if st.session_state.em_execucao:
            enviar_comando_arduino("D")
            
            agora = obter_hora_brasilia()
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
            
            ARQUIVO_LOG = "historico_uso.csv"
            if not os.path.exists(ARQUIVO_LOG):
                novo_registro.to_csv(ARQUIVO_LOG, index=False)
            else:
                try:
                    novo_registro.to_csv(ARQUIVO_LOG, mode='a', index=False, header=False)
                except Exception:
                    novo_registro.to_csv(ARQUIVO_LOG, index=False)
            
            st.session_state.em_execucao = False
            st.warning(f"⏹️ Operação encerrada às {hora_fim_str}. Registro salvo e máquina BLOQUEADA!")
            st.rerun()

st.divider()

# --- HISTÓRICO E CONTADOR DIÁRIO ---
st.subheader("📋 Histórico de Operações")

ARQUIVO_LOG = "historico_uso.csv"
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

    hoje_str = obter_hora_brasilia().strftime("%Y-%m-%d")
    df_hoje = df_log[df_log['Data'].astype(str) == hoje_str]
    grelhas_hoje = df_hoje["Grelhas Limpas"].sum()

st.metric(label="📅 Grelhas Limpas HOJE", value=int(grelhas_hoje))
st.write("")

st.dataframe(df_log.iloc[::-1], use_container_width=True)

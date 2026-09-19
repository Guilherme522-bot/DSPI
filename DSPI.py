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

# --- CONFIGURAÇÃO DO LOGO E CAMINHO DO ARQUIVO ---
NOME_ARQUIVO_LOGO = "Tecno Grill_27923a.jpg"
ARQUIVO_LOG = "historico_uso.csv"

# --- FUNÇÃO PARA CONVERTER IMAGEM PARA BASE64 ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_base64 = get_base64_image(NOME_ARQUIVO_LOGO)

# --- SPLASH SCREEN ---
splash_screen_html = f"""
    <div id="splash-screen">
        <div id="splash-content">
            <img src="data:image/jpeg;base64,{logo_base64}" alt="Tecno Grill Logo" id="splash-logo">
            <div id="loader"></div>
            <p id="splash-text">Iniciando aplicação...</p>
        </div>
    </div>

    <style>
        #splash-screen {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            transition: opacity 1s ease, visibility 1s ease;
        }}
        #splash-content {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }}
        #splash-logo {{
            max-width: 320px;
            height: auto;
            margin-bottom: 25px;
        }}
        #loader {{
            border: 4px solid #e1e1e1;
            border-top: 4px solid #0056b3;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }}
        #splash-text {{
            color: #555555;
            font-size: 15px;
            font-family: sans-serif;
            margin: 0;
        }}
        #splash-screen.fade-out {{
            opacity: 0;
            visibility: hidden;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>

    <script>
        setTimeout(function() {{
            var splash = document.getElementById('splash-screen');
            if (splash) {{
                splash.classList.add('fade-out');
            }}
        }}, 3000);
    </script>
"""

st.components.v1.html(splash_screen_html, height=0)

# --- ESTILIZAÇÃO VISUAL ---
st.markdown("""
    <style>
    .stApp { margin-top: -30px; }
    div.stButton > button[data-testid="baseButton-primary"] {
        background-color: #16a34a !important; color: #ffffff !important; border: none !important;
        font-weight: bold !important; font-size: 18px !important; height: 3.5em !important;
    }
    div.stButton > button[data-testid="baseButton-secondary"] {
        background-color: #dc2626 !important; color: #ffffff !important; border: none !important;
        font-weight: bold !important; font-size: 18px !important; height: 3.5em !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if "em_execucao" not in st.session_state:
    st.session_state.em_execucao = False
if "hora_inicio" not in st.session_state:
    st.session_state.hora_inicio = None

# --- CABEÇALHO ---
st.title("⚡ Controle e Registro de Operação")
st.caption("Protótipo de Limpeza de Grelhas para Corte a Laser")

st.divider()

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
    min_value=0, step=1, value=0,
    disabled=not st.session_state.em_execucao
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
            
            # Estrutura com colunas separadas
            novo_registro = pd.DataFrame([{
                "Data": data_str,
                "Hora Início": hora_inicio_str,
                "Hora Fim": hora_fim_str,
                "Operador": operador,
                "Grelhas Limpas": grelhas_limpas
            }])
            
            # Se o arquivo não existir ou for antigo, cria/sobrescreve com o novo formato
            if not os.path.exists(ARQUIVO_LOG):
                novo_registro.to_csv(ARQUIVO_LOG, index=False)
            else:
                try:
                    df_existente = pd.read_csv(ARQUIVO_LOG)
                    # Verifica se o CSV antigo ainda tem o formato antigo
                    if "Hora Início" not in df_existente.columns:
                        novo_registro.to_csv(ARQUIVO_LOG, index=False)
                    else:
                        novo_registro.to_csv(ARQUIVO_LOG, mode='a', index=False, header=False)
                except Exception:
                    novo_registro.to_csv(ARQUIVO_LOG, index=False)
            
            st.session_state.hora_inicio = datetime.now()
            st.success("✅ Registro gravado com sucesso!")
            st.rerun()

st.divider()

# --- HISTÓRICO ---
st.subheader("📋 Histórico de Operações")

colunas_desejadas = ["Data", "Hora Início", "Hora Fim", "Operador", "Grelhas Limpas"]

if os.path.exists(ARQUIVO_LOG):
    try:
        df_log = pd.read_csv(ARQUIVO_LOG)
        # Garante que só exibe as colunas novas e separadas
        df_log = df_log.reindex(columns=colunas_desejadas).fillna("-")
    except Exception:
        df_log = pd.DataFrame(columns=colunas_desejadas)
else:
    df_log = pd.DataFrame(columns=colunas_desejadas)

st.dataframe(df_log.iloc[::-1], use_container_width=True)

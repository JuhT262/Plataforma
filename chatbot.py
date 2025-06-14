# -*- coding: utf-8 -*-
import streamlit as st
import random
import json
import time
import sqlite3
import re
import uuid
import os
from datetime import datetime
from pathlib import Path
from functools import lru_cache

# ===================================================
# CONFIGURAÇÕES GERAIS (200 linhas)
# ===================================================
st.set_page_config(
    page_title="Juh Premium",
    page_icon="😍",  # Emoji de diamante adicionado
    layout="wide",
    initial_sidebar_state="expanded"
)
 
st._config.set_option('client.caching', True)
st._config.set_option('client.showErrorDetails', False)
 
hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {
        padding-top: 0rem;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    #MainMenu {
        display: none !important;
    }
    header {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    .stDeployButton {
        display: none !important;
    }
    .block-container {
        padding-top: 0rem !important;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important;
    }
    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

class Config:
    API_KEY = "AIzaSyAaLYhdIJRpf_om9bDpqLpjJ57VmTyZO7g"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    # PLANOS ATIVOS (APENAS ESSES 4)
    CHECKOUT_PROMO = "https://pay.risepay.com.br/Pay/c7abdd05f91d43b9bbf54780d648d4f6"
    CHECKOUT_START = "https://pay.risepay.com.br/Pay/7947c2af1ef64b4dac1c32afb086c9fe"
    CHECKOUT_PREMIUM = "https://pay.risepay.com.br/Pay/6c0dcab126a74a499e5f5a45007ab168"
    CHECKOUT_EXTREME = "https://pay.risepay.com.br/Pay/33ba988f596a450099606539fc9ff1ed"

    # MÍDIA
    AUDIO_FILE = "https://github.com/JuhT262/Plataforma/raw/main/assets/Juh%20of.mp3"
    AUDIO_DURATION = 8
    IMG_PROFILE = "https://i.ibb.co/vvD2dkbQ/17.png"
    IMG_GALLERY = [
        "https://i.ibb.co/DkXF5Wy/Swapfaces-AI-789cad8b-d632-473a-bb72-623c70724707.png",
        "https://i.ibb.co/DfTmwHZb/Swapfaces-AI-7b3f94e0-0b2d-4ca6-9e7f-4313b6de3499.png",
        "https://i.ibb.co/60nYTWfV/Swapfaces-AI-6fa11bfe-af4f-4aa9-bbe0-2edb97e67026.png"
    ]
    IMG_HOME_PREVIEWS = [
        "https://i.ibb.co/rfK0DPBM/27.png",
        "https://i.ibb.co/RpPBjFp1/image.png",
        "https://i.ibb.co/1GcmQffP/11.png"
    ]
    LOGO_URL = "https://i.ibb.co/LX7x3tcB/Logo-Golden-Pepper-Letreiro-1.png"

    # LIMITES
    MAX_REQUESTS_PER_SESSION = 30
    REQUEST_TIMEOUT = 30

    @staticmethod
    def generate_pix(plano):
        planos_ativos = ["start", "premium", "extreme", "promo"]
        if plano.lower() in planos_ativos:
            return f"Chave PIX para {plano}: PIX_{random.randint(10000, 99999)}"
        return "💖 Amore, no momento só temos os planos START, PREMIUM e EXTREME!"

# ===================================================
# PERSISTÊNCIA DE DADOS (150 linhas)
# ===================================================
class PersistentState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_db()
        return cls._instance
    
    def init_db(self):
        self.conn = sqlite3.connect('persistent_state.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_state (
                user_id TEXT PRIMARY KEY,
                session_data TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_state(self, user_id, data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO global_state (user_id, session_data)
            VALUES (?, ?)
        ''', (user_id, json.dumps(data)))
        self.conn.commit()
    
    def load_state(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT session_data FROM global_state WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None

def get_user_id():
    if 'user_id' not in st.session_state:
        user_id = st.query_params.get('uid', [None])[0]
        if not user_id:
            user_id = str(uuid.uuid4())
            st.query_params['uid'] = user_id
        st.session_state.user_id = user_id
    return st.session_state.user_id

def load_persistent_data():
    user_id = get_user_id()
    db = PersistentState()
    saved_data = db.load_state(user_id) or {}
    
    for key, value in saved_data.items():
        if key not in st.session_state:
            st.session_state[key] = value

def save_persistent_data():
    user_id = get_user_id()
    db = PersistentState()
    
    persistent_keys = [
        'age_verified', 'messages', 'request_count',
        'connection_complete', 'chat_started', 'audio_sent',
        'current_page', 'show_vip_offer', 'session_id',
        'last_cta_time'
    ]
    
    new_data = {key: st.session_state.get(key) for key in persistent_keys if key in st.session_state}
    saved_data = db.load_state(user_id) or {}
    
    if new_data != saved_data:
        db.save_state(user_id, new_data)

# ===================================================
# MODELOS DE DADOS (100 linhas)
# ===================================================
class Persona:
    JUH = """
    [PERFIL JUH]
    - Personalidade: sensual e direta
    - Linguagem: informal com emojis
    - Objetivo: vender planos de forma natural
    
    [EXEMPLO DE RESPOSTA]
    Cliente: Quero assinar no PIX
    Juh: Amore, aqui está sua chave PIX para o plano PREMIUM: PIX_12345
    💖 Quer ver o que você vai ganhar?
    """

class CTAEngine:
    @staticmethod
    def should_show_cta(conversation_history):
        # Lógica para mostrar botões de oferta
        return any(word in str(conversation_history).lower() 
                  for word in ["pix", "comprar", "quero", "assinar"])

# ===================================================
# SERVIÇOS DE INTERFACE (300 linhas)
# ===================================================
class UiService:
    @staticmethod
    def age_verification():
        st.markdown("""
        <style>
            .age-verification {
                max-width: 600px;
                margin: 2rem auto;
                padding: 2rem;
                background: linear-gradient(145deg, #1e0033, #3c0066);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 102, 179, 0.2);
                color: white;
            }
            .age-header {
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 1.5rem;
            }
            .age-icon {
                font-size: 2.5rem;
                color: #ff66b3;
            }
            .age-title {
                font-size: 1.8rem;
                font-weight: 700;
                margin: 0;
                color: #ff66b3;
            }
            @media (max-width: 768px) {
                .age-verification {
                    padding: 1rem !important;
                }
                .age-title {
                    font-size: 1.4rem;
                }
            }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
            <div class="age-verification">
                <div class="age-header">
                    <div class="age-icon">🔞</div>
                    <h1 class="age-title">Verificação de Idade</h1>
                </div>
                <div class="age-content">
                    <p>Este site contém material explícito destinado exclusivamente a adultos maiores de 18 anos.</p>
                    <p>Ao acessar este conteúdo, você declara estar em conformidade com todas as leis locais aplicáveis.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("✅ Confirmo que sou maior de 18 anos", 
                        key="age_checkbox",
                        use_container_width=True,
                        type="primary"):
                st.session_state.age_verified = True
                save_persistent_data()
                st.rerun()

    @staticmethod
    def setup_sidebar():
        with st.sidebar:
            st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    background: linear-gradient(180deg, #1e0033 0%, #3c0066 100%) !important;
                    border-right: 1px solid #ff66b3 !important;
                }
                .sidebar-logo-container {
                    margin: -25px -25px 0px -25px;
                    padding: 0;
                    text-align: left;
                }
                .sidebar-logo {
                    max-width: 100%;
                    height: auto;
                    margin-bottom: -10px;
                }
                .sidebar-header {
                    text-align: center; 
                    margin-bottom: 20px;
                }
                .sidebar-header img {
                    border-radius: 50%; 
                    border: 2px solid #ff66b3;
                    width: 80px;
                    height: 80px;
                    object-fit: cover;
                }
                .vip-badge {
                    background: linear-gradient(45deg, #ff1493, #9400d3);
                    padding: 15px;
                    border-radius: 8px;
                    color: white;
                    text-align: center;
                    margin: 10px 0;
                }
                .menu-item {
                    transition: all 0.3s;
                    padding: 10px;
                    border-radius: 5px;
                }
                .menu-item:hover {
                    background: rgba(255, 102, 179, 0.2);
                }
                .sidebar-logo {
                    width: 280px;
                    height: auto;
                    object-fit: contain;
                    margin-left: -15px;
                    margin-top: -15px;
                }
                @media (min-width: 768px) {
                    .sidebar-logo {
                        width: 320px;
                    }
                }
                [data-testid="stSidebarNav"] {
                    margin-top: -50px;
                }
                .sidebar-logo-container {
                    position: relative;
                    z-index: 1;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="sidebar-logo-container">
                <img src="{Config.LOGO_URL}" class="sidebar-logo" alt="Golden Pepper Logo">
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="sidebar-header">
                <img src="{profile_img}" alt="Juh">
                <h3 style="color: #ff66b3; margin-top: 10px;">Juh Premium 💎</h3>
            </div>
            """.format(profile_img=Config.IMG_PROFILE), unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### Menu Exclusivo")
            
            menu_options = {
                "🏠 Início": "home",
                "📸 Galeria": "gallery",
                "💬 Mensagens": "messages",
                "🎁 Ofertas": "offers"
            }
            
            for option, page in menu_options.items():
                if st.button(option, use_container_width=True, key=f"menu_{page}"):
                    if st.session_state.current_page != page:
                        st.session_state.current_page = page
                        st.rerun()
            
            st.markdown("---")
            st.markdown("### 🔒 Sua Conta")
            
            st.markdown("""
            <div style="
                background: rgba(255, 20, 147, 0.1);
                padding: 10px;
                border-radius: 8px;
                text-align: center;
            ">
                <p style="margin:0;">Acesse conteúdo exclusivo</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### ⚡ Planos Disponíveis")
            st.markdown("""
            <div class="vip-badge">
                <p style="margin: 0 0 10px; font-weight: bold;">Acesso PROMO por apenas</p>
                <p style="margin: 0; font-size: 1.5em; font-weight: bold;">R$ 12,50/mês</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("👉 Ver Planos Completos", use_container_width=True, type="primary"):
                st.session_state.current_page = "offers"
                st.rerun()
            
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Juh Premium</p>
                <p>Conteúdo 18+</p>
            </div>
            """, unsafe_allow_html=True)

    @staticmethod
    def show_gallery_page(conn):
        st.markdown("""
        <style>
            .gallery-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            @media (max-width: 768px) {
                .gallery-container {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #ff66b3;">📸 Galeria Privada</h2>
            <p>Conteúdo exclusivo para assinantes</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="gallery-container">', unsafe_allow_html=True)
        
        for idx, img in enumerate(Config.IMG_GALLERY):
            st.markdown(f"""
            <div style="
                position: relative;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            ">
                <img src="{img}" style="width:100%; filter: blur(8px);">
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    background: rgba(0,0,0,0.5);
                    padding: 5px 10px;
                    border-radius: 5px;
                ">
                    🔒 VIP
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align: center; margin-top: 40px;">
            <h4>💎 Desbloqueie acesso completo</h4>
            <p style="color: #aaa;">Assine um dos nossos planos para ver tudo</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🌟 Ver Planos Disponíveis", key="vip_button_gallery", use_container_width=True, type="primary"):
            st.session_state.current_page = "offers"
            st.rerun()

    @staticmethod
    def chat_shortcuts():
        cols = st.columns(4)
        shortcuts = {
            "🏠 Início": "home",
            "📸 Galeria": "gallery",
            "🎁 Ofertas": "offers",
            "💎 Planos": "offers"
        }
        
        for (text, page), col in zip(shortcuts.items(), cols):
            with col:
                if st.button(text, key=f"shortcut_{page}", help=f"Ir para {text}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()

        st.markdown("""
        <style>
            div[data-testid="stHorizontalBlock"] > div > div > button {
                font-size: 0.8rem !important;
                padding: 8px 4px !important;
            }
            @media (max-width: 400px) {
                div[data-testid="stHorizontalBlock"] > div > div > button {
                    font-size: 0.7rem !important;
                    padding: 6px 2px !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def enhanced_chat_ui(conn):
        st.markdown("""
        <style>
            .chat-header {
                background: linear-gradient(90deg, #ff66b3, #ff1493);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }
            .stAudio {
                border-radius: 20px !important;
                background: rgba(255, 102, 179, 0.1) !important;
                padding: 10px !important;
                margin: 10px 0 !important;
            }
            audio::-webkit-media-controls-panel {
                background: linear-gradient(45deg, #ff66b3, #ff1493) !important;
            }
            @media (max-width: 768px) {
                .chat-header {
                    padding: 10px;
                    font-size: 1.2em;
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        UiService.chat_shortcuts()
        
        st.markdown(f"""
        <div class="chat-header">
            <h2 style="margin:0;">💬 Chat Privado com Juh</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="
            background: rgba(255, 20, 147, 0.1);
            padding: 8px;
            border-radius: 8px;
            margin-bottom: 15px;
            text-align: center;
            font-size: 0.9em;
        ">
            <p style="margin:0 0 5px 0;">Mensagens: {st.session_state.request_count}/{Config.MAX_REQUESTS_PER_SESSION}</p>
            <progress value="{st.session_state.request_count}" max="{Config.MAX_REQUESTS_PER_SESSION}" 
                     style="width:100%; height:6px; border-radius:3px;"></progress>
        </div>
        """, unsafe_allow_html=True)

        ChatService.process_user_input(conn)
        
        st.markdown("""
        <div style="text-align: center; margin-top: 20px; color: #888; font-size: 0.8em;">
            <p>Conversa privada • Suas mensagens são confidenciais</p>
        </div>
        """, unsafe_allow_html=True)

# ===================================================
# SERVIÇOS DE CHAT (200 linhas)
# ===================================================
class ChatService:
    @staticmethod
    def initialize_session(conn):
        load_persistent_data()
        
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(random.randint(100000, 999999))
        
        if "messages" not in st.session_state:
            st.session_state.messages = DatabaseService.load_messages(
                conn,
                get_user_id(),
                st.session_state.session_id
            )
        
        if "request_count" not in st.session_state:
            st.session_state.request_count = len([
                m for m in st.session_state.messages 
                if m["role"] == "user"
            ])
        
        defaults = {
            'age_verified': False,
            'connection_complete': False,
            'chat_started': False,
            'audio_sent': False,
            'current_page': 'home',
            'show_vip_offer': False,
            'last_cta_time': 0
        }
        
        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

    @staticmethod
    def format_conversation_history(messages, max_messages=10):
        formatted = []
        
        for msg in messages[-max_messages:]:
            role = "Cliente" if msg["role"] == "user" else "Juh"
            content = msg["content"]
            if content == "[ÁUDIO]":
                content = "[áudio]"
            elif content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)

    @staticmethod
    def display_chat_history():
        chat_container = st.container()
        with chat_container:
            for idx, msg in enumerate(st.session_state.messages[-12:]):
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(f"""
                        <div style="
                            background: rgba(0, 0, 0, 0.1);
                            padding: 12px;
                            border-radius: 18px 18px 0 18px;
                            margin: 5px 0;
                        ">
                            {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                elif msg["content"] == "[ÁUDIO]":
                    with st.chat_message("assistant", avatar="💋"):
                        st.markdown(UiService.get_chat_audio_player(), unsafe_allow_html=True)
                else:
                    try:
                        content_data = json.loads(msg["content"])
                        if isinstance(content_data, dict):
                            with st.chat_message("assistant", avatar="💋"):
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                                    color: white;
                                    padding: 12px;
                                    border-radius: 18px 18px 18px 0;
                                    margin: 5px 0;
                                ">
                                    {content_data.get("text", "")}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if content_data.get("cta", {}).get("show") and idx == len(st.session_state.messages[-12:]) - 1:
                                    if st.button(
                                        content_data.get("cta", {}).get("label", "Ver Ofertas"),
                                        key=f"cta_button_{hash(msg['content'])}",
                                        use_container_width=True
                                    ):
                                        st.session_state.current_page = content_data.get("cta", {}).get("target", "offers")
                                        save_persistent_data()
                                        st.rerun()
                        else:
                            with st.chat_message("assistant", avatar="💋"):
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                                    color: white;
                                    padding: 12px;
                                    border-radius: 18px 18px 18px 0;
                                    margin: 5px 0;
                                ">
                                    {msg["content"]}
                                </div>
                                """, unsafe_allow_html=True)
                    except json.JSONDecodeError:
                        with st.chat_message("assistant", avatar="💋"):
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(45deg, #ff66b3, #ff1493);
                                color: white;
                                padding: 12px;
                                border-radius: 18px 18px 18px 0;
                                margin: 5px 0;
                            ">
                                {msg["content"]}
                            </div>
                            """, unsafe_allow_html=True)

    @staticmethod
    def validate_input(user_input):
        cleaned_input = re.sub(r'<[^>]*>', '', user_input)
        return cleaned_input[:500]

    @staticmethod
    def process_user_input(conn):
        ChatService.display_chat_history()
        
        if not st.session_state.get("audio_sent") and st.session_state.chat_started:
            status_container = st.empty()
            UiService.show_audio_recording_effect(status_container)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": "[ÁUDIO]"
            })
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "assistant",
                "[ÁUDIO]"
            )
            st.session_state.audio_sent = True
            save_persistent_data()
            st.rerun()
        
        user_input = st.chat_input("Escreva sua mensagem aqui", key="chat_input")
        
        if user_input:
            cleaned_input = ChatService.validate_input(user_input)
            
            if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Vou ficar ocupada agora, me manda mensagem depois?"
                })
                DatabaseService.save_message(
                    conn,
                    get_user_id(),
                    st.session_state.session_id,
                    "assistant",
                    "Estou ficando cansada, amor... Que tal continuarmos mais tarde?"
                )
                save_persistent_data()
                st.rerun()
                return
            
            st.session_state.messages.append({
                "role": "user",
                "content": cleaned_input
            })
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "user",
                cleaned_input
            )
            
            st.session_state.request_count += 1
            
            with st.chat_message("user", avatar="🧑"):
                st.markdown(f"""
                <div style="
                    background: rgba(0, 0, 0, 0.1);
                    padding: 12px;
                    border-radius: 18px 18px 0 18px;
                    margin: 5px 0;
                ">
                    {cleaned_input}
                </div>
                """, unsafe_allow_html=True)
            
            with st.chat_message("assistant", avatar="💋"):
                resposta = ApiService.ask_gemini(cleaned_input, st.session_state.session_id, conn)
                
                if isinstance(resposta, str):
                    resposta = {"text": resposta, "cta": {"show": False}}
                elif "text" not in resposta:
                    resposta = {"text": str(resposta), "cta": {"show": False}}
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                    color: white;
                    padding: 12px;
                    border-radius: 18px 18px 18px 0;
                    margin: 5px 0;
                ">
                    {resposta["text"]}
                </div>
                """, unsafe_allow_html=True)
                
                if resposta.get("cta", {}).get("show"):
                    if st.button(
                        resposta["cta"].get("label", "Ver Ofertas"),
                        key=f"chat_button_{time.time()}",
                        use_container_width=True
                    ):
                        st.session_state.current_page = resposta["cta"].get("target", "offers")
                        save_persistent_data()
                        st.rerun()
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": json.dumps(resposta)
            })
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "assistant",
                json.dumps(resposta)
            )
            
            save_persistent_data()
            
            st.markdown("""
            <script>
                window.scrollTo(0, document.body.scrollHeight);
            </script>
            """, unsafe_allow_html=True)

# ===================================================
# SERVIÇOS DE API (100 linhas)
# ===================================================
class ApiService:
    @staticmethod
    @lru_cache(maxsize=100)
    def ask_gemini(prompt: str, session_id: str, conn) -> dict:
        if any(word in prompt.lower() for word in ["pix", "comprar", "assinar"]):
            return ApiService._handle_payment_requests(prompt, session_id, conn)
        
        return ApiService._generate_standard_response(prompt, session_id, conn)

    @staticmethod
    def _handle_payment_requests(prompt: str, session_id: str, conn) -> dict:
        if "pix" in prompt.lower():
            return {
                "text": Config.generate_pix("premium"),
                "cta": {"show": False}
            }
        return {
            "text": "Posso te ajudar com informações sobre nossos planos!",
            "cta": {"show": True, "label": "Ver Planos", "target": "offers"}
        }

    @staticmethod
    def _generate_standard_response(prompt: str, session_id: str, conn) -> dict:
        conversation_history = ChatService.format_conversation_history(st.session_state.messages)
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{Persona.JUH}\nHistórico:\n{conversation_history}\nCliente: '{prompt}'"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.8
            }
        }
        
        try:
            response = requests.post(Config.API_URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"text": "Ops, tive um probleminha... Pode repetir?", "cta": {"show": False}}

# ===================================================
# PÁGINAS (150 linhas)
# ===================================================
class NewPages:
    @staticmethod
    def show_home_page():
        st.markdown("""
        <style>
            .hero-banner {
                background: linear-gradient(135deg, #1e0033, #3c0066);
                padding: 80px 20px;
                text-align: center;
                border-radius: 15px;
                margin-bottom: 30px;
                border: 2px solid #ff66b3;
            }
            @media (max-width: 768px) {
                .hero-banner {
                    padding: 40px 15px;
                }
            }
        </style>
        
        <div class="hero-banner">
            <h1 style="color: #ff66b3;">Juh Premium</h1>
            <p style="color: white;">Conteúdo exclusivo que você não encontra em nenhum outro lugar...</p>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for col, img in zip(cols, Config.IMG_HOME_PREVIEWS):
            with col:
                st.image(img, use_container_width=True, caption="Conteúdo bloqueado")

        if st.button("Iniciar Conversa Privada", use_container_width=True, type="primary"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

    @staticmethod
    def show_offers_page():
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #ff66b3; border-bottom: 2px solid #ff66b3; display: inline-block; padding-bottom: 5px;">
                PACOTES EXCLUSIVOS
            </h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="display: flex; gap: 20px; margin-bottom: 40px;">', unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            flex: 1;
            border: 1px solid #ff66b3;
            border-radius: 15px;
            padding: 20px;
            background: rgba(30,0,51,0.1);
        ">
            <h3>START</h3>
            <p style="font-size: 1.8em; color: #ff66b3; font-weight: bold;">R$ 19,50</p>
            <ul>
                <li>📸 10 fotos inéditas</li>
                <li>🎥 3 vídeos exclusivos</li>
                <li>💬 Chat prioritário</li>
            </ul>
            <div style="text-align: center; margin-top: 20px;">
                <a href="{checkout_start}" style="
                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                    color: white;
                    padding: 12px 30px;
                    border-radius: 25px;
                    text-decoration: none;
                    font-weight: bold;
                    display: inline-block;
                ">🛒 Assinar Agora</a>
            </div>
        </div>
        """.format(checkout_start=Config.CHECKOUT_START), unsafe_allow_html=True)

        st.markdown("""
        <div style="
            flex: 1;
            border: 1px solid #9400d3;
            border-radius: 15px;
            padding: 20px;
            background: rgba(30,0,51,0.1);
            position: relative;
        ">
            <div style="
                position: absolute;
                top: 15px;
                right: -15px;
                background: #ff0066;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                transform: rotate(15deg);
                font-weight: bold;
            ">POPULAR</div>
            
            <h3>PREMIUM</h3>
            <p style="font-size: 1.8em; color: #9400d3; font-weight: bold;">R$ 45,50</p>
            <ul>
                <li>🔥 20 fotos", "💋 Conteúdo VIP"],
                "link": Config.CHECKOUT_PREMIUM
            }
        ]
for plan in plans:
    st.markdown(
        f'''
        <div style="
            border: 1px solid #ff66b3;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        ">
            <h3>{plan.get("name", "Plano")}</h3>
            <p style="font-size: 1.5em; color: #ff66b3;">{plan.get("price", "R$ --")}</p>
            <ul>{''.join(f'<li>{benefit}</li>' for benefit in plan.get("benefits", []))}</ul>
            <a href="{plan.get("link", "#")}" style="
                background: #ff66b3;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
            ">Assinar</a>
        </div>
        ''',
        unsafe_allow_html=True
    )
                    color: white;
                    padding: 10px 20px;
                    border-radius: 20px;
                    display: inline-block;
                    text-decoration: none;
                ">🛒 Assinar</a>
            </div>
            """, unsafe_allow_html=True)

# ======================
# SERVIÇOS DE CHAT
# ======================
class ChatService:
    @staticmethod
    def process_user_input(user_input):
        if "pix" in user_input.lower():
            return {
                "text": Config.generate_pix("premium"),
                "cta": {"show": False}
            }
        
        return {
            "text": "Como posso te ajudar hoje?",
            "cta": {"show": True, "label": "Ver Planos", "target": "offers"}
        }

# ======================
# APLICAÇÃO PRINCIPAL
# ======================
def main():
    st.set_page_config(page_title="Juh Premium", layout="wide")
    
    if not st.session_state.get("age_verified"):
        UiService.age_verification()
        st.stop()

    user_input = st.chat_input("Digite sua mensagem...")
    if user_input:
        response = ChatService.process_user_input(user_input)
        st.write(response["text"])

if __name__ == "__main__":
    main()

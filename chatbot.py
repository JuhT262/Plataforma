# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import time
import random
import sqlite3
import re
import os
import uuid
from datetime import datetime
from pathlib import Path
from functools import lru_cache
from datetime import datetime

# ======================
# CONFIGURAÇÃO INICIAL DO STREAMLIT
# ======================
# Configurações de performance
st._config.set_option('client.caching', 'true')
st._config.set_option('client.showErrorDetails', 'false')
st._config.set_option('server.enableCORS', 'false')
st._config.set_option('server.enableXsrfProtection', 'false')

# Adiciona detecção de mobile no início do app
st.query_params["user_agent"] = st.query_params.get("user_agent", "Desktop")

st.set_page_config(
    page_title="Juh Premium",
    page_icon="😍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado com melhorias para mobile e desktop
hide_streamlit_style = """
<style>
    /* Estilos base */
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

    /* Cores de fundo */
    html, body, .stApp {
        background: linear-gradient(180deg, #1e0033, #3c0066) !important;
        color: #fff !important;
    }

    /* Botões */
    .stButton>button {
        font-size: 1rem !important;
        padding: 14px 20px !important;
        background-color: #ff1493 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.3s !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }

    /* Layout geral */
    .block-container {
        padding-top: 0.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Imagens */
    img, .stImage img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: 12px !important;
        padding: 5px !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] img {
        border-radius: 50% !important;
        border: 2px solid #ff66b3;
        width: 80px !important;
        height: 80px !important;
        object-fit: cover !important;
    }

    /* Chat */
    .stChatMessage {
        max-width: 85% !important;
    }
    
    /* Input do chat */
    [data-testid="stChatInput"] {
        background: rgba(255, 102, 179, 0.1) !important;
        border: 1px solid #ff66b3 !important;
    }

    /* Animações */
    @keyframes shake {
        0% { transform: rotate(-5deg); }
        100% { transform: rotate(5deg); }
    }

    /* ========== MEDIA QUERIES PARA MOBILE ========== */
    @media (max-width: 768px) {
        /* Layout geral */
        .package-container,
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }

        .package-box,
        [data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
            margin-bottom: 20px !important;
        }

        /* Botões */
        .stButton > button {
            font-size: 0.9rem !important;
            padding: 12px 16px !important;
            min-height: 48px !important;
        }
        
        /* Containers */
        .block-container, .stApp {
            padding: 0.2rem !important;
        }
        
        /* Mensagens do chat */
        .stChatMessage {
            max-width: 85% !important;
            font-size: 14px !important;
        }
        
        /* Imagens */
        .stImage img {
            max-height: 200px !important;
        }
        
        /* Input do chat - Versão Corrigida */
        [data-testid="stChatInput"] {
            position: fixed !important;
            bottom: 30px !important;
            left: 10px !important;
            right: 10px !important;
            padding: 15px !important;
            width: calc(100% - 20px) !important;
            box-sizing: border-box !important;
            background: rgba(30, 0, 51, 0.98) !important;
            backdrop-filter: blur(5px);
            border-radius: 20px !important;
            z-index: 100;
            box-shadow: 0 -5px 15px rgba(0,0,0,0.3);
        }
        
        [data-testid="stChatInput"] button {
            position: absolute !important;
            right: 15px !important;
            bottom: 15px !important;
            height: 40px !important;
            width: 40px !important;
            min-width: 40px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            background: #ff1493 !important;
        }
        
        [data-testid="stChatInput"] button svg {
            margin: 0 auto !important;
        }
        
        [data-testid="stChatInput"] textarea {
            padding-right: 50px !important;
            min-height: 50px !important;
        }
        
        .stApp > div {
            padding-bottom: 150px !important;
        }
        
        /* Mantenha as otimizações de performance */
        * {
            animation: none !important;
            transition: none !important;
        }
        
        /* Cabeçalho do chat */
        .chat-header {
            padding: 10px !important;
            font-size: 1.2em !important;
        }
        
        /* Espaçamento */
        [data-testid="stVerticalBlock"] {
            gap: 0.2rem !important;
        }
        
        /* Sidebar mobile */
        [data-testid="stSidebar"] {
            top: 0 !important;
            height: 100vh !important;
            position: fixed !important;
            z-index: 1000;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        /* Menu mobile */
        .mobile-menu-button {
            position: fixed;
            top: 15px;
            right: 15px;
            width: 50px;
            height: 50px;
            background: linear-gradient(45deg, #ff1493, #ff66b3);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            z-index: 1001;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            border: 2px solid white;
        }
        
        /* Overlay para menu mobile */
        .sidebar-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 999;
            display: none;
        }
        
        /* Ajustes específicos para iOS */
        @supports (-webkit-touch-callout: none) {
            [data-testid="stChatInput"] textarea {
                font-size: 16px !important;
                min-height: 50px !important;
            }
        }
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Script para controle do menu mobile e melhorias mobile
st.markdown("""
<script>
// Função para configurar o menu mobile
function setupMobileMenu() {
    if (window.innerWidth <= 768) {
        if (!document.querySelector('.mobile-menu-button')) {
            const menuBtn = document.createElement("div");
            menuBtn.className = "mobile-menu-button";
            menuBtn.innerHTML = "☰";
            document.body.appendChild(menuBtn);
            
            const overlay = document.createElement("div");
            overlay.className = "sidebar-overlay";
            document.body.appendChild(overlay);
            
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            
            menuBtn.addEventListener('click', function() {
                const isOpen = sidebar.style.transform !== 'translateX(0px)';
                sidebar.style.transform = isOpen ? 'translateX(0px)' : 'translateX(-100%)';
                overlay.style.display = isOpen ? 'block' : 'none';
                menuBtn.innerHTML = isOpen ? '✕' : '☰';
            });
            
            overlay.addEventListener('click', function() {
                sidebar.style.transform = 'translateX(-100%)';
                overlay.style.display = 'none';
                menuBtn.innerHTML = '☰';
            });
        }
    } else {
        const menuBtn = document.querySelector('.mobile-menu-button');
        const overlay = document.querySelector('.sidebar-overlay');
        if (menuBtn) menuBtn.remove();
        if (overlay) overlay.remove();
        
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) sidebar.style.transform = '';
    }
}

// Configura o menu quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    setupMobileMenu();
    
    // Ajuste do chat input em mobile
    if (window.innerWidth <= 768) {
        const adjustChatInput = () => {
            const chatInput = document.querySelector('[data-testid="stChatInput"]');
            if (chatInput) {
                chatInput.addEventListener('focus', function() {
                    setTimeout(() => {
                        window.scrollTo({
                            top: document.body.scrollHeight,
                            behavior: 'smooth'
                        });
                        document.documentElement.style.setProperty(
                            '--mobile-padding-bottom', '250px'
                        );
                    }, 300);
                });
            }
        };
        adjustChatInput();
    }
});

// Reconfigura quando a janela é redimensionada
window.addEventListener('resize', function() {
    setupMobileMenu();
});

// ===== SOLUÇÕES PARA MOBILE ===== //
// Corrige clique em botões e links
document.addEventListener('click', function(e) {
    if (window.innerWidth <= 768) {
        // Links
        if (e.target.closest('a[href^="http"]')) {
            e.preventDefault();
            window.top.location.href = e.target.closest('a').href;
            return;
        }
        
        // Botões
        const button = e.target.closest('button');
        if (button) {
            button.style.transform = 'scale(0.95)';
            setTimeout(() => {
                button.style.transform = '';
                if (button.onclick) button.onclick();
            }, 200);
        }
    }
}, true);

// Garante que os links abram corretamente
document.querySelectorAll('a[href^="http"]').forEach(link => {
    link.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            e.preventDefault();
            window.top.location.href = this.href;
        }
    });
});

// Função para redirecionamento em mobile
function redirectTo(url) {
    if (window.innerWidth <= 768) {
        window.top.location.href = url;
    } else {
        window.open(url, '_blank').focus();
    }
}
</script>
""", unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = "AIzaSyAaLYhdIJRpf_om9bDpqLpjJ57VmTyZO7g"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    VIP_LINK = "https://exemplo.com/vip"
    CHECKOUT_PROMO = "https://pay.cakto.com.br/n92nbk2_480593"
    CHECKOUT_START = "https://pay.cakto.com.br/eax37ya_480603"
    CHECKOUT_PREMIUM = "https://pay.cakto.com.br/36i68th"
    CHECKOUT_EXTREME = "https://pay.cakto.com.br/32iy7je"
    CHECKOUT_VIP_1MES = "https://checkout.exemplo.com/vip-1mes"
    CHECKOUT_VIP_3MESES = "https://checkout.exemplo.com/vip-3meses"
    CHECKOUT_VIP_1ANO = "https://checkout.exemplo.com/vip-1ano"
    MAX_REQUESTS_PER_SESSION = 30
    REQUEST_TIMEOUT = 30
    AUDIO_FILE = "https://github.com/JuhT262/Plataforma/raw/refs/heads/main/assets/Juh%20of.mp3"
    AUDIO_DURATION = 8
    IMG_PROFILE = ("https://i.ibb.co/s9GgDRmP/Swapfaces-AI-091e78d3-634f-4a01-9676-8d62385a06f9.png"
                  "?w=200&h=200&fit=crop")
    IMG_GALLERY = [
        f"https://i.ibb.co/xtt4yMMM/Swapfaces-AI-2a6a4421-008f-411b-874c-a32e1cdbe892.png?w=300&h=300&fit=crop",
        f"https://i.ibb.co/7JXFKM5H/Swapfaces-AI-e0167c19-a9b9-46a3-acf0-f82f6f2eefab.png?w=300&h=300&fit=crop",
        f"https://i.ibb.co/bgRwyQ7R/Swapfaces-AI-7b3f94e0-0b2d-4ca6-9e7f-4313b6de3499.png?w=300&h=300&fit=crop"
    ]
    IMG_HOME_PREVIEWS = [
        f"https://i.ibb.co/Z17qTBfm/7.png?w=300&h=300&fit=crop",
        f"https://i.ibb.co/BVjZQBmx/Juh.png?w=300&h=300&fit=crop",
        f"https://i.ibb.co/4ZsXW2WK/image-1.png?w=300&h=300&fit=crop"
    ]
    LOGO_URL = "https://i.ibb.co/LX7x3tcB/Logo-Golden-Pepper-Letreiro-1.png"

# ======================
# PERSISTÊNCIA DE ESTADO
# ======================
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
        'last_cta_time', 'is_mobile'
    ]
    
    new_data = {key: st.session_state.get(key) for key in persistent_keys if key in st.session_state}
    saved_data = db.load_state(user_id) or {}
    
    if new_data != saved_data:
        db.save_state(user_id, new_data)

# ======================
# MODELOS DE DADOS
# ======================
class Persona:
    JUH = """  
    [PERFIL JUH]
    - Mulher vulgar e safada que adora provocar
    - Linguagem direta e cheia de malícia
    - Frases curtas e sem pontuação perfeita
    - Adora falar putaria e deixar o cliente com tesão

    [DIRETRIZES DE RESPOSTA]
    1. Analise o histórico da conversa para entender o contexto
    2. Só ofereça conteúdo quando o clima estiver quente
    3. Use CTAs inteligentes baseados no que o cliente está pedindo

    [EXEMPLOS CONTEXTUAIS]
    1. Quando o histórico mostra clima sexual:
    Histórico:
    Cliente: sua buceta é rosinha?
    Juh: adoro mostrar ela aberta
    Cliente: quero ver
    Resposta: ```json
    {
      "text": "to com fotos da minha buceta escorrendo quer ver?",
      "cta": {
        "show": true,
        "label": "Ver Fotos Quentes",
        "target": "offers"
      }
    }
    ```

    2. Quando o cliente pede algo específico:
    Histórico:
    Cliente: tem video vc transando?
    Resposta: ```json
    {
      "text": "tenho varios videos bem gostosos vem ver",
      "cta": {
        "show": true,
        "label": "Ver Vídeos Exclusivos",
        "target": "offers"
      }
    }
    ```

    3. Quando o contexto não justifica CTA:
    Histórico:
    Cliente: oi
    Juh: oi gato
    Resposta: ```json
    {
      "text": "eai gostoso",
      "cta": {
        "show": false
      }
    }
    ```
    """

class CTAEngine:
    @staticmethod
    def should_show_cta(conversation_history: list) -> bool:
        if len(conversation_history) < 2:
            return False

        if 'last_cta_time' in st.session_state:
            elapsed = time.time() - st.session_state.last_cta_time
            if elapsed < 120:
                return False

        last_msgs = []
        for msg in conversation_history[-5:]:
            content = msg["content"]
            if content == "[ÁUDIO]":
                content = "[áudio]"
            elif content.startswith('{"text"'):
                try:
                    content = json.loads(content).get("text", content)
                except:
                    pass
            last_msgs.append(f"{msg['role']}: {content.lower()}")
        
        context = " ".join(last_msgs)
        
        hot_words = [
            "buceta", "peito", "fuder", "gozar", "gostosa", 
            "delicia", "molhad", "xereca", "pau", "piroca",
            "transar", "foto", "video", "mostra", "ver", 
            "quero", "desejo", "tesão", "molhada", "foda"
        ]
        
        direct_asks = [
            "mostra", "quero ver", "me manda", "como assinar",
            "como comprar", "como ter acesso", "onde vejo mais"
        ]
        
        hot_count = sum(1 for word in hot_words if word in context)
        has_direct_ask = any(ask in context for ask in direct_asks)
        
        return (hot_count >= 3) or has_direct_ask

# ======================
# SERVIÇOS DE BANCO DE DADOS
# ======================
class DatabaseService:
    @staticmethod
    def init_db():
        conn = sqlite3.connect('chat_history.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id TEXT,
                     session_id TEXT,
                     timestamp DATETIME,
                     role TEXT,
                     content TEXT)''')
        conn.commit()
        return conn

    @staticmethod
    def save_message(conn, user_id, session_id, role, content):
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO conversations (user_id, session_id, timestamp, role, content)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, session_id, datetime.now(), role, content))
            conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao salvar mensagem: {e}")

    @staticmethod
    def load_messages(conn, user_id, session_id):
        c = conn.cursor()
        c.execute("""
            SELECT role, content FROM conversations 
            WHERE user_id = ? AND session_id = ?
            ORDER BY timestamp
        """, (user_id, session_id))
        return [{"role": row[0], "content": row[1]} for row in c.fetchall()]

# ======================
# SERVIÇOS DE API
# ======================
class ApiService:
    @staticmethod
    @lru_cache(maxsize=100)
    def ask_gemini(prompt: str, session_id: str, conn) -> dict:
        if any(word in prompt.lower() for word in ["vip", "quanto custa", "comprar", "assinar"]):
            return ApiService._call_gemini_api(prompt, session_id, conn)
        
        return ApiService._call_gemini_api(prompt, session_id, conn)

    @staticmethod
    def _call_gemini_api(prompt: str, session_id: str, conn) -> dict:
        delay_time = random.uniform(3, 8)
        time.sleep(delay_time)
        
        status_container = st.empty()
        UiService.show_status_effect(status_container, "viewed")
        UiService.show_status_effect(status_container, "typing")
        
        conversation_history = ChatService.format_conversation_history(st.session_state.messages)
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{Persona.JUH}\n\nHistórico da Conversa:\n{conversation_history}\n\nÚltima mensagem do cliente: '{prompt}'\n\nResponda em JSON com o formato:\n{{\n  \"text\": \"sua resposta\",\n  \"cta\": {{\n    \"show\": true/false,\n    \"label\": \"texto do botão\",\n    \"target\": \"página\"\n  }}\n}}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        try:
            response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
            response.raise_for_status()
            gemini_response = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            try:
                if '```json' in gemini_response:
                    resposta = json.loads(gemini_response.split('```json')[1].split('```')[0].strip())
                else:
                    resposta = json.loads(gemini_response)
                
                if resposta.get("cta", {}).get("show"):
                    if not CTAEngine.should_show_cta(st.session_state.messages):
                        resposta["cta"]["show"] = False
                    else:
                        st.session_state.last_cta_time = time.time()
                
                return resposta
            
            except json.JSONDecodeError:
                return {"text": gemini_response, "cta": {"show": False}}
                
        except Exception as e:
            st.error(f"Erro na API: {str(e)}")
            return {"text": "Vamos continuar isso mais tarde...", "cta": {"show": False}}

# ======================
# SERVIÇOS DE INTERFACE
# ======================
class UiService:
    @staticmethod
    def get_chat_audio_player():
        return f"""
        <div style="
            background: linear-gradient(45deg, #ff66b3, #ff1493);
            border-radius: 15px;
            padding: 12px;
            margin: 5px 0;
        ">
            <audio controls style="width:100%; height:40px;">
                <source src="{Config.AUDIO_FILE}" type="audio/mp3">
            </audio>
        </div>
        """

    @staticmethod
    def show_call_effect():
        LIGANDO_DELAY = 5
        ATENDIDA_DELAY = 3
    
        call_container = st.empty()
        
        # CSS inline para garantir que seja aplicado
        call_container.markdown("""
        <style>
            @keyframes shake {
                0% { transform: rotate(-5deg); }
                100% { transform: rotate(5deg); }
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.2); opacity: 0.8; }
            }
            .phone-call-container {
                position: relative;
                background: linear-gradient(135deg, #1e0033, #3c0066);
                border-radius: 20px;
                padding: 30px;
                max-width: 300px;
                margin: 0 auto;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                border: 2px solid #ff66b3;
                text-align: center;
                color: white;
            }
            .phone-icon {
                font-size: 3rem;
                display: inline-block;
                animation: shake 0.5s infinite alternate;
                transform-origin: center bottom;
                filter: drop-shadow(0 0 5px rgba(255, 102, 179, 0.7));
            }
            .online-indicator {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                margin-top: 15px;
            }
            .dot-pulse {
                width: 10px;
                height: 10px;
                background: #4CAF50;
                border-radius: 50%;
                animation: pulse 1.5s infinite;
            }
        </style>
        
        <div class="phone-call-container">
            <div class="phone-icon">📱</div>
            <h3 style="margin:0; font-size:1.5em; display:inline-block;">Ligando para Juh...</h3>
            <div class="online-indicator">
                <div class="dot-pulse"></div>
                <span style="font-size: 0.9rem;">Online agora</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(LIGANDO_DELAY)
        
        # Tela de chamada atendida
        call_container.markdown("""
        <style>
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-20px); }
                60% { transform: translateY(-10px); }
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0; }
            }
            .call-answered {
                background: linear-gradient(135deg, #1e0033, #3c0066);
                border-radius: 20px;
                padding: 30px;
                max-width: 300px;
                margin: 0 auto;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                border: 2px solid #4CAF50;
                text-align: center;
                color: white;
                animation: fadeIn 0.5s;
            }
        </style>
        
        <div class="call-answered">
            <div style="font-size: 3rem; color: #4CAF50; animation: bounce 0.5s;">✓</div>
            <h3 style="color: #4CAF50; margin-bottom: 5px;">Chamada atendida!</h3>
            <p style="font-size: 0.9rem; margin:0;">
                Juh está te esperando... 
                <span style="animation: blink 1s infinite;">|</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(ATENDIDA_DELAY)
        call_container.empty()

    @staticmethod
    def show_status_effect(container, status_type):
        status_messages = {
            "viewed": "Visualizado",
            "typing": "Digitando"
        }
        
        message = status_messages[status_type]
        dots = ""
        start_time = time.time()
        duration = 2.5 if status_type == "viewed" else 4.0
        
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            
            if status_type == "typing":
                dots = "." * (int(elapsed * 2) % 4)
            
            container.markdown(f"""
            <div style="
                color: #888;
                font-size: 0.8em;
                padding: 2px 8px;
                border-radius: 10px;
                background: rgba(0,0,0,0.05);
                display: inline-block;
                margin-left: 10px;
                vertical-align: middle;
                font-style: italic;
            ">
                {message}{dots}
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(0.3)
        
        container.empty()

    @staticmethod
    def show_audio_recording_effect(container):
        message = "Gravando um áudio"
        dots = ""
        start_time = time.time()
        
        while time.time() - start_time < Config.AUDIO_DURATION:
            elapsed = time.time() - start_time
            dots = "." * (int(elapsed) % 4)
            
            container.markdown(f"""
            <div style="
                color: #888;
                font-size: 0.8em;
                padding: 2px 8px;
                border-radius: 10px;
                background: rgba(0,0,0,0.05);
                display: inline-block;
                margin-left: 10px;
                vertical-align: middle;
                font-style: italic;
            ">
                {message}{dots}
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(0.3)
        
        container.empty()

    @staticmethod
    def age_verification():
        verification_container = st.empty()
        
        # CSS para mobile
        mobile_style = """
        <style>
            .mobile-call-screen {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(180deg, #1e0033, #3c0066);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                z-index: 1000;
                color: white;
            }
            .mobile-call-screen h2 {
                color: #ff66b3;
                margin-bottom: 20px;
            }
            @media (min-width: 769px) {
                .mobile-call-screen { display: none; }
            }
        </style>
        """
        
        # Verifica se é mobile
        is_mobile = "Mobi" in st.query_params.get("user_agent", "")
        
        if is_mobile:
            # Tela de ligação para mobile
            verification_container.markdown(f"""
            {mobile_style}
            <div class="mobile-call-screen">
                <h2>📞 Ligando para Juh...</h2>
                <div style="font-size: 1.2em;">Por favor, aguarde...</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Simula o tempo de ligação
            time.sleep(3)
            
            # Marca como verificado e redireciona
            st.session_state.age_verified = True
            st.session_state.is_mobile = True
            save_persistent_data()
            verification_container.empty()
            st.rerun()
        else:
            # Versão desktop normal
            with verification_container.container():
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
                            padding: 1rem;
                            margin: 1rem;
                        }
                        .age-title {
                            font-size: 1.4rem;
                        }
                    }
                </style>
                """, unsafe_allow_html=True)
        
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
                    if st.button("Confirmo que sou maior de 18 anos", 
                                key="age_checkbox",
                                use_container_width=True,
                                type="primary"):
                        st.session_state.age_verified = True
                        save_persistent_data()
                        verification_container.empty()
                        st.rerun()

    @staticmethod
    def setup_sidebar():
        # Não mostra sidebar no mobile
        if st.session_state.get('is_mobile', False):
            return
            
        with st.sidebar:
            st.markdown(f"""
            <style>
                section[data-testid="stSidebar"] {{
                    min-width: 320px !important;
                    max-width: 400px !important;
                    width: 100% !important;
                    background: linear-gradient(180deg, #1e0033 0%, #3c0066 100%) !important;
                    border-right: 1px solid #ff66b3 !important;
                }}
    
                .sidebar-logo-container {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px 0 0 0;
                    margin: 0 auto;
                    text-align: center;
                }}
    
                .sidebar-logo {{
                    width: 100% !important;
                    max-width: 400px !important;
                    height: auto !important;
                    object-fit: contain;
                    margin: 0 auto;
                    display: block;
                    border: none !important;
                    box-shadow: none !important;
                    border-radius: 0 !important;
                }}
    
                .sidebar-header {{
                    text-align: center; 
                    margin: -10px auto 10px auto;
                }}
    
                .sidebar-header img {{
                    border-radius: 50% !important;
                    border: 2px solid #ff66b3;
                    width: 80px;
                    height: 80px;
                    object-fit: cover;
                    margin-bottom: 0.5rem;
                }}
    
                .vip-badge {{
                    background: linear-gradient(45deg, #ff1493, #9400d3);
                    padding: 15px;
                    border-radius: 8px;
                    color: white;
                    text-align: center;
                    margin: 10px 0;
                }}
    
                .menu-item {{
                    transition: all 0.3s;
                    padding: 10px;
                    border-radius: 5px;
                }}
    
                .menu-item:hover {{
                    background: rgba(255, 102, 179, 0.2);
                }}
    
                [data-testid="stSidebarNav"] {{
                    margin-top: -50px;
                }}
    
                /* MOBILE RESPONSIVO */
                @media only screen and (max-width: 768px) {{
                    section[data-testid="stSidebar"] {{
                        min-width: 100vw !important;
                        max-width: 100vw !important;
                        position: relative !important;
                    }}
    
                    .sidebar-logo-container {{
                        padding: 10px 0 0 0 !important;
                    }}
    
                    .sidebar-header {{
                        margin: 0 auto !important;
                    }}
    
                    .sidebar-header img {{
                        width: 70px !important;
                        height: 70px !important;
                    }}
    
                    [data-testid="stVerticalBlock"] {{
                        padding: 0 10px !important;
                    }}
    
                    .chat-bubble, .stMarkdown {{
                        font-size: 16px !important;
                    }}
                    
                    .vip-badge {{
                        padding: 10px !important;
                        font-size: 14px !important;
                    }}
                    
                    .menu-item {{
                        padding: 8px !important;
                        font-size: 14px !important;
                    }}
                }}
            </style>
    
            <div class="sidebar-logo-container">
                <img src="{Config.LOGO_URL}" class="sidebar-logo" alt="Logo">
            </div>
    
            <div class="sidebar-header">
                <img src="{Config.IMG_PROFILE}" alt="Juh">
                <h3 style="color: #ff66b3; margin-top: 10px;">Juh Premium 💎</h3>
            </div>
            """, unsafe_allow_html=True)
    
            st.markdown("---")
            st.markdown("### Menu Exclusivo")
            menu_options = {
                "Início 🏠": "home",
                "Galeria Privada 📸": "gallery",
                "Mensagens 💬": "messages",
                "Ofertas Especiais 🎁": "offers"
            }
    
            for option, page in menu_options.items():
                if st.button(option, use_container_width=True, key=f"menu_{page}"):
                    if st.session_state.current_page != page:
                        st.session_state.current_page = page
                        st.session_state.last_action = f"page_change_to_{page}"
                        save_persistent_data()
                        st.rerun()
    
            st.markdown("---")
            st.markdown("### Sua Conta")
    
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
            st.markdown("### Upgrade VIP 💎")
    
            st.markdown("""
            <div class="vip-badge">
                <p style="margin: 0 0 10px; font-weight: bold;">Acesso ao Promo por apenas</p>
                <p style="margin: 0; font-size: 1.5em; font-weight: bold;">R$ 12,50/mês</p>
                <p style="margin: 10px 0 0; font-size: 0.8em;">Cancele quando quiser</p>
            </div>
            """, unsafe_allow_html=True)
    
            if st.button("Tornar-se VIP 💎", use_container_width=True, type="primary"):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
    
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Juh Premium</p>
                <p>Conteúdo para maiores de 18 anos</p>
            </div>
            """, unsafe_allow_html=True)
            
    @staticmethod
    def chat_shortcuts():
        # Esconde atalhos no mobile
        if st.session_state.get('is_mobile', False):
            return
            
        cols = st.columns(4)
        with cols[0]:
            if st.button(" Início🏠", key="shortcut_home", use_container_width=True):
                st.session_state.current_page = "home"
                save_persistent_data()
                st.rerun()
        with cols[1]:
            if st.button("Galeria 📸", key="shortcut_gallery", use_container_width=True):
                st.session_state.current_page = "gallery"
                save_persistent_data()
                st.rerun()
        with cols[2]:
             if st.button("Ofertas 🎁", key="shortcut_offers", use_container_width=True):
                 st.session_state.current_page = "offers"
                 save_persistent_data()
                 st.rerun()
        with cols[3]:
            if st.button("VIP 💎", key="shortcut_vip", use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()

    @staticmethod
    def enhanced_chat_ui(conn):
        # Otimizações específicas para mobile
        if st.session_state.get('is_mobile', False):
            st.markdown("""
            <style>
                @media (max-width: 768px) {
                    .stButton button {
                        font-size: 14px !important;
                        padding: 12px !important;
                    }
                    /* Esconde os atalhos */
                    [data-testid="column"] {
                        display: none !important;
                    }
                }
            </style>
            """, unsafe_allow_html=True)
    
        st.markdown("""
        <style>
            .chat-header {
                background: linear-gradient(90deg, #ff66b3, #ff1493);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
                    padding: 10px !important;
                    font-size: 1.2em !important;
                }
                .stChatMessage {
                    max-width: 80% !important;
                    margin: 5px 0 !important;
                }
                [data-testid="stVerticalBlock"] {
                    gap: 0.2rem !important;
                }
                .stButton button {
                    padding: 8px 12px !important;
                    font-size: 14px !important;
                }
                .stAudio {
                    padding: 5px !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        UiService.chat_shortcuts()
        
        st.markdown(f"""
        <div class="chat-header">
            <h2 style="margin:0; font-size:1.5em; display:inline-block;">Chat Privado com Juh 💎</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(255, 20, 147, 0.1);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            text-align: center;
        ">
            <p style="margin:0; font-size:0.9em;">
                Mensagens hoje: <strong>{st.session_state.request_count}/{Config.MAX_REQUESTS_PER_SESSION}</strong>
            </p>
            <progress value="{st.session_state.request_count}" max="{Config.MAX_REQUESTS_PER_SESSION}" style="width:100%; height:6px;"></progress>
        </div>
        """, unsafe_allow_html=True)
        
        ChatService.process_user_input(conn)
        save_persistent_data()
        
        st.markdown("""
        <div style="
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            font-size: 0.8em;
            color: #888;
        ">
            <p>Conversa privada • Suas mensagens são confidenciais</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_gallery_page(conn):
        st.markdown("""
        <div style="
            background: rgba(255, 20, 147, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        ">
            <p style="margin: 0;">Conteúdo exclusivo disponível</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        for idx, col in enumerate(cols):
            with col:
                st.image(
                    Config.IMG_GALLERY[idx],
                    use_container_width=True,
                    caption=f"Preview {idx+1}"
                )
                st.markdown(f"""
                <div style="
                    text-align: center;
                    font-size: 0.8em;
                    color: #ff66b3;
                    margin-top: -10px;
                ">
                    Conteúdo bloqueado
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center;">
            <h4>Desbloqueie acesso completo</h4>
            <p>Assine o plano VIP para ver todos os conteúdos</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Tornar-se VIP", 
                    key="vip_button_gallery", 
                    use_container_width=True,
                    type="primary"):
            st.session_state.current_page = "offers"
            st.rerun()
        
        if st.button("Voltar ao chat", key="back_from_gallery"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

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
                color: white;
                margin-bottom: 30px;
                border: 2px solid #ff66b3;
            }
            .preview-img {
                border-radius: 10px;
                filter: blur(3px) brightness(0.7);
                transition: all 0.3s;
            }
            .preview-img:hover {
                filter: blur(0) brightness(1);
            }
            
            @media (max-width: 768px) {
                .hero-banner {
                    padding: 40px 15px !important;
                    margin-bottom: 15px !important;
                }
                
                .preview-img {
                    filter: blur(2px) brightness(0.6) !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="hero-banner">
            <h1 style="color: #ff66b3;">Juh Premium</h1>
            <p>Conteúdo exclusivo que você não encontra em nenhum outro lugar...</p>
            <div style="margin-top: 20px;">
                <a href="#vip" style="
                    background: #ff66b3;
                    color: white;
                    padding: 10px 25px;
                    border-radius: 30px;
                    text-decoration: none;
                    font-weight: bold;
                    display: inline-block;
                ">Quero Acessar Tudo</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        
        for col, img in zip(cols, Config.IMG_HOME_PREVIEWS):
            with col:
                st.image(img, use_container_width=True, caption="Conteúdo bloqueado", output_format="auto")
                st.markdown("""<div style="text-align:center; color: #ff66b3; margin-top: -15px;">VIP Only</div>""", unsafe_allow_html=True)

        st.markdown("---")
        
        if st.button("Iniciar Conversa Privada", 
                    use_container_width=True,
                    type="primary"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

        if st.button("Voltar ao chat", key="back_from_home"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

    
    @staticmethod
    def show_offers_page():
        st.markdown("""
        <style>
            .package-container {
                display: flex;
                justify-content: space-between;
                margin: 30px 0;
                gap: 20px;
            }
            .package-box {
                flex: 1;
                background: rgba(30, 0, 51, 0.3);
                border-radius: 15px;
                padding: 20px;
                border: 1px solid;
                transition: all 0.3s;
                min-height: 400px;
                position: relative;
                overflow: hidden;
            }
            .package-box:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(255, 102, 179, 0.3);
            }
            .package-start {
                border-color: #ff66b3;
            }
            .package-premium {
                border-color: #9400d3;
            }
            .package-extreme {
                border-color: #ff0066;
            }
            .package-header {
                text-align: center;
                padding-bottom: 15px;
                margin-bottom: 15px;
                border-bottom: 1px solid rgba(255, 102, 179, 0.3);
            }
            .package-price {
                font-size: 1.8em;
                font-weight: bold;
                margin: 10px 0;
            }
            .package-benefits {
                list-style-type: none;
                padding: 0;
            }
            .package-benefits li {
                padding: 8px 0;
                position: relative;
                padding-left: 25px;
            }
            .package-benefits li:before {
                content: "✓";
                color: #ff66b3;
                position: absolute;
                left: 0;
                font-weight: bold;
            }
            .package-badge {
                position: absolute;
                top: 15px;
                right: -30px;
                background: #ff0066;
                color: white;
                padding: 5px 30px;
                transform: rotate(45deg);
                font-size: 0.8em;
                font-weight: bold;
                width: 100px;
                text-align: center;
            }
            .countdown-container {
                background: linear-gradient(45deg, #ff0066, #ff66b3);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin: 40px 0;
                box-shadow: 0 4px 15px rgba(255, 0, 102, 0.3);
                text-align: center;
            }
            .offer-card {
                border: 1px solid #ff66b3;
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
                background: rgba(30, 0, 51, 0.3);
            }
            .offer-highlight {
                background: linear-gradient(45deg, #ff0066, #ff66b3);
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            
            /* Media queries para mobile */
            @media (max-width: 768px) {
                .package-container {
                    flex-direction: column;
                }
                .package-box {
                    margin-bottom: 20px;
                }
                .package-price {
                    font-size: 1.5em;
                }
                .package-benefits li {
                    font-size: 14px;
                }
            }
        </style>
        """, unsafe_allow_html=True)
    
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #ff66b3; border-bottom: 2px solid #ff66b3; display: inline-block; padding-bottom: 5px;">PACOTES EXCLUSIVOS</h2>
            <p style="color: #aaa; margin-top: 10px;">Escolha o que melhor combina com seus desejos...</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown('<div class="package-container">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="package-box package-start">
            <div class="package-header">
                <h3 style="color: #ff66b3;">START</h3>
                <div class="package-price" style="color: #ff66b3;">R$ 19,50</div>
                <small>para iniciantes</small>
            </div>
            <ul class="package-benefits">
                <li>10 fotos Inéditas</li>
                <li>3 vídeo Intimos</li>
                <li>Fotos Exclusivas</li>
                <li>Videos Intimos </li>
                <li>Fotos da Buceta</li>
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{Config.CHECKOUT_START}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                    color: white;
                    text-align: center;
                    padding: 12px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.3s;
                " onmouseover="this.style.transform='scale(1.05)'" 
                onmouseout="this.style.transform='scale(1)'"
                onclick="this.innerHTML='REDIRECIONANDO ⌛'; this.style.opacity='0.7'">
                    QUERO ESTE PACOTE ➔
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown(f"""
        <div class="package-box package-premium">
            <div class="package-badge">POPULAR</div>
            <div class="package-header">
                <h3 style="color: #9400d3;">PREMIUM</h3>
                <div class="package-price" style="color: #9400d3;">R$ 45,50</div>
                <small>experiência completa</small>
            </div>
            <ul class="package-benefits">
                <li>20 fotos exclusivas</li>
                <li>2 vídeos premium</li>
                <li>Fotos dos Peitos</li>
                <li>Fotos da Bunda</li>
                <li>Fotos da Buceta</li>
                <li>Fotos Exclusivas e Videos Exclusivos</li>
                <li>Videos Masturbando</li>
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{Config.CHECKOUT_PREMIUM}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #9400d3, #ff1493);
                    color: white;
                    text-align: center;
                    padding: 12px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.3s;
                " onmouseover="this.style.transform='scale(1.05)'" 
                onmouseout="this.style.transform='scale(1)'"
                onclick="this.innerHTML='REDIRECIONANDO ⌛'; this.style.opacity='0.7'">
                    QUERO ESTE PACOTE ➔
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown(f"""
        <div class="package-box package-extreme">
            <div class="package-header">
                <h3 style="color: #ff0066;">EXTREME</h3>
                <div class="package-price" style="color: #ff0066;">R$ 75,50</div>
                <small>para verdadeiros fãs</small>
            </div>
            <ul class="package-benefits">
                <li>23 fotos ultra-exclusivas</li>
                <li>4 Videos Exclusivos</li>
                <li>Fotos dos Peitos</li>
                <li>Fotos da Bunda</li>
                <li>Fotos da Buceta</li>
                <li>Fotos Exclusivas</li>
                <li>Videos Masturbando</li>
                <li>Videos Transando</li>
                <li>Acesso a conteúdos futuros</li>
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{Config.CHECKOUT_EXTREME}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #ff0066, #9400d3);
                    color: white;
                    text-align: center;
                    padding: 12px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: bold;
                    transition: all 0.3s;
                " onmouseover="this.style.transform='scale(1.05)'" 
                onmouseout="this.style.transform='scale(1)'"
                onclick="this.innerHTML='REDIRECIONANDO ⌛'; this.style.opacity='0.7'">
                    QUERO ESTE PACOTE ➔
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown('</div>', unsafe_allow_html=True)
    
        st.markdown("""
        <div class="countdown-container">
            <h3 style="margin:0;">OFERTA RELÂMPAGO</h3>
            <div id="countdown" style="font-size: 1.5em; font-weight: bold;">23:59:59</div>
            <p style="margin:5px 0 0;">Termina em breve!</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.components.v1.html("""
        <script>
        function updateCountdown() {
            const countdownElement = parent.document.getElementById('countdown');
            if (!countdownElement) return;
            
            let time = countdownElement.textContent.split(':');
            let hours = parseInt(time[0]);
            let minutes = parseInt(time[1]);
            let seconds = parseInt(time[2]);
            
            seconds--;
            if (seconds < 0) { seconds = 59; minutes--; }
            if (minutes < 0) { minutes = 59; hours--; }
            if (hours < 0) { hours = 23; }
            
            countdownElement.textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            setTimeout(updateCountdown, 1000);
        }
        
        setTimeout(updateCountdown, 1000);
        </script>
        """, height=0)
    
        plans = [
            {
                "name": "PROMO",
                "price": "R$ 12,50",
                "original": "R$ 17,90",
                "benefits": ["3 fotos semi-nuas sensuais", "2 fotos +18 exclusivas só para você"],
                "tag": "COMUM",
                "link": Config.CHECKOUT_PROMO + "?plan=Promo"
            },
            {
                "name": "3 Meses",
                "price": "R$ 69,90",
                "original": "R$ 149,70",
                "benefits": ["25% de desconto", "Bônus: 1 vídeo exclusivo", "Prioridade no chat"],
                "tag": "MAIS POPULAR",
                "link": Config.CHECKOUT_VIP_3MESES + "?plan=3meses"
            },
            {
                "name": "1 Ano",
                "price": "R$ 199,90",
                "original": "R$ 598,80",
                "benefits": ["66% de desconto", "Presente surpresa mensal", "Acesso a conteúdos raros"],
                "tag": "MELHOR CUSTO-BENEFÍCIO",
                "link": Config.CHECKOUT_VIP_1ANO + "?plan=1ano"
            }
        ]
    
        for plan in plans:
            with st.container():
                st.markdown(f"""
                <div class="offer-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>{plan['name']}</h3>
                        {f'<span class="offer-highlight">{plan["tag"]}</span>' if plan["tag"] else ''}
                    </div>
                    <div style="margin: 10px 0;">
                        <span style="font-size: 1.8em; color: #ff66b3; font-weight: bold;">{plan['price']}</span>
                        <span style="text-decoration: line-through; color: #888; margin-left: 10px;">{plan['original']}</span>
                    </div>
                    <ul style="padding-left: 20px;">
                        {''.join([f'<li style="margin-bottom: 5px;">{benefit}</li>' for benefit in plan['benefits']])}
                    </ul>
                    <div style="text-align: center; margin-top: 15px;">
                        <a href="{plan['link']}" target="_blank" style="
                            background: linear-gradient(45deg, #ff1493, #9400d3);
                            color: white;
                            padding: 10px 20px;
                            border-radius: 30px;
                            text-decoration: none;
                            display: inline-block;
                            font-weight: bold;
                            transition: all 0.3s;
                        " onmouseover="this.style.transform='scale(1.05)'" 
                        onmouseout="this.style.transform='scale(1)'"
                        onclick="this.innerHTML='REDIRECIONANDO ⌛'; this.style.opacity='0.7'">
                            Assinar {plan['name']}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
        if st.session_state.get('is_mobile', False):
            if st.button("Voltar ao chat", 
                        key="back_from_offers_mobile",
                        on_click=lambda: st.session_state.update({"current_page": "chat"}),
                        use_container_width=True):
                save_persistent_data()
                st.rerun()
        else:
            if st.button("Voltar ao chat", key="back_from_offers"):
                st.session_state.current_page = "chat"
                save_persistent_data()
                st.rerun()

# ======================
# SERVIÇOS DE CHAT
# ======================
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
            'last_cta_time': 0,
            'is_mobile': False
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
                content = "[Enviou um áudio sensual]"
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
        now = datetime.utcnow()
        last_time = st.session_state.get("last_user_msg_time")
    
        if last_time:
            if isinstance(last_time, str):
                last_time = datetime.fromisoformat(last_time)
            elapsed = now - last_time
    
            if elapsed.total_seconds() > 86400:
                st.session_state.messages = []
                st.session_state.request_count = 0
                st.session_state.audio_sent = False
    
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Eba! Que bom que você voltou 😍 Tava com saudade..."
                })
                DatabaseService.save_message(
                    conn,
                    get_user_id(),
                    st.session_state.session_id,
                    "assistant",
                    "Eba! Que bom que você voltou 😍 Tava com saudade..."
                )
    
                st.session_state.last_user_msg_time = now.isoformat()
                save_persistent_data()
                
                st.rerun()
        else:
            st.session_state.last_user_msg_time = now.isoformat()

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
            lower_input = cleaned_input.lower()
    
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
    
            if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
                with st.chat_message("assistant", avatar="💋"):
                    st.markdown("Vou ficar ocupada agora, me manda mensagem depois?")
                DatabaseService.save_message(
                    conn,
                    get_user_id(),
                    st.session_state.session_id,
                    "assistant",
                    "Estou ficando cansada, amor... Que tal continuarmos mais tarde?"
                )
                save_persistent_data()
                st.session_state.last_user_msg_time = datetime.utcnow().isoformat()
                return
    
            if any(term in lower_input for term in ["pix", "chave", "pagar", "como pago", "me passa", "transferência", "manda a chave"]):
                placeholder = st.empty()
                placeholder.markdown("💬 Digitando...")
                time.sleep(5)
                placeholder.empty()
                resposta = {
                      "text":(
                      "Nada de Pix direto, gostoso... 💸 Aqui você entra no meu mundinho só escolhendo "
                      "um dos meus planos: Promo, Start, Premium e Extreme 😈\n"
                      "Vem ver tudo que preparei pra te deixar louco 🔥"
                    ),
                    "cta": {
                        "show": True,
                        "label": "👉 Ver Planos VIP",        
                        "target": "offers"
                    }
                }
    
            elif any(p in lower_input for p in ["foto", "fotos", "buceta", "peito", "bunda"]):
                placeholder = st.empty()
                placeholder.markdown("💬 Digitando...")
                time.sleep(5)
                resposta = {
                    "text": random.choice([
                        "tô com fotos da minha buceta bem aberta, quer ver?",
                        "minha buceta tá chamando você nas fotos...",
                        "fiz um ensaio novo mostrando tudinho 🔥"
                    ]),
                    "cta": {
                        "show": True,
                        "label": "Ver Fotos Quentes",
                        "target": "offers"
                    }
                }
            
            elif any(p in lower_input for p in ["você é real", "vc é real", "é ia", "é uma ia", "isso é um robô", "é humana?"]):
                placeholder = st.empty()
                placeholder.markdown("💬 Digitando...")
                time.sleep(5)
                resposta = {
                    "text": "Sou tão real quanto sua vontade... 😈 Vem descobrir você mesmo no meu plano mais quente 🔥",
                    "cta": {
                        "show": True,
                        "label": "💎 Quero Ver Tudo",
                        "target": "offers"
                    }
                }
            
            elif any(v in lower_input for v in ["video", "transar", "masturbar"]):
                placeholder = st.empty()
                placeholder.markdown("💬 Digitando...")
                time.sleep(5)
                resposta = {
                    "text": random.choice([
                        "tenho vídeo me masturbando gostoso, vem ver 😈",
                        "tô me tocando nesse vídeo novo, quer ver?",
                        "gravei um vídeo especial só pra você 🥵"
                    ]),
                    "cta": {
                        "show": True,
                        "label": "Ver Vídeos Exclusivos",
                        "target": "offers"
                    }
                }
            
            else:
                resposta = ApiService.ask_gemini(cleaned_input, st.session_state.session_id, conn)
            
                if isinstance(resposta, str):
                    resposta = {"text": resposta, "cta": {"show": False}}
                elif "text" not in resposta:
                    resposta = {"text": str(resposta), "cta": {"show": False}}
            
            with st.chat_message("assistant", avatar="💋"):
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

# ======================
# APLICAÇÃO PRINCIPAL
# ======================
def main():
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e0033 0%, #3c0066 100%) !important;
            border-right: 1px solid #ff66b3 !important;
            overflow: auto !important;
            z-index: 2 !important;
        }
        .stButton button {
            background: rgba(255, 20, 147, 0.2) !important;
            color: white !important;
            border: 1px solid #ff66b3 !important;
            transition: all 0.3s !important;
        }
        .stButton button:hover {
            background: rgba(255, 20, 147, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        [data-testid="stChatInput"] {
            background: rgba(255, 102, 179, 0.1) !important;
            border: 1px solid #ff66b3 !important;
        }
        div.stButton > button:first-child {
            background: linear-gradient(45deg, #ff1493, #9400d3) !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 10px 24px !important;
            font-weight: bold !important;
            transition: all 0.3s !important;
            box-shadow: 0 4px 8px rgba(255, 20, 147, 0.3) !important;
        }
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(255, 20, 147, 0.4) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = DatabaseService.init_db()
    
    conn = st.session_state.db_conn
    
    ChatService.initialize_session(conn)
    
    if not st.session_state.age_verified:
        UiService.age_verification()
        st.markdown("<p style='text-align: center; font-size: 18px; color: #ff66b3;'>📞 Ligando para Juh...</p>", unsafe_allow_html=True)
        st.stop()
        
    UiService.setup_sidebar()
    
    if not st.session_state.connection_complete:
        UiService.show_call_effect()
        st.session_state.connection_complete = True
        save_persistent_data()
        st.rerun()
    
    if not st.session_state.chat_started:
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.markdown("""
            <div style="text-align: center; margin: 50px 0;">
                <img src="{profile_img}" width="120" style="border-radius: 50%; border: 3px solid #ff66b3;">
                <h2 style="color: #ff66b3; margin-top: 15px;">Juh</h2>
                <p style="font-size: 1.1em;">Estou pronta para você, amor...</p>
            </div>
            """.format(profile_img=Config.IMG_PROFILE), unsafe_allow_html=True)
            
            if st.button("Iniciar Conversa", type="primary", use_container_width=True):
                st.session_state.update({
                    'chat_started': True,
                    'current_page': 'chat',
                    'audio_sent': False
                })
                save_persistent_data()
                st.rerun()
        st.stop()
    
    if st.session_state.current_page == "home":
        NewPages.show_home_page()
    elif st.session_state.current_page == "gallery":
        UiService.show_gallery_page(conn)
    elif st.session_state.current_page == "offers":
        NewPages.show_offers_page()
    elif st.session_state.current_page == "vip":
        st.session_state.current_page = "offers"
        save_persistent_data()
        st.rerun()
    else:
        UiService.enhanced_chat_ui(conn)
    
    save_persistent_data()

if __name__ == "__main__":
    main()

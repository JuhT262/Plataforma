


# ======================
# IMPORTAÇÕES
# ======================
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
import traceback
import sys

def initialize_application_state():
    """Garante que todos os estados essenciais existam"""
    required_states = {
        'age_verified': False,
        'messages': [],
        'request_count': 0,
        'session_id': str(uuid.uuid4()),
        'connection_complete': False,
        'chat_started': False,
        'audio_sent': False,
        'current_page': 'home',
        'show_vip_offer': False,
        'last_cta_time': 0,
        'user_id': get_user_id(),  # Garante que o user_id sempre exista
        'db_conn': None,  # Conexão com o banco de dados
        'last_action': None,  # Última ação registrada
        'vip_access': False,  # Controle de acesso VIP
        'error_count': 0  # Contador de erros (para debug)
    }
    
    for key, default in required_states.items():
        if key not in st.session_state:
            st.session_state[key] = default

def log_error(error_msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("error_log.txt", "a") as f:
        f.write(f"[{timestamp}] {error_msg}\n")









# ======================
# CONFIGURAÇÃO INICIAL DO STREAMLIT
# ======================
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

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:

    API_KEY = "AIzaSyAaLYhdIJRpf_om9bDpqLpjJ57VmTyZO7g"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    VIP_LINK = "https://exemplo.com/vip"
    CHECKOUT_PROMO = "https://pay.risepay.com.br/Pay/c7abdd05f91d43b9bbf54780d648d4f6"
    CHECKOUT_START = "https://pay.risepay.com.br/Pay/7947c2af1ef64b4dac1c32afb086c9fe"
    CHECKOUT_PREMIUM = "https://pay.risepay.com.br/Pay/6c0dcab126a74a499e5f5a45007ab168"
    CHECKOUT_EXTREME = "https://pay.risepay.com.br/Pay/33ba988f596a450099606539fc9ff1ed"
    CHECKOUT_VIP_1MES = "https://checkout.exemplo.com/vip-1mes"
    CHECKOUT_VIP_3MESES = "https://checkout.exemplo.com/vip-3meses"
    CHECKOUT_VIP_1ANO = "https://checkout.exemplo.com/vip-1ano"
    MAX_REQUESTS_PER_SESSION = 30
    REQUEST_TIMEOUT = 30
    AUDIO_FILE = "https://github.com/JuhT262/Plataforma/raw/refs/heads/main/assets/Juh%20of.mp3"
    AUDIO_DURATION = 8
    # Na classe Config, atualize as URLs das imagens para garantir que sejam acessíveis:
IMG_PROFILE = "https://i.ibb.co/vvD2dkbQ/17.png"  # Verifique se esta URL ainda está válida
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
            if key == 'messages' and not isinstance(value, list):
                st.session_state[key] = []
            else:
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

# ======================
# MODELOS DE DADOS
# ======================
class Persona:
    JUH = """  # Alterado de PALOMA para JUH
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
    Juh: adoro mostrar ela aberta  # Alterado de Paloma para Juh
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
    Juh: oi gato  # Alterado de Paloma para Juh
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

    @staticmethod
    def generate_response(user_input: str) -> dict:
        user_input = user_input.lower()
        
        if any(p in user_input for p in ["foto", "fotos", "buceta", "peito", "bunda"]):
            return {
                "text": random.choice([
                    "to com fotos da minha buceta bem aberta quer ver",
                    "minha buceta ta chamando vc nas fotos",
                    "fiz um ensaio novo mostrando tudinho"
                ]),
                "cta": {
                    "show": True,
                    "label": "Ver Fotos Quentes",
                    "target": "offers"
                }
            }
        
        elif any(v in user_input for v in ["video", "transar", "masturbar"]):
            return {
                "text": random.choice([
                    "tenho video me masturbando gostoso vem ver",
                    "to me tocando nesse video novo quer ver",
                    "gravei um video especial pra vc"
                ]),
                "cta": {
                    "show": True,
                    "label": "Ver Vídeos Exclusivos",
                    "target": "offers"
                }
            }
        
        else:
            return {
                "text": random.choice([
                    "quero te mostrar tudo que eu tenho aqui",
                    "meu privado ta cheio de surpresas pra vc",
                    "vem ver o que eu fiz pensando em voce"
                ]),
                "cta": {
                    "show": False
                }
            }

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
        max_retries = 3
        for attempt in range(max_retries):
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversations (user_id, session_id, timestamp, role, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, session_id, datetime.now(), role, content))
                conn.commit()
                return True
            except sqlite3.Error as e:
                if attempt == max_retries - 1:  # Última tentativa
                    log_error(f"Falha ao salvar mensagem após {max_retries} tentativas: {str(e)}")
                    st.session_state.error_count += 1
                    return False
                time.sleep(0.5 * (attempt + 1))  

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
    def _call_gemini_api(prompt: str, session_id: str, conn, max_retries=3):
        api_data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
    
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    Config.API_URL,
                    headers={"Content-Type": "application/json"},
                    json=api_data,
                    timeout=Config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt == max_retries - 1:
                    return {"text": "🔴 Desculpe, estou tendo problemas com a net, volto mais tarde mb", "cta": {"show": False}}
                time.sleep(2 ** attempt)

# ======================
# SERVIÇOS DE INTERFACE
# ======================  

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
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #ff66b3;
            text-align: center;
            color: white;
            animation: pulse-ring 2s infinite;
        ">
            <div style="font-size: 3rem;">📱</div>
            <h3 style="color: #ff66b3; margin-bottom: 5px;">Ligando para Juh...</h3>  <!-- Alterado de Paloma para Juh -->
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 15px;">
                <div style="width: 10px; height: 10px; background: #4CAF50; border-radius: 50%;"></div>
                <span style="font-size: 0.9rem;">Online agora</span>
            </div>
        </div>
        <style>
            @keyframes pulse-ring {{
                0% {{ transform: scale(0.95); opacity: 0.8; }}
                50% {{ transform: scale(1.05); opacity: 1; }}
                100% {{ transform: scale(0.95); opacity: 0.8; }}
            }}
        </style>
        """, unsafe_allow_html=True)
        
        time.sleep(LIGANDO_DELAY)
        call_container.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1e0033, #3c0066);
            border-radius: 20px;
            padding: 30px;
            max-width: 300px;
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 2px solid #4CAF50;
            text-align: center;
            color: white;
        ">
            <div style="font-size: 3rem; color: #4CAF50;">✓</div>
            <h3 style="color: #4CAF50; margin-bottom: 5px;">Chamada atendida!</h3>
            <p style="font-size: 0.9rem; margin:0;">Juh está te esperando...</p>  <!-- Alterado de Paloma para Juh -->
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
            if st.button("Confirmo que sou maior de 18 anos", 
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
            /* Estilos para mobile */
            @media (max-width: 768px) {
                [data-testid="stSidebar"] {
                    width: 100% !important;
                    max-width: 100% !important;
                }
                .sidebar-logo {
                    width: 200px !important;
                }
                .sidebar-header img {
                    width: 60px !important;
                    height: 60px !important;
                }
                .vip-badge {
                    padding: 10px !important;
                    font-size: 0.9em !important;
                }
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
                <img src="{profile_img}" alt="Juh">  <!-- Alterado de Paloma para Juh -->
                <h3 style="color: #ff66b3; margin-top: 10px;">Juh Premium 💎</h3>  <!-- Alterado e adicionado emoji de diamante -->
            </div>
            """.format(profile_img=Config.IMG_PROFILE), unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### Menu Exclusivo")
            
            menu_options = {
                "Início": "home",
                "Galeria Privada": "gallery",
                "Mensagens": "messages",
                "Ofertas Especiais": "offers"
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
            st.markdown("### Upgrade VIP 💎")  # Adicionado emoji de diamante
            st.markdown("""
            <div class="vip-badge">
                <p style="margin: 0 0 10px; font-weight: bold;">Acesso ao Promo por apenas</p>
                <p style="margin: 0; font-size: 1.5em; font-weight: bold;">R$ 12,50/mês</p>
                <p style="margin: 10px 0 0; font-size: 0.8em;">Cancele quando quiser</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Tornar-se VIP 💎", use_container_width=True, type="primary"):  # Adicionado emoji de diamante
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
            
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Juh Premium</p>  <!-- Alterado de Paloma Premium para Juh Premium -->
                <p>Conteúdo para maiores de 18 anos</p>
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
                    use_column_width=True,  # Corrigido para column_width
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
    
    if st.button("Tornar-se VIP 💎",
                key="vip_button_gallery", 
                use_container_width=True,
                type="primary"):
        st.session_state.current_page = "offers"
        st.rerun()
    
    if st.button("Voltar ao chat", key="back_from_gallery"):
        st.session_state.current_page = "chat"
        save_persistent_data()
        st.rerun()

    @staticmethod
    def chat_shortcuts():
        cols = st.columns(4)
        with cols[0]:
            if st.button("Início 😘", key="shortcut_home",
                       help="Voltar para a página inicial",
                       use_container_width=True):
                st.session_state.current_page = "home"
                save_persistent_data()
                st.rerun()
                
        with cols[1]:
            if st.button("Galeria 📷", key="shortcut_gallery",
                       help="Acessar galeria privada",
                       use_container_width=True):
                st.session_state.current_page = "gallery"
                save_persistent_data()
                st.rerun()
        with cols[2]:
            if st.button("Ofertas 🎉", key="shortcut_offers",  # Adicionado emoji de diamante
                       help="Ver ofertas especiais",
                       use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
        with cols[3]:
            if st.button("VIP 💎", key="shortcut_vip",  # Adicionado emoji de diamante
                       help="Acessar área VIP",
                       use_container_width=True):
                st.session_state.current_page = "vip"
                save_persistent_data()
                st.rerun()

        st.markdown("""
        <style>
            div[data-testid="stHorizontalBlock"] > div > div > button {
                color: white !important;
                border: 1px solid #ff66b3 !important;
                background: rgba(255, 102, 179, 0.15) !important;
                transition: all 0.3s !important;
                font-size: 0.8rem !important;
            }
            div[data-testid="stHorizontalBlock"] > div > div > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 2px 8px rgba(255, 102, 179, 0.3) !important;
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
        """Interface aprimorada do chat"""
        st.markdown("""    
        <style>
            /* Estilos gerais do chat */
            .chat-header {
                 background: linear-gradient(90deg, #ff66b3, #ff1493);
                 color: white;
                 padding: 15px;
                 border-radius: 10px;
                 margin-bottom: 20px;
                 text-align: center;
                 box-shadow: 0 4px 8px rgba(0,0,0,0.1);
             }
         </style>
        """, unsafe_allow_html=True)
            
            st.markdown("""
            <style>
            /* Estilos específicos para mobile */
                @media (max-width: 768px) {
                    .chat-header {
                        padding: 10px;
                        font-size: 0.9em;
                    }
                    [data-testid="stChatInput"] {
                        padding: 8px !important;
                    }
                    .stChatMessage {
                        max-width: 80% !important;
                    }
                    .stButton > button {
                        padding: 8px 12px !important;
                        font-size: 0.8rem !important;
                    }
                }
            </style>
            """, unsafe_allow_html=True)
    
    # Resto da implementação do chat...
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
        </style>
        """, unsafe_allow_html=True)
    
        UiService.chat_shortcuts()
        
        st.markdown(f"""
        <div class="chat-header">
            <h2 style="margin:0; font-size:1.5em; display:inline-block;">Chat Privado com Juh 💎</h2>
        </div>
        """, unsafe_allow_html=True)

        if conn is None:
            st.error("ERRO: Conexão com banco de dados é None!")
            return
            
        ChatService.process_user_input(conn)
        
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

# ======================
# PÁGINAS
# ======================
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
        </style>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #ff66b3; border-bottom: 2px solid #ff66b3; display: inline-block; padding-bottom: 5px;">PACOTES EXCLUSIVOS</h2>
            <p style="color: #aaa; margin-top: 10px;">Escolha o que melhor combina com seus desejos...</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="package-container">', unsafe_allow_html=True)
        
        st.markdown("""
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
                <a href="{checkout_start}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #ff66b3, #ff1493);
                    color: white;
                    text-align: center;
                    padding: 10px;
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
        """.format(checkout_start=Config.CHECKOUT_START), unsafe_allow_html=True)

        st.markdown("""
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
                <a href="{checkout_premium}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #9400d3, #ff1493);
                    color: white;
                    text-align: center;
                    padding: 10px;
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
        """.format(checkout_premium=Config.CHECKOUT_PREMIUM), unsafe_allow_html=True)

        st.markdown("""
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
                <a href="{checkout_extreme}" target="_blank" rel="noopener noreferrer" style="
                    display: block;
                    background: linear-gradient(45deg, #ff0066, #9400d3);
                    color: white;
                    text-align: center;
                    padding: 10px;
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
        """.format(checkout_extreme=Config.CHECKOUT_EXTREME), unsafe_allow_html=True)

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
                "benefits": ["Acesso total", "Conteúdo único", "Chat privado"],
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
                        <a href="{plan['link']}" style="
                            background: linear-gradient(45deg, #ff1493, #9400d3);
                            color: white;
                            padding: 10px 20px;
                            border-radius: 30px;
                            text-decoration: none;
                            display: inline-block;
                            font-weight: bold;
                        ">
                            Assinar {plan['name']}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

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
        """Agora só carrega mensagens do banco"""
        db_messages = DatabaseService.load_messages(
            conn,
            get_user_id(),
            st.session_state.session_id
        )
        if db_messages:
            st.session_state.messages = db_messages

    @staticmethod
    def process_user_input(conn):
        try:
        # Verificar conexão com banco de dados primeiro
            if conn is None:
                st.error("Erro: Conexão com o banco de dados perdida!")
                return

        # Verificar e enviar áudio inicial se necessário
            if not st.session_state.get("audio_sent", False) and st.session_state.get("chat_started", False):
                try:
                    status_container = st.empty()
                    UiService.show_audio_recording_effect(status_container)
                
                    DatabaseService.save_message(
                        conn,
                        get_user_id(),
                        st.session_state.session_id,
                        "assistant",
                        "[ÁUDIO]"
                    )
                    st.session_state.audio_sent = True
                    save_persistent_data()
                except Exception as e:
                    log_error(f"Erro no envio de áudio: {str(e)}")
                    st.session_state.audio_sent = True
                    st.rerun()

            # Restante da lógica do chat
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            
        # Exibir histórico de mensagens
            for msg in st.session_state.messages[-12:]:
                role = msg.get("role", "")
                content = msg.get("content", "")
            
                avatar = "🧑" if role == "user" else "💋"
                with st.chat_message(role, avatar=avatar):
                    if content == "[ÁUDIO]":
                        st.audio(Config.AUDIO_FILE)
                    else:
                        st.markdown(content)

        # Obter e processar input do usuário
            user_input = st.chat_input("Digite sua mensagem...")
            if user_input:
                cleaned_input = str(user_input)[:500].strip()
                if cleaned_input:
                # Salvar mensagem do usuário
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

                # Gerar resposta
                    user_input_lower = cleaned_input.lower()
                    if any(word in user_input_lower for word in ["pix", "chave pix", "pagamento", "comprar", "quanto custa"]):
                        resposta = {
                            "text": "💰 Planos disponíveis:\n\n• PROMO: R$12,50\n• START: R$19,50\n• PREMIUM: R$45,50\n• EXTREME: R$75,50",
                            "cta": {
                                "show": True,
                                "label": "QUERO ASSINAR",
                                "target": "offers"
                            }
                        }
                    else:
                        resposta = {
                            "text": "Oi amor! Quer ver meus conteúdos especiais? 😘",
                            "cta": {
                                "show": True,
                                "label": "VER CONTEÚDOS",
                                "target": "offers"
                            }
                        }

                # Exibir e salvar resposta
                    with st.chat_message("assistant", avatar="💋"):
                        st.markdown(resposta["text"])
                        if resposta["cta"]["show"]:
                            if st.button(resposta["cta"]["label"]):
                                st.session_state.current_page = resposta["cta"]["target"]
                                st.rerun()

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": json.dumps(resposta, ensure_ascii=False)
                    })

                    DatabaseService.save_message(
                        conn,
                        get_user_id(),
                        st.session_state.session_id,
                        "assistant",
                        json.dumps(resposta, ensure_ascii=False)
                    )
    
        except Exception as e:
            error_msg = f"Erro no chat: {str(e)}"
            log_error(error_msg)
            st.error("""
            ⚠️ Ops! Ocorreu um erro inesperado

            Por favor:
            1. Clique no botão abaixo para recarregar
            2. Se o problema persistir, contate o suporte
            """)
        
            if st.button("🔄 Recarregar Página", key="reload_chat_button"):
                st.rerun()


    
    

# ======================
# APLICAÇÃO PRINCIPAL
# ======================



# ======================
# APLICAÇÃO PRINCIPAL
# ======================
def main():
    try:
        # Inicialização do sistema
        initialize_application_state()
        
        # Conexão com banco de dados
        if 'db_conn' not in st.session_state:
            try:
                st.session_state.db_conn = DatabaseService.init_db()
            except Exception as db_error:
                error_msg = f"""
                [ERRO DE BANCO DE DADOS] {datetime.now()}
                {str(db_error)}
                {traceback.format_exc()}
                """
                with open("error_log.txt", "a") as f:
                    f.write(error_msg)
                st.error("Sistema temporariamente indisponível. Tente novamente em alguns minutos.")
                st.stop()
        
        # Verificação de idade
        if not st.session_state.get('age_verified', False):
            UiService.age_verification()
            st.stop()
        
        # Configuração inicial
        UiService.setup_sidebar()
        
        if not st.session_state.get('connection_complete', False):
            try:
                UiService.show_call_effect()
                st.session_state.connection_complete = True
                save_persistent_data()
                st.rerun()
            except Exception as effect_error:
                log_error(f"Erro no efeito de chamada: {str(effect_error)}")
                st.session_state.connection_complete = True  # Pula o efeito em caso de erro
                st.rerun()
        
        # Controle de navegação
        try:
            page_handlers = {
                'home': NewPages.show_home_page,
                'gallery': UiService.show_gallery_page,
                'offers': NewPages.show_offers_page,
                'chat': UiService.enhanced_chat_ui
            }
            
            current_page = st.session_state.get('current_page', 'home')
            
            if current_page == 'vip':
                st.session_state.show_vip_offer = True
                save_persistent_data()
                st.rerun()
            elif st.session_state.get('show_vip_offer', False):
                st.warning("Página VIP em desenvolvimento")
                if st.button("Voltar ao chat"):
                    st.session_state.show_vip_offer = False
                    save_persistent_data()
                    st.rerun()
            else:
                handler = page_handlers.get(current_page)
                if handler:
                    if current_page == 'gallery':
                        handler(st.session_state.db_conn)
                    else:
                        handler()
            
            save_persistent_data()
            
        except Exception as page_error:
            log_error(f"Erro na página {st.session_state.get('current_page')}: {str(page_error)}")
            st.error("Erro ao carregar o conteúdo. Recarregando...")
            time.sleep(2)
            st.rerun()
            
    except Exception as main_error:
        critical_error = f"""
        [ERRO CRÍTICO] {datetime.now()}
        {str(main_error)}
        {traceback.format_exc()}
        Estado da Sessão: {json.dumps(st.session_state.to_dict(), indent=2)}
        """
        with open("error_log.txt", "a") as f:
            f.write(critical_error)
        
        st.error("""
        ⚠️ Falha crítica no sistema
        Por favor:
        1. Recarregue a página (F5)
        2. Se persistir, espere 5 minutos
        3. Entre em contato com o suporte se o problema continuar
        """)
        st.stop()

# ======================
# HANDLER DE ERROS GLOBAIS
# ======================
def handle_global_error(error):
    """Registra erros críticos e exibe mensagem amigável"""
    try:
        error_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_info = {
            'timestamp': error_time,
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'session_state': dict(st.session_state.items()) if hasattr(st, 'session_state') else {}
        }
        
        # Registrar em arquivo de log
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(error_info, indent=2) + "\n")
        
        # Mensagem amigável com botão de recarregar
        st.error("""
        ⚠️ Ops! Ocorreu um erro inesperado

        Por favor:
        1. Clique no botão abaixo para recarregar
        2. Se o problema persistir, contate o suporte
        """)
        
        if st.button("🔄 Recarregar Página", key="reload_button"):
            st.rerun()
        
        st.stop()
    
    except Exception as fallback_error:
        print(f"FALHA NO TRATAMENTO DE ERROS: {str(fallback_error)}")
        st.stop()

# ======================
# PONTO DE ENTRADA SEGURO
# ======================
if __name__ == "__main__":
    try:
        # Configura handler global de exceções
        sys.excepthook = lambda exctype, exc, tb: handle_global_error(exc)
        
        # Verificação inicial
        if not all(hasattr(Config, attr) for attr in ['IMG_PROFILE', 'AUDIO_FILE', 'LOGO_URL']):
            raise ValueError("Configurações essenciais faltando na classe Config")
        
        # Execução principal
        main()
    
    except Exception as e:
        handle_global_error(e)


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
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from functools import lru_cache

# ======================
# CONSTANTES GLOBAIS
# ======================
MESSAGE_EXPIRATION_HOURS = 2  # Mensagens expiram após 2 horas
RETURNING_USER_MESSAGE = {
    'pt': "Que bom que voltou! 😍",
    'en': "Welcome back! 😍", 
    'es': "¡Qué bueno que volviste! 😍"
}

# ======================
# CONFIGURAÇÕES INICIAIS
# ======================
st.set_page_config(
    page_title="Juh Premium",
    page_icon="😍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# SERVIÇO DE TRADUÇÃO
# ======================
class GoogleTranslator:
    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"
    
    def translate(self, text, dest='pt', src='auto'):
        if not text or dest == 'pt':
            return text
            
        try:
            params = {
                'client': 'gtx',
                'sl': src,
                'tl': dest,
                'dt': 't',
                'q': text
            }
            response = requests.get(self.base_url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()[0][0][0]
            return text
        except Exception as e:
            print(f"Erro na tradução: {str(e)}")
            return text

translator = GoogleTranslator()

class TranslationService:
    @staticmethod
    def translate_text(text, target_lang='pt'):
        return translator.translate(text, dest=target_lang)
    
    @staticmethod
    def get_translated_content(key, lang='pt'):
        translations = {
            'welcome_back': RETURNING_USER_MESSAGE,
            'age_verification_title': {
                'pt': 'Verificação de Idade',
                'en': 'Age Verification',
                'es': 'Verificación de Edad'
            },
            'age_verification_text': {
                'pt': 'Este site contém material explícito destinado exclusivamente a adultos maiores de 18 anos.',
                'en': 'This site contains explicit material intended exclusively for adults over 18 years old.',
                'es': 'Este sitio contiene material explícito destinado exclusivamente a adultos mayores de 18 años.'
            },
            'age_verification_button': {
                'pt': 'Confirmo que sou maior de 18 anos',
                'en': 'I confirm I am over 18 years old',
                'es': 'Confirmo que soy mayor de 18 años'
            },
            'chat_input_placeholder': {
                'pt': 'Escreva sua mensagem aqui',
                'en': 'Type your message here',
                'es': 'Escribe tu mensaje aquí'
            },
            'vip_button': {
                'pt': 'Tornar-se VIP 💎',
                'en': 'Become VIP 💎',
                'es': 'Hazte VIP 💎'
            }
        }
        return translations.get(key, {}).get(lang, key)

# ======================
# DETECÇÃO DE DISPOSITIVO E IDIOMA
# ======================
def detect_device_and_language():
    user_agent = st.query_params.get('user_agent', '')
    
    # Detecção de dispositivo
    is_mobile = 'Mobi' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent or 'iPad' in user_agent
    
    # Detecção de idioma
    lang = st.query_params.get('lang', 'pt')
    if lang not in ['pt', 'en', 'es']:
        lang = 'pt'
    
    return {
        'is_mobile': is_mobile,
        'language': lang
    }

device_info = detect_device_and_language()

def detect_user_language(user_input):
    """Detecta o idioma baseado no texto do usuário"""
    if not user_input:
        return 'pt'
        
    user_input = user_input.lower()
    
    # Palavras-chave em inglês
    english_words = ["the", "you", "are", "is", "this", "hi", "hello", "how", "what"]
    # Palavras-chave em espanhol
    spanish_words = ["el", "la", "qué", "es", "hola", "quiero", "tú", "cómo", "qué"]
    
    if any(word in user_input for word in english_words):
        return 'en'
    elif any(word in user_input for word in spanish_words):
        return 'es'
    else:
        return 'pt'

# ======================
# ESTILOS RESPONSIVOS (ATUALIZADO)
# ======================
def get_responsive_styles(device_info):
    is_mobile = device_info['is_mobile']
    lang = device_info['language']
    
    base_styles = f"""
    <style>
        /* CONFIGURAÇÕES GERAIS PARA TODOS OS DISPOSITIVOS */
        * {{
            -webkit-overflow-scrolling: touch !important;
            overscroll-behavior: contain !important;
        }}
        
        /* MELHORIA: Visibilidade das mensagens */
        .stChatMessage {{
            color: white !important;
        }}
        
        .stChatMessage[data-testid="user"] > div {{
            background: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 18px 18px 0 18px !important;
        }}
        
        .stChatMessage[data-testid="assistant"] > div {{
            background: linear-gradient(45deg, #ff66b3, #ff1493) !important;
            color: white !important;
            border-radius: 18px 18px 18px 0 !important;
        }}
        
        #root > div:nth-child(1) > div > div > div > div > section > div {{
            padding-top: 0rem;
        }}
        
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        div[data-testid="stStatusWidget"],
        #MainMenu, header, footer,
        .stDeployButton {{
            display: none !important;
        }}
        
        .block-container {{
            padding-top: 0rem !important;
        }}
        
        [data-testid="stVerticalBlock"] {{
            gap: 0.5rem !important;
        }}
        
        [data-testid="stHorizontalBlock"] {{
            gap: 0.5rem !important;
        }}
        
        .stApp {{
            margin: 0 !important;
            padding: 0 !important;
        }}
        
        html, body, .stApp {{
            background: linear-gradient(180deg, #1e0033, #3c0066) !important;
            color: #fff !important;
        }}
        
        .stButton>button {{
            font-size: 1rem !important;
            padding: 14px 20px !important;
            background-color: #ff1493 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
        }}
        
        .block-container {{
            padding-top: 0.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        
        img, .stImage img {{
            max-width: 100% !important;
            height: auto !important;
            border-radius: 12px !important;
            padding: 5px !important;
        }}
        
        [data-testid="stSidebar"] img {{
            border-radius: 50% !important;
            border: 2px solid #ff66b3;
            width: 80px !important;
            height: 80px !important;
            object-fit: cover !important;
        }}
        
        /* MENU MOBILE */
        .mobile-menu-button {{
            position: fixed;
            top: 15px;
            right: 15px;
            background: linear-gradient(45deg, #ff1493, #ff66b3);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: none;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            z-index: 1000;
            border: 2px solid white;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }}
        
        /* BOTÃO ABRIR CHAT MOBILE */
        .mobile-chat-menu {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(45deg, #ff1493, #ff66b3) !important;
            color: white !important;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: none;
            justify-content: center;
            align-items: center;
            font-size: 28px;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(255, 20, 147, 0.6);
            border: 2px solid white;
        }}
        
        /* SELEÇÃO DE IDIOMA */
        .language-selector {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            display: flex;
            gap: 5px;
        }}
        
        .language-btn {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 1px solid #ff66b3;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .language-btn.active {{
            background: #ff66b3;
            font-weight: bold;
        }}
        
        /* EFEITO DE GRAVAÇÃO DE ÁUDIO VISÍVEL */
        .audio-recording-effect {{
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 102, 179, 0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            animation: pulse 1.5s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 0.8; transform: translateX(-50%) scale(0.95); }}
            50% {{ opacity: 1; transform: translateX(-50%) scale(1.05); }}
            100% {{ opacity: 0.8; transform: translateX(-50%) scale(0.95); }}
        }}
    </style>
    """
    
    mobile_styles = """
    <style>
        /* CONFIGURAÇÕES ESPECÍFICAS PARA MOBILE */
        @media (max-width: 768px) {
            .block-container, .stApp {
                padding: 0.2rem !important;
            }
            
            [data-testid="stVerticalBlock"] {
                gap: 0.2rem !important;
            }
            
            .stChatMessage {
                max-width: 85% !important;
                font-size: 14px !important;
            }
            
            [data-testid="stChatInput"] {
                padding: 8px 12px !important;
                font-size: 14px !important;
                position: fixed !important;
                bottom: 10px;
                left: 10px;
                right: 10px;
                width: calc(100% - 20px) !important;
            }
            
            .stImage img {
                max-height: 200px !important;
            }
            
            .chat-header {
                padding: 10px !important;
                font-size: 1.2em !important;
            }
            
            * {
                animation: none !important;
                transition: none !important;
            }
            
            .mobile-menu-button {
                display: flex;
            }
            
            [data-testid="stSidebar"] {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            [data-testid="stSidebar"].open {
                transform: translateX(0);
            }
            
            .mobile-chat-menu {
                display: flex;
            }
            
            .language-selector {
                bottom: 90px;
            }
            
            .audio-recording-effect {
                bottom: 120px;
                font-size: 14px;
                padding: 8px 15px;
            }
        }
        
        /* GALERIA MOBILE */
        .gallery-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            padding: 10px;
        }
        
        .gallery-item {
            position: relative;
            overflow: hidden;
            border-radius: 12px;
            aspect-ratio: 1/1;
        }
        
        .gallery-item img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
        }
        
        @media (max-width: 480px) {
            .gallery-container {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        /* CHAT MOBILE */
        .chat-container {
            height: calc(100vh - 120px) !important;
            overflow-y: auto;
            padding-bottom: 80px;
        }
    </style>
    """
    
    desktop_styles = """
    <style>
        /* CONFIGURAÇÕES ESPECÍFICAS PARA DESKTOP */
        @media (min-width: 769px) {
            [data-testid="stSidebar"] {
                min-width: 320px !important;
                max-width: 400px !important;
            }
            
            .chat-container {
                height: calc(100vh - 180px) !important;
            }
            
            .mobile-menu-button,
            .mobile-chat-menu {
                display: none !important;
            }
            
            .audio-recording-effect {
                bottom: 100px;
            }
        }
    </style>
    """
    
    return base_styles + (mobile_styles if is_mobile else desktop_styles)

# Aplicar estilos
st.markdown(get_responsive_styles(device_info), unsafe_allow_html=True)

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
    INTERNATIONAL_LINK = "https://exemplo.com/international"
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
# PERSISTÊNCIA DE ESTADO (ATUALIZADA)
# ======================
class PersistentState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_db()
        return cls._instance
    
    def init_db(self):
        try:
            os.makedirs('data', exist_ok=True)
            self.conn = sqlite3.connect('data/persistent_state.db', check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.create_tables()
        except Exception as e:
            st.error(f"Erro ao inicializar banco de dados: {str(e)}")
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            self.create_tables()
    
    def create_tables(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS global_state (
                    user_id TEXT PRIMARY KEY,
                    session_data TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    language TEXT DEFAULT 'pt'
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            st.error(f"Erro ao criar tabelas: {str(e)}")
            try:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS global_state (
                        user_id TEXT,
                        session_data TEXT,
                        language TEXT
                    )
                ''')
                self.conn.commit()
            except:
                pass

    def save_state(self, user_id, data, language='pt'):
        if not user_id:
            return False
            
        try:
            if not self.conn:
                self.init_db()
                
            # Adiciona timestamp de atualização
            data['last_updated'] = datetime.now().isoformat()
                
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO global_state (user_id, session_data, language, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (str(user_id), json.dumps(data), language, datetime.now().isoformat()))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar estado: {str(e)}")
            return False
    
    def load_state(self, user_id):
        if not user_id:
            return None, 'pt'
            
        try:
            if not self.conn:
                self.init_db()
                
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT session_data, language, last_updated FROM global_state 
                WHERE user_id = ?
            ''', (str(user_id),))
            
            result = cursor.fetchone()
            if result:
                session_data, language, last_updated = result
                
                # Verifica se as mensagens expiraram (2 horas)
                if last_updated:
                    last_updated = datetime.fromisoformat(last_updated)
                    if datetime.now() - last_updated > timedelta(hours=MESSAGE_EXPIRATION_HOURS):
                        try:
                            data = json.loads(session_data)
                            data['messages'] = []  # Limpa mensagens antigas
                            return data, language
                        except:
                            return None, language
                
                try:
                    return json.loads(session_data), language
                except json.JSONDecodeError:
                    return None, language if language else 'pt'
            return None, 'pt'
        except sqlite3.Error as e:
            print(f"Erro ao carregar estado: {str(e)}")
            return None, 'pt'
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            return None, 'pt'

def get_user_id():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def save_persistent_data():
    try:
        user_id = get_user_id()
        if not user_id:
            return
            
        db = PersistentState()
        
        data_to_save = {
            'age_verified': st.session_state.get('age_verified', False),
            'messages': st.session_state.get('messages', []),
            'request_count': st.session_state.get('request_count', 0),
            'connection_complete': st.session_state.get('connection_complete', False),
            'chat_started': st.session_state.get('chat_started', False),
            'audio_sent': st.session_state.get('audio_sent', False),
            'current_page': st.session_state.get('current_page', 'home'),
            'show_vip_offer': st.session_state.get('show_vip_offer', False),
            'session_id': st.session_state.get('session_id', str(uuid.uuid4())),
            'last_cta_time': st.session_state.get('last_cta_time', 0),
            'language': st.session_state.get('language', 'pt'),
            'last_updated': datetime.now().isoformat()
        }
        
        db.save_state(user_id, data_to_save, st.session_state.get('language', 'pt'))
    except Exception as e:
        print(f"Erro ao salvar dados persistentes: {str(e)}")

def load_persistent_data():
    try:
        user_id = get_user_id()
        if not user_id:
            user_id = str(uuid.uuid4())
            st.session_state.user_id = user_id
            
        db = PersistentState()
        
        if not db.conn:
            db.init_db()
            
        saved_data, saved_lang = db.load_state(user_id)
        
        if saved_lang not in ['pt', 'en', 'es']:
            saved_lang = 'pt'
            
        url_lang = st.query_params.get('lang', 'pt')
        if url_lang and url_lang in ['pt', 'en', 'es']:
            st.session_state.language = url_lang
        elif saved_lang:
            st.session_state.language = saved_lang
        else:
            st.session_state.language = 'pt'
        
        if saved_data:
            for key, value in saved_data.items():
                if key not in st.session_state:
                    st.session_state[key] = value
                    
        defaults = {
            'age_verified': False,
            'messages': [],
            'request_count': 0,
            'connection_complete': False,
            'chat_started': False,
            'audio_sent': False,
            'current_page': 'home',
            'show_vip_offer': False,
            'session_id': str(uuid.uuid4()),
            'last_cta_time': 0
        }
        
        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default
                
    except Exception as e:
        print(f"Erro crítico em load_persistent_data: {str(e)}")
        st.session_state.update({
            'user_id': str(uuid.uuid4()),
            'language': device_info.get('language', 'pt'),
            'age_verified': False,
            'messages': [],
            'request_count': 0,
            'connection_complete': False,
            'chat_started': False,
            'audio_sent': False,
            'current_page': 'home',
            'show_vip_offer': False,
            'session_id': str(uuid.uuid4()),
            'last_cta_time': 0
        })

# ======================
# MODELOS DE DADOS
# ======================
class Persona:
    @staticmethod
    def get_persona(language='pt'):
        personas = {
            'pt': """
            [PERFIL JUH]
            - Mulher vulgar e safada que adora provocar
            - Linguagem direta e cheia de malícia
            - Frases curtas e sem pontuação perfeita
            - Adora falar putaria e deixar o cliente com tesão
            """,
            'en': """
            [PROFILE JUH]
            - Vulgar and naughty woman who loves to tease
            - Direct and mischievous language
            - Short sentences with imperfect punctuation
            - Loves dirty talk and turning clients on
            """,
            'es': """
            [PERFIL JUH]
            - Mujer vulgar y traviesa que adora provocar
            - Lenguaje directo y lleno de malicia
            - Frases cortas sin puntuación perfecta
            - Le encanta hablar obscenidades y excitar al cliente
            """
        }
        return personas.get(language, personas['pt'])

    @staticmethod
    def get_response_guidelines(language='pt'):
        guidelines = {
            'pt': """
            [DIRETRIZES DE RESPOSTA]
            1. Analise o histórico da conversa para entender o contexto
            2. Só ofereça conteúdo quando o clima estiver quente
            3. Use CTAs inteligentes baseados no que o cliente está pedindo
            """,
            'en': """
            [RESPONSE GUIDELINES]
            1. Analyze conversation history to understand context
            2. Only offer content when the mood is hot
            3. Use smart CTAs based on what the client is asking
            """,
            'es': """
            [PAUTAS DE RESPUESTA]
            1. Analiza el historial de conversación para entender el contexto
            2. Ofrece contenido solo cuando el ambiente esté caliente
            3. Usa CTAs inteligentes basados en lo que pide el cliente
            """
        }
        return guidelines.get(language, guidelines['pt'])

    @staticmethod
    def get_examples(language='pt'):
        examples = {
            'pt': """
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
            """,
            'en': """
            [CONTEXTUAL EXAMPLES]
            1. When history shows sexual mood:
            History:
            Client: is your pussy pink?
            Juh: love to show it wide open
            Client: I want to see
            Response: ```json
            {
              "text": "got pics of my dripping wet pussy wanna see?",
              "cta": {
                "show": true,
                "label": "See Hot Pics",
                "target": "offers"
              }
            }
            ```
            """,
            'es': """
            [EJEMPLOS CONTEXTUALES]
            1. Cuando el historial muestra clima sexual:
            Historial:
            Cliente: ¿tu coño es rosado?
            Juh: me encanta mostrarlo abierto
            Cliente: quiero ver
            Respuesta: ```json
            {
              "text": "tengo fotos de mi coño mojado ¿quieres ver?",
              "cta": {
                "show": true,
                "label": "Ver Fotos Calientes",
                "target": "offers"
              }
            }
            ```
            """
        }
        return examples.get(language, examples['pt'])

    @classmethod
    def get_full_persona(cls, language='pt'):
        return cls.get_persona(language) + "\n\n" + cls.get_response_guidelines(language) + "\n\n" + cls.get_examples(language)

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
        
        hot_words = {
            'pt': ["buceta", "peito", "fuder", "gozar", "gostosa", "delicia", "molhad", "xereca", "pau", "piroca", "transar", "foto", "video", "mostra", "ver", "quero", "desejo", "tesão", "molhada", "foda"],
            'en': ["pussy", "tits", "fuck", "cum", "sexy", "delicious", "wet", "cunt", "cock", "dick", "fuck", "photo", "video", "show", "see", "want", "desire", "horny", "wet", "fuck"],
            'es': ["coño", "tetas", "follar", "correrse", "rica", "delicia", "mojad", "choocha", "polla", "pene", "follar", "foto", "video", "mostrar", "ver", "quiero", "deseo", "caliente", "mojada", "follar"]
        }
        
        direct_asks = {
            'pt': ["mostra", "quero ver", "me manda", "como assinar", "como comprar", "como ter acesso", "onde vejo mais"],
            'en': ["show me", "I want to see", "send me", "how to subscribe", "how to buy", "how to get access", "where can I see more"],
            'es': ["muéstrame", "quiero ver", "envíame", "cómo suscribirme", "cómo comprar", "cómo obtener acceso", "dónde puedo ver más"]
        }
        
        lang = st.session_state.get('language', 'pt')
        hot_count = sum(1 for word in hot_words.get(lang, hot_words['pt']) if word in context)
        has_direct_ask = any(ask in context for ask in direct_asks.get(lang, direct_asks['pt']))
        
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
                     content TEXT,
                     language TEXT)''')
        conn.commit()
        return conn

    @staticmethod
    def save_message(conn, user_id, session_id, role, content, language='pt'):
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO conversations (user_id, session_id, timestamp, role, content, language)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, session_id, datetime.now(), role, content, language))
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
        
        # Usa o idioma da sessão que foi detectado anteriormente
        user_lang = st.session_state.get('language', 'pt')
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{Persona.get_full_persona(user_lang)}\n\nHistórico da Conversa:\n{conversation_history}\n\nÚltima mensagem do cliente: '{prompt}'\n\nResponda em JSON com o formato:\n{{\n  \"text\": \"sua resposta\",\n  \"cta\": {{\n    \"show\": true/false,\n    \"label\": \"texto do botão\",\n    \"target\": \"página\"\n  }}\n}}"}]
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
            <h3 style="color: #ff66b3; margin-bottom: 5px;">Ligando para Juh...</h3>
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
            <p style="font-size: 0.9rem; margin:0;">Juh está te esperando...</p>
        </div>
        """, unsafe_allow_html=True)
        
        time.sleep(ATENDIDA_DELAY)
        call_container.empty()

    @staticmethod
    def show_status_effect(container, status_type):
        status_messages = {
            "viewed": {
                'pt': "Visualizado",
                'en': "Viewed",
                'es': "Visto"
            },
            "typing": {
                'pt': "Digitando",
                'en': "Typing",
                'es': "Escribiendo"
            }
        }
        
        lang = st.session_state.get('language', 'pt')
        message = status_messages[status_type].get(lang, status_messages[status_type]['pt'])
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
    def show_audio_recording_effect():
        messages = {
            'pt': "Gravando um áudio",
            'en': "Recording audio",
            'es': "Grabando audio"
        }
        
        lang = st.session_state.get('language', 'pt')
        message = messages.get(lang, messages['pt'])
        dots = ""
        start_time = time.time()
        
        # Mostra o efeito de gravação fixo na tela
        recording_container = st.empty()
        
        while time.time() - start_time < Config.AUDIO_DURATION:
            elapsed = time.time() - start_time
            dots = "." * (int(elapsed) % 4)
            
            recording_container.markdown(f"""
            <div class="audio-recording-effect">
                {message}{dots}
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(0.3)
        
        recording_container.empty()

    @staticmethod
    def age_verification():
        if st.session_state.get('age_verified', False):
            return True
        
        lang = st.session_state.get('language', 'pt')
        verification_container = st.empty()
        
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
    
            title = TranslationService.get_translated_content('age_verification_title', lang)
            text = TranslationService.get_translated_content('age_verification_text', lang)
            button_text = TranslationService.get_translated_content('age_verification_button', lang)
    
            st.markdown(f"""
            <div class="age-verification">
                <div class="age-header">
                    <div class="age-icon">🔞</div>
                    <h1 class="age-title">{title}</h1>
                </div>
                <div class="age-content">
                    <p>{text}</p>
                    <p>Ao acessar este conteúdo, você declara estar em conformidade com todas as leis locais aplicáveis.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                if st.button(button_text, 
                            key="age_verify_btn",
                            use_container_width=True,
                            type="primary"):
                    st.session_state.age_verified = True
                    
                    if 'db_conn' in st.session_state:
                        try:
                            cursor = st.session_state.db_conn.cursor()
                            cursor.execute('''
                                INSERT OR REPLACE INTO global_state (user_id, session_data, language)
                                VALUES (?, ?, ?)
                            ''', (get_user_id(), json.dumps({'age_verified': True}), lang))
                            st.session_state.db_conn.commit()
                        except Exception as e:
                            st.error(f"Erro ao salvar verificação: {str(e)}")
                    
                    verification_container.empty()
                    st.rerun()
        
        if not st.session_state.get('age_verified', False):
            st.stop()
            
    @staticmethod
    def setup_sidebar():
        if not st.session_state.get('age_verified', False):
            return
            
        with st.sidebar:
            lang = st.session_state.get('language', 'pt')
            
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
            
            menu_options = {
                'pt': {
                    "Início 🏠": "home",
                    "Galeria Privada 📸": "gallery",
                    "Mensagens 💬": "messages",
                    "Ofertas Especiais 🎁": "offers"
                },
                'en': {
                    "Home 🏠": "home",
                    "Private Gallery 📸": "gallery",
                    "Messages 💬": "messages",
                    "Special Offers 🎁": "offers"
                },
                'es': {
                    "Inicio 🏠": "home",
                    "Galería Privada 📸": "gallery",
                    "Mensajes 💬": "messages",
                    "Ofertas Especiales 🎁": "offers"
                }
            }
            
            current_menu = menu_options.get(lang, menu_options['pt'])
            
            st.markdown(f"### {TranslationService.translate_text('Menu Exclusivo', lang)}")
            
            for option, page in current_menu.items():
                if st.button(option, use_container_width=True, key=f"menu_{page}"):
                    if st.session_state.current_page != page:
                        st.session_state.current_page = page
                        st.session_state.last_action = f"page_change_to_{page}"
                        save_persistent_data()
                        st.rerun()
    
            st.markdown("---")
            st.markdown(f"### {TranslationService.translate_text('Sua Conta', lang)}")
    
            st.markdown("""
            <div style="
                background: rgba(255, 20, 147, 0.1);
                padding: 10px;
                border-radius: 8px;
                text-align: center;
            ">
                <p style="margin:0;">{access_text}</p>
            </div>
            """.format(access_text=TranslationService.translate_text("Acesse conteúdo exclusivo", lang)), unsafe_allow_html=True)
    
            st.markdown("---")
            st.markdown(f"### {TranslationService.translate_text('Upgrade VIP', lang)} 💎")
    
            vip_text = {
                'pt': {
                    "title": "Acesso ao Promo por apenas",
                    "price": "R$ 12,50/mês",
                    "note": "Cancele quando quiser"
                },
                'en': {
                    "title": "Access to Promo for only",
                    "price": "$12.50/month",
                    "note": "Cancel anytime"
                },
                'es': {
                    "title": "Acceso a Promo por solo",
                    "price": "$12.50/mes",
                    "note": "Cancela cuando quieras"
                }
            }
            
            current_vip_text = vip_text.get(lang, vip_text['pt'])
            
            st.markdown(f"""
            <div class="vip-badge">
                <p style="margin: 0 0 10px; font-weight: bold;">{current_vip_text['title']}</p>
                <p style="margin: 0; font-size: 1.5em; font-weight: bold;">{current_vip_text['price']}</p>
                <p style="margin: 10px 0 0; font-size: 0.8em;">{current_vip_text['note']}</p>
            </div>
            """, unsafe_allow_html=True)
    
            vip_button_text = TranslationService.get_translated_content('vip_button', lang)
            if st.button(vip_button_text, use_container_width=True, type="primary"):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
    
            st.markdown("---")
            st.markdown("""
            <div style="text-align: center; font-size: 0.7em; color: #888;">
                <p>© 2024 Juh Premium</p>
                <p>{age_text}</p>
            </div>
            """.format(age_text=TranslationService.translate_text("Conteúdo para maiores de 18 anos", lang)), unsafe_allow_html=True)
            
    @staticmethod
    def chat_shortcuts():
        cols = st.columns(4)
        lang = st.session_state.get('language', 'pt')
        
        shortcuts = {
            'pt': ["Início🏠", "Galeria 📸", "Ofertas 🎁", "VIP 💎"],
            'en': ["Home🏠", "Gallery 📸", "Offers 🎁", "VIP 💎"],
            'es': ["Inicio🏠", "Galería 📸", "Ofertas 🎁", "VIP 💎"]
        }
        
        current_shortcuts = shortcuts.get(lang, shortcuts['pt'])
        
        with cols[0]:
            if st.button(current_shortcuts[0], key="shortcut_home", use_container_width=True):
                st.session_state.current_page = "home"
                save_persistent_data()
                st.rerun()
        with cols[1]:
            if st.button(current_shortcuts[1], key="shortcut_gallery", use_container_width=True):
                st.session_state.current_page = "gallery"
                save_persistent_data()
                st.rerun()
        with cols[2]:
             if st.button(current_shortcuts[2], key="shortcut_offers", use_container_width=True):
                 st.session_state.current_page = "offers"
                 save_persistent_data()
                 st.rerun()
        with cols[3]:
            if st.button(current_shortcuts[3], key="shortcut_vip", use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()

    @staticmethod
    def enhanced_chat_ui(conn):
        lang = st.session_state.get('language', 'pt')
        
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
        
        chat_title = TranslationService.translate_text("Chat Privado com Juh", lang)
        st.markdown(f"""
        <div class="chat-header">
            <h2 style="margin:0; font-size:1.5em; display:inline-block;">{chat_title} 💎</h2>
        </div>
        """, unsafe_allow_html=True)
        
        msgs_today = TranslationService.translate_text("Mensagens hoje", lang)
        st.sidebar.markdown(f"""
        <div style="
            background: rgba(255, 20, 147, 0.1);
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            text-align: center;
        ">
            <p style="margin:0; font-size:0.9em;">
                {msgs_today}: <strong>{st.session_state.request_count}/{Config.MAX_REQUESTS_PER_SESSION}</strong>
            </p>
            <progress value="{st.session_state.request_count}" max="{Config.MAX_REQUESTS_PER_SESSION}" style="width:100%; height:6px;"></progress>
        </div>
        """, unsafe_allow_html=True)
        
        ChatService.process_user_input(conn)
        save_persistent_data()
        
        private_chat = TranslationService.translate_text("Conversa privada • Suas mensagens são confidenciais", lang)
        st.markdown(f"""
        <div style="
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            font-size: 0.8em;
            color: #888;
        ">
            <p>{private_chat}</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_gallery_page(conn):
        lang = st.session_state.get('language', 'pt')
        
        blocked_content = TranslationService.translate_text("Conteúdo bloqueado", lang)
        unlock_text = TranslationService.translate_text("Desbloqueie acesso completo", lang)
        vip_text = TranslationService.translate_text("Assine o plano VIP para ver todos os conteúdos", lang)
        vip_button = TranslationService.translate_text("Tornar-se VIP", lang)
        back_button = TranslationService.translate_text("Voltar ao chat", lang)
        
        st.markdown(f"""
        <div class="gallery-container">
            <div class="gallery-item">
                <img src="{Config.IMG_GALLERY[0]}" alt="Preview 1">
                <div style="text-align: center; color: #ff66b3; margin-top: 5px;">{blocked_content}</div>
            </div>
            <div class="gallery-item">
                <img src="{Config.IMG_GALLERY[1]}" alt="Preview 2">
                <div style="text-align: center; color: #ff66b3; margin-top: 5px;">{blocked_content}</div>
            </div>
            <div class="gallery-item">
                <img src="{Config.IMG_GALLERY[2]}" alt="Preview 3">
                <div style="text-align: center; color: #ff66b3; margin-top: 5px;">{blocked_content}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center;">
            <h4>{unlock_text}</h4>
            <p>{vip_text}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(vip_button, 
                    key="vip_button_gallery", 
                    use_container_width=True,
                    type="primary"):
            st.session_state.current_page = "offers"
            st.rerun()
        
        if st.button(back_button, key="back_from_gallery"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

class NewPages:
    @staticmethod
    def show_home_page():
        lang = st.session_state.get('language', 'pt')
        
        hero_title = TranslationService.translate_text("Juh Premium", lang)
        hero_text = TranslationService.translate_text("Conteúdo exclusivo que você não encontra em nenhum outro lugar...", lang)
        button_text = TranslationService.translate_text("Quero Acessar Tudo", lang)
        blocked_text = TranslationService.translate_text("VIP Only", lang)
        start_chat = TranslationService.translate_text("Iniciar Conversa Privada", lang)
        back_button = TranslationService.translate_text("Voltar ao chat", lang)
        
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

        st.markdown(f"""
        <div class="hero-banner">
            <h1 style="color: #ff66b3;">{hero_title}</h1>
            <p>{hero_text}</p>
            <div style="margin-top: 20px;">
                <a href="#vip" style="
                    background: #ff66b3;
                    color: white;
                    padding: 10px 25px;
                    border-radius: 30px;
                    text-decoration: none;
                    font-weight: bold;
                    display: inline-block;
                ">{button_text}</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        
        for col, img in zip(cols, Config.IMG_HOME_PREVIEWS):
            with col:
                caption = TranslationService.translate_text("Conteúdo bloqueado", lang)
                st.image(img, use_container_width=True, caption=caption, output_format="auto")
                st.markdown(f"""<div style="text-align:center; color: #ff66b3; margin-top: -15px;">{blocked_text}</div>""", unsafe_allow_html=True)

        st.markdown("---")
        
        if st.button(start_chat, 
                    use_container_width=True,
                    type="primary"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

        if st.button(back_button, key="back_from_home"):
            st.session_state.current_page = "chat"
            save_persistent_data()
            st.rerun()

    @staticmethod
    def show_offers_page():
        lang = st.session_state.get('language', 'pt')
        
        # Se for gringo, mostrar apenas o link
        if lang in ['en', 'es']:
            st.markdown(f"""
            <div style="text-align: center; padding: 50px 0;">
                <h2 style="color: #ff66b3;">{TranslationService.translate_text("Exclusive Content", lang)}</h2>
                <p>{TranslationService.translate_text("Click below to access all my exclusive content", lang)}</p>
                <a href="{Config.INTERNATIONAL_LINK}" target="_blank" style="
                    display: inline-block;
                    background: linear-gradient(45deg, #ff1493, #9400d3);
                    color: white;
                    padding: 15px 30px;
                    border-radius: 30px;
                    text-decoration: none;
                    font-weight: bold;
                    margin-top: 20px;
                ">
                    {TranslationService.translate_text("GET FULL ACCESS NOW", lang)}
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(TranslationService.translate_text("Back to chat", lang), key="back_from_offers"):
                st.session_state.current_page = "chat"
                save_persistent_data()
                st.rerun()
            return
        
        # Código existente para mostrar pacotes em português
        packages_title = TranslationService.translate_text("PACOTES EXCLUSIVOS", lang)
        packages_subtitle = TranslationService.translate_text("Escolha o que melhor combina com seus desejos...", lang)
        flash_offer = TranslationService.translate_text("OFERTA RELÂMPAGO", lang)
        ends_soon = TranslationService.translate_text("Termina em breve!", lang)
        back_button = TranslationService.translate_text("Voltar ao chat", lang)
        want_package = TranslationService.translate_text("QUERO ESTE PACOTE ➔", lang)
        
        st.markdown("""
        <style>
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

        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #ff66b3; border-bottom: 2px solid #ff66b3; display: inline-block; padding-bottom: 5px;">{packages_title}</h2>
            <p style="color: #aaa; margin-top: 10px;">{packages_subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="package-container">', unsafe_allow_html=True)
        
        # Pacote START
        start_title = TranslationService.translate_text("START", lang)
        start_desc = TranslationService.translate_text("para iniciantes", lang)
        start_benefits = [
            TranslationService.translate_text("10 fotos Inéditas", lang),
            TranslationService.translate_text("3 vídeo Intimos", lang),
            TranslationService.translate_text("Fotos Exclusivas", lang),
            TranslationService.translate_text("Videos Intimos", lang),
            TranslationService.translate_text("Fotos da Buceta", lang)
        ]
        
        st.markdown(f"""
        <div class="package-box package-start">
            <div class="package-header">
                <h3 style="color: #ff66b3;">{start_title}</h3>
                <div class="package-price" style="color: #ff66b3;">R$ 19,50</div>
                <small>{start_desc}</small>
            </div>
            <ul class="package-benefits">
                {''.join([f'<li>{benefit}</li>' for benefit in start_benefits])}
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{Config.CHECKOUT_START}" target="_blank" rel="noopener noreferrer" style="
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
                    {want_package}
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Pacote PREMIUM
        premium_title = TranslationService.translate_text("PREMIUM", lang)
        premium_desc = TranslationService.translate_text("experiência completa", lang)
        popular_text = TranslationService.translate_text("POPULAR", lang)
        premium_benefits = [
            TranslationService.translate_text("20 fotos exclusivas", lang),
            TranslationService.translate_text("2 vídeos premium", lang),
            TranslationService.translate_text("Fotos dos Peitos", lang),
            TranslationService.translate_text("Fotos da Bunda", lang),
            TranslationService.translate_text("Fotos da Buceta", lang),
            TranslationService.translate_text("Fotos Exclusivas e Videos Exclusivos", lang),
            TranslationService.translate_text("Videos Masturbando", lang)
        ]
        
        st.markdown(f"""
        <div class="package-box package-premium">
            <div class="package-badge">{popular_text}</div>
            <div class="package-header">
                <h3 style="color: #9400d3;">{premium_title}</h3>
                <div class="package-price" style="color: #9400d3;">R$ 45,50</div>
                <small>{premium_desc}</small>
            </div>
            <ul class="package-benefits">
                {''.join([f'<li>{benefit}</li>' for benefit in premium_benefits])}
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{Config.CHECKOUT_PREMIUM}" target="_blank" rel="noopener noreferrer" style="
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
                    {want_package}
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Pacote EXTREME
        extreme_title = TranslationService.translate_text("EXTREME", lang)
        extreme_desc = TranslationService.translate_text("para verdadeiros fãs", lang)
        extreme_benefits = [
            TranslationService.translate_text("23 fotos ultra-exclusivas", lang),
            TranslationService.translate_text("4 Videos Exclusivos", lang),
            TranslationService.translate_text("Fotos dos Peitos", lang),
            TranslationService.translate_text("Fotos da Bunda", lang),
            TranslationService.translate_text("Fotos da Buceta", lang),
            TranslationService.translate_text("Fotos Exclusivas", lang),
            TranslationService.translate_text("Videos Masturbando", lang),
            TranslationService.translate_text("Videos Transando", lang),
            TranslationService.translate_text("Acesso a conteúdos futuros", lang)
        ]
        
        st.markdown(f"""
        <div class="package-box package-extreme">
            <div class="package-header">
                <h3 style="color: #ff0066;">{extreme_title}</h3>
                <div class="package-price" style="color: #ff0066;">R$ 75,50</div>
                <small>{extreme_desc}</small>
            </div>
            <ul class="package-benefits">
                {''.join([f'<li>{benefit}</li>' for benefit in extreme_benefits])}
            </ul>
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px);">
                <a href="{Config.CHECKOUT_EXTREME}" target="_blank" rel="noopener noreferrer" style="
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
                    {want_package}
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="countdown-container">
            <h3 style="margin:0;">{flash_offer}</h3>
            <div id="countdown" style="font-size: 1.5em; font-weight: bold;">23:59:59</div>
            <p style="margin:5px 0 0;">{ends_soon}</p>
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
                "benefits": [
                    TranslationService.translate_text("3 fotos semi-nuas sensuais", lang),
                    TranslationService.translate_text("2 fotos +18 exclusivas só para você", lang)
                ],
                "tag": TranslationService.translate_text("COMUM", lang),
                "link": Config.CHECKOUT_PROMO + "?plan=Promo"
            },
            {
                "name": TranslationService.translate_text("3 Meses", lang),
                "price": "R$ 69,90",
                "original": "R$ 149,70",
                "benefits": [
                    TranslationService.translate_text("25% de desconto", lang),
                    TranslationService.translate_text("Bônus: 1 vídeo exclusivo", lang),
                    TranslationService.translate_text("Prioridade no chat", lang)
                ],
                "tag": TranslationService.translate_text("MAIS POPULAR", lang),
                "link": Config.CHECKOUT_VIP_3MESES + "?plan=3meses"
            },
            {
                "name": TranslationService.translate_text("1 Ano", lang),
                "price": "R$ 199,90",
                "original": "R$ 598,80",
                "benefits": [
                    TranslationService.translate_text("66% de desconto", lang),
                    TranslationService.translate_text("Presente surpresa mensal", lang),
                    TranslationService.translate_text("Acesso a conteúdos raros", lang)
                ],
                "tag": TranslationService.translate_text("MELHOR CUSTO-BENEFÍCIO", lang),
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
                            {TranslationService.translate_text("Assinar", lang)} {plan['name']}
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if st.button(back_button, key="back_from_offers"):
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
            'language': device_info['language']
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
        with st.container():
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            
            for msg in st.session_state.messages[-12:]:
                role = "user" if msg["role"] == "user" else "assistant"
                avatar = "🧑" if role == "user" else "💋"
                
                with st.chat_message(role, avatar=avatar):
                    if msg["content"] == "[ÁUDIO]":
                        st.markdown(UiService.get_chat_audio_player(), unsafe_allow_html=True)
                    else:
                        try:
                            content_data = json.loads(msg["content"])
                            if isinstance(content_data, dict):
                                st.markdown(content_data.get("text", ""))
                        except:
                            st.markdown(msg["content"])
            
            st.markdown('</div>', unsafe_allow_html=True)

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
    
                welcome_msg = {
                    'pt': "Eba! Que bom que você voltou 😍 Tava com saudade...",
                    'en': "Yay! So glad you're back 😍 Missed you...",
                    'es': "¡Genial! Qué bueno que volviste 😍 Te extrañaba..."
                }
                
                lang = st.session_state.get('language', 'pt')
                msg = welcome_msg.get(lang, welcome_msg['pt'])
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": msg
                })
                DatabaseService.save_message(
                    conn,
                    get_user_id(),
                    st.session_state.session_id,
                    "assistant",
                    msg,
                    lang
                )
    
                st.session_state.last_user_msg_time = now.isoformat()
                save_persistent_data()
                st.rerun()
        else:
            st.session_state.last_user_msg_time = now.isoformat()

        ChatService.display_chat_history()

        if not st.session_state.get("audio_sent") and st.session_state.chat_started:
            
            UiService.show_audio_recording_effect()
    
            st.session_state.messages.append({
                "role": "assistant",
                "content": "[ÁUDIO]"
            })
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "assistant",
                "[ÁUDIO]",
                st.session_state.get('language', 'pt')
            )
            st.session_state.audio_sent = True
            save_persistent_data()
            st.rerun()
    
        lang = st.session_state.get('language', 'pt')
        placeholder = TranslationService.get_translated_content('chat_input_placeholder', lang)
        
        user_input = st.chat_input(placeholder, key="chat_input")
    
        if user_input:
            cleaned_input = ChatService.validate_input(user_input)
            lower_input = cleaned_input.lower()
            
            # Detecta o idioma do usuário
            user_lang = detect_user_language(cleaned_input)
            st.session_state.language = user_lang  # Atualiza o idioma na sessão
            
            with st.chat_message("user", avatar="🧑"):
                st.markdown(cleaned_input)
    
            st.session_state.messages.append({
                "role": "user",
                "content": cleaned_input
            })
            DatabaseService.save_message(
                conn,
                get_user_id(),
                st.session_state.session_id,
                "user",
                cleaned_input,
                user_lang
            )
            st.session_state.request_count += 1
    
            if st.session_state.request_count >= Config.MAX_REQUESTS_PER_SESSION:
                busy_msg = {
                    'pt': "Vou ficar ocupada agora, me manda mensagem depois?",
                    'en': "I'll be busy now, message me later?",
                    'es': "Estaré ocupada ahora, ¿me envías un mensaje más tarde?"
                }
                
                with st.chat_message("assistant", avatar="💋"):
                    st.markdown(busy_msg.get(user_lang, busy_msg['pt']))
                DatabaseService.save_message(
                    conn,
                    get_user_id(),
                    st.session_state.session_id,
                    "assistant",
                    busy_msg.get(user_lang, busy_msg['pt']),
                    user_lang
                )
                save_persistent_data()
                st.session_state.last_user_msg_time = datetime.utcnow().isoformat()
                return
    
            # Respostas específicas para certos tipos de mensagens
            if any(term in lower_input for term in ["pix", "chave", "pagar", "como pago", "me passa", "transferência", "manda a chave"]):
                placeholder = st.empty()
                placeholder.markdown("💬 Digitando...")
                time.sleep(5)
                placeholder.empty()
                
                if user_lang in ['en', 'es']:  # Gringos - link único
                    responses = {
                        'en': {
                            "text": "For international fans, here's my exclusive content link:",
                            "cta": {
                                "show": True,
                                "label": "👉 Get Full Access",        
                                "target": Config.INTERNATIONAL_LINK  # Link para gringos
                            }
                        },
                        'es': {
                            "text": "Para fans internacionales, aquí está mi enlace de contenido exclusivo:",
                            "cta": {
                                "show": True,
                                "label": "👉 Obtener Acceso Completo",        
                                "target": Config.INTERNATIONAL_LINK  # Link para gringos
                            }
                        }
                    }
                else:  # Brasileiros - oferta de pacotes
                    responses = {
                        'pt': {
                            "text": (
                                "Nada de Pix direto, gostoso... 💸 Aqui você entra no meu mundinho só escolhendo "
                                "um dos meus planos: Promo, Start, Premium e Extreme 😈\n"
                                "Vem ver tudo que preparei pra te deixar louco 🔥"
                            ),
                            "cta": {
                                "show": True,
                                "label": "👉 Ver Planos VIP",        
                                "target": "offers"  # Página de ofertas normal
                            }
                        }
                    }
                    
                resposta = responses.get(user_lang, responses['pt'] if user_lang == 'pt' else responses['en'])
            
            elif any(p in lower_input for p in ["foto", "fotos", "buceta", "peito", "bunda"]):
                placeholder = st.empty()
                placeholder.markdown("💬 Digitando...")
                time.sleep(5)
                
                photo_responses = {
                    'pt': [
                        "tô com fotos da minha buceta bem aberta, quer ver?",
                        "minha buceta tá chamando você nas fotos...",
                        "fiz um ensaio novo mostrando tudinho 🔥"
                    ],
                    'en': [
                        "I have pics of my wide open pussy, wanna see?",
                        "my pussy is calling you in the pics...",
                        "I did a new photoshoot showing everything 🔥"
                    ],
                    'es': [
                        "tengo fotos de mi coño bien abierto, ¿quieres ver?",
                        "mi coño te está llamando en las fotos...",
                        "hice una nueva sesión mostrando todo 🔥"
                    ]
                }
                
                cta_labels = {
                    'pt': "Ver Fotos Quentes",
                    'en': "See Hot Pics",
                    'es': "Ver Fotos Calientes"
                }
                
                resposta = {
                    "text": random.choice(photo_responses.get(user_lang, photo_responses['pt'])),
                    "cta": {
                        "show": True,
                        "label": cta_labels.get(user_lang, cta_labels['pt']),
                        "target": "offers"
                    }
                }
            
            elif any(p in lower_input for p in ["você é real", "vc é real", "é ia", "é uma ia", "isso é um robô", "é humana?"]):
                placeholder = st.empty()
                placeholder.markdown("💬 Digitando...")
                time.sleep(5)
                
                responses = {
                    'pt': {
                        "text": "Sou tão real quanto sua vontade... 😈 Vem descobrir você mesmo no meu plano mais quente 🔥",
                        "cta": {
                            "show": True,
                            "label": "💎 Quero Ver Tudo",
                            "target": "offers"
                        }
                    },
                    'en': {
                        "text": "I'm as real as your desire... 😈 Come find out for yourself in my hottest plan 🔥",
                        "cta": {
                            "show": True,
                            "label": "💎 I Want to See Everything",
                            "target": "offers"
                        }
                    },
                    'es': {
                        "text": "Soy tan real como tu deseo... 😈 Ven a descubrirlo por ti mismo en mi plan más caliente 🔥",
                        "cta": {
                            "show": True,
                            "label": "💎 Quiero Ver Todo",
                            "target": "offers"
                        }
                    }
                }
                
                resposta = responses.get(user_lang, responses['pt'])
            
            elif any(v in lower_input for v in ["video", "transar", "masturbar"]):
                placeholder = st.empty()
                placeholder.markdown("💬 Digitando...")
                time.sleep(5)
                
                video_responses = {
                    'pt': [
                        "tenho vídeo me masturbando gostoso, vem ver 😈",
                        "tô me tocando nesse vídeo novo, quer ver?",
                        "gravei um vídeo especial só pra você 🥵"
                    ],
                    'en': [
                        "I have a video of me masturbating hard, come see 😈",
                        "I'm touching myself in this new video, wanna see?",
                        "I recorded a special video just for you 🥵"
                    ],
                    'es': [
                        "tengo un vídeo masturbándome rico, ven a ver 😈",
                        "me estoy tocando en este nuevo vídeo, ¿quieres ver?",
                        "grabé un vídeo especial solo para ti 🥵"
                    ]
                }
                
                cta_labels = {
                    'pt': "Ver Vídeos Exclusivos",
                    'en': "See Exclusive Videos",
                    'es': "Ver Vídeos Exclusivos"
                }
                
                resposta = {
                    "text": random.choice(video_responses.get(user_lang, video_responses['pt'])),
                    "cta": {
                        "show": True,
                        "label": cta_labels.get(user_lang, cta_labels['pt']),
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
                st.markdown(resposta["text"])
            
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
                json.dumps(resposta),
                user_lang
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
        }
        .stButton button {
            background: rgba(255, 20, 147, 0.2) !important;
            color: white !important;
            border: 1px solid #ff66b3 !important;
        }
        [data-testid="stChatInput"] {
            background: rgba(255, 102, 179, 0.1) !important;
            border: 1px solid #ff66b3 !important;
        }
        div.stButton > button:first-child {
            background: linear-gradient(45deg, #ff1493, #9400d3) !important;
            color: white !important;
            border: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 1. Inicialização do sistema
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = DatabaseService.init_db()
    
    conn = st.session_state.db_conn
    
    # 2. Carrega dados persistentes
    load_persistent_data()  # Adicione esta linha para carregar o estado salvo
    
    # 3. Verificação de idade (etapa crítica)
    if not st.session_state.get('age_verified', False):
        # Mostra a verificação de idade
        UiService.age_verification()
        
        # Exibe mensagem de carregamento
        calling_text = TranslationService.translate_text("📞 Ligando para Juh...", 
                      st.session_state.get('language', 'pt'))
        st.markdown(f"""
        <div style="text-align: center; margin-top: 50px;">
            <p style="font-size: 18px; color: #ff66b3;">{calling_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.stop()  # Impede qualquer execução adicional
    
    # 4. Configuração da sidebar
    UiService.setup_sidebar()
    
    # 5. Efeito de chamada (apenas na primeira vez)
    if not st.session_state.get('connection_complete', False):
        with st.spinner(''):  # Container vazio para o efeito
            UiService.show_call_effect()
        st.session_state.connection_complete = True
        save_persistent_data()
        st.rerun()
    
    # 6. Tela de boas-vindas antes do chat
    if not st.session_state.get('chat_started', False):
        with st.container():
            col1, col2, col3 = st.columns([1,3,1])
            with col2:
                ready_text = TranslationService.translate_text(
                    "Estou pronta para você, amor...", 
                    st.session_state.get('language', 'pt'))
                
                start_chat_text = TranslationService.translate_text(
                    "Iniciar Conversa", 
                    st.session_state.get('language', 'pt'))
                
                st.markdown(f"""
                <div style="text-align: center; margin: 50px 0;">
                    <img src="{Config.IMG_PROFILE}" 
                         width="120" 
                         style="border-radius: 50%; border: 3px solid #ff66b3;">
                    <h2 style="color: #ff66b3; margin-top: 15px;">Juh</h2>
                    <p style="font-size: 1.1em;">{ready_text}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(start_chat_text, 
                            type="primary", 
                            use_container_width=True,
                            key="start_chat_btn"):
                    st.session_state.update({
                        'chat_started': True,
                        'current_page': 'chat',
                        'audio_sent': False
                    })
                    save_persistent_data()
                    st.rerun()
        
        st.stop()
    
    # 7. Roteamento principal
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
    
    # 8. Persistência final
    save_persistent_data()

if __name__ == "__main__":
    # Reset de desenvolvimento (apenas para debug)
    # st.session_state.clear()  # Descomente se necessário para testes
    main()

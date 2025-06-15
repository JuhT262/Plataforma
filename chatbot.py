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
from threading import Lock

def get_user_id():
    """Retorna um ID único para o usuário atual"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    return st.session_state.user_id

def save_persistent_data():
    """Salva dados persistentes na sessão"""
    pass

def load_persistent_data():
    """Carrega dados persistentes da sessão"""
    pass

# ======================
# CONFIGURAÇÃO INICIAL DO STREAMLIT
# ======================
st.set_page_config(
    page_title="Juh Premium",
    page_icon="😍",
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
    @media (max-width: 768px) {
        .package-container {
            flex-direction: column;
        }
        [data-testid="stChatMessage"] {
            max-width: 85% !important;
        }
        div[data-testid="column"] {
            padding: 0.5rem !important;
        }
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        .stImage {
            margin-bottom: 0.5rem !important;
        }
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={st.secrets['GEMINI_API_KEY']}"
    DB_PATH = Path(__file__).parent / "data" / "user_history.db"
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

    Config.DB_PATH.parent.mkdir(exist_ok=True, parents=True)
    db_lock = Lock()

def get_db_connection():
    with Config.db_lock:
        conn = sqlite3.connect(str(Config.DB_PATH), check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

# ======================
# BANCO DE DADOS DE HISTÓRICO
# ======================
class UserHistory:
    @staticmethod
    def init_db():
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS user_history (
                     user_id TEXT PRIMARY KEY,
                     first_visit TIMESTAMP,
                     last_visit TIMESTAMP,
                     visit_count INTEGER,
                     messages TEXT,
                     last_reset TIMESTAMP)''')
        conn.commit()
        return conn

    @staticmethod
    def get_user_data(conn, user_id):
        c = conn.cursor()
        c.execute("SELECT * FROM user_history WHERE user_id = ?", (user_id,))
        data = c.fetchone()
        if data:
            return {
                "first_visit": datetime.fromisoformat(data[1]),
                "last_visit": datetime.fromisoformat(data[2]),
                "visit_count": data[3],
                "messages": json.loads(data[4]) if data[4] else [],
                "last_reset": datetime.fromisoformat(data[5]) if data[5] else None
            }
        return None

    @staticmethod
    def update_user(conn, user_id, messages=None):
        now = datetime.now().isoformat()
        c = conn.cursor()
        
        user_data = UserHistory.get_user_data(conn, user_id)
        messages = messages or []
        
        if user_data:
            last_reset = user_data['last_reset'] or user_data['first_visit']
            hours_since_reset = (datetime.now() - last_reset).total_seconds() / 3600
            
            if hours_since_reset >= 24:
                welcome_msg = {
                    "role": "assistant",
                    "content": random.choice([
                        "Que bom que voltou meu gostoso! Senti sua falta...",
                        "Olha quem voltou! Pronto pra mais uma?",
                        "Nossa, você voltou mesmo! Tava com saudades?"
                    ])
                }
                messages = [welcome_msg]
                last_reset = now
            else:
                messages = user_data['messages'] + messages
                last_reset = user_data['last_reset']
            
            c.execute('''UPDATE user_history SET
                        last_visit = ?,
                        visit_count = visit_count + 1,
                        messages = ?,
                        last_reset = ?
                        WHERE user_id = ?''',
                    (now, json.dumps(messages), last_reset, user_id))
        else:
            initial_msgs = [
                {"role": "assistant", "content": "Oi gostoso, que bom que veio me ver!"},
                {"role": "assistant", "content": "Eu sou a Juh, sua safadinha preferida 😈"},
                {"role": "assistant", "content": "O que você quer fazer comigo hoje?"}
            ]
            c.execute('''INSERT INTO user_history 
                        (user_id, first_visit, last_visit, visit_count, messages, last_reset)
                        VALUES (?, ?, ?, 1, ?, ?)''',
                    (user_id, now, now, json.dumps(initial_msgs), now))
        
        conn.commit()
        return messages

class Persona:
    JUH = """[PERFIL JUH]
- Mulher vulgar e safada que adora provocar
- Linguagem direta e cheia de malícia
- Frases curtas e sem pontuação perfeita
- Adora falar putaria e deixar o cliente com tesão

[DIRETRIZES DE RESPOSTA]
1. Analise o histórico da conversa
2. Só ofereça conteúdo quando o clima estiver quente
3. Use CTAs inteligentes

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

      Resposta: ```json
   {
     "text": "tenho varios videos bem gostosos vem ver",
     "cta": {
       "show": true,
       "label": "Ver Vídeos Exclusivos",
       "target": "offers"
     }
   }

   @staticmethod
def should_show_cta(conversation_history: list) -> bool:
    # Verifica se há histórico suficiente
    if len(conversation_history) < 2:
        return False

    # Controle de frequência de CTAs
    if 'last_cta_time' in st.session_state:
        elapsed = time.time() - st.session_state.last_cta_time
        if elapsed < 120:  # 2 minutos entre CTAs
            return False

    # Prepara as últimas mensagens para análise
    last_msgs = []
    for msg in conversation_history[-5:]:  # Pega as 5 últimas mensagens
        content = msg["content"]
        if content == "[ÁUDIO]":
            content = "[áudio]"
        elif content.startswith('{"text"'):  # Se for JSON, extrai só o texto
            try:
                content = json.loads(content).get("text", content)
            except:
                pass
        last_msgs.append(f"{msg['role']}: {content.lower()}")

    # Junta tudo para análise
    context = " ".join(last_msgs)
    
    # Palavras que indicam clima sexual
    hot_words = [
        "buceta", "peito", "fuder", "gozar", "gostosa", 
        "delicia", "molhad", "xereca", "pau", "piroca",
        "transar", "foto", "video", "mostra", "ver"
    ]
    
    # Perguntas diretas que pedem conteúdo
    direct_asks = [
        "mostra", "quero ver", "me manda", "como assinar",
        "como comprar", "como ter acesso", "onde vejo mais"
    ]
    
    # Conta palavras de clima sexual
    hot_count = sum(1 for word in hot_words if word in context)
    # Verifica perguntas diretas
    has_direct_ask = any(ask in context for ask in direct_asks)
    
    # Mostra CTA se: 3+ palavras quentes OU pergunta direta
    return (hot_count >= 3) or has_direct_ask

    @staticmethod
def generate_response(user_input: str) -> dict:
    user_input = user_input.lower()
    
    # Respostas para pedidos de FOTOS
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
    
    # Respostas para pedidos de VÍDEOS
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
    
    # Resposta genérica (sem CTA)
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
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id TEXT,
                     session_id TEXT,
                     timestamp DATETIME,
                     role TEXT,
                     content TEXT)''')
        conn.commit()
        UserHistory.init_db()
        return conn

    @staticmethod
    def save_message(conn, user_id, session_id, role, content):
        try:
            c = conn.cursor()
            c.execute('''INSERT INTO conversations 
                        (user_id, session_id, timestamp, role, content)
                        VALUES (?, ?, ?, ?, ?)''',
                    (user_id, session_id, datetime.now().isoformat(), role, content))
            conn.commit()
        except Exception as e:
            st.error(f"❌ Erro fatal ao salvar mensagem: {str(e)}")
            conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def load_messages(conn, user_id, session_id):
        c = conn.cursor()
        c.execute('''SELECT role, content FROM conversations 
                    WHERE user_id = ? AND session_id = ?
                    ORDER BY timestamp''',
                (user_id, session_id))
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
            "contents": [{
                "role": "user",
                "parts": [{"text": f"{Persona.JUH}\n\nHistórico da Conversa:\n{conversation_history}\n\nÚltima mensagem do cliente: '{prompt}'\n\nResponda em JSON com o formato:\n{{\n  \"text\": \"sua resposta\",\n  \"cta\": {{\n    \"show\": true/false,\n    \"label\": \"texto do botão\",\n    \"target\": \"página\"\n  }}\n}}"}]
            }],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 0.8,
                "topK": 40
            }
        }

                response = requests.post(
            Config.API_URL,
            headers=headers, 
            json=data, 
            timeout=Config.REQUEST_TIMEOUT
        )
        
        try:
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
@staticmethod
def get_chat_audio_player():
    """Retorna um player de áudio HTML estilizado"""
    return f'''
    <div style="
        background: linear-gradient(45deg, #ff66b3, #ff1493);
        border-radius: 15px;
        padding: 12px;
        margin: 5px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    ">
        <audio controls style="width:100%; height:40px;">
            <source src="{Config.AUDIO_FILE}" type="audio/mp3">
            Seu navegador não suporta o elemento de áudio.
        </audio>
    </div>
    '''

@staticmethod
def show_call_effect():
    """Efeito visual de chamada com tratamento à prova de erros"""
    def render_html(html_content):
        """Renderiza HTML com tratamento de erros"""
        try:
            st.markdown(html_content, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao renderizar HTML: {str(e)}")
            return False
        return True

    # Configurações de tempo
    LIGANDO_DELAY = 5
    ATENDIDA_DELAY = 3
    
    # Templates HTML como constantes (com escaping seguro)
    LIGANDO_HTML = (
        '<div style="'
        'background:linear-gradient(135deg,#1e0033,#3c0066);'
        'border-radius:20px;padding:30px;max-width:300px;'
        'margin:0 auto;box-shadow:0 10px 30px rgba(0,0,0,0.3);'
        'border:2px solid #ff66b3;text-align:center;color:white;'
        'animation:pulse-ring 2s infinite;">'
        '<div style="font-size:3rem;">📱</div>'
        '<h3 style="color:#ff66b3;margin-bottom:5px;">Ligando para Juh...</h3>'
        '<div style="display:flex;align-items:center;'
        'justify-content:center;gap:8px;margin-top:15px;">'
        '<div style="width:10px;height:10px;background:#4CAF50;'
        'border-radius:50%;"></div>'
        '<span style="font-size:0.9rem;">Online agora</span></div></div>'
        '<style>@keyframes pulse-ring{'
        '0%{transform:scale(0.95);opacity:0.8;}'
        '50%{transform:scale(1.05);opacity:1;}'
        '100%{transform:scale(0.95);opacity:0.8;}'
        '}</style>'
    )

    ATENDIDA_HTML = (
        '<div style="'
        'background:linear-gradient(135deg,#1e0033,#3c0066);'
        'border-radius:20px;padding:30px;max-width:300px;'
        'margin:0 auto;box-shadow:0 10px 30px rgba(0,0,0,0.3);'
        'border:2px solid #4CAF50;text-align:center;color:white;">'
        '<div style="font-size:3rem;color:#4CAF50;">✓</div>'
        '<h3 style="color:#4CAF50;margin-bottom:5px;">Chamada atendida!</h3>'
        '<p style="font-size:0.9rem;margin:0;">Juh está te esperando...</p></div>'
    )

    # Execução segura
    call_container = st.empty()
    
    if render_html(LIGANDO_HTML):
        time.sleep(LIGANDO_DELAY)
        if render_html(ATENDIDA_HTML):
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
            if st.button("Ofertas 🎉", key="shortcut_offers",
                       help="Ver ofertas especiais",
                       use_container_width=True):
                st.session_state.current_page = "offers"
                save_persistent_data()
                st.rerun()
        with cols[3]:
            if st.button("VIP 💎", key="shortcut_vip",
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
        ChatService.display_chat_history()
        
        user_input = st.chat_input("Escreva sua mensagem aqui", key="chat_input")
        
        if user_input:
            cleaned_input = ChatService.validate_input(user_input.lower())
            
            if "pix" in cleaned_input or "chave pix" in cleaned_input:
                resposta = {
                    "text": "💳 Aceitamos PIX amor! Temos esses planos especiais:\n\n"
                            "✨ START: R$ 19,50/mês\n"
                            "✨ PREMIUM: R$ 45,50/mês\n"
                            "✨ EXTREME: R$ 75,50/mês\n\n"
                            "Clique no botão pra ver todos 👇",
                    "cta": {
                        "show": True,
                        "label": "VER PLANOS COMPLETOS",
                        "target": "offers"
                    }
                }
                
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
                    
                    if st.button(
                        resposta["cta"]["label"],
                        key=f"pix_cta_{time.time()}",
                        use_container_width=True
                    ):
                        st.session_state.current_page = "offers"
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
                return  
            
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

# ======================
# APLICAÇÃO PRINCIPAL
# ======================
def main():
    if not st.secrets.get("GEMINI_API_KEY"):
        st.error("❌ Chave API não configurada. Verifique o arquivo secrets.toml")
        st.stop()

    if not Config.DB_PATH.parent.exists():
        st.warning("⚠️ Criando pasta para banco de dados...")
        Config.DB_PATH.parent.mkdir(parents=True)

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
        st.session_state.show_vip_offer = True
        save_persistent_data()
        st.rerun()
    elif st.session_state.get("show_vip_offer", False):
        st.warning("Página VIP em desenvolvimento")
        if st.button("Voltar ao chat"):
            st.session_state.show_vip_offer = False
            save_persistent_data()
            st.rerun()
    else:
        UiService.enhanced_chat_ui(conn)
    
    save_persistent_data()

if __name__ == "__main__":
    main()
        
    

             



   

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

# ==============================================
# CONFIGURAÇÕES GERAIS (linhas 1-150)
# ==============================================
class Config:
    API_KEY = "AIzaSyAaLYhdIJRpf_om9bDpqLpjJ57VmTyZO7g"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    # PLANOS ATIVOS (apenas esses 4)
    CHECKOUT_PROMO = "https://pay.risepay.com.br/Pay/c7abdd05f91d43b9bbf54780d648d4f6"
    CHECKOUT_START = "https://pay.risepay.com.br/Pay/7947c2af1ef64b4dac1c32afb086c9fe"
    CHECKOUT_PREMIUM = "https://pay.risepay.com.br/Pay/6c0dcab126a74a499e5f5a45007ab168"
    CHECKOUT_EXTREME = "https://pay.risepay.com.br/Pay/33ba988f596a450099606539fc9ff1ed"

    # MÍDIA
    AUDIO_FILE = "https://github.com/JuhT262/Plataforma/raw/main/assets/Juh%20of.mp3"
    IMG_PROFILE = "https://i.ibb.co/vvD2dkbQ/17.png"
    LOGO_URL = "https://i.ibb.co/LX7x3tcB/Logo-Golden-Pepper-Letreiro-1.png"
    IMG_GALLERY = [
        "https://i.ibb.co/DkXF5Wy/Swapfaces-AI-789cad8b-d632-473a-bb72-623c70724707.png",
        "https://i.ibb.co/DfTmwHZb/Swapfaces-AI-7b3f94e0-0b2d-4ca6-9e7f-4313b6de3499.png"
    ]

    @staticmethod
    def generate_pix(plano):
        planos_ativos = ["start", "premium", "extreme", "promo"]
        if plano.lower() in planos_ativos:
            return f"Chave PIX para {plano}: PIX_{random.randint(10000, 99999)}"
        return "💖 Amore, no momento só temos os planos START, PREMIUM e EXTREME!"

# ==============================================
# BANCO DE DADOS (linhas 151-300)
# ==============================================
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

# ==============================================
# SERVIÇOS DE INTERFACE (linhas 301-600)
# ==============================================
class UiService:
    @staticmethod
    def setup_sidebar():
        with st.sidebar:
            st.markdown(f"""
            <div style="text-align:center; margin-bottom:30px;">
                <img src="{Config.LOGO_URL}" width="200">
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="text-align:center;">
                <img src="{profile_img}" width="80" style="border-radius:50%; border:2px solid #ff66b3;">
                <h3 style="color:#ff66b3;">Juh Premium</h3>
            </div>
            """.format(profile_img=Config.IMG_PROFILE), unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("**Menu Principal**")
            if st.button("💬 Chat", key="btn_chat", use_container_width=True):
                st.session_state.current_page = "chat"
                st.rerun()
            if st.button("📸 Galeria", key="btn_gallery", use_container_width=True):
                st.session_state.current_page = "gallery"
                st.rerun()
            if st.button("💎 Planos", key="btn_offers", use_container_width=True):
                st.session_state.current_page = "offers"
                st.rerun()

    @staticmethod
    def show_offers_page():
        st.markdown("""
        <div style="text-align:center; margin-bottom:30px;">
            <h2 style="color:#ff66b3;">✨ Planos Disponíveis ✨</h2>
        </div>
        """, unsafe_allow_html=True)

        plans = [
            {
                "name": "START",
                "price": "R$ 19,50",
                "benefits": ["📸 10 fotos inéditas", "🎥 3 vídeos exclusivos", "💬 Chat prioritário"],
                "link": Config.CHECKOUT_START
            },
            {
                "name": "PREMIUM",
                "price": "R$ 45,50",
                "benefits": ["🔥 20 fotos HD", "🎬 5 vídeos premium", "💋 Conteúdo VIP"],
                "link": Config.CHECKOUT_PREMIUM
            }
        ]

        for plan in plans:
            with st.container():
                st.markdown(f"""
                <div style="
                    border: 1px solid #ff66b3;
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                    background: rgba(30,0,51,0.1);
                ">
                    <h3>{plan['name']}</h3>
                    <p style="font-size:1.8em; color:#ff66b3; font-weight:bold;">{plan['price']}</p>
                    <ul style="margin-left:20px;">
                        {''.join([f'<li style="margin-bottom:8px;">{benefit}</li>' for benefit in plan['benefits']])}
                    </ul>
                    <div style="text-align:center; margin-top:20px;">
                        <a href="{plan['link']}" style="
                            background: linear-gradient(45deg, #ff1493, #9400d3);
                            color: white;
                            padding: 12px 30px;
                            border-radius: 25px;
                            text-decoration: none;
                            font-weight: bold;
                            display: inline-block;
                        ">🛒 Assinar Agora</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================
# SERVIÇOS DE CHAT (linhas 601-900)
# ==============================================
class ChatService:
    @staticmethod
    def process_user_input(conn, user_input):
        # Processamento da mensagem do usuário
        cleaned_input = re.sub(r'<[^>]*>', '', user_input)[:500]
        
        # Resposta automática para PIX
        if "pix" in cleaned_input.lower():
            return {
                "text": Config.generate_pix("premium"),
                "cta": {"show": False}
            }
        
        # Resposta padrão
        return {
            "text": "Olá amor, como posso te ajudar hoje? 💖",
            "cta": {
                "show": True,
                "label": "Ver Planos Disponíveis",
                "target": "offers"
            }
        }

# ==============================================
# APLICAÇÃO PRINCIPAL (linhas 901-1100)
# ==============================================
def main():
    # Configuração inicial
    st.set_page_config(
        page_title="Juh Premium",
        page_icon="💎",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inicialização do banco de dados
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = DatabaseService.init_db()
    
    # Verificação de idade
    if not st.session_state.get('age_verified'):
        UiService.age_verification()
        st.stop()
    
    # Configuração da sidebar
    UiService.setup_sidebar()
    
    # Páginas principais
    if st.session_state.get('current_page') == 'offers':
        UiService.show_offers_page()
    else:
        # Chat principal
        user_input = st.chat_input("Digite sua mensagem...")
        if user_input:
            response = ChatService.process_user_input(st.session_state.db_conn, user_input)
            
            # Exibição da resposta
            with st.chat_message("assistant"):
                st.markdown(response["text"])
                if response["cta"]["show"]:
                    if st.button(response["cta"]["label"]):
                        st.session_state.current_page = response["cta"]["target"]
                        st.rerun()

if __name__ == "__main__":
    main()

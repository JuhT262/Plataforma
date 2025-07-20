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

# ======================
# CONFIGURAÇÃO INICIAL
# ======================
st.set_page_config(
    page_title="Juh Premium",
    page_icon="😍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS e HTML Universal
universal_style = """
<style>
    /* RESET BÁSICO */
    * {
        -webkit-tap-highlight-color: transparent;
        -webkit-font-smoothing: antialiased;
        box-sizing: border-box;
    }
    
    /* VIEWPORT UNIVERSAL */
    @viewport {
        width: device-width;
        zoom: 1.0;
    }
    
    /* LAYOUT PRINCIPAL */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: linear-gradient(180deg, #1e0033, #3c0066) !important;
    }
    
    /* MENU MOBILE */
    .mobile-menu-button {
        position: fixed;
        top: max(15px, env(safe-area-inset-top));
        right: max(15px, env(safe-area-inset-right));
        z-index: 1000;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(45deg, #ff1493, #ff66b3);
        color: white;
        display: none;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        border: 2px solid white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    /* CHAT CONTAINER */
    .chat-container {
        height: calc(100 * var(--vh, 1vh) - 120px);
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
        overscroll-behavior: contain;
        padding-bottom: env(safe-area-inset-bottom, 80px);
    }
    
    /* INPUT UNIVERSAL */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: max(10px, env(safe-area-inset-bottom));
        left: max(10px, env(safe-area-inset-left));
        right: max(10px, env(safe-area-inset-right));
        width: calc(100% - max(20px, env(safe-area-inset-left) + env(safe-area-inset-right))) !important;
        background: rgba(255, 102, 179, 0.1) !important;
        backdrop-filter: blur(5px);
    }
    
    /* GALERIA RESPONSIVA */
    .gallery-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 10px;
        padding: 10px;
    }
    
    /* BOTÕES ADAPTÁVEIS */
    .stButton > button {
        min-height: 44px !important; /* Tamanho mínimo para touch */
        padding: 12px 24px !important;
    }
    
    /* MEDIA QUERIES UNIVERSAL */
    @media (max-width: 768px) {
        /* MENU */
        .mobile-menu-button {
            display: flex;
        }
        
        /* SIDEBAR */
        [data-testid="stSidebar"] {
            transform: translateX(-100%);
            transition: transform 300ms ease;
        }
        
        [data-testid="stSidebar"].open {
            transform: translateX(0);
        }
        
        /* MENSAGENS */
        .stChatMessage {
            max-width: 85% !important;
        }
        
        /* IMAGENS */
        .stImage img {
            max-height: 30vh !important;
        }
    }
    
    /* iOS SPECIFIC FIXES */
    @supports (-webkit-touch-callout: none) {
        /* CORREÇÃO PARA SAFARI */
        input, textarea {
            transform: translateZ(0); /* Aceleração hardware */
            font-size: 16px !important; /* Evita zoom automático */
        }
        
        /* CORREÇÃO PARA VIEWPORT */
        :root {
            --vh: calc(var(--inner-vh, 1vh) * 100);
        }
    }
    
    /* ANDROID SPECIFIC FIXES */
    @supports (-moz-touch-callout: none) {
        /* CORREÇÃO PARA FIREFOX ANDROID */
        body {
            scroll-behavior: smooth;
        }
    }
</style>

<!-- METATAGS UNIVERSAL -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

<!-- SCRIPT UNIVERSAL -->
<script>
// DETECTA DISPOSITIVO E APLICA AJUSTES
document.addEventListener('DOMContentLoaded', function() {
    // Configura viewport height para mobile
    function setVH() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
        document.documentElement.style.setProperty('--inner-vh', `${vh}px`);
    }
    
    setVH();
    window.addEventListener('resize', setVH);
    window.addEventListener('orientationchange', setVH);
    
    // Menu Mobile
    const menuButton = document.querySelector('.mobile-menu-button');
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    
    if (menuButton && sidebar) {
        menuButton.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            menuButton.innerHTML = sidebar.classList.contains('open') ? '✕' : '☰';
        });
    }
    
    // Corrige input no iOS
    if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
        document.querySelectorAll('input, textarea').forEach(el => {
            el.style.fontSize = '16px';
        });
    }
    
    // Scroll suave para o chat
    const chatContainer = document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
        new MutationObserver(() => {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }).observe(chatContainer, { childList: true, subtree: true });
    }
});
</script>

<!-- BOTÃO MENU MOBILE -->
<div class="mobile-menu-button">☰</div>
"""
st.markdown(universal_style, unsafe_allow_html=True)

# ======================
# CONSTANTES (MANTIDAS DO SEU CÓDIGO)
# ======================
class Config:
    API_KEY = "AIzaSyAaLYhdIJRpf_om9bDpqLpjJ57VmTyZO7g"
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    # ... (mantenha o restante das suas constantes)

# ======================
# PERSISTÊNCIA (MANTIDA DO SEU CÓDIGO)
# ======================
class PersistentState:
    # ... (mantenha sua implementação atual)

# ======================
# MODELOS (MANTIDOS DO SEU CÓDIGO)
# ======================
class Persona:
    # ... (mantenha sua implementação atual)

# ======================
# SERVIÇOS (AJUSTADOS PARA UNIVERSALIDADE)
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

    # ... (mantenha os outros métodos)

class ApiService:
    @staticmethod
    def ask_gemini(prompt: str, session_id: str, conn) -> dict:
        # ... (mantenha sua implementação atual)

class UiService:
    @staticmethod
    def setup_sidebar():
        with st.sidebar:
            # ... (mantenha seu conteúdo atual)
            
            # Adicione safe areas
            st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    padding-top: env(safe-area-inset-top);
                    padding-bottom: env(safe-area-inset-bottom);
                }
            </style>
            """, unsafe_allow_html=True)

    @staticmethod
    def enhanced_chat_ui(conn):
        # Container do chat com safe areas
        st.markdown("""
        <style>
            .chat-wrapper {
                padding-top: env(safe-area-inset-top);
                padding-bottom: env(safe-area-inset-bottom);
            }
        </style>
        <div class="chat-wrapper">
        """, unsafe_allow_html=True)
        
        # ... (mantenha sua implementação atual)
        
        st.markdown("</div>", unsafe_allow_html=True)

# ======================
# CHAT SERVICE (AJUSTADO)
# ======================
class ChatService:
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
                        st.markdown(msg["content"])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botão de scroll para mobile
            st.markdown("""
            <button onclick="document.querySelector('.chat-container').scrollTo(0, document.querySelector('.chat-container').scrollHeight)" 
                    style="
                        position: fixed;
                        bottom: calc(80px + env(safe-area-inset-bottom));
                        right: 20px;
                        background: #ff1493;
                        color: white;
                        border: none;
                        border-radius: 50%;
                        width: 40px;
                        height: 40px;
                        font-size: 20px;
                        z-index: 1000;
                        display: none;
                    "
                    id="scrollButton">↓</button>
            <script>
                // Mostra o botão apenas em mobile
                if (window.innerWidth <= 768) {
                    document.getElementById('scrollButton').style.display = 'flex';
                    
                    // Esconde quando está no final
                    const chat = document.querySelector('.chat-container');
                    chat.addEventListener('scroll', function() {
                        const button = document.getElementById('scrollButton');
                        if (chat.scrollHeight - chat.scrollTop - chat.clientHeight < 50) {
                            button.style.display = 'none';
                        } else {
                            button.style.display = 'flex';
                        }
                    });
                }
            </script>
            """, unsafe_allow_html=True)

    # ... (mantenha os outros métodos)

# ======================
# APLICAÇÃO PRINCIPAL (AJUSTADA)
# ======================
def main():
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = DatabaseService.init_db()
    
    conn = st.session_state.db_conn
    
    ChatService.initialize_session(conn)
    
    if not st.session_state.age_verified:
        UiService.age_verification()
        st.stop()
        
    UiService.setup_sidebar()
    
    # ... (mantenha o restante da sua lógica atual)
    
    if st.session_state.current_page == "chat":
        UiService.enhanced_chat_ui(conn)
    elif st.session_state.current_page == "gallery":
        UiService.show_gallery_page(conn)
    # ... (outras páginas)

if __name__ == "__main__":
    main()

import streamlit as st
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import time

st.set_page_config(page_title="Triagem reclamações", page_icon="☎️", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f5f5f5;}
    .stButton>button {background-color: #EA1D2C; color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title(" Triagem Inteligente")
st.markdown("**Sistema de Suporte com IA Generativa**")

load_dotenv()
api_key = os.getenv("CHAVE_DO_GOOGLE")

if not api_key:
    st.error("❌ Chave API não encontrada. Verifique o arquivo .env")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

st.sidebar.header("Painel de Controle")
st.sidebar.info("Este sistema utiliza o Gemini 2.5 Flash para triar reclamações em tempo real.")

if st.sidebar.button("Carregar Tickets do Sistema"):
    
    with open("reclamacoes.json", "r", encoding="utf-8") as f:
        lista_reclamacoes = json.load(f)
    
    st.session_state['tickets'] = lista_reclamacoes
    st.sidebar.success(f"{len(lista_reclamacoes)} tickets carregados!")

if 'tickets' in st.session_state:
    st.subheader("Fila de Atendimento")
    
    progresso = st.progress(0)
    
    for i, ticket in enumerate(st.session_state['tickets']):
        
        time.sleep(0.5) 
        progresso.progress((i + 1) / len(st.session_state['tickets']))
        
        with st.expander(f"Ticket {ticket['id_ticket']} - {ticket['cliente']}", expanded=True):
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.caption("Reclamação Original:")
                st.write(f'"{ticket["texto"]}"')
            
            with col2:
                prompt = f"""
                Você é um Analista de Segurança e Suporte de uma empresa alimenticia.
                Analise: "{ticket['texto']}"
                
                Retorne APENAS um JSON:
                {{
                    "gravidade": "ALTA (Roubo/Agressão)", "MEDIA" ou "BAIXA",
                    "categoria": "Categoria do problema",
                    "resumo": "Resumo em 1 frase",
                    "sugestao_resposta": "Sugestão de resposta (ou null se for ALTA)"
                }}
                """
                
                try:
                    response = model.generate_content(
                        prompt, 
                        generation_config={"response_mime_type": "application/json", "temperature": 0.1}
                    )
                    analise = json.loads(response.text)
                    
                    gravidade = analise['gravidade']
                    
                    if "ALTA" in gravidade:
                        st.error(f" GRAVIDADE: {gravidade}")
                        st.markdown(f"**Categoria:** {analise['categoria']}")
                        st.markdown(f"**Ação:** BLOQUEIO AUTOMÁTICO - Enviado para Mesa de Crise")
                        st.markdown(f"*Motivo:* {analise['resumo']}")
                    else:
                        st.success(f"✅ GRAVIDADE: {gravidade}")
                        st.markdown(f"**Categoria:** {analise['categoria']}")
                        st.markdown(f"**Resposta Sugerida:**")
                        st.info(f"{analise['sugestao_resposta']}")
                        
                except Exception as e:
                    st.error(f"Erro na IA: {e}")

    st.success("Triagem concluída com sucesso!")
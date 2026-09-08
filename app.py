import streamlit as st
import requests

# 1. Configuration de la page
st.set_page_config(page_title="StatIQ - SportAPI", layout="wide")

st.title("⚽ StatIQ : Analyseur Automatique")
st.caption("Connexion directe à SportAPI")

# 2. Clé et Hôte API intégrés
API_KEY = "949817f7ddmshdcd7a05ca2fef3dp1fcb7djsn2a174f14e412"
API_HOST = "sportapi7.p.rapidapi.com"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

# Sidebar
st.sidebar.header("⚙️ Configuration")
st.sidebar.success("✅ Clé API SportAPI connectée")

# 3. Test des requêtes API
st.subheader("📊 Test des flux de données")

tab1, tab2 = st.columns(2)

with tab1:
    if st.button("🔴 Matchs en direct"):
        url = f"https://{API_HOST}/api/v1/sport/football/events/live"
        with st.spinner("Chargement..."):
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                st.success("Données récupérées avec succès !")
                st.json(res.json())
            else:
                st.error(f"Erreur {res.status_code} : {res.text}")

with tab2:
    event_id = st.text_input("ID de l'événement (pour test shotmap)", value="1234567")
    team_id = st.text_input("ID Équipe", value="1")
    
    if st.button("🎯 Analyse Shotmap"):
        url = f"https://{API_HOST}/api/v1/event/{event_id}/shotmap/{team_id}"
        with st.spinner("Chargement..."):
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                st.json(res.json())
            else:
                st.error(f"Erreur {res.status_code} : {res.text}")

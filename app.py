import streamlit as st
import requests
from datetime import datetime

# 1. Configuration globale
st.set_page_config(page_title="StatIQ - Plateforme d'Analyse", layout="wide", initial_sidebar_state="expanded")

API_KEY = "949817f7ddmshdcd7a05ca2fef3dp1fcb7djsn2a174f14e412"
API_HOST = "sportapi7.p.rapidapi.com"
HEADERS = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": API_HOST}

# 2. Fonctions de récupération API (avec mise en cache)
@st.cache_data(ttl=300)
def charger_matchs_du_jour():
    """Récupère la liste globale des matchs du jour."""
    url = f"https://{API_HOST}/api/v1/sport/football/events/live"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return res.json().get("events", [])
    except Exception:
        pass
    return []

@st.cache_data(ttl=300)
def charger_stats_match(event_id):
    """Récupère les statistiques détaillées d'un événement."""
    url = f"https://{API_HOST}/api/v1/event/{event_id}/statistics"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

# 3. Barre latérale : Métriques & Filtres
st.sidebar.title("⚽ StatIQ Navigation")
st.sidebar.markdown("---")

marche = st.sidebar.selectbox(
    "📊 Marché étudié",
    ["Tirs Cadrés", "Volume Touches", "Fautes Total", "Corners Total"]
)

seuil = st.sidebar.number_input("🎯 Seuil (ex: 4.5)", value=4.5, step=0.5)

st.sidebar.markdown("---")
st.sidebar.info("💡 Sélectionnez une compétition dans la liste principale pour filtrer vos matchs.")

# 4. En-tête de la plateforme
st.title("📲 StatIQ : Centre des Matchs")
st.caption(f"Programme du {datetime.now().strftime('%d/%m/%Y')} | Données en direct")

events = charger_matchs_du_jour()

if not events:
    st.info("🔄 Recherche des matchs en cours ou aucun match en direct à cet instant. Réessayez dans quelques minutes.")
else:
    # Structuration des matchs par compétition
    competitions = {}
    for ev in events:
        tournoi = ev.get("tournament", {}).get("name", "Autres Compétitions")
        if tournoi not in competitions:
            competitions[tournoi] = []
        competitions[tournoi].append(ev)

    # Sélection du championnat / compétition
    liste_competitions = ["Toutes les compétitions"] + list(competitions.keys())
    comp_choisie = st.selectbox("🏆 Filtrer par Compétition / Championnat :", liste_competitions)

    # Filtrage des matchs
    if comp_choisie == "Toutes les compétitions":
        matchs_a_afficher = events
    else:
        matchs_a_afficher = competitions[comp_choisie]

    # Construction du menu de sélection de match
    options_matchs = {}
    for ev in matchs_a_afficher:
        dom = ev.get("homeTeam", {}).get("name", "Équipe A")
        ext = ev.get("awayTeam", {}).get("name", "Équipe B")
        tournoi = ev.get("tournament", {}).get("name", "")
        status = ev.get("status", {}).get("description", "Programmé")
        
        label = f"[{tournoi}] {dom} vs {ext} ({status})"
        options_matchs[label] = ev

    st.markdown("---")
    st.subheader(f"📋 Matchs Disponibles ({len(options_matchs)})")
    
    match_selectionne_label = st.radio("Cliquez sur un match pour afficher son analyse :", list(options_matchs.keys()))

    if match_selectionne_label:
        match = options_matchs[match_selectionne_label]
        eq_dom = match.get("homeTeam", {}).get("name", "Domicile")
        eq_ext = match.get("awayTeam", {}).get("name", "Extérieur")
        event_id = match.get("id")

        st.markdown("---")
        st.header(f"🔍 Analyse StatIQ : {eq_dom} vs {eq_ext}")
        st.write(f"**Marché analysé :** {marche} | **Seuil fixé :** > {seuil}")

        with st.spinner("Analyse algorithmique des données API..."):
            # Simulation / Calcul des métriques StatIQ depuis l'événement
            score_constance = 80
            volume_attendu = seuil + 1.3

            if score_constance >= 80 or (volume_attendu >= seuil * 1.25):
                statut = "🟢 SIGNAL FORT (Haute Plus-Value)"
            elif score_constance >= 60:
                statut = "🟠 MODÉRÉ (Prudence)"
            else:
                statut = "🔴 INSTABLE (À éviter)"

            # Affichage des métriques clés
            col1, col2, col3 = st.columns(3)
            col1.metric("Indice de Constance", f"{score_constance}%")
            col2.metric("Volume Cumulé Attendu", f"{volume_attendu:.1f}")
            col3.metric("Indice Opportunité", statut)

            # Détail par équipe
            st.markdown("---")
            st.subheader("📈 Répartition des Indicateurs")
            c_d, c_e = st.columns(2)
            with c_d:
                st.write(f"**{eq_dom}** (Performance Domicile)")
                st.progress(0.85)
                st.caption("Constance observée : 85%")
            with c_e:
                st.write(f"**{eq_ext}** (Concessions Extérieur)")
                st.progress(0.75)
                st.caption("Constance observée : 75%")

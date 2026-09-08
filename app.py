import streamlit as st
import requests
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="StatIQ - Bet365 Football", page_icon="⚽", layout="wide")

st.markdown("""
    <style>
    h1, h2, h3 { color: #00E676 !important; font-weight: 700 !important; }
    div[data-testid="stMetric"] {
        background-color: #101820;
        border-left: 4px solid #00E676;
        padding: 12px;
        border-radius: 8px;
    }
    .stButton>button {
        background-color: #00E676 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Clés API Bet365
API_KEY = "949817f7ddmshdcd7a05ca2fef3dp1fcb7djsn2a174f14e412"
API_HOST = "bet36528.p.rapidapi.com"
HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

@st.cache_data(ttl=300)
def charger_donnees_bet365(date_formatted):
    # Lendpoint /historical-odds exige obligatoirement sport_id et date
    url = f"https://{API_HOST}/historical-odds"
    params = {
        "sport_id": "1",           # 1 = Football
        "date": date_formatted     # Format YYYYMMDD
    }
    try:
        res = requests.get(url, headers=HEADERS, params=params, timeout=12)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return data, 200
            elif isinstance(data, dict):
                items = data.get("results") or data.get("events") or data.get("data") or []
                return items, 200
        return [], res.status_code
    except Exception:
        return [], 500

def extraire_match(ev):
    if not isinstance(ev, dict):
        return None, None, None
    
    home = ev.get("home", {}).get("name") if isinstance(ev.get("home"), dict) else ev.get("home")
    away = ev.get("away", {}).get("name") if isinstance(ev.get("away"), dict) else ev.get("away")
    league = ev.get("league", {}).get("name") if isinstance(ev.get("league"), dict) else ev.get("league")
    
    home_str = str(home).strip() if home and str(home).lower() != "none" else None
    away_str = str(away).strip() if away and str(away).lower() != "none" else None
    league_str = str(league).strip() if league and str(league).lower() != "none" else "Compétition Général"
    
    return home_str, away_str, league_str

# 3. Sidebar
st.sidebar.title("⚽ StatIQ Bet365")
date_selectionnee = st.sidebar.date_input("📅 Date des matchs :", datetime.now())
date_api_str = date_selectionnee.strftime("%Y%m%d")

if st.sidebar.button("🔄 Actualiser"):
    st.cache_data.clear()
    st.rerun()

marche = st.sidebar.selectbox(
    "📊 Marché d'Analyse :",
    ["🎯 Tirs Cadrés", "⚽ Tirs Totaux", "🚩 Corners Totaux"]
)
seuil = st.sidebar.number_input("🎯 Seuil fixé", value=4.5, step=0.5)

# 4. Traitement & Affichage
st.title("⚽ Programme & Analyse Bet365")

events, status_code = charger_donnees_bet365(date_api_str)

if status_code != 200:
    st.error(f"❌ Erreur de réponse de l'API Bet365 (Code HTTP: {status_code}).")
    st.info("💡 Remarque : Vérifiez que la date sélectionnée contient des données historiques disponibles.")
else:
    matchs_valides = []
    for ev in events:
        h, a, l = extraire_match(ev)
        if h and a:
            matchs_valides.append({"home": h, "away": a, "league": l})

    if not matchs_valides:
        st.warning(f"⚠️ Aucun match de football trouvé pour la date du {date_selectionnee.strftime('%d/%m/%Y')}.")
    else:
        st.success(f"✅ **{len(matchs_valides)} matchs trouvés**.")
        options = {f"{m['home']} vs {m['away']} — ({m['league']})": m for m in matchs_valides}
        choix = st.selectbox("Sélectionnez le match :", list(options.keys()))

        if choix:
            m = options[choix]
            h, a, l = m["home"], m["away"], m["league"]
            
            st.markdown("---")
            st.header(f"🔍 Analyse : {h} vs {a}")
            st.caption(f"**Ligue :** {l} | **Marché :** {marche} | **Seuil :** > {seuil}")

            col_h, col_a = st.columns(2)
            with col_h:
                st.subheader(f"🏠 {h} (Domicile)")
                st.metric("Potentiel Domicile", f"{(seuil/2) + 0.8:.1f}")
                st.progress(0.75)

            with col_a:
                st.subheader(f"✈️ {a} (Extérieur)")
                st.metric("Potentiel Extérieur", f"{(seuil/2) + 0.3:.1f}")
                st.progress(0.60)

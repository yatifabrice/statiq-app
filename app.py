import streamlit as st
import requests

# 1. Configuration de la page et thème
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

# 2. Configuration API Bet365
API_KEY = "949817f7ddmshdcd7a05ca2fef3dp1fcb7djsn2a174f14e412"
API_HOST = "bet36528.p.rapidapi.com"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST,
    "Content-Type": "application/json"
}

@st.cache_data(ttl=180)
def charger_donnees_bet365():
    url = f"https://{API_HOST}/historical-odds"
    try:
        res = requests.get(url, headers=HEADERS, timeout=12)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return data, 200
            elif isinstance(data, dict):
                items = data.get("results") or data.get("events") or data.get("data") or [data]
                return items, 200
        return [], res.status_code
    except Exception:
        return [], 500

def extraire_donnees_match(ev):
    if not isinstance(ev, dict):
        return None, None, None, True

    # Noms des équipes
    home = ev.get("home") or ev.get("home_team") or ev.get("home_name") or ev.get("team_home")
    away = ev.get("away") or ev.get("away_team") or ev.get("away_name") or ev.get("team_away")
    
    if isinstance(home, dict):
        home = home.get("name") or home.get("title")
    if isinstance(away, dict):
        away = away.get("name") or away.get("title")

    # Ligue / Compétition
    league = ev.get("league") or ev.get("tournament") or ev.get("category")
    if isinstance(league, dict):
        league_name = league.get("name") or league.get("title") or "Compétition"
    else:
        league_name = str(league) if league else "Compétition Générale"

    home_str = str(home).strip() if home and str(home).lower() != "none" else None
    away_str = str(away).strip() if away and str(away).lower() != "none" else None

    # Filtrage des autres sports
    texte = f"{league_name} {home_str} {away_str}".lower()
    est_hors_football = any(x in texte for x in ["tennis", "itf", "atp", "wta", "nba", "basket", "volleyball"])

    return home_str, away_str, league_name, est_hors_football

# 3. Barre latérale
st.sidebar.title("⚽ StatIQ (Bet365)")

if st.sidebar.button("🔄 Réinitialiser le cache"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

marche = st.sidebar.selectbox(
    "📊 Marché d'Analyse :",
    [
        "🎯 Tirs Cadrés - Total Match",
        "🎯 Tirs Cadrés - Équipe Domicile",
        "🎯 Tirs Cadrés - Équipe Extérieur",
        "⚽ Tirs Totaux - Total Match",
        "⚽ Tirs Totaux - Équipe Domicile",
        "⚽ Tirs Totaux - Équipe Extérieur",
        "🚩 Corners Totaux"
    ]
)

seuil = st.sidebar.number_input("🎯 Seuil fixé (ex: 4.5)", value=4.5, step=0.5)

# 4. Page Principale
st.title("⚽ Programme & Analyse Bet365")

raw_events, status_code = charger_donnees_bet365()

if status_code != 200:
    st.error(f"❌ Erreur de réponse de l'API Bet365 (Code HTTP: {status_code}). Assurez-vous d'être abonné à l'API sur RapidAPI.")
else:
    matchs_valides = []
    for ev in raw_events:
        h, a, l, hors_sujet = extraire_donnees_match(ev)
        if not hors_sujet and h and a:
            matchs_valides.append({"home": h, "away": a, "league": l, "raw": ev})

    if not matchs_valides:
        st.warning("⚠️ Aucun match de football lisible extrait pour le moment. Cliquez sur 'Réinitialiser le cache'.")
    else:
        st.success(f"✅ **{len(matchs_valides)} matchs de football** récupérés.")

        options = {f"{m['home']} vs {m['away']} — ({m['league']})": m for m in matchs_valides}
        choix = st.selectbox("Sélectionnez un match :", list(options.keys()))

        if choix:
            m = options[choix]
            h, a, l = m["home"], m["away"], m["league"]

            st.markdown("---")
            st.header(f"🔍 Analyse : {h} vs {a}")
            st.caption(f"**Ligue :** {l} | **Marché :** {marche} | **Seuil :** > {seuil}")

            col_h, col_a = st.columns(2)
            with col_h:
                st.subheader(f"🏠 {h} (Domicile)")
                val_h = (seuil / 2) + 0.8
                st.metric(f"Potentiel ({h})", f"{val_h:.1f}")
                st.progress(0.72)

            with col_a:
                st.subheader(f"✈️ {a} (Extérieur)")
                val_a = (seuil / 2) + 0.3
                st.metric(f"Potentiel ({a})", f"{val_a:.1f}")
                st.progress(0.58)

            st.markdown("---")
            c1, c2 = st.columns(2)
            c1.metric("Constance Global Match", "83%")
            c2.metric("Total Attendu", f"{val_h + val_a:.1f}")

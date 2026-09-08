import streamlit as st
import pandas as pd
​st.set_page_config(page_title="StatIQ - Volume & Constance", layout="wide")
​st.title("⚽ StatIQ : Analyseur de Volume & Constance")
st.caption("Grands Championnats & Compétitions UEFA/FIFA")
​st.sidebar.header("⚙️ Configuration")
ligue = st.sidebar.selectbox(
"Compétition",
["Premier League", "La Liga", "Ligue 1", "Serie A", "Bundesliga", "Ligue des Champions", "Ligue Conférence"],
key="sb_ligue"
)
​st.subheader("📌 Analyse Détaillée de Match")
c_dom, c_ext = st.columns(2)
eq_dom = c_dom.text_input("Équipe Domicile", "Arsenal", key="inp_dom")
eq_ext = c_ext.text_input("Équipe Extérieure", "Brighton", key="inp_ext")
​marche = st.selectbox(
"Marché à analyser",
["Tirs Cadrés", "Volume Touches", "Fautes Total", "Corners Total"],
key="sb_marche"
)
​seuil = st.number_input("Seuil étudié (ex: 4.5 ou 34.5)", value=4.5, step=0.5, key="inp_seuil")
​st.markdown("---")
st.write("### 📊 Données des 5 Derniers Matchs")
​col1, col2 = st.columns(2)
​stats_dom = []
with col1:
st.write(f"{eq_dom} (5 derniers matchs)")
for i in range(5):
val = st.number_input(f"Match {i+1} ({eq_dom})", value=5.0, key=f"dom_{i}")
stats_dom.append(val)
​stats_ext = []
with col2:
st.write(f"{eq_ext} (5 derniers subis/concédés)")
for i in range(5):
val = st.number_input(f"Match {i+1} ({eq_ext})", value=4.0, key=f"ext_{i}")
stats_ext.append(val)
​taux_dom = (sum(1 for v in stats_dom if v >= seuil) / 5) * 100
taux_ext = (sum(1 for v in stats_ext if v >= seuil) / 5) * 100
​moy_dom = sum(stats_dom) / 5
moy_ext = sum(stats_ext) / 5
​volume_attendu = (moy_dom + moy_ext) / 2
score_constance = (taux_dom + taux_ext) / 2
​st.markdown("---")
st.subheader("🎯 Résultats de l'Algorithme")
​kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Constance Dom/Ext", f"{score_constance:.0f}%")
kpi2.metric("Volume Cumulé Attendu", f"{volume_attendu:.1f}")
​if score_constance >= 80 or (volume_attendu >= seuil * 1.25):
statut = "🟢 SIGNAL FORT (Haute Plus-Value)"
elif score_constance >= 60:
statut = "🟠 MODÉRÉ (Prudence)"
else:
statut = "🔴 INSTABLE (À éviter)"
​kpi3.metric("Indice Opportunité", statut)
​st.markdown("---")
st.subheader("📓 Bilan de Test (Étude 2 mois)")
with st.form("suivi_form"):
cote = st.number_input("Cote proposée", value=1.80, step=0.05, key="form_cote")
mise = st.number_input("Mise virtuelle (€)", value=10, key="form_mise")
soumettre = st.form_submit_button("Enregistrer l'opportunité")
if soumettre:
st.success(f"Enregistré : {eq_dom} vs {eq_ext} | {marche} > {seuil} @ {cote}")

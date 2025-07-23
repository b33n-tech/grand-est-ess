import streamlit as st
import pandas as pd
import altair as alt

st.title("Explorateur ESS Alsace – Tableau & Diagramme croisés")

# === Chargement du fichier ===
st.sidebar.header("Source des données")

# Option 1 : uploader un fichier
uploaded_file = st.sidebar.file_uploader("Uploader un fichier Excel (.xlsx)", type=["xlsx"])

# Option 2 : fichier par défaut (sur GitHub ou local)
use_default = st.sidebar.checkbox("Utiliser le fichier de démonstration par défaut", value=True)

@st.cache_data
def load_default_data():
    url = "https://raw.githubusercontent.com/ton-utilisateur/ton-repo/main/data/ess_alsace.xlsx"
    return pd.read_excel(url)

# Lecture des données
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Fichier importé avec succès.")
elif use_default:
    df = load_default_data()
    st.info("Fichier de démonstration chargé depuis GitHub.")
else:
    st.warning("Veuillez uploader un fichier ou utiliser l'exemple.")
    st.stop()

# === Aperçu des données ===
st.subheader("Aperçu du fichier importé")
st.dataframe(df.head())

# === Configuration du tableau croisé ===
st.subheader("Tableau croisé dynamique")
rows = st.selectbox("Choisir les lignes :", df.columns, index=1)
columns = st.selectbox("Choisir les colonnes :", df.columns, index=3)
values = st.selectbox("Valeur à calculer :", ['N°SIREN'], index=0)
aggfunc = st.selectbox("Fonction d’agrégation :", ['count', 'nunique'])

# === Création du tableau croisé ===
try:
    if aggfunc == 'count':
        pivot_table = pd.pivot_table(df, index=rows, columns=columns, values=values, aggfunc='count', fill_value=0)
    else:
        pivot_table = pd.pivot_table(df, index=rows, columns=columns, values=values, aggfunc='nunique', fill_value=0)
    st.dataframe(pivot_table)
except Exception as e:
    st.error(f"Erreur dans la création du tableau croisé : {e}")
    st.stop()

# === Diagramme croisé ===
st.subheader("Visualisation des données")

pivot_reset = pivot_table.reset_index().melt(id_vars=[rows], var_name=columns, value_name='Valeur')
chart_type = st.radio("Choisir un type de graphique", ["Barres", "Camembert (lignes seulement)"])

if chart_type == "Barres":
    chart = alt.Chart(pivot_reset).mark_bar().encode(
        x=alt.X(columns + ':N', title=columns),
        y='Valeur:Q',
        color=rows + ':N',
        tooltip=[rows, columns, 'Valeur']
    ).properties(width=700, height=400)
    st.altair_chart(chart)

elif chart_type == "Camembert (lignes seulement)":
    if columns != rows:
        st.warning("Le camembert est affichable uniquement si la colonne = ligne.")
    else:
        pie_data = df[rows].value_counts().reset_index()
        pie_data.columns = [rows, 'Valeur']
        chart = alt.Chart(pie_data).mark_arc().encode(
            theta='Valeur',
            color=rows,
            tooltip=[rows, 'Valeur']
        ).properties(width=500, height=500)
        st.altair_chart(chart)

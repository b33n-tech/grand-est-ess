import streamlit as st
import pandas as pd
import altair as alt

# Configuration de la page
st.set_page_config(page_title="ESS Alsace – Explorateur", layout="wide")
st.title("🔍 Explorateur des organisations ESS en Alsace")

# === Chargement des données depuis GitHub ===

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/b33n-tech/grand-est-ess/main/base-alsace.xlsx"
    return pd.read_excel(url, engine='openpyxl')

# Chargement du fichier
try:
    df = load_data()
    st.success("✅ Données chargées depuis GitHub : `base-alsace.xlsx`")
except Exception as e:
    st.error("❌ Erreur de chargement du fichier Excel.")
    st.stop()

# === Aperçu des données ===
st.subheader("📄 Aperçu des données")
st.dataframe(df.head())

# === Configuration du tableau croisé ===
st.subheader("📊 Tableau croisé dynamique")

col1, col2, col3 = st.columns(3)
with col1:
    rows = st.selectbox("🏷️ Variable en ligne :", df.columns, index=1)
with col2:
    columns = st.selectbox("📁 Variable en colonne :", df.columns, index=3)
with col3:
    values = st.selectbox("🔢 Valeur à mesurer :", ['N°SIREN'], index=0)

aggfunc = st.radio("⚙️ Méthode d'agrégation :", ['count', 'nunique'], horizontal=True)

# === Création du pivot ===
try:
    if aggfunc == 'count':
        pivot_table = pd.pivot_table(df, index=rows, columns=columns, values=values, aggfunc='count', fill_value=0)
    else:
        pivot_table = pd.pivot_table(df, index=rows, columns=columns, values=values, aggfunc='nunique', fill_value=0)

    st.subheader("📑 Résultat du tableau croisé")
    st.dataframe(pivot_table)
except Exception as e:
    st.error(f"Erreur lors de la génération du tableau croisé : {e}")
    st.stop()

# === Visualisation ===
st.subheader("📈 Diagramme croisé interactif")

pivot_reset = pivot_table.reset_index().melt(id_vars=[rows], var_name=columns, value_name='Valeur')
chart_type = st.radio("Type de graphique", ["Barres", "Camembert (lignes uniquement)"], horizontal=True)

if chart_type == "Barres":
    chart = alt.Chart(pivot_reset).mark_bar().encode(
        x=alt.X(columns + ':N', title=columns),
        y='Valeur:Q',
        color=rows + ':N',
        tooltip=[rows, columns, 'Valeur']
    ).properties(width=800, height=400)

    st.altair_chart(chart)

elif chart_type == "Camembert (lignes uniquement)":
    if rows != columns:
        st.warning("⚠️ Le camembert nécessite que ligne = colonne.")
    else:
        pie_data = df[rows].value_counts().reset_index()
        pie_data.columns = [rows, 'Valeur']
        chart = alt.Chart(pie_data).mark_arc().encode(
            theta='Valeur',
            color=rows,
            tooltip=[rows, 'Valeur']
        ).properties(width=500, height=500)

        st.altair_chart(chart)

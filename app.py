import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="ESS Alsace – Explorateur", layout="wide")
st.title("🔍 Explorateur ESS Alsace avec multi-dimensions")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/b33n-tech/grand-est-ess/main/base-alsace.xlsx"
    return pd.read_excel(url, engine='openpyxl')

df = load_data()

st.subheader("📄 Aperçu des données")
st.dataframe(df.head())

st.subheader("📊 Configuration tableau croisé dynamique")

# Sélection multiple de lignes (index)
rows = st.multiselect("Variables en ligne (au moins 1)", options=df.columns, default=[df.columns[1]])

# Sélection multiple de colonnes (colonnes pivot)
columns = st.multiselect("Variables en colonne (optionnel)", options=df.columns, default=[df.columns[3]])

values = st.selectbox("Valeur à agréger", options=['N°SIREN'], index=0)
aggfunc = st.radio("Fonction d’agrégation", ['count', 'nunique'], horizontal=True)

if len(rows) == 0:
    st.warning("Sélectionnez au moins une variable en ligne.")
    st.stop()

try:
    pivot_table = pd.pivot_table(
        df,
        index=rows,
        columns=columns if len(columns) > 0 else None,
        values=values,
        aggfunc=aggfunc,
        fill_value=0,
    )
    st.subheader("📑 Résultat du tableau croisé")
    st.dataframe(pivot_table)
except Exception as e:
    st.error(f"Erreur lors de la création du tableau croisé : {e}")
    st.stop()

# === Visualisation simple avec Altair (sur les 2 premières dimensions seulement) ===
st.subheader("📈 Visualisation")

# Réduction du pivot pour Altair : reset_index + melt
pivot_reset = pivot_table.reset_index()

# Si colonnes sélectionnées : pivot.columns est un MultiIndex → aplatissement
if columns:
    pivot_reset = pivot_reset.melt(id_vars=rows, var_name="_col", value_name='Valeur')
    x_axis = "_col"
else:
    # Pas de colonnes : transformer en format long
    pivot_reset = pivot_reset.melt(id_vars=rows, var_name='variable', value_name='Valeur')
    x_axis = rows[-1]  # dernière variable en ligne comme x

if len(rows) > 1:
    color = rows[0]
else:
    color = None

chart_type = st.radio("Type de graphique", ["Barres", "Camembert (si 1 variable)"], horizontal=True)

if chart_type == "Barres":
    enc = {
        'x': alt.X(x_axis + ':N', title=x_axis),
        'y': 'Valeur:Q',
        'tooltip': [x_axis, 'Valeur']
    }
    if color:
        enc['color'] = alt.Color(color + ':N')
        enc['tooltip'].append(color)

    chart = alt.Chart(pivot_reset).mark_bar().encode(**enc).properties(width=800, height=400)
    st.altair_chart(chart)

elif chart_type == "Camembert (si 1 variable)":
    if len(rows) == 1 and not columns:
        pie_data = df[rows[0]].value_counts().reset_index()
        pie_data.columns = [rows[0], 'Valeur']
        chart = alt.Chart(pie_data).mark_arc().encode(
            theta='Valeur',
            color=rows[0],
            tooltip=[rows[0], 'Valeur']
        ).properties(width=500, height=500)
        st.altair_chart(chart)
    else:
        st.warning("Le camembert fonctionne uniquement avec une seule variable en ligne et aucune en colonne.")

import streamlit as st
import pandas as pd
import altair as alt

st.title("Visualisation synthèse ESS par commune")

@st.cache_data
def load_data(file):
    return pd.read_excel(file, engine='openpyxl')

# Upload fichier
uploaded_file = st.file_uploader("Uploader un fichier Excel synthèse (.xlsx)", type="xlsx")

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.success("✅ Fichier chargé avec succès")
    except Exception as e:
        st.error(f"Erreur à la lecture du fichier : {e}")
        st.stop()
else:
    st.info("Aucun fichier uploadé — chargement du fichier par défaut `synthese_communes.xlsx`")
    try:
        df = load_data("synthese_communes.xlsx")
    except Exception as e:
        st.error(f"Erreur à la lecture du fichier par défaut : {e}")
        st.stop()

st.subheader("Aperçu des données")
st.dataframe(df.head())

# Préparer colonnes (exclure colonne commune et total si existant)
columns = list(df.columns)
commune_col = "Libellé de la commune de l'établissement"
if commune_col in columns:
    columns.remove(commune_col)
if "TOTAL" in columns:
    columns.remove("TOTAL")

# Sélection communes
communes = df[commune_col].unique()
selected_communes = st.multiselect("Sélectionner une ou plusieurs communes", communes, default=communes[:5])

filtered_df = df[df[commune_col].isin(selected_communes)]

# Mise en forme longue
data_melted = filtered_df.melt(id_vars=[commune_col],
                               value_vars=columns,
                               var_name="Type d'organisation",
                               value_name="Nombre")

st.subheader("Diagramme interactif")

chart = alt.Chart(data_melted).mark_bar().encode(
    x=alt.X("Type d'organisation:N", title="Type d'organisation"),
    y=alt.Y("Nombre:Q", title="Nombre d'organisations"),
    color=alt.Color(f"{commune_col}:N", title="Commune"),
    tooltip=[commune_col, "Type d'organisation", "Nombre"]
).properties(width=800, height=400).interactive()

st.altair_chart(chart)

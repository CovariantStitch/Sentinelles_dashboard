import streamlit as st

page_information = st.Page("./pages/Informations.py", title="Informations", icon=":material/info:")
page_suivi = st.Page("./pages/Suivi_recent.py", title="Suivi récent", icon="🤒")
page_general = st.Page("./pages/Vue générale.py", title="Données historiques", icon=":material/history:")
page_analyse = st.Page("./pages/Analyse.py", title="Analyse gaussienne", icon=":material/airwave:")
page_temperature = st.Page("./pages/Analyse_temperature.py", title="Analyse température",
                           icon="⛅")
page_model_comp = st.Page("./pages/Modele_comparaison.py", title="Comparaison de modèles")

pg = st.navigation({
    "Général": [page_information, page_suivi, page_general],
    "Analyses": [page_analyse, page_temperature],
    "Modèles": [page_model_comp]
})

st.set_page_config(
    page_title="Données sentinelles",
    page_icon=":material/microbiology:",
    layout="wide",
)

pg.run()

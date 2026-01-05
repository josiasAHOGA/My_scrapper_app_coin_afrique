"""
Application de Scraping CoinAfrique
Projet Master AI - DIT
Auteur: Josias
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os
import re

sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Configuration
st.set_page_config(
    page_title="CoinAfrique Scraper",
    page_icon="📊",
    layout="wide"
)

# Titre principal
st.title("Projet CoinAfrique - Scraping et Analyse de Données")
st.markdown("**Master AI - Dakar Institute of Technology | Auteur: Josias**")
st.markdown("---")

# Fonction pour la page d'accueil
def page_accueil():
    st.header("Bienvenue")
    
    st.write("""
    Cette application permet de :
    - Scraper des données depuis CoinAfrique
    - Importer des fichiers CSV
    - Visualiser les données avec des graphiques
    - Analyser les tendances du marché
    """)
    
    st.subheader("Statistiques des Données Disponibles")
    
    categories = ['vetements_homme', 'chaussures_homme', 'vetements_enfants', 'chaussures_enfants']
    cols = st.columns(4)
    
    for idx, categorie in enumerate(categories):
        fichier = f"data/{categorie}_nettoye.csv"
        with cols[idx]:
            if os.path.exists(fichier):
                try:
                    df = pd.read_csv(fichier)
                    st.metric(categorie.replace('_', ' ').title(), f"{len(df)} annonces")
                except:
                    st.info("Pas de données")
            else:
                st.info("Pas de données")
    
    st.markdown("---")
    st.write("**Navigation:** Utilisez le menu latéral pour accéder aux différentes fonctionnalités.")

# Fonction pour le scraping
def page_scraping():
    st.header("Scraper les Données")
    
    st.write("Sélectionnez les catégories à scraper depuis CoinAfrique:")
    
    col1, col2 = st.columns(2)
    with col1:
        vet_homme = st.checkbox("Vêtements Homme", value=True)
        chau_homme = st.checkbox("Chaussures Homme", value=True)
    with col2:
        vet_enfants = st.checkbox("Vêtements Enfants", value=True)
        chau_enfants = st.checkbox("Chaussures Enfants", value=True)
    
    max_annonces = st.slider(
        "Nombre maximum d'annonces par catégorie",
        min_value=10,
        max_value=500,
        value=50,
        step=10
    )
    
    if st.button("Lancer le Scraping", type="primary"):
        categories_selectionnees = []
        if vet_homme:
            categories_selectionnees.append(('vetements_homme', 'https://sn.coinafrique.com/categorie/vetements-homme'))
        if chau_homme:
            categories_selectionnees.append(('chaussures_homme', 'https://sn.coinafrique.com/categorie/chaussures-homme'))
        if vet_enfants:
            categories_selectionnees.append(('vetements_enfants', 'https://sn.coinafrique.com/categorie/vetements-enfants'))
        if chau_enfants:
            categories_selectionnees.append(('chaussures_enfants', 'https://sn.coinafrique.com/categorie/chaussures-enfants'))
        
        if not categories_selectionnees:
            st.error("Veuillez sélectionner au moins une catégorie!")
            return
        
        progress_bar = st.progress(0)
        status = st.empty()
        
        try:
            from scraper_coinafrique import CoinAfriqueScraper
            scraper = CoinAfriqueScraper()
            
            total = len(categories_selectionnees)
            resultats = {}
            
            for idx, (nom_cat, url) in enumerate(categories_selectionnees):
                status.text(f"Scraping: {nom_cat}...")
                progress_bar.progress((idx + 1) / total)
                
                annonces = scraper.scraper_page(url, max_annonces)
                
                if annonces:
                    df = pd.DataFrame(annonces)
                    if 'vetements' in nom_cat:
                        df.columns = ['type_habits', 'prix', 'adresse', 'image_lien']
                    else:
                        df.columns = ['type_chaussures', 'prix', 'adresse', 'image_lien']
                    
                    fichier = f"data/{nom_cat}_nettoye.csv"
                    df.to_csv(fichier, index=False, encoding='utf-8-sig')
                    resultats[nom_cat] = df
                    
                    st.success(f"{nom_cat}: {len(df)} annonces collectées")
            
            status.text("Scraping terminé!")
            
            # Afficher les données collectées
            st.subheader("Données Collectées")
            for nom_cat, df in resultats.items():
                with st.expander(f"{nom_cat} - {len(df)} annonces"):
                    st.dataframe(df.head(20), use_container_width=True)
            
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

# Fonction pour l'import
def page_import():
    st.header("Importer des Données CSV")
    
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Fichier chargé: {len(df)} lignes, {len(df.columns)} colonnes")
            
            st.subheader("Aperçu des données")
            st.dataframe(df.head(20), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Lignes", len(df))
            col2.metric("Colonnes", len(df.columns))
            col3.metric("Valeurs manquantes", df.isnull().sum().sum())
            
            nom_fichier = st.text_input("Nom du fichier", "donnees_importees.csv")
            if st.button("Sauvegarder"):
                df.to_csv(f"data/{nom_fichier}", index=False, encoding='utf-8-sig')
                st.success(f"Fichier sauvegardé: data/{nom_fichier}")
                
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
    
    st.markdown("---")
    st.subheader("Télécharger les données existantes")
    
    categories = ['vetements_homme', 'chaussures_homme', 'vetements_enfants', 'chaussures_enfants']
    for categorie in categories:
        fichier = f"data/{categorie}_nettoye.csv"
        if os.path.exists(fichier):
            try:
                df = pd.read_csv(fichier)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    f"Télécharger {categorie} ({len(df)} annonces)",
                    csv,
                    f"{categorie}.csv",
                    "text/csv"
                )
            except:
                pass

# Fonction pour le dashboard
def page_dashboard():
    st.header("Dashboard et Visualisations")
    
    categories = {
        'Vêtements Homme': 'vetements_homme',
        'Chaussures Homme': 'chaussures_homme',
        'Vêtements Enfants': 'vetements_enfants',
        'Chaussures Enfants': 'chaussures_enfants'
    }
    
    cat_select = st.selectbox("Sélectionner une catégorie", list(categories.keys()))
    fichier = f"data/{categories[cat_select]}_nettoye.csv"
    
    if not os.path.exists(fichier):
        st.warning("Aucune donnée disponible pour cette catégorie")
        st.info("Utilisez la page 'Scraper' pour collecter des données")
        return
    
    try:
        df = pd.read_csv(fichier)
        
        # Statistiques générales
        st.subheader("Statistiques Générales")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Annonces", len(df))
        
        # Extraction des prix numériques
        df['prix_num'] = df['prix'].apply(lambda x: 
            float(re.sub(r'[^\d]', '', str(x))) if 'demande' not in str(x).lower() and re.sub(r'[^\d]', '', str(x)) else None
        )
        
        prix_valides = df['prix_num'].dropna()
        
        if len(prix_valides) > 0:
            col2.metric("Prix Moyen", f"{prix_valides.mean():,.0f} CFA")
            col3.metric("Prix Min", f"{prix_valides.min():,.0f} CFA")
            col4.metric("Prix Max", f"{prix_valides.max():,.0f} CFA")
        
        st.markdown("---")
        
        # Graphiques
        tab1, tab2, tab3 = st.tabs(["Par Localisation", "Distribution Prix", "Top Produits"])
        
        with tab1:
            if 'adresse' in df.columns:
                df['ville'] = df['adresse'].apply(lambda x: 
                    x.split(',')[0] if isinstance(x, str) and ',' in x else 'Non spécifié'
                )
                villes = df['ville'].value_counts().head(10)
                
                fig = px.bar(
                    x=villes.index,
                    y=villes.values,
                    labels={'x': 'Ville', 'y': 'Nombre d\'annonces'},
                    title="Top 10 des villes"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if len(prix_valides) > 0:
                fig = px.histogram(
                    df.dropna(subset=['prix_num']),
                    x='prix_num',
                    labels={'prix_num': 'Prix (CFA)'},
                    title='Distribution des Prix'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col_type = 'type_habits' if 'type_habits' in df.columns else 'type_chaussures'
            top_produits = df[col_type].value_counts().head(15)
            
            fig = px.bar(
                x=top_produits.values,
                y=top_produits.index,
                orientation='h',
                labels={'x': 'Nombre', 'y': 'Produit'},
                title='Top 15 Produits'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Tableau de données
        st.subheader("Données Brutes")
        
        recherche = st.text_input("Rechercher")
        df_affiche = df.copy()
        
        if recherche:
            df_affiche = df_affiche[
                df_affiche.astype(str).apply(
                    lambda row: row.str.contains(recherche, case=False, na=False).any(),
                    axis=1
                )
            ]
        
        st.dataframe(df_affiche.drop(columns=['prix_num'], errors='ignore'), use_container_width=True)
        
        csv = df_affiche.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("Télécharger les données", csv, f"{categories[cat_select]}.csv", "text/csv")
        
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

# Fonction pour l'évaluation
def page_evaluation():
    st.header("Formulaire d'Évaluation")
    
    with st.form("evaluation"):
        st.subheader("Informations")
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom complet")
            email = st.text_input("Email")
        with col2:
            organisation = st.text_input("Organisation")
            role = st.selectbox("Rôle", ["Étudiant", "Enseignant", "Chercheur", "Professionnel", "Autre"])
        
        st.subheader("Évaluation")
        col1, col2 = st.columns(2)
        
        with col1:
            note_interface = st.slider("Interface", 1, 5, 3)
            note_fonctions = st.slider("Fonctionnalités", 1, 5, 3)
        with col2:
            note_perf = st.slider("Performance", 1, 5, 3)
            note_global = st.slider("Note globale", 1, 5, 3)
        
        commentaires = st.text_area("Commentaires")
        
        submitted = st.form_submit_button("Soumettre")
        
        if submitted:
            if not nom or not email:
                st.error("Veuillez remplir le nom et l'email")
            else:
                eval_data = {
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'nom': nom,
                    'email': email,
                    'organisation': organisation,
                    'role': role,
                    'note_interface': note_interface,
                    'note_fonctions': note_fonctions,
                    'note_perf': note_perf,
                    'note_global': note_global,
                    'commentaires': commentaires
                }
                
                fichier = "data/evaluations.csv"
                if os.path.exists(fichier):
                    df_eval = pd.read_csv(fichier)
                    df_eval = pd.concat([df_eval, pd.DataFrame([eval_data])], ignore_index=True)
                else:
                    df_eval = pd.DataFrame([eval_data])
                
                df_eval.to_csv(fichier, index=False, encoding='utf-8-sig')
                st.success("Évaluation enregistrée. Merci!")

# Navigation
def main():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choisir une page",
        ["Accueil", "Scraper", "Importer", "Dashboard", "Évaluation"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **À propos**
    
    Projet Master AI  
    DIT - 2026  
    Auteur: Josias
    """)
    
    if page == "Accueil":
        page_accueil()
    elif page == "Scraper":
        page_scraping()
    elif page == "Importer":
        page_import()
    elif page == "Dashboard":
        page_dashboard()
    elif page == "Évaluation":
        page_evaluation()

if __name__ == "__main__":
    main()

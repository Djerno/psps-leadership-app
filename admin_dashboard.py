import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Admin PSPS",
    page_icon="📊",
    layout="wide"
)

# 📁 Configuration des données
DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "evaluations.csv")


@st.cache_data
def load_data():
    """
    Charge les données des évaluations depuis le fichier CSV.
    """
    if not os.path.exists(CSV_FILE):
        st.warning("📁 Création du dossier data...")
        os.makedirs(DATA_DIR, exist_ok=True)

        # Créer un DataFrame exemple si le fichier n'existe pas
        sample_data = {
            "Nom": ["Jean Dupont", "Marie Curie", "Pierre Martin"],
            "Student_ID": ["PSPS001", "PSPS002", "PSPS003"],
            "Email": ["jean@example.com", "marie@example.com", "pierre@example.com"],
            "Date": ["2024-01-15", "2024-01-16", "2024-01-17"],
            "Programme": ["Politiques Publiques et Leadership", "Développement Durable", "Développement International Saemaul"],
            "Semestre": ["semestre 1", "semestre 2", "semestre 1"],
            "Promotion": ["2023", "2023", "2024"],
            "Score Global": [75.5, 82.3, 68.9],
            "Leadership Stratégique": [80, 85, 70],
            "Communication Efficace": [75, 80, 65],
            "Gestion du Temps": [70, 85, 75],
            "Initiative et Autonomie": [80, 75, 60],
            "Gestion des Conflits": [65, 90, 70],
            "Travail d'Équipe": [85, 80, 75],
            "Adaptabilité": [70, 85, 65],
            "Développement Personnel": [75, 80, 70],
            "Éthique et Responsabilité": [90, 85, 80],
            "Prise de Décision": [65, 80, 60],
            "Gestion du Stress": [70, 75, 65],
            "Innovation et Créativité": [80, 85, 70]
        }

        df = pd.DataFrame(sample_data)
        df.to_csv(CSV_FILE, index=False, encoding='utf-8')
        st.info("📋 Fichier d'exemple créé avec des données de démonstration")

    try:
        df = pd.read_csv(CSV_FILE, encoding='utf-8')

        # Nettoyage des données
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

        if "Semestre" in df.columns:
            df["Semestre"] = df["Semestre"].astype(str)

        return df

    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {e}")
        return pd.DataFrame()


def check_data_quality(df):
    """
    Vérifie la qualité des données et affiche des statistiques.
    """
    if df.empty:
        return

    with st.expander("🔍 Qualité des données"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Nombre d'étudiants", df["Nom"].nunique())

        with col2:
            st.metric("Nombre d'évaluations", len(df))

        with col3:
            completeness = (1 - df.isnull().sum().sum() /
                            (df.shape[0] * df.shape[1])) * 100
            st.metric("Complétude", f"{completeness:.1f}%")

        with col4:
            st.metric("Dernière mise à jour", df["Date"].max().strftime(
                "%Y-%m-%d") if "Date" in df.columns else "N/A")


def admin_dashboard(df):
    """
    Dashboard administratif complet.
    """
    st.title("📊 Dashboard Administratif - Évaluations Leadership PSPS")

    # Vérification des données
    if df.empty:
        st.warning(
            "⚠️ Aucune donnée disponible. Le fichier d'exemple a été créé.")
        return

    # Métriques globales
    st.subheader("📈 Vue d'ensemble")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_score = df["Score Global"].mean()
        st.metric("Score Moyen Global", f"{avg_score:.1f}/100")

    with col2:
        total_students = df["Nom"].nunique()
        st.metric("Nombre d'Étudiants", total_students)

    with col3:
        total_evaluations = len(df)
        st.metric("Total des Évaluations", total_evaluations)

    with col4:
        best_score = df["Score Global"].max()
        st.metric("Meilleur Score", f"{best_score:.1f}/100")

    # Menu principal
    st.sidebar.title("🧭 Navigation")
    menu_option = st.sidebar.radio(
        "Sélectionnez une vue :",
        [
            "🏠 Tableau de bord",
            "📊 Analyse par promotion",
            "👤 Suivi individuel",
            "📈 Comparaison programmes",
            "📤 Export des données",
            "🏅 Classements"
        ]
    )

    # Liste des compétences
    competences = [
        "Leadership Stratégique", "Communication Efficace", "Gestion du Temps",
        "Initiative et Autonomie", "Gestion des Conflits", "Travail d'Équipe",
        "Adaptabilité", "Développement Personnel", "Éthique et Responsabilité",
        "Prise de Décision", "Gestion du Stress", "Innovation et Créativité"
    ]

    if menu_option == "🏠 Tableau de bord":
        show_dashboard_overview(df, competences)

    elif menu_option == "📊 Analyse par promotion":
        show_promotion_analysis(df, competences)

    elif menu_option == "👤 Suivi individuel":
        show_individual_tracking(df, competences)

    elif menu_option == "📈 Comparaison programmes":
        show_program_comparison(df, competences)

    elif menu_option == "📤 Export des données":
        show_data_export(df)

    elif menu_option == "🏅 Classements":
        show_rankings(df)


def show_dashboard_overview(df, competences):
    """
    Affiche le tableau de bord principal.
    """
    st.header("🏠 Vue d'ensemble")

    # Filtres
    col1, col2, col3 = st.columns(3)

    with col1:
        programmes = ["Tous"] + df["Programme"].unique().tolist()
        selected_programme = st.selectbox("🎓 Programme", programmes)

    with col2:
        semestres = ["Tous"] + sorted(df["Semestre"].unique().tolist())
        selected_semestre = st.selectbox("📚 Semestre", semestres)

    with col3:
        promotions = ["Toutes"] + sorted(df["Promotion"].unique().tolist())
        selected_promotion = st.selectbox("🎯 Promotion", promotions)

    # Application des filtres
    filtered_df = df.copy()

    if selected_programme != "Tous":
        filtered_df = filtered_df[filtered_df["Programme"]
                                  == selected_programme]

    if selected_semestre != "Tous":
        filtered_df = filtered_df[filtered_df["Semestre"] == selected_semestre]

    if selected_promotion != "Toutes":
        filtered_df = filtered_df[filtered_df["Promotion"]
                                  == selected_promotion]

    # Graphiques principaux
    col1, col2 = st.columns(2)

    with col1:
        # Distribution des scores globaux
        fig = px.histogram(
            filtered_df,
            x="Score Global",
            nbins=20,
            title="Distribution des Scores Globaux",
            color_discrete_sequence=['#3366CC']
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Scores moyens par compétence
        comp_scores = filtered_df[competences].mean(
        ).sort_values(ascending=True)

        fig = px.bar(
            x=comp_scores.values,
            y=comp_scores.index,
            orientation='h',
            title="Scores Moyens par Compétence",
            color=comp_scores.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Évolution temporelle
    if "Date" in filtered_df.columns and len(filtered_df) > 1:
        st.subheader("📅 Évolution temporelle")

        timeline_df = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))[
            "Score Global"].mean().reset_index()
        timeline_df["Date"] = timeline_df["Date"].astype(str)

        fig = px.line(
            timeline_df,
            x="Date",
            y="Score Global",
            title="Évolution du Score Global dans le temps",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)


def show_promotion_analysis(df, competences):
    """
    Analyse détaillée par promotion.
    """
    st.header("📊 Analyse par Promotion")

    # Sélection de la promotion
    promotions = df["Promotion"].unique()
    selected_promotions = st.multiselect(
        "Sélectionnez les promotions à comparer :",
        promotions,
        default=promotions[:2] if len(promotions) >= 2 else promotions
    )

    if not selected_promotions:
        st.warning("Veuillez sélectionner au moins une promotion.")
        return

    filtered_df = df[df["Promotion"].isin(selected_promotions)]

    # Graphique de comparaison
    fig = go.Figure()

    for promotion in selected_promotions:
        promo_data = filtered_df[filtered_df["Promotion"] == promotion]
        comp_means = promo_data[competences].mean()

        fig.add_trace(go.Scatterpolar(
            r=comp_means.values,
            theta=comp_means.index,
            fill='toself',
            name=f"Promotion {promotion}"
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Comparaison des Compétences par Promotion",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tableau détaillé
    st.subheader("📋 Statistiques détaillées")

    stats_df = filtered_df.groupby("Promotion")[
        competences + ["Score Global"]].agg(['mean', 'std', 'count']).round(2)
    st.dataframe(stats_df, use_container_width=True)


def show_individual_tracking(df, competences):
    """
    Suivi individuel des étudiants.
    """
    st.header("👤 Suivi Individuel")

    # Sélection de l'étudiant
    students = df["Nom"].unique()
    selected_student = st.selectbox("Sélectionnez un étudiant :", students)

    if not selected_student:
        return

    student_data = df[df["Nom"] == selected_student].sort_values("Date")

    if student_data.empty:
        st.warning("Aucune donnée pour cet étudiant.")
        return

    # Informations de l'étudiant
    col1, col2, col3 = st.columns(3)

    with col1:
        latest_record = student_data.iloc[-1]
        st.metric("Programme", latest_record["Programme"])

    with col2:
        st.metric("Promotion", latest_record["Promotion"])

    with col3:
        latest_score = latest_record["Score Global"]
        st.metric("Dernier Score", f"{latest_score:.1f}/100")

    # Graphique d'évolution
    st.subheader("📈 Évolution des performances")

    if len(student_data) > 1:
        fig = go.Figure()

        # Score global
        fig.add_trace(go.Scatter(
            x=student_data["Date"],
            y=student_data["Score Global"],
            mode='lines+markers',
            name='Score Global',
            line=dict(color='blue', width=3)
        ))

        # Compétences principales
        main_competences = competences[:4]  # Premières 4 compétences
        colors = ['red', 'green', 'orange', 'purple']

        for i, comp in enumerate(main_competences):
            fig.add_trace(go.Scatter(
                x=student_data["Date"],
                y=student_data[comp],
                mode='lines+markers',
                name=comp,
                line=dict(color=colors[i], width=2, dash='dot')
            ))

        fig.update_layout(
            title=f"Évolution des performances - {selected_student}",
            xaxis_title="Date",
            yaxis_title="Score",
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    # Détail des dernières évaluations
    st.subheader("📋 Détail des évaluations")
    st.dataframe(student_data, use_container_width=True)


def show_program_comparison(df, competences):
    """
    Comparaison entre les programmes.
    """
    st.header("📈 Comparaison des Programmes")

    # Graphique de comparaison
    program_scores = df.groupby("Programme")[
        competences + ["Score Global"]].mean()

    fig = px.bar(
        program_scores.reset_index(),
        x="Programme",
        y="Score Global",
        title="Score Global Moyen par Programme",
        color="Score Global",
        color_continuous_scale="Viridis"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Heatmap des compétences
    st.subheader("🎯 Profil des compétences par programme")

    comp_by_program = df.groupby("Programme")[competences].mean()

    fig = px.imshow(
        comp_by_program.T,
        aspect="auto",
        color_continuous_scale="Viridis",
        title="Heatmap des Compétences par Programme"
    )

    st.plotly_chart(fig, use_container_width=True)


def show_data_export(df):
    """
    Export des données.
    """
    st.header("📤 Export des Données")

    # Options d'export
    export_format = st.radio(
        "Format d'export :",
        ["CSV", "Excel", "JSON"]
    )

    # Filtres pour l'export
    st.subheader("🔧 Options d'export")

    col1, col2 = st.columns(2)

    with col1:
        include_columns = st.multiselect(
            "Colonnes à inclure :",
            df.columns.tolist(),
            default=df.columns.tolist()
        )

    with col2:
        # Filtre par date si disponible
        if "Date" in df.columns:
            min_date = df["Date"].min()
            max_date = df["Date"].max()

            date_range = st.date_input(
                "Période :",
                [min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )

    # Préparation des données
    export_df = df[include_columns]

    if "Date" in df.columns and len(date_range) == 2:
        start_date, end_date = date_range
        export_df = export_df[
            (export_df["Date"] >= pd.Timestamp(start_date)) &
            (export_df["Date"] <= pd.Timestamp(end_date))
        ]

    # Boutons d'export
    col1, col2, col3 = st.columns(3)

    with col1:
        if export_format == "CSV":
            csv_data = export_df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv_data,
                file_name="evaluations_psps.csv",
                mime="text/csv"
            )

    with col2:
        if export_format == "Excel":
            excel_data = export_df.to_excel(index=False, engine='openpyxl')
            st.download_button(
                label="📥 Télécharger Excel",
                data=excel_data,
                file_name="evaluations_psps.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with col3:
        if export_format == "JSON":
            json_data = export_df.to_json(
                indent=2, orient='records', force_ascii=False)
            st.download_button(
                label="📥 Télécharger JSON",
                data=json_data,
                file_name="evaluations_psps.json",
                mime="application/json"
            )

    # Aperçu des données
    st.subheader("👀 Aperçu des données")
    st.dataframe(export_df, use_container_width=True)

    # Statistiques de l'export
    st.metric("Nombre de lignes exportées", len(export_df))
    st.metric("Nombre de colonnes", len(export_df.columns))


def show_rankings(df):
    """
    Classements des étudiants.
    """
    st.header("🏅 Classements")

    # Classement par score global
    st.subheader("📊 Classement par Score Global")

    ranking_df = df.groupby("Nom").agg({
        "Score Global": "mean",
        "Programme": "first",
        "Promotion": "first"
    }).reset_index()

    ranking_df = ranking_df.sort_values("Score Global", ascending=False)
    ranking_df["Rang"] = range(1, len(ranking_df) + 1)

    # Affichage anonymisé optionnel
    show_anonymous = st.checkbox("Afficher de manière anonyme", value=True)

    if show_anonymous:
        display_df = ranking_df.copy()
        display_df["Nom"] = [
            f"Étudiant #{i:03d}" for i in range(1, len(display_df) + 1)]
    else:
        display_df = ranking_df

    # Top 10
    st.subheader("🎖️ Top 10")
    top_10 = display_df.head(10)

    fig = px.bar(
        top_10,
        x="Score Global",
        y="Nom",
        orientation='h',
        title="Top 10 des étudiants",
        color="Score Global",
        color_continuous_scale="Viridis"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tableau complet
    st.subheader("📋 Classement complet")
    st.dataframe(
        display_df[["Rang", "Nom", "Score Global", "Programme", "Promotion"]],
        use_container_width=True
    )


def main():
    """
    Fonction principale.
    """
    # Chargement des données
    df = load_data()

    # Vérification de la qualité des données
    check_data_quality(df)

    # Dashboard principal
    admin_dashboard(df)

    # Pied de page
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**PSPS Leadership Assessment**\n\n"
        "Dashboard administratif pour le suivi des évaluations de leadership."
    )


if __name__ == "__main__":
    main()

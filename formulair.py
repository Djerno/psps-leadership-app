import streamlit as st
from datetime import date
import tempfile
import os
import pycountry
from dotenv import load_dotenv

from translations import translations
from generate_student_pdf import generate_student_pdf
# Assurez-vous que la fonction existe bien dans send_email.py
# Corrigez le nom si besoin, par exemple: send_email
from send_email import send_email_with_pdf

load_dotenv()  # Charge les variables mail.env

# === Langues disponibles ===
LANGUAGES = {
    "Français": "fr",
    "English": "en",
    "한국어": "ko",
    "中文": "zh",
    "Tiếng Việt": "vi",
    "Bahasa Indonesia": "id"
}

# === PAGE CONFIG ===
st.set_page_config(page_title="Évaluation Leadership", layout="centered")

# === LANGUE ===
selected_language_label = st.selectbox(
    "🌐 Choisissez votre langue / Select your language", list(LANGUAGES.keys()))
lang_code = LANGUAGES[selected_language_label]
texts = translations.get(lang_code, translations["fr"])

st.title(texts["title"])

# === CONSENTEMENT - DOIT ÊTRE VISIBLE TOUT DE SUITE ===
st.markdown(f"### {texts['consent_title']}")
st.markdown(texts["consent_text"])
consent = st.checkbox(texts["consent_checkbox"], value=False)

if not consent:
    st.warning(texts["consent_warning"])
    st.stop()

# === FORMULAIRE ===
with st.form("leadership_form"):
    nom = st.text_input(texts["name_label"])
    student_id = st.text_input(texts["student_id_label"])
    email = st.text_input(texts["email_label"])
    dob = st.date_input(texts["dob_label"], min_value=date(
        1950, 1, 1), max_value=date.today())

    # Pays (liste complète sans discrimination)
    countries = sorted([country.name for country in pycountry.countries])
    country = st.selectbox(texts["country_label"], countries)

    # Programme
    programme = st.selectbox(texts["programme_label"], texts["programmes"])

    # Semestre
    semestre = st.selectbox(texts["semester_label"], texts["semesters"])

    # Promotion (2011 à année en cours)
    current_year = date.today().year
    promotions = [str(y) for y in range(2011, current_year + 1)]
    promotion = st.selectbox(texts["promotion_label"], promotions)

    # Photo - Upload uniquement, caméra déco
    st.markdown(f"**{texts['photo_upload_label']}**")
    photo = st.file_uploader("Photo", type=["png", "jpg", "jpeg"])
    st.markdown(f"_{texts['photo_camera_label']}_")  # décoratif uniquement

    st.markdown("---")
    st.subheader(texts["skills_subheader"])

    competences_scores = {}
    for comp_key, questions in texts["competences"].items():
        st.markdown(f"### {texts['competences_labels'][comp_key]}")
        scores = []
        for q in questions:
            score = st.slider(q, 0, 100, 50, key=f"{comp_key}_{q}")
            scores.append(score)
        competences_scores[comp_key] = sum(scores) / len(scores)

    st.markdown("---")
    mail_option = st.checkbox(texts["mail_option"])

    submitted = st.form_submit_button(texts["submit_button"])

# === TRAITEMENT ===
if submitted:
    pdf_path = None
    try:
        score_global = sum(competences_scores.values()) / \
            len(competences_scores)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf_path = tmp_pdf.name

            # Générer le PDF (le fichier est fermé à ce stade)
            image_file = photo if photo is not None else None
            generate_student_pdf(
                nom=nom,
                student_id=student_id,
                programme=programme,
                semestre=semestre,
                promotion=promotion,
                date=dob.strftime("%Y-%m-%d"),
                competences=competences_scores,
                score_global=score_global,
                pdf_path=pdf_path,
                image_file=image_file,
                historique_df=None,
                lang=lang_code
            )

            # Vérification de l'existence et de la taille du PDF
            if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) < 1000:
                st.error(
                    "❌ Le fichier PDF n'a pas pu être généré correctement. Veuillez réessayer ou contacter l'administrateur.")
            else:
                # Télécharger le PDF
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=texts["download_button_label"],
                        data=f.read(),
                        file_name=f"rapport_{student_id}.pdf",
                        mime="application/pdf"
                    )

                # Envoyer le PDF par email (le fichier est bien fermé et existe)
                if mail_option and email:
                    try:
                        success = send_email_with_pdf(
                            to_email=email,
                            pdf_path=pdf_path
                        )
                        if success:
                            st.success(texts["email_success"])
                        else:
                            st.error(texts.get("email_error",
                                     "Erreur lors de l'envoi de l'email."))
                    except Exception as e:
                        st.error(
                            f"{texts.get('email_error', 'Erreur lors de l\'envoi de l\'email.')}.\nDétail technique : {e}")

    except Exception as e:
        st.error(f"Une erreur inattendue est survenue : {e}")
    finally:
        # Suppression sécurisée du PDF temporaire
        try:
            if pdf_path and os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception:
            pass

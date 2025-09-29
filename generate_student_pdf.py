import os
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import qrcode
from PIL import Image as PILImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from translations import translations

# Chemin du logo - à adapter selon votre structure
LOGO_PATH = "assets/psps_logo.png"

# === UTILS ===


def draw_buffer_image(canvas_obj, img_buffer, x, y, width=None, height=None):
    """
    Insère une image depuis un buffer BytesIO dans le PDF.
    """
    try:
        img_buffer.seek(0)
        pil_img = PILImage.open(img_buffer)

        # Redimensionnement proportionnel si nécessaire
        if width and height:
            # Conserver les proportions
            img_ratio = pil_img.width / pil_img.height
            target_ratio = width / height

            if img_ratio > target_ratio:
                # Image plus large que la cible
                new_width = width
                new_height = width / img_ratio
            else:
                # Image plus haute que la cible
                new_height = height
                new_width = height * img_ratio

            # Centrer l'image
            x_offset = x + (width - new_width) / 2
            y_offset = y + (height - new_height) / 2

            canvas_obj.drawInlineImage(pil_img, x_offset, y_offset,
                                       width=new_width, height=new_height)
        else:
            canvas_obj.drawInlineImage(
                pil_img, x, y, width=width, height=height)

    except Exception as e:
        print(f"[Erreur insertion image] {e}")


def create_radar_chart(data: dict, lang: str = 'fr'):
    """
    Crée un radar chart depuis un dictionnaire {label: score (0-100)}.
    Renvoie un BytesIO (image en mémoire).
    """
    try:
        # Récupérer les textes de traduction
        texts = translations.get(lang, translations['fr'])

        labels = []
        values = []

        # Convertir les clés en labels traduits
        for key, value in data.items():
            # Utiliser competences_labels pour la traduction
            label = texts['competences_labels'].get(key, key)
            labels.append(label)
            values.append(value)

        # Préparer les données pour le radar chart
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]  # Fermer le polygone
        angles += angles[:1]

        # Création du graphique
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        # Plot the data
        ax.plot(angles, values, 'o-', linewidth=2, label='Compétences')
        ax.fill(angles, values, alpha=0.25)

        # Ajouter les labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=10)

        # Configuration de l'axe Y
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
        ax.grid(True)

        # Titre
        ax.set_title('Profil des Compétences en Leadership',
                     size=14, fontweight='bold')

        # Sauvegarde en mémoire
        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='PNG', dpi=150, bbox_inches='tight')
        plt.close(fig)

        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"[Erreur création radar chart] {e}")
        return None


def create_history_chart(df, title="Historique des Scores", lang: str = 'fr'):
    """
    Crée un graphique d'historique depuis un DataFrame.
    DataFrame attendu avec colonnes : 'Semestre' et 'Score Global'.
    """
    try:
        texts = translations.get(lang, translations['fr'])

        fig, ax = plt.subplots(figsize=(10, 5))

        # Vérifier que les colonnes nécessaires existent
        if "Semestre" in df.columns and "Score Global" in df.columns:
            ax.plot(df["Semestre"], df["Score Global"], marker='o',
                    linestyle='-', linewidth=2, markersize=8)

            # Personnalisation
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel(texts.get('semester_label', 'Semestre'), fontsize=12)
            ax.set_ylabel(texts.get('average_score_label',
                          'Score Global'), fontsize=12)
            ax.grid(True, alpha=0.3)

            # Rotation des labels x si nécessaire
            plt.xticks(rotation=45)

            # Ajuster les limites
            y_min = max(0, df["Score Global"].min() - 10)
            y_max = min(100, df["Score Global"].max() + 10)
            ax.set_ylim(y_min, y_max)

        buffer = BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='PNG', dpi=150, bbox_inches='tight')
        plt.close(fig)

        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"[Erreur graphique historique] {e}")
        return None


def create_qr_code(data: str):
    """
    Crée un QR code depuis une chaîne de texte.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"[Erreur QR code] {e}")
        return None

# === FONCTION PRINCIPALE ===


def generate_student_pdf(
    nom: str,
    student_id: str,
    programme: str,
    semestre: str,
    date: str,
    competences: dict,
    score_global: float,
    pdf_path: str,
    image_file=None,
    historique_df=None,
    lang: str = 'fr',
    promotion: str = None
):
    """
    Génère un PDF avec les informations de l'étudiant et ses résultats.
    """
    try:
        # === TRADUCTIONS ===
        texts = translations.get(lang, translations['fr'])

        # === CANVAS INIT ===
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        # === EN-TÊTE ===
        c.setFillColor(colors.HexColor("#004080"))  # Bleu PSPS
        c.rect(0, height - 3*cm, width, 3*cm, fill=True, stroke=False)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height - 2*cm,
                     "Park Chung Hee School of Policy and Saemaul")
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, height - 2.5*cm, "Leadership Assessment Report")

        # === LOGO ===
        if os.path.exists(LOGO_PATH):
            try:
                c.drawImage(LOGO_PATH, width - 4.5*cm, height - 2.7*cm,
                            width=2*cm, height=2*cm, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"[Erreur logo] {e}")

        c.setFillColor(colors.black)

        # === INFORMATIONS ÉTUDIANT ===
        y_cursor = height - 4.5*cm

        # Ligne 1 : Nom et ID
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y_cursor, f"{texts['name_label']}: {nom}")
        c.drawString(10*cm, y_cursor,
                     f"{texts['student_id_label']}: {student_id}")
        y_cursor -= 0.7*cm

        # Ligne 2 : Programme et Semestre
        c.drawString(2*cm, y_cursor,
                     f"{texts['programme_label']}: {programme}")
        c.drawString(10*cm, y_cursor, f"{texts['semester_label']}: {semestre}")
        y_cursor -= 0.7*cm

        # Ligne 3 : Date et Promotion
        c.drawString(2*cm, y_cursor, f"{texts['dob_label']}: {date}")
        if promotion:
            promotion_text = texts.get('promotion_label', 'Promotion')
            c.drawString(10*cm, y_cursor, f"{promotion_text}: {promotion}")
        y_cursor -= 0.7*cm

        # Ligne 4 : Score Global
        c.setFillColor(colors.HexColor("#D32F2F"))  # Rouge pour le score
        score_text = texts.get('average_score_label', 'Score Global')
        c.drawString(2*cm, y_cursor, f"{score_text}: {score_global:.1f}/100")
        c.setFillColor(colors.black)
        y_cursor -= 1*cm

        # === PHOTO ÉTUDIANT ===
        photo_height = 4*cm
        if image_file:
            try:
                if hasattr(image_file, 'read'):
                    # Fichier uploadé (BytesIO)
                    image_file.seek(0)
                    draw_buffer_image(c, image_file, width - 6*cm, y_cursor - photo_height,
                                      width=4*cm, height=photo_height)
                elif os.path.exists(str(image_file)):
                    # Chemin de fichier
                    c.drawImage(str(image_file), width - 6*cm, y_cursor - photo_height,
                                width=4*cm, height=photo_height, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"[Erreur image étudiant] {e}")

        # === RADAR CHART ===
        radar_img = create_radar_chart(competences, lang)
        if radar_img:
            # Vérifier l'espace disponible
            if y_cursor - 15*cm < 2*cm:
                c.showPage()
                y_cursor = height - 3*cm

            # Titre du radar chart
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y_cursor, "Profil des Compétences")
            y_cursor -= 1*cm

            # Insérer le radar chart
            draw_buffer_image(c, radar_img, 2*cm, y_cursor - 14*cm,
                              width=14*cm, height=14*cm)
            y_cursor -= 15*cm

        # === HISTORIQUE (si disponible) ===
        if historique_df is not None and not historique_df.empty:
            if y_cursor - 8*cm < 2*cm:
                c.showPage()
                y_cursor = height - 3*cm

            hist_img = create_history_chart(
                historique_df, "Évolution des Scores", lang)
            if hist_img:
                c.setFont("Helvetica-Bold", 14)
                c.drawString(2*cm, y_cursor, "Historique des Performances")
                y_cursor -= 1*cm

                draw_buffer_image(c, hist_img, 2*cm, y_cursor - 7*cm,
                                  width=16*cm, height=7*cm)
                y_cursor -= 8*cm

        # === PIED DE PAGE ===
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.gray)
        c.drawString(2*cm, 1*cm, f"Généré le {date} • Rapport confidentiel")
        c.drawRightString(width - 2*cm, 1*cm, "PSPS Leadership Assessment")

        # === SAUVEGARDE ===
        c.save()
        print(f"✅ PDF généré avec succès : {pdf_path}")

    except Exception as e:
        print(f"❌ Erreur lors de la génération du PDF : {e}")
        raise

# === FONCTION POUR GÉNÉRER UN RAPPORT SIMPLE (fallback) ===


def generate_simple_pdf(nom, student_id, programme, competences, score_global, pdf_path, lang='fr'):
    """
    Version simplifiée pour fallback en cas d'erreur.
    """
    try:
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4

        texts = translations.get(lang, translations['fr'])

        # En-tête simple
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height - 2*cm, texts['title'])
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, height - 3*cm, f"{texts['name_label']}: {nom}")
        c.drawString(2*cm, height - 4*cm,
                     f"{texts['student_id_label']}: {student_id}")
        c.drawString(2*cm, height - 5*cm,
                     f"{texts['programme_label']}: {programme}")

        # Score
        c.drawString(2*cm, height - 6*cm,
                     f"{texts['average_score_label']}: {score_global:.1f}")

        # Compétences
        y_pos = height - 8*cm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2*cm, y_pos, "Compétences:")
        y_pos -= 0.7*cm

        c.setFont("Helvetica", 10)
        for competence, score in competences.items():
            if y_pos < 2*cm:
                c.showPage()
                y_pos = height - 2*cm

            label = texts['competences_labels'].get(competence, competence)
            c.drawString(3*cm, y_pos, f"{label}: {score:.1f}")
            y_pos -= 0.5*cm

        c.save()
        print(f"✅ PDF simple généré : {pdf_path}")

    except Exception as e:
        print(f"❌ Erreur même avec le PDF simple : {e}")
        raise

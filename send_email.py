import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('mail.env')


def send_email_with_pdf(to_email, pdf_path, subject=None, body=None):
    """
    Envoie un email avec un PDF en pièce jointe.

    Args:
        to_email (str): Email du destinataire
        pdf_path (str): Chemin vers le fichier PDF
        subject (str): Sujet de l'email (optionnel)
        body (str): Corps de l'email (optionnel)

    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Configuration SMTP
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    from_email = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')

    # Vérification des variables d'environnement
    if not from_email or not password:
        error_msg = "Les variables d'environnement EMAIL_USER et EMAIL_PASS doivent être définies dans mail.env"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)

    # Vérification du fichier PDF
    if not os.path.exists(pdf_path):
        error_msg = f"Le fichier PDF n'existe pas : {pdf_path}"
        print(f"❌ {error_msg}")
        raise FileNotFoundError(error_msg)

    # Sujet et corps par défaut
    subject = subject or "Votre rapport d'évaluation PSPS"
    body = body or (
        "Bonjour,\n\n"
        "Veuillez trouver en pièce jointe votre rapport d'évaluation du leadership.\n\n"
        "Cordialement,\nL'équipe PSPS"
    )

    # Création du message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Ajout du fichier PDF en pièce jointe
    try:
        with open(pdf_path, "rb") as f:
            pdf_part = MIMEApplication(f.read(), _subtype="pdf")

        # Nom du fichier pour la pièce jointe
        filename = os.path.basename(pdf_path)
        pdf_part.add_header('Content-Disposition',
                            'attachment', filename=filename)
        msg.attach(pdf_part)
        print(f"✅ Fichier PDF '{filename}' attaché avec succès")

    except Exception as e:
        error_msg = f"Erreur lors de l'ouverture du fichier PDF : {e}"
        print(f"❌ {error_msg}")
        raise

    # Envoi du mail via SMTP
    try:
        print(f"🔗 Connexion au serveur SMTP {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()  # Chiffrement TLS
            server.ehlo()

            print(f"🔐 Authentification avec {from_email}...")
            server.login(from_email, password)

            print(f"📤 Envoi de l'email à {to_email}...")
            server.send_message(msg)

        print(f"✅ Email envoyé avec succès à {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"Échec de l'authentification : {e}"
        print(f"❌ {error_msg}")
        print("💡 Vérifiez votre email et mot de passe dans mail.env")
        return False

    except smtplib.SMTPException as e:
        error_msg = f"Erreur SMTP : {e}"
        print(f"❌ {error_msg}")
        return False

    except Exception as e:
        error_msg = f"Erreur inattendue lors de l'envoi : {e}"
        print(f"❌ {error_msg}")
        return False

# Fonction de test


def test_email_configuration():
    """
    Teste la configuration email sans envoyer de vrai email
    """
    print("🧪 Test de configuration email...")

    from_email = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASS')

    if not from_email or not password:
        print("❌ Variables d'environnement manquantes")
        return False

    print(f"✅ EMAIL_USER: {from_email}")
    print(f"✅ EMAIL_PASS: {'*' * len(password)}")

    # Test de connexion SMTP
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(from_email, password)
            server.quit()

        print("✅ Connexion SMTP réussie")
        return True

    except Exception as e:
        print(f"❌ Échec de la connexion SMTP: {e}")
        return False


if __name__ == "__main__":
    # Mode test
    print("=== TEST CONFIGURATION EMAIL ===")
    if test_email_configuration():
        print("\n🎉 Configuration email OK!")
    else:
        print("\n❌ Problème de configuration détecté")
        print("\n🔧 Solutions possibles :")
        print("1. Vérifiez les variables dans mail.env")
        print("2. Pour Gmail, utilisez un mot de passe d'application")
        print("3. Activez l'accès aux applications moins sécurisées (déconseillé)")
        print("4. Vérifiez votre connexion internet")

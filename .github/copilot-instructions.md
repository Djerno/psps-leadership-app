
# Instructions Copilot pour psps_leadership

## Vue d'ensemble du projet
Ce projet est une application web Streamlit permettant l'auto-évaluation des compétences de leadership par les étudiants de la Park Chung Hee School of Policy and Saemaul (PSPS).

- **Interface principale :** `Formulair.py` implémente le formulaire d'évaluation étudiant avec Streamlit, collectant nom, programme, semestre et six compétences de leadership (notées de 0 à 100).
- **Stockage des données :** Les soumissions sont ajoutées à `data/evaluations.csv` (créé automatiquement si absent). Chaque entrée inclut les métadonnées et les scores.
- **Dépendances :**
  - `streamlit` pour l'interface web
  - `pandas` pour la gestion des données
  - Librairies Python standard : `os`, `datetime`

## Conventions et patterns clés
- **Nom des fichiers :** Le fichier principal est `Formulair.py` (orthographe française). Les autres fichiers peuvent être des brouillons ou versions anciennes.
- **Répertoire de données :** Toutes les données persistantes sont stockées dans le sous-dossier `data/`. S'assurer qu'il existe ou le créer à l'exécution.
- **Structure du formulaire :** Utiliser les widgets Streamlit (`st.text_input`, `st.selectbox`, `st.slider`, `st.button`) pour tous les champs utilisateur.
- **Calcul du score :** Le score global est la moyenne des six compétences, arrondie à deux décimales.
- **Ajout CSV :** Si `evaluations.csv` existe, ajouter les nouvelles lignes sans entête ; sinon, écrire avec entête.
- **Confirmation :** Toujours afficher un retour utilisateur après soumission (ex : `st.success`).

## Bonnes pratiques développeur
- **Lancer localement :**
  ```powershell
  streamlit run Formulair.py
  ```
- **Installer les dépendances :**
  ```powershell
  pip install streamlit pandas
  ```
- **Pas de tests automatisés** ni de scripts de build. Les tests se font manuellement via l'UI Streamlit.

## Conseils spécifiques pour les agents IA
- **Ne pas renommer** `Formulair.py` sauf demande explicite de standardisation.
- **Préserver le mélange français/anglais** dans les libellés UI et les commentaires.
- **Pour ajouter une fonctionnalité :**
  - Utiliser les widgets et retours Streamlit.
  - Stocker les nouvelles données dans le même format CSV, en ajoutant des colonnes si besoin.
- **En cas de refactoring :**
  - Garder la compatibilité avec les données CSV existantes.
  - Conserver l'application en un seul fichier sauf demande de modularisation.

## Exemple : Ajouter une nouvelle compétence
Pour ajouter une compétence (ex : "Gestion du Temps") :
1. Ajouter une entrée dans le dictionnaire `competences` et un `st.slider` correspondant.
2. Vérifier que le calcul du score global inclut la nouvelle compétence.
3. Adapter la logique d'écriture CSV pour inclure la nouvelle colonne.

---

Pour toute question ou modification majeure, consulter le propriétaire du projet.

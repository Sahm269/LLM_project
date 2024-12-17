# LLM_project

## architecture du projet 

```r

LLM-RAG-Recettes/
├── app/                   # Code principal de l'application
│   ├── main.py            # Point d'entrée de l'application (Streamlit)
│   ├── utils/             # Fonctions utilitaires (gestion des données, calculs nutritionnels)
│   ├── components/        # Composants spécifiques pour l'interface
├── database/              # Scripts et modèles pour la base de données
│   ├── schema.sql         # Schéma de la base de données
│   ├── seed_data.sql      # Données initiales pour la base
│   └── queries/           # Requêtes SQL organisées par fonction
├── scraping/              # Scripts pour le scraping des recettes
│   ├── marmiton_scraper.py
│   ├── sainplement_scraper.py
│   └── data/              # Données collectées (format JSON/CSV)
├── models/                # Gestion des modèles de LLM
│   ├── prompt_templates/  # Modèles de prompts pour la génération
│   ├── memory/            # Gestion de la mémoire des interactions
│   └── rag_pipeline.py    # Implémentation de la logique RAG
├── security/              # Scripts et tests liés à la sécurité
│   ├── input_validation.py
│   ├── tests/             # Tests unitaires pour la sécurité
├── tests/                 # Tests pour l'ensemble de l'application
│   ├── test_app.py        # Tests de l'interface utilisateur
│   ├── test_models.py     # Tests des modèles LLM
│   └── test_scraping.py   # Tests des scripts de scraping
├── docs/                  # Documentation
│   ├── requirements.txt   # Dépendances Python
│   ├── architecture.md    # Description de l'architecture du projet
│   └── user_guide.md      # Guide utilisateur
├── config/                # Fichiers de configuration
│   ├── settings.yaml      # Configuration globale
│   ├── database.yaml      # Configuration de la base de données
├── Dockerfile             # Fichier pour créer une image Docker
├── .gitignore             # Fichiers/dossiers à ignorer par Git
└── README.md              # Description du projet

```

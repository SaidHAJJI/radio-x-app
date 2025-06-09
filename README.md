# LLM Local avec Apprentissage Continu (Simulation)

## Description Courte

Ce projet simule un pipeline pour un Modèle de Langage Large (LLM) local (TinyLlama 1.1B) capable d'apprentissage continu (fine-tuning) et d'utilisation d'une base de connaissances externe via RAG (Retrieval Augmented Generation) avec ChromaDB. L'objectif est de permettre au LLM de répondre à des questions en utilisant des informations stockées et potentiellement d'intégrer de nouvelles connaissances via un processus de fine-tuning. Ce projet a été développé dans un environnement GitHub Codespaces et est conscient des limitations de ressources de cet environnement, notamment pour la phase de fine-tuning.

## Structure des Fichiers

*   `test_model.py`: Charge et teste le modèle LLM de base (TinyLlama) pour s'assurer qu'il fonctionne.
*   `knowledge_base.py`: Gère la création, l'ajout de documents et l'interrogation d'une base de connaissances vectorielle persistante en utilisant ChromaDB.
*   `rag_module.py`: Implémente la logique RAG. Il utilise le LLM (TinyLlama) et le retriever ChromaDB pour générer des réponses augmentées par le contexte de la base de connaissances.
*   `cli_app.py`: Fournit une interface en ligne de commande (CLI) pour interagir avec le système. Permet de poser des questions, d'ajouter des documents à ChromaDB, de fournir des données pour l'apprentissage, et de lancer le processus de fine-tuning.
*   `fine_tune_model.py`: Script pour tenter de fine-tuner le modèle LLM TinyLlama avec les données textuelles fournies. Ce script est configuré pour s'exécuter sur CPU et est fortement limité par les ressources disponibles.
*   `learning_data.txt`: Fichier texte où sont stockées les phrases ou paragraphes fournis par l'utilisateur en vue du fine-tuning. Chaque nouvelle entrée est ajoutée à la suite.
*   `requirements.txt`: Liste toutes les dépendances Python nécessaires pour le projet.
*   `chroma_db_store/`: Répertoire où ChromaDB stocke ses données vectorielles persistantes.
*   `tinyllama_finetuned/`: Répertoire où le script `fine_tune_model.py` tentera de sauvegarder le modèle fine-tuné.

## Installation

1.  **Cloner le dépôt** (si vous ne l'avez pas déjà fait).
2.  **Environnement**: Assurez-vous d'être dans un environnement GitHub Codespaces ou un environnement Python 3.8+ local. Pour le fine-tuning, un environnement avec une RAM significativement élevée (>16GB, idéalement plus) est nécessaire.
3.  **Installer les dépendances**:
    ```bash
    pip install -r requirements.txt
    ```

## Lancement de l'Application

Pour démarrer l'interface en ligne de commande, exécutez :
```bash
python cli_app.py
```

## Utilisation de la CLI

L'application CLI vous présentera un menu avec les options suivantes :

*   **"1. Poser une question"**:
    Permet à l'utilisateur de poser une question. Le système utilisera le RAG (TinyLlama + ChromaDB) pour tenter de fournir une réponse basée sur les informations de la base de connaissances.

*   **"2. Ajouter une connaissance (ChromaDB)"**:
    Permet à l'utilisateur d'ajouter un nouveau morceau d'information (un document texte) à la base de connaissances ChromaDB. Un ID unique sera demandé ou généré.

*   **"3. Fournir des données pour l'apprentissage (fichier learning_data.txt)"**:
    Permet à l'utilisateur de saisir une phrase ou un petit paragraphe qui sera ajouté au fichier `learning_data.txt`. Ces données sont destinées à être utilisées par le processus de fine-tuning.

*   **"4. Mettre à jour le modèle avec les nouvelles données (fine-tuning)"**:
    Lance le script `fine_tune_model.py`. Ce script tentera de fine-tuner le modèle TinyLlama en utilisant toutes les données accumulées dans `learning_data.txt`.

*   **"5. Quitter"**:
    Ferme l'application CLI.

## Apprentissage Continu (Fine-tuning)

L'option "4. Mettre à jour le modèle..." dans la CLI est conçue pour initier le processus de fine-tuning du modèle LLM.

*   Elle exécute le script `fine_tune_model.py`.
*   Ce script charge le modèle TinyLlama 1.1B de base, lit les données depuis `learning_data.txt`, et tente un fine-tuning de type "continuer à pré-entraîner".

*   **AVERTISSEMENT IMPORTANT SUR LES RESSOURCES :**
    Le fine-tuning d'un modèle comme TinyLlama 1.1B, même avec des configurations minimales sur CPU, est extrêmement gourmand en mémoire (RAM) et en temps de calcul. Dans un environnement GitHub Codespaces standard (par exemple, 2-4 cœurs CPU, 8-16GB RAM), **ce processus sera très probablement interrompu par le système d'exploitation (erreur "Killed" ou similaire) en raison d'une mémoire insuffisante.** Un environnement avec significativement plus de RAM (>32GB serait préférable) et idéalement un GPU compatible CUDA est requis pour espérer un fine-tuning réussi.

*   **Utilisation du modèle fine-tuné (si réussi) :**
    Si le fine-tuning parvenait à son terme (ce qui est improbable dans Codespaces sans ressources supplémentaires), le modèle serait sauvegardé dans le répertoire `tinyllama_finetuned/`. Pour que l'application CLI (et donc `rag_module.py`) utilise ce nouveau modèle, vous devriez **manuellement** modifier la variable `MODEL_NAME` (ou équivalent) dans `rag_module.py` (et potentiellement `test_model.py` ou `cli_app.py` aux endroits où le modèle de base est chargé) pour qu'elle pointe vers `"./tinyllama_finetuned/"` au lieu de `"TinyLlama/TinyLlama-1.1B-Chat-v1.0"`. Après cette modification, l'application devrait être redémarrée. Une gestion dynamique du chemin du modèle n'est pas implémentée dans cette version.

## Limitations Connues

*   **Qualité des réponses du LLM**: TinyLlama 1.1B est un modèle relativement petit. Ses réponses peuvent être verbeuses, incomplètes, ou ne pas toujours suivre parfaitement les instructions du prompt (par exemple, l'instruction de dire "je ne sais pas" lorsque l'information n'est pas dans le contexte fourni par RAG).
*   **Fine-tuning dans Codespaces**: Comme mentionné ci-dessus, le fine-tuning est pratiquement irréalisable dans un Codespaces standard en raison des limitations de RAM. Les scripts sont fournis à titre de démonstration du pipeline.
*   **Tests CLI automatisés**: L'interactivité de la CLI (`input()`) n'a pas pu être testée via les outils d'automatisation disponibles dans cet environnement de développement, qui ont provoqué des erreurs `EOFError`. Les fonctionnalités sous-jacentes ont été testées via des appels de scripts directs lorsque possible.
*   **Propagation des ID de documents sources**: L'ID des documents récupérés par le RAG et affiché dans la CLI peut apparaître comme "N/A" en raison de la manière dont les métadonnées sont gérées entre ChromaDB et l'intégration LangChain utilisée. Le contenu du document est cependant correctement récupéré.

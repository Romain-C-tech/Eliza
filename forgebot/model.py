"""
ml_model.py — Intent classification model using scikit-learn.
Replaces the LLM with a real ML model trained on labeled data.
"""

import json
import pickle
import os
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


# Constants

MODEL_PATH = "forgebot_model.pkl"


#Training Dataset 
# Format: (user input text, intent label)
# The more examples provided, the better the model will perform.

TRAINING_DATA = {

    # Server type 
    "server_type": [
        # Gaming
        ("gaming", "gaming"),
        ("jeu", "gaming"),
        ("jeux vidéo", "gaming"),
        ("je veux jouer", "gaming"),
        ("pour jouer avec mes amis", "gaming"),
        ("un serveur pour gamer", "gaming"),
        ("on joue ensemble", "gaming"),
        ("fps stratégie moba", "gaming"),
        ("minecraft fortnite valorant", "gaming"),
        ("esport compétition tournoi", "gaming"),
        ("clan guilde équipe gaming", "gaming"),
        ("streamer twitch youtube gaming", "gaming"),
        ("serveur de jeu", "gaming"),
        ("pour les gamers", "gaming"),
        ("communauté gaming", "gaming"),

        # School
        ("école", "école"),
        ("scolaire", "école"),
        ("classe", "école"),
        ("promo", "école"),
        ("étudiants", "école"),
        ("université fac", "école"),
        ("lycée collège", "école"),
        ("cours devoirs", "école"),
        ("pour ma classe", "école"),
        ("groupe de travail scolaire", "école"),
        ("révisions examens bac", "école"),
        ("entraide scolaire", "école"),
        ("master licence BTS", "école"),
        ("école ingénieur", "école"),
        ("communauté étudiante", "école"),

        # Professional community / business
        ("business", "communauté"),
        ("entreprise", "communauté"),
        ("travail", "communauté"),
        ("startup", "communauté"),
        ("équipe pro", "communauté"),
        ("collègues professionnels", "communauté"),
        ("réunion projet", "communauté"),
        ("télétravail remote", "communauté"),
        ("agence boite société", "communauté"),
        ("communication interne", "communauté"),
        ("collaborer avec mon équipe", "communauté"),
        ("freelance clients", "communauté"),
        ("gestion de projet", "communauté"),
        ("productivité organisation", "communauté"),
        ("serveur pro", "communauté"),
        ("communauté", "communauté"),
        ("fans", "communauté"),
        ("passion hobby", "communauté"),
        ("groupe de personnes", "communauté"),
        ("réseau social", "communauté"),
        ("rassemblement rencontres", "communauté"),
        ("association club", "communauté"),
        ("forum discussion", "communauté"),
        ("partage intérêts communs", "communauté"),
        ("amis proches", "communauté"),
        ("serveur général", "communauté"),
        ("art musique littérature", "communauté"),
        ("anime manga lecture", "communauté"),
        ("cinéma films séries", "communauté"),
        ("sport fitness", "communauté"),
    ],

    # Confirmation (yes / no) 
    "confirmation": [
        ("oui", "yes"),
        ("yes", "yes"),
        ("ouais", "yes"),
        ("yep", "yes"),
        ("ok", "yes"),
        ("d'accord", "yes"),
        ("confirme", "yes"),
        ("c'est bon", "yes"),
        ("allons-y", "yes"),
        ("go", "yes"),
        ("parfait", "yes"),
        ("super", "yes"),
        ("let's go", "yes"),
        ("je confirme", "yes"),
        ("validé", "yes"),

        ("non", "no"),
        ("no", "no"),
        ("nope", "no"),
        ("annuler", "no"),
        ("cancel", "no"),
        ("recommencer", "no"),
        ("pas comme ça", "no"),
        ("je veux changer", "no"),
        ("c'est pas ça", "no"),
        ("modifier", "no"),
    ],

    #Special channels (yes / no / list)
    "special_channels": [
        ("non", "none"),
        ("aucun", "none"),
        ("rien", "none"),
        ("pas besoin", "none"),
        ("no", "none"),
        ("c'est bon comme ça", "none"),
        ("skip", "none"),
        ("passer", "none"),

        ("oui", "has_channels"),
        ("yes", "has_channels"),
        ("j'ai besoin de", "has_channels"),
        ("ajoute", "has_channels"),
        ("je veux aussi", "has_channels"),
        ("met aussi", "has_channels"),
        ("tournois clips memes", "has_channels"),
        ("homework ressources", "has_channels"),
        ("projets réunion", "has_channels"),
        ("fan-art showcase", "has_channels"),
        ("recrutement", "has_channels"),
    ],

    # Server size
    "member_count": [
        ("petit", "small"),
        ("peu de monde", "small"),
        ("entre amis", "small"),
        ("moins de 50", "small"),
        ("juste nous", "small"),
        ("une dizaine", "small"),
        ("20 personnes", "small"),
        ("5 membres", "small"),
        ("intime", "small"),
        ("une vingtaine de personnes", "small"),
        ("on est peu", "small"),
        ("juste quelques amis", "small"),
        ("petit groupe", "small"),
        ("moins de 20", "small"),
        ("on est 10", "small"),
        ("quelques personnes", "small"),
        ("5 à 10 membres", "small"),
        ("entre amis proches", "small"),
        ("petit cercle", "small"),
        ("une dizaine d'amis", "small"),
        ("pas beaucoup de monde", "small"),
        (0, "small"),
        (10, "small"),
        (20, "small"),
        (30, "small"),
        (40, "small"),
        (1, "small"),
        (2, "small"),
        (3, "small"),
        (4, "small"),
        (5, "small"),
        (6, "small"),
        (7, "small"),
        (8, "small"),
        (9, "small"),
        (11, "small"),
        (15, "small"),
        (25, "small"),
        (12, "small"),
        (13, "small"),
        (14, "small"),
        (16, "small"),
        (17, "small"),
        (18, "small"),
        (19, "small"),
        (21, "small"),
        (22, "small"),
        (23, "small"),
        (24, "small"),
        (26, "small"),
        (27, "small"),
        (28, "small"),
        (29, "small"),
        (31, "small"),
        (35, "small"),
        (32, "small"),
        (33, "small"),
        (34, "small"),
        (36, "small"),
        (37, "small"),
        (38, "small"),
        (39, "small"),
        (41, "small"),
        (42, "small"),
        (43, "small"),
        (44, "small"),
        (45, "small"),
        (46, "small"),
        (47, "small"),
        (48, "small"),
        (49, "small"),

        ("moyen", "medium"),
        ("50 à 200", "medium"),
        ("une centaine", "medium"),
        ("100 membres", "medium"),
        ("quelques dizaines", "medium"),
        ("150 personnes environ", "medium"),
        ("ma promo 80 élèves", "medium"),
        ("environ 100 personnes", "medium"),
        ("une centaine", "medium"),
        ("entre 50 et 150", "medium"),
        ("80 élèves", "medium"),
        ("quelques dizaines", "medium"),
        ("une centaine de membres", "medium"),

        ("grand", "large"),
        ("beaucoup", "large"),
        ("plus de 200", "large"),
        ("grande communauté", "large"),
        ("500 membres", "large"),
        ("ouvert au public", "large"),
        ("on va scaler", "large"),
        ("milliers", "large"),
        ("plusieurs centaines", "large"),
        ("ouvert au public", "large"),
        ("plus de 500", "large"),
        ("milliers de membres", "large"),
        ("très grande communauté", "large"),
        ("serveur public", "large"),
    ],
}


# Predefined step responses

RESPONSES = {
    "step_1_ask": (
        "👋 **What kind of server do you want to create?**\n\n"
        "🎮 `gaming` — To play with your community\n"
        "🎓 `école` — For your class or cohort\n"
        "👥 `communauté` — For a group around a shared passion\n\n"
        "*You can also write freely, I'll understand!*"
    ),
    "step_1_unknown": (
        "I didn't quite understand. Try describing your server differently!\n"
        "For example: *'to play with my friends'*, *'my final year class'*, *'my work team'*..."
    ),
    "step_2_ask": "Great! **What do you want to name your server?** ",
    "step_3_ask": (
        "How many members are you expecting approximately? 👥\n\n"
        "• `small` — fewer than 50\n"
        "• `medium` — 50 to 200\n"
        "• `large` — more than 200"
    ),
    "step_4_ask": (
        "Do you have any **special channels** to include? 📺\n"
        "*(e.g. tournaments, clips, homework, projects...)*\n\n"
        "Otherwise type `no` to skip."
    ),
    "step_5_confirm_yes": "Let's go! Building your server...",
    "step_5_confirm_no": "Ok, cancelled. Type `/setup` to start over!",
    "step_5_unknown": "Reply with `yes` to confirm or `no` to cancel.",
}


# Intent Classifier 

class IntentClassifier:
    """
    Intent classifier based on TF-IDF and Logistic Regression.
    Trains one model per intent type (server_type, confirmation, etc.).
    """

    def __init__(self):
        """Initialize the classifier with an empty model registry."""
        self.models: dict[str, Pipeline] = {}

    def _build_pipeline(self) -> Pipeline:
        """
        Build a TF-IDF + Logistic Regression pipeline.

        Returns:
            Pipeline: A scikit-learn pipeline ready to be fitted.
        """
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                analyzer="char_wb",  # Character n-grams: robust to typos and abbreviations
                ngram_range=(2, 4),
                max_features=5000,
                sublinear_tf=True,
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=5.0,
                solver="lbfgs",
            ))
        ])

    def train(self):
        """
        Train one model per intent type using the global TRAINING_DATA.
        Prints a classification report for each model after fitting.
        """
        print("Training ForgeBot model...")
        for intent_name, data in TRAINING_DATA.items():
            texts = [d[0] for d in data]
            labels = [d[1] for d in data]

            # Use a train/test split only when there is enough data and label diversity
            if len(set(labels)) > 1 and len(texts) > 10:
                X_train, X_test, y_train, y_test = train_test_split(
                    texts, labels, test_size=0.2, random_state=42, stratify=labels
                )
            else:
                # Fall back to training and evaluating on the full dataset
                X_train, y_train = texts, labels
                X_test, y_test = texts, labels

            pipeline = self._build_pipeline()
            pipeline.fit(X_train, y_train)

            # Evaluate and display a classification report
            y_pred = pipeline.predict(X_test)
            print(f"\nModel '{intent_name}':")
            print(classification_report(y_test, y_pred, zero_division=0))

            self.models[intent_name] = pipeline

        print("Training complete!")

    def predict(self, intent_name: str, text: str) -> tuple[str, float]:
        """
        Predict the label for a given text under a specific intent model.

        Args:
            intent_name (str): The intent model to use (e.g. 'server_type').
            text (str): The raw user input to classify.

        Returns:
            tuple[str, float]: The predicted label and its confidence score.

        Raises:
            ValueError: If no model exists for the given intent name.
        """
        if intent_name not in self.models:
            raise ValueError(f"Model '{intent_name}' not found.")

        model = self.models[intent_name]
        text = text.lower().strip()

        label = model.predict([text])[0]
        proba = model.predict_proba([text])[0]
        confidence = float(np.max(proba))

        return label, confidence

    def save(self, path: str = MODEL_PATH):
        """
        Serialize and save all trained models to disk.

        Args:
            path (str): File path where the model will be saved. Defaults to MODEL_PATH.
        """
        with open(path, "wb") as f:
            pickle.dump(self.models, f)
        print(f"Model saved to '{path}'")

    def load(self, path: str = MODEL_PATH) -> bool:
        """
        Load previously trained models from disk.

        Args:
            path (str): File path to load the model from. Defaults to MODEL_PATH.

        Returns:
            bool: True if the model was loaded successfully, False if the file does not exist.
        """
        if not os.path.exists(path):
            return False
        with open(path, "rb") as f:
            self.models = pickle.load(f)
        print(f"Model loaded from '{path}'")
        return True


# Global classifier instance

classifier = IntentClassifier()



def load_or_train():
    """
    Load the model from disk if it exists, otherwise train and save a new one.
    Should be called once at startup before any classification is performed.
    """
    if not classifier.load():
        classifier.train()
        classifier.save()


def classify(intent_name: str, text: str, threshold: float = 0.4) -> tuple[str, float]:
    """
    Public interface for classifying a user input text.
    Returns ('unknown', score) if the confidence falls below the threshold.

    Args:
        intent_name (str): The intent model to use (e.g. 'confirmation').
        text (str): The raw user input to classify.
        threshold (float): Minimum confidence score to accept a prediction. Defaults to 0.4.

    Returns:
        tuple[str, float]: The predicted label and confidence score.
                           Returns ('unknown', score) if confidence is below threshold.
    """
    label, confidence = classifier.predict(intent_name, text)
    if confidence < threshold:
        return "unknown", confidence
    return label, confidence


# Standalone training script 

if __name__ == "__main__":
    print("ForgeBot — ML Model Training")
    print("=" * 50)

    classifier.train()
    classifier.save()

    # Run a set of manual tests to verify predictions after training
    tests = [
        ("server_type", "je veux un serveur pour gamer avec mes potes"),
        ("server_type", "c'est pour ma classe de première"),
        ("server_type", "startup avec mon équipe"),
        ("confirmation", "ouais c'est bon go"),
        ("confirmation", "non je veux changer"),
        ("member_count", "on est une vingtaine"),
        ("member_count", "grande communauté ouverte"),
    ]

    for intent, text in tests:
        label, score = classify(intent, text)
        print(f"  '{text}' → {label} ({score:.0%})")
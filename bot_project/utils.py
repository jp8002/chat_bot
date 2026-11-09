from random import choice
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from preprocessing import user_input_cleaning
nltk.download('vader_lexicon', quiet=True)

_GREETING_OPTIONS = (
    "Hello there!\nI am your protocol droid of knowledge. Ask me anything about Star Wars!",
    "Hi! Nice to have you here.\nI know everything about a galaxy far, far away—please ask away!",
    "Welcome to MovieBot.\nMay the Force be with you! What would you like to know about Star Wars?",
    "Greetings, traveler!\nI've traversed the galaxy to answer your questions about the Jedi, Sith, and beyond.",
    "Bounty incoming!\nDrop your Star Wars questions here and let's see what we uncover.",
    "Ah, a visitor!\nStep into the cantina of knowledge. What Star Wars lore can I clear up for you today?",
)

def get_greeting() -> str:
    return choice(_GREETING_OPTIONS)


def analisar_sentimentos(text):
    nltk_classifier = SentimentIntensityAnalyzer()

    cleaned_text = user_input_cleaning(text)
    sentimento = nltk_classifier.polarity_scores(cleaned_text)

    return sentimento
from random import choice

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
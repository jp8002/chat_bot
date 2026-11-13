import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout,
    QScrollArea, QHBoxLayout, QLineEdit, QPushButton, QFrame, QMenu
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer

from preprocessing import preprocessing
from answer import answer
from scrapper import Scrapper
import utils


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cleaned_sentences = []
        self.original_sentences = []
        self.current_mood = "empatico" 

        self.setWindowTitle("Movies ChatBot")
        self.resize(960, 720)
        self.center_window()

        central_container = QWidget()
        self.setCentralWidget(central_container)

        main_layout = QVBoxLayout(central_container)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        header = self.create_header()
        main_layout.addWidget(header)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        self.messagesContainer = QWidget()
        self.messagesContainer.setStyleSheet("background-color: transparent;")
        self.chatLayout = QVBoxLayout(self.messagesContainer)
        self.chatLayout.setAlignment(Qt.AlignTop)
        self.chatLayout.setSpacing(12)
        self.chatLayout.setContentsMargins(14, 14, 14, 14)

        self.scrollArea.setWidget(self.messagesContainer)
        main_layout.addWidget(self.scrollArea, 1)

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask something about Star Wars...")
        self.message_input.returnPressed.connect(self.envioUsuario)

        self.mood_button = QPushButton("Empático ▴")
        self.mood_button.setObjectName("moodButton")
        self.mood_button.setCursor(Qt.PointingHandCursor)
        self.mood_button.clicked.connect(self.show_mood_menu)

        send_button = QPushButton("Send ➤")
        send_button.setObjectName("sendButton")
        send_button.setCursor(Qt.PointingHandCursor)
        send_button.clicked.connect(self.envioUsuario)

        input_layout.addWidget(self.message_input, 1)
        input_layout.addWidget(self.mood_button)
        input_layout.addWidget(send_button)
        main_layout.addLayout(input_layout)

        self.iniciar_bot()

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(max(0, x), max(0, y))

    def create_header(self):
        header = QFrame()
        header.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 10, 14, 10)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        title = QLabel("Movies ChatBot")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #cdd6f4;")
        self.lbl_mood_status = QLabel("Humor: Empático")
        self.lbl_mood_status.setStyleSheet("font-size: 11px; color: #89b4fa;")

        text_layout.addWidget(title)
        text_layout.addWidget(self.lbl_mood_status)
        header_layout.addLayout(text_layout)
        header_layout.addStretch(1)

        online_lbl = QLabel("● Online")
        online_lbl.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(online_lbl)

        return header

    def show_mood_menu(self):
        menu = QMenu(self)

        moods = [
            ("empatico", "Empático"),
            ("formal", "Formal"),
            ("sarcastico", "Sarcástico"),
        ]

        for key, label in moods:
            action = QAction(label, self)
            action.triggered.connect(lambda checked=False, k=key, l=label: self.set_mood(k, l))
            menu.addAction(action)

        menu_size = menu.sizeHint()
        pos = self.mood_button.mapToGlobal(QPoint(0, -menu_size.height() - 6))
        menu.exec(pos)

    def set_mood(self, mood_key, mood_label):
        self.current_mood = mood_key
        self.mood_button.setText(f"{mood_label} ▴")
        clean_name = mood_label.split(" ", 1)[1] if " " in mood_label else mood_label
        self.lbl_mood_status.setText(f"Humor: {clean_name}")

    def iniciar_bot(self):
        base_path = Path("base.txt")
        file_is_empty = not base_path.exists() or not base_path.read_text(encoding='utf-8')

        if file_is_empty:
            Scrapper().findLink(start_url="https://en.wikipedia.org/wiki/Star_Wars_(film)")

        article = base_path.read_text(encoding='utf-8')

        self.original_sentences = [sentence for sentence in nltk.sent_tokenize(article)]
        for sentence in self.original_sentences:
            self.cleaned_sentences.append(preprocessing(sentence))

        self.tfidf = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        self.x_sentences = self.tfidf.fit_transform(self.cleaned_sentences)

        text = utils.get_greeting()
        self.sendMessage(text, user=False)

    def sendMessage(self, text, user=True, sentiment=None):
        message_layout = QHBoxLayout()
        message_layout.setSpacing(10)

        bubble_frame = QFrame()
        bubble_layout = QVBoxLayout(bubble_frame)
        bubble_layout.setContentsMargins(14, 10, 14, 10)
        bubble_layout.setSpacing(4)

        if user:
            top_layout = QHBoxLayout()
            lbl_sender = QLabel("Usuário")
            lbl_sender.setStyleSheet("font-size: 11px; font-weight: bold; color: #b4befe;")
            top_layout.addWidget(lbl_sender)
            top_layout.addStretch(1)

            if sentiment:
                comp = sentiment.get("compound", 0.0)
                if comp >= 0.3:
                    badge_style = "background-color: #2e4d3a; color: #a6e3a1; border-radius: 6px; padding: 2px 6px; font-size: 10px; font-weight: bold;"
                    badge_text = f"Positivo ({comp:+.2f})"
                elif comp <= -0.5:
                    badge_style = "background-color: #4d2e38; color: #f38ba8; border-radius: 6px; padding: 2px 6px; font-size: 10px; font-weight: bold;"
                    badge_text = f"Negativo ({comp:.2f})"
                else:
                    badge_style = "background-color: #3b3c4a; color: #f9e2af; border-radius: 6px; padding: 2px 6px; font-size: 10px; font-weight: bold;"
                    badge_text = f"Neutro ({comp:+.2f})"

                badge_lbl = QLabel(badge_text)
                badge_lbl.setStyleSheet(badge_style)
                top_layout.addWidget(badge_lbl)

            bubble_layout.addLayout(top_layout)

            content_lbl = QLabel(text)
            content_lbl.setWordWrap(True)
            content_lbl.setStyleSheet("color: #ffffff; font-size: 13px;")
            bubble_layout.addWidget(content_lbl)

            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #3e487a;
                    border-radius: 14px;
                    border: 1px solid #4e598c;
                }
            """)
            bubble_frame.setMaximumWidth(650)
        else:
            print(text)
            top_layout = QHBoxLayout()
            lbl_sender = QLabel("Bot")
            lbl_sender.setStyleSheet("font-size: 11px; font-weight: bold; color: #89b4fa;")
            top_layout.addWidget(lbl_sender)
            top_layout.addStretch(1)
            bubble_layout.addLayout(top_layout)

            content_lbl = QLabel(text)
            content_lbl.setWordWrap(True)
            content_lbl.setStyleSheet("color: #cdd6f4; font-size: 13px;")
            bubble_layout.addWidget(content_lbl)

            bubble_frame.setStyleSheet("""
                QFrame {
                    background-color: #24253a;
                    border-radius: 14px;
                    border: 1px solid #313244;
                }
            """)
            bubble_frame.setMaximumWidth(650)
            
            message_layout.addWidget(bubble_frame)
            message_layout.addStretch(1)

        self.chatLayout.addLayout(message_layout)
        QApplication.processEvents()
        self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().maximum()
        )

    def envioUsuario(self):
        user_text = self.message_input.text().strip()
        if not user_text:
            return
        self.message_input.clear()

        sentimento = utils.analisar_sentimentos(user_text)
        compound_score = sentimento.get("compound", 0.0)

        self.sendMessage(user_text, user=True, sentiment=sentimento)
        self.respostaBot(user_text, compound_score=compound_score)

    def respostaBot(self, user_text, compound_score):
        resposta = answer(
            original_sentences=self.original_sentences,
            x_sentences=self.x_sentences,
            user_text=user_text,
            tfidf=self.tfidf
        )

        if self.current_mood == "empatico":
            if compound_score <= -0.5:
                resposta = (
                    "I'm sorry if my previous response seemed vague or unsatisfactory! \n"
                    + resposta
                )
            elif compound_score >= 0.3:
                resposta = (
                    "Thank you for your compliment, I'm here to help! \n"
                    + resposta
                )

        elif self.current_mood == "formal":
            if compound_score <= -0.5:
                resposta = (
                    "We acknowledge your dissatisfaction and apologize for any inconvenience. Here is the requested information:\n"
                    + resposta
                )
            elif compound_score >= 0.3:
                resposta = (
                    "Your positive feedback is appreciated. Please find the relevant details below:\n"
                    + resposta
                )
            else:
                resposta = (
                    "Here is the information retrieved from our database:\n"
                    + resposta
                )

        elif self.current_mood == "sarcastico":
            if compound_score <= -0.5:
                resposta = (
                    "Oh, someone woke up on the Dark Side today... Fine, here is your answer:\n"
                    + resposta
                )
            elif compound_score >= 0.3:
                resposta = (
                    "Flattery will get you everywhere, Padawan. Anyway, here you go:\n"
                    + resposta
                )
            else:
                resposta = (
                    "If you insist on asking something so obvious:\n"
                    + resposta
                )

        self.sendMessage(resposta, user=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    style_path = Path(__file__).parent / "style.qss"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

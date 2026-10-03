from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy
from PySide6.QtCore import Qt
import spacy
from PySide6.QtWidgets import QMessageBox
import nltk
from preprocessing import preprocessing
from answer import answer
from sklearn.feature_extraction.text import TfidfVectorizer
from scrapper import Scrapper



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.cleaned_sentences =[]
        self.nlp = spacy.load("en_core_web_lg")          
        
        self.setWindowTitle("Movies ChatBot")
        
        centralContainer = QWidget()
        self.resize(1920,1200)
        
        self.setCentralWidget(centralContainer)
        mainlayout = QVBoxLayout(centralContainer)

        messagesContainer =QWidget()
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        
        self.chatLayout = QVBoxLayout(messagesContainer)
        self.chatLayout.setAlignment(Qt.AlignTop)
        
        self.scrollArea.setWidget(messagesContainer)
        mainlayout.addWidget(self.scrollArea)
        
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        send_button = QPushButton("Send")
        
        send_button.clicked.connect(self.envioUsuario)
        self.message_input.returnPressed.connect(self.envioUsuario)
                
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_button)
        mainlayout.addLayout(input_layout)
        
        self.iniciar_bot()
        
    def iniciar_bot(self):
        with open("base.txt","r") as f:
            article = f.read()
            
        if article == "":
            Scrapper().findLink(start_url="https://en.wikipedia.org/wiki/Star_Wars_(film)")
            with open("base.txt","r") as f:
                        article = f.read()
            
        self.original_sentences = [sentence for sentence in nltk.sent_tokenize(article)]
        for sentence in self.original_sentences:
                self.cleaned_sentences.append(preprocessing(sentence,self.nlp))
        
        self.tfidf = TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True)
        self.x_sentences = self.tfidf.fit_transform(self.cleaned_sentences)
                
        text = 'Hello! I am a chatbot and I will answer your questions about Star wars'
        self.sendMessage(text,False)
    
    def sendMessage(self,text, user = True):
        message_layout = QHBoxLayout()
        label = QLabel()
        label.setWordWrap(True)
        label.setMaximumWidth(700)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Fixed)

        if user:
            text = "Usuário: " + text
            label.setStyleSheet("background-color:green;color:white; border-radius: 10px; padding:10px;")
            # Empurra a mensagem para a DIREITA
            message_layout.addStretch(1)
            message_layout.addWidget(label,3)


        else:
            text = "Bot: " + text
            label.setStyleSheet("background-color:red;color:white; border-radius: 10px; padding:10px;")
            # Mantém a mensagem na ESQUERDA e empurra o espaço vago para a direita
            message_layout.addWidget(label,3)
            message_layout.addStretch(1)
        
        self.chatLayout.addLayout(message_layout)
        label.setText(text)
        self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().maximum()
        )
    
    def envioUsuario(self):
        user_text = self.message_input.text()
        if not user_text:
            return
        self.sendMessage(user_text)
        self.message_input.clear()
        self.respostaBot(user_text)
    
    def respostaBot(self, user_text):
        resposta = answer(original_sentences=self.original_sentences,x_sentences=self.x_sentences, user_text=user_text, tfidf=self.tfidf)
        self.sendMessage(resposta, False)        
        
app = QApplication()

window = MainWindow()
window.show()

with open("style.qss","r") as f:
    _style = f.read()
    app.setStyleSheet(_style)

app.exec()
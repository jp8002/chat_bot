from answer import answer
from scrapper import Scrapper
import spacy
import en_core_web_lg
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from preprocessing import preprocessing
from rich.progress import Progress
 

def main():
    escolha = input("Você deseja jogar o jogo ou realizar um novo scrapping ante de começar (S/n)").strip().lower()
        
    if escolha in ["s", "sim", ""]:
        url = input("Informe uma URL para começar a raspagem: ")
        scrapper = Scrapper()
        scrapper.findLink(start_url=url)

    with open("base.txt","r") as f:
            article = f.read()
            
    if article == "":
        print("A base de conhecimento está vazia. Necessário realizar a raspagem")
        return
    
    nlp = spacy.load("en_core_web_lg")
    nltk.download("punkt_tab")
    cleaned_sentences =[]
    
    with Progress() as p:
        t = p.add_task("Tokenizando a base...", total=100)
        while not p.finished:
            p.update(t, advance=1)
            original_sentences = nltk.sent_tokenize(article)
    
     
    with Progress() as p:
        t = p.add_task("Preprocessando os tokens...", total=100)
        
        for sentence in original_sentences:
            p.update(t, advance=(100/len(original_sentences)))
            cleaned_sentences.append(preprocessing(sentence,nlp))
    
    tfidf = TfidfVectorizer(ngram_range=(1, 2))
    x_sentences = tfidf.fit_transform(cleaned_sentences)

    print('Hello! I am a chatbot and I will answer your questions about Star Wars')
    while True:
        user_text = input()
        if user_text != "quit":
            user_text = preprocessing(user_text,nlp)
            print('Chatbot: ')
            print(answer(user_text= user_text, original_sentences = original_sentences, x_sentences= x_sentences, tfidf=tfidf))
        else:
            print('Chatbot: Bye! see you soon')
            break

if __name__ == "__main__":
    main()
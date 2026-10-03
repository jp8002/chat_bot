from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def answer(user_text , tfidf ,original_sentences, x_sentences, threshold = 0.1):
    user_vac = tfidf.transform([user_text])
    
    similiraty = cosine_similarity(user_vac,x_sentences)[0]
    
    sentence_index = similiraty.argsort()[-1]
    
    chatbot_answer = ''
    
    print(similiraty[sentence_index])
    
    if similiraty[sentence_index] < threshold:
        chatbot_answer += "sorry, no answer was found"
    
    else:
        chatbot_answer += original_sentences[sentence_index]
    
    return chatbot_answer
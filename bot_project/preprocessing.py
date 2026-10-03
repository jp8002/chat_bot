import re

def preprocessing(sentence, nlp):
    sentence = sentence.lower()
    
    tokens = []
    tokens = [token.text for token in nlp(sentence)if not (token.is_stop or token.like_num
                                                           or token.is_punct or token.is_space                                                       or len(token)==1)]
    tokens = " ".join([element for element in tokens])
    return tokens

def simple_cleaning(text):
    text = re.sub(r"\[\d{1,4}\]", "", text)         # remove só citações [35], [1], [999]...
    text = re.sub(r"[^A-Za-z0-9,.\-]", " ", text)  # mantém letras, dígitos, vírgula, ponto, hífen
    text = re.sub(r"\s+", " ", text).strip()
    
    return text
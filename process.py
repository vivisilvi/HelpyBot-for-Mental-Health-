import json
import random
import nltk
import string
import numpy as np
import pickle
import tensorflow as tf
from nltk.stem import WordNetLemmatizer
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

global responses, lemmatizer, tokenizer, le, model, input_shape
input_shape = 10

responses = {}
with open('dataset/helpybot.json', encoding="utf-8") as content:
    data = json.load(content)
for intent in data['intents']:
    responses[intent['tag']]=intent['responses']
# import dataset answer
def load_response():
    global responses
    responses = {}
    with open('dataset/helpybot.json', encoding="utf-8") as content:
        data = json.load(content)
    for intent in data['intents']:
        responses[intent['tag']]=intent['responses']

# import model dan download nltk file
def preparation():
    load_response()
    global lemmatizer, tokenizer, le, model
    tokenizer = pickle.load(open('model/tokenizer.pkl', 'rb'))
    le = pickle.load(open('model/labelencoder.pkl', 'rb'))
    model = keras.models.load_model('model/helpybot.h5', compile = False)
    model.compile()
    lemmatizer = WordNetLemmatizer()
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)

# hapus tanda baca
def remove_punctuation(text):
    texts_p = []
    text = [letters.lower() for letters in text if letters not in string.punctuation]
    text = ''.join(text)
    texts_p.append(text)
    return texts_p

# mengubah text menjadi vector
def vectorization(texts_p):
    vector = tokenizer.texts_to_sequences(texts_p)
    vector = np.array(vector).reshape(-1)
    vector = pad_sequences([vector], input_shape)
    return vector

# klasifikasi pertanyaan user
def predict(vector):
    output = model.predict(vector)
    output = output.argmax()
    response_tag = le.inverse_transform([output])[0]
    return response_tag

# menghasilkan jawaban berdasarkan pertanyaan user
def generate_response(text):
    texts_p = []
    text = [letters.lower() for letters in text if letters not in string.punctuation]
    text = ''.join(text)
    texts_p.append(text)

    # Tokenisasi input
    text = tokenizer.texts_to_sequences(texts_p)
    text = np.array(text).reshape(-1)
    text = pad_sequences([text], maxlen=18)

    # Prediksi
    output = model.predict(text)
    output = output.argmax()

    # Mengubah hasil prediksi menjadi tag
    response_tag = le.inverse_transform([output])[0]
    q_response = next((intent for intent in responses if intent == response_tag), None)
    if q_response:
        resp_list = responses[q_response]
    answer = random.choice(responses[response_tag])
    return answer
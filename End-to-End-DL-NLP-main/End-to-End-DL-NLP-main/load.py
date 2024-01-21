import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import json
import numpy as np
import psycopg2
from psycopg2 import sql

import re
from nltk.tokenize import word_tokenize

model = tf.keras.models.load_model("s_model")
with open('saved_tokenizer_config.json', 'r', encoding='utf-8') as f:
    tokenizer_config = json.load(f)
custom_tokens = tokenizer_config['config']['word_index']
word_indexs = json.loads(custom_tokens)
def clean_text(data):
        # remove hashtags and @usernames
        data = re.sub(r"(#[\d\w\.]+)", '', data)
        data = re.sub(r"(@[\d\w\.]+)", '', data)
        # tekenization using nltk
        data = word_tokenize(data)
        return data
def model_pred(text):

    text = clean_text(text)
    tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=len(word_indexs) + 1, oov_token='<OOV>')
    tokenizer.word_index = word_indexs
    seq = tokenizer.texts_to_sequences(text)
    flattened_list = [item for sublist in seq if sublist and sublist[0] is not None for item in sublist]
    flattened_list = [flattened_list]
    pad_seq = pad_sequences(flattened_list,maxlen=500)
    pred = model.predict(pad_seq)
    class_names = ['joy', 'fear', 'anger', 'sadness', 'neutral']
    return class_names[np.argmax(pred)]
#text = 'There was a hairline scratch on the screen which is not clearly visible directly. When we tried contacting Amazon for the replacement, they asked us to connect to apple and when connected to apple, they asked to connect with Amazon. Blame game begins and we end up paying the price. Awfull service. I am going to tag on the social media both Amazon and apple. Such a big scam'

# Connect to the PostgreSQL server without specifying a database
db_connection = psycopg2.connect(
    user="postgres",
    password="leo@#838",
    host="localhost",
    port=5432
)

# Create a cursor object
db_cursor = db_connection.cursor()

# Check if the database exists, if not, create it
db_cursor.execute("SELECT 1 FROM pg_database WHERE datname='modelLog';")
if not db_cursor.fetchone():
    db_cursor.execute("CREATE DATABASE modelLog;")

# Close the cursor and connection to the default database
db_cursor.close()
db_connection.close()

# Connect to the PostgreSQL database
db_connection = psycopg2.connect(
    dbname="modelLog",
    user="postgres",
    password="leo@#838",
    host="localhost",
    port=5432
)
# Create a cursor object
db_cursor = db_connection.cursor()

# Check if the table exists, if not, create it
db_cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'prediction_logs';")
if not db_cursor.fetchone():
    db_cursor.execute("""
        CREATE TABLE prediction_logs (
            log_id SERIAL PRIMARY KEY,
            request_id UUID NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            input_data TEXT NOT NULL,
            prediction_result TEXT NOT NULL
        );
    """)
    db_connection.commit()


# Create a cursor object
db_cursor = db_connection.cursor()


def predict_text_and_log(input_text):
    # Make prediction
    prediction = model_pred(input_text)

    # Log the prediction request and result in the database
    insert_query = sql.SQL("INSERT INTO prediction_logs (request_id, input_data, prediction_result) VALUES (uuid_generate_v4(), %s, %s);")
    db_cursor.execute(insert_query, (input_text, prediction))
    db_connection.commit()

    return prediction
import requests
import nltk
import os
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
from pymongo import MongoClient, server_api
from urllib.parse import quote_plus
import os
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# Load environment variables
load_dotenv()
url = os.getenv("URL")
api_key = os.getenv('API_KEY')
 

# Set the date to 1 days ago
date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

# Function to fetch articles from the API and process them into a dictionary list
def get_articles(file):
    article_results = []
    for i in range(len(file)):
        article_dict = {
            'title': file[i]['title'],
            'author': file[i]['author'],
            'source': file[i]['source'],
            'description': file[i]['description'],
            'content': file[i]['content'],
            'pub_date': file[i]['publishedAt'],
            'url': file[i]["url"],
            'photo_url': file[i]['urlToImage']
        }
        article_results.append(article_dict)
    return article_results

# Fetch news articles from multiple domains
def fetch_articles(domains, url, api_key, date):
    responses_list = []
    for domain in domains:
        parameters_headlines = {
            'domains': domain,
            'sortBy': 'popularity',
            'pageSize': 100,
            'apiKey': api_key,
            'language': 'en',
            'from': date
        }
        rr = requests.get(url, params=parameters_headlines)
        data = rr.json()
        responses = data.get("articles", [])
        responses_list.append(pd.DataFrame(get_articles(responses)))
    
    return pd.concat(responses_list, ignore_index=True)

# Extract the source names from the source dictionary
def source_getter(df):
    df['source'] = df['source'].apply(lambda x: x['name'] if isinstance(x, dict) and 'name' in x else None)
    return df

# Clean text by removing punctuation, contractions, and other unwanted characters
def clean_text(text):
    text = text.lower()
    text = re.sub(r"what's", "what is ", text)
    text = text.replace('(ap)', '')
    text = re.sub(r"\'s", " is ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r'\W+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r"\\", "", text)
    text = re.sub(r"\'", "", text)
    text = re.sub(r"\"", "", text)
    text = re.sub('[^a-zA-Z ?!]+', '', text)
    text = "".join(i for i in text if ord(i) < 128)  # Remove non-ASCII characters
    return text.strip()

# Remove stopwords from a list of tokens
def remove_stopwords(word_tokens):
    stop_words = set(stopwords.words('english'))
    specific_words_list = ['char', 'u', 'hindustan', 'doj', 'washington']
    stop_words.update(specific_words_list)
    return [w for w in word_tokens if w not in stop_words]

# Lemmatize tokens
def lemmatize(tokens):
    lemmatizer = WordNetLemmatizer()
    return ' '.join([lemmatizer.lemmatize(word) for word in tokens])

# Tokenize text
tokenizer = RegexpTokenizer(r'\w+')
def tokenize(text):
    return tokenizer.tokenize(text)

# Process the news data
def process_news_data(news_articles_df):
    # Clean the text
    news_articles_df['combined_text'] = news_articles_df['title'].map(str) + " " + news_articles_df['content'].map(str)
    news_articles_df['combined_text'] = news_articles_df['combined_text'].map(clean_text)

    # Tokenize, remove stopwords, and lemmatize
    news_articles_df['tokens'] = news_articles_df['combined_text'].map(tokenize)
    news_articles_df['tokens'] = news_articles_df['tokens'].map(remove_stopwords)
    news_articles_df['lems'] = news_articles_df['tokens'].map(lemmatize)

    # Drop rows with missing data
    news_articles_df.dropna(inplace=True)

    # Convert pub_date to datetime format
    news_articles_df['pub_date'] = pd.to_datetime(news_articles_df['pub_date']).apply(lambda x: x.date())

    # Extract source names
    news_articles_df = source_getter(news_articles_df)

    return news_articles_df

# Save the processed DataFrame to MongoDB
def save_to_mongodb(df, collection_name):
    # Get MongoDB credentials from environment variables
    mongo_username = quote_plus(os.getenv('MONGO_USERNAME'))
    db_password = quote_plus(os.getenv('MONGO_PASSWORD'))
    db_name = os.getenv('DB_NAME')

    # MongoDB connection URI with escaped username and password
    uri = f"mongodb+srv://{mongo_username}:{db_password}@news-analyzer.0ittn.mongodb.net/{db_name}?retryWrites=true&w=majority&appName=News-analyzer"

    # Create a new client and connect to the MongoDB server
    client = MongoClient(uri, server_api=server_api.ServerApi('1'))

    # Test connection by pinging the MongoDB server
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    # Access the database and collection
    db = client[db_name]
    collection = db[collection_name]

    data_dict = df.to_dict("records")
    for record in data_dict:
        if 'pub_date' in record :
            # Convert date to datetime
            record['pub_date'] = datetime.combine(record['pub_date'], datetime.min.time())

    # Convert DataFrame to dictionary and insert into MongoDB
    try:
        
        collection.insert_many(data_dict)
        print(f"{len(data_dict)} records inserted into the {collection_name} collection in MongoDB.")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")
# Save the processed DataFrame to CSV
def save_to_csv(df, path="assets/news_articles_clean.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Ensure the directory exists
    df.to_csv(path, index=False)
    print(f"CSV file saved to {path}.")

# Main function to fetch, process, and save the articles
def main():
    domains = ['wsj.com','aljazeera.com','bbc.co.uk','techcrunch.com', 'nytimes.com','bloomberg.com','businessinsider.com',
             'cbc.ca','cnbc.com','cnn.com','ew.com','espn.go.com','espncricinfo.com','foxnews.com', 'apnews.com',
             'news.nationalgeographic.com','nymag.com','reuters.com','rte.ie','thehindu.com','huffingtonpost.com',
             'irishtimes.com','timesofindia.indiatimes.com','washingtonpost.com','time.com','medicalnewstoday.com',
             'ndtv.com','theguardian.com','dailymail.co.uk','firstpost.com','thejournal.ie', 'hindustantimes.com',
             'economist.com','news.vice.com','usatoday.com','telegraph.co.uk','metro.co.uk','mirror.co.uk','news.google.com']
    news_articles_df = fetch_articles(domains, url, api_key, date)
    news_articles_df = process_news_data(news_articles_df)

    # Save to CSV and MongoDB
    save_to_csv(news_articles_df, path=f"assets/{date}.csv")
    save_to_mongodb(news_articles_df, collection_name="DailyNews")


# Allow this script to be used as an importable module or run as a standalone script
if __name__ == "__main__":
    main()

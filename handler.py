import os
import tweepy as tw
import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, String

DB_CONN = os.environ.get('DB_CONN')
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')

metadata = MetaData()

sample_table = Table('sample_tweets', metadata,
    Column('id', String(100), primary_key=True),
    Column('text', String(300), nullable=False),
    Column('created_at', String(20), nullable=False),
)

def setupAPI():
    auth = tw.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    return tw.API(auth)

def getData(query, limit, lang='fr'):
    api = setupAPI()
    return tw.Cursor(api.search, q=query, lang=lang).items(limit)

def cleanup(item):
    return {
        'id': item.id_str,
        'text': item.text,
        'created_at': item.created_at.strftime("%d/%m/%Y")
    }

def init_tables(engine):
    sample_table.drop(engine, checkfirst=True)
    metadata.create_all(engine)

def main(event, context):
    data = getData('Macron', 5)
    cleaned_data = [cleanup(item) for item in data]

    engine = create_engine(DB_CONN)
    init_tables(engine)
    conn = engine.connect()
    conn.execute(sample_table.insert().values(cleaned_data))
    
    return cleaned_data


import requests
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime
from dash import Dash, html, dcc
import plotly.express as px

# 📥 Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# 🔐 Use your own NewsAPI key here
API_KEY = 'cde756796fd3467794f4e941613b361a'  # Replace with your key
NEWS_URL = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={API_KEY}'

# 1. Fetch data from NewsAPI
response = requests.get(NEWS_URL)
data = response.json()

articles = data.get('articles', [])
titles = []
times = []

for article in articles:
    if article['title'] and article['publishedAt']:
        titles.append(article['title'])
        # Convert to datetime object
        times.append(datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')))

# 2. Create DataFrame
df = pd.DataFrame({'title': titles, 'published_at': times})
df['hour'] = df['published_at'].dt.hour

# 3. Frequency of articles by hour
hour_data = df['hour'].value_counts().sort_index()
hour_df = pd.DataFrame({'Hour': hour_data.index, 'Posts': hour_data.values})

# 4. Most common words in headlines
all_words = []
stop_words = set(stopwords.words('english'))

for title in df['title']:
    tokens = title.lower().split()
    filtered = [word for word in tokens if word.isalpha() and word not in stop_words]
    all_words.extend(filtered)

word_freq = pd.Series(all_words).value_counts().head(10)
word_df = pd.DataFrame({'Word': word_freq.index, 'Frequency': word_freq.values})

# 5. Dash App
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1('📰 Live News Dashboard (NewsAPI)', style={'textAlign': 'center'}),

    dcc.Graph(
        figure=px.bar(hour_df, x='Hour', y='Posts', title='🕒 Article Frequency by Hour')
    ),

    dcc.Graph(
        figure=px.bar(word_df, x='Word', y='Frequency', title='🔤 Top 10 Frequent Words in Headlines')
    )
])

if __name__ == '__main__':
    app.run(debug=True)


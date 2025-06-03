# app.py
import streamlit as st
import pandas as pd
import requests
import os
from textblob import TextBlob

# Set up API key from Streamlit secrets
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY", "")

st.set_page_config(page_title="YouTube Sentiment Analyzer", layout="wide")
st.title("🔍 YouTube Video Comment Sentiment Analyzer")

# Input YouTube video ID or full URL
youtube_url = st.text_input("Enter YouTube Video URL or ID:", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Extract video ID from URL
import re
match = re.search(r"(?:v=|youtu.be/)([\w-]+)", youtube_url)
video_id = match.group(1) if match else youtube_url

# Fetch comments from YouTube API
def get_comments(video_id, api_key, max_results=50):
    comments = []
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?key={api_key}&textFormat=plainText&part=snippet&videoId={video_id}&maxResults={max_results}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    data = response.json()
    for item in data.get("items", []):
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments

# Analyze sentiment with TextBlob
def analyze_sentiment(comment):
    blob = TextBlob(comment)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# If API key present and valid input
if YOUTUBE_API_KEY and video_id:
    comments = get_comments(video_id, YOUTUBE_API_KEY)
    if not comments:
        st.error("No comments found or invalid video ID/API key.")
    else:
        df = pd.DataFrame(comments, columns=["Comment"])
        df["Sentiment"] = df["Comment"].apply(analyze_sentiment)

        st.write(f"Fetched {len(df)} comments. Sentiment breakdown:")
        st.dataframe(df)

        sentiment_counts = df["Sentiment"].value_counts()
        st.bar_chart(sentiment_counts)
else:
    st.info("Please enter a valid YouTube video URL and ensure API key is set.")

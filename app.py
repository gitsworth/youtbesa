import streamlit as st
from googleapiclient.discovery import build
from textblob import TextBlob
import pandas as pd

st.title("YouTube Video Comments Sentiment Analyzer")

api_key = st.text_input("Enter your YouTube API Key", type="password")
video_id = st.text_input("Enter YouTube Video ID (e.g. dQw4w9WgXcQ)")

if api_key and video_id:
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        comments = []
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )
        response = request.execute()

        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        if not comments:
            st.warning("No comments found for this video.")
        else:
            df = pd.DataFrame(comments, columns=['Comment'])
            df['Polarity'] = df['Comment'].apply(lambda x: TextBlob(x).sentiment.polarity)
            df['Sentiment'] = df['Polarity'].apply(
                lambda x: 'Positive' if x > 0 else ('Negative' if x < 0 else 'Neutral'))
            
            st.dataframe(df)

            st.write("### Sentiment Summary")
            st.bar_chart(df['Sentiment'].value_counts())

            st.write("### Example Comments by Sentiment")
            for sentiment in ['Positive', 'Neutral', 'Negative']:
                st.write(f"**{sentiment} comments:**")
                examples = df[df['Sentiment'] == sentiment]['Comment'].head(3).tolist()
                for c in examples:
                    st.write(f"- {c}")

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please enter your API key and a YouTube video ID.")

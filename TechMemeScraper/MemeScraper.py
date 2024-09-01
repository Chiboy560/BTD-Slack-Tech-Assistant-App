import os
import praw
import schedule
from flask import Flask
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_USER_AGENT = "BTD Tech Meme Scraper"

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)  # Initialize Flask app

COMMUNITY_MEMES_ID = "Insert your Channel ID here"  # Community Memes channel ID

client = WebClient(token=SLACK_BOT_TOKEN)

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Scrape memes from a specific subreddit
def scrape_reddit_memes(subredditName, limit=3):
    memes = []
    subreddit = reddit.subreddit(subredditName)

    for submission in subreddit.hot(limit=limit):
        if not submission.stickied:
            if submission.url.endswith(('jpg', 'png', 'gif', 'jpeg')) and not submission.over_18:
                meme = {
                    'title': submission.title,
                    'url' : submission.url,
                    'permalink': submission.permalink,
                    'image_url': submission.url 
                }
            memes.append(meme)

    return memes

# Post memes to the Community Memes channel on Slack
def post_reddit_memes_to_slack(memes):
    for meme in memes:
        try:
            attachments = []
            if meme['image_url']:
                attachments.append({
                    "fallback": "Image not available.",
                    "text": f"<https://reddit.com{meme['permalink']}|{meme['title']}>",  
                    "image_url": meme['image_url'],      
                })
            client.chat_postMessage(
                channel=COMMUNITY_MEMES_ID,  # Community Memes channel ID
                text= f"*{meme['title']}*",
                text= f"*{meme['title']}*",
                attachments=attachments
            )
        except SlackApiError as e:
            print(f"Error posting meme to Slack: {e.response['error']}")

# Run the daily meme job to scrape and post memes
def run_daily_meme_job():
    memes = scrape_reddit_memes('ProgrammerHumor', limit=3)
    post_reddit_memes_to_slack(memes)

# Schedule the daily meme job to run every day
def schedule_meme_job():
    schedule.every().day.at("09:00").do(run_daily_meme_job)

if __name__ == "__main__":
    schedule_meme_job()  # Schedule daily meme job
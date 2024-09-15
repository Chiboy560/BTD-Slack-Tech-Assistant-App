import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request
from slackeventsapi import SlackEventAdapter
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from apscheduler.schedulers.background import BackgroundScheduler
import praw  # Reddit API library

app = Flask(__name__)

# Initialize Flask app

# Slack and Reddit API credentials
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_SECRET = os.getenv('REDDIT_SECRET')
REDDIT_USER_AGENT = "BTD Tech Meme Scraper"

# Initialize Slack event adapter and WebClient
slack_event_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, '/slack/events', app)
client = WebClient(token=SLACK_BOT_TOKEN)

# Messages and Channel IDs
WELCOME_MESSAGE = "<@{user_id}> Welcome to the BTD Tech Community 🎉! Check your DMs to see the onboarding message I sent to you and then please provide a formal introduction in the #introductions channel!"
ONBOARDING_MESSAGE = "Hello <@{user_id}>, Beyond the Dome (BTD) is the preeminent career development program that provides the platform for College of Arts and Letters students to explore a range of potential career paths while creating access, exposure, and opportunities to break into their desired career industry. Please go to this link https://al.nd.edu/careers/ to learn more about!\n\n Anyways.. What is the BTD Tech Career Community? Well, we are a subset of BTD that establishes a community of Arts and Letters students who are more tech-focused and desire to break into the tech-industry. Our mission is to assist in paving your tech-oriented career path through different resources like tech info sessions, events, internship opportunities and certainly a centralized hub like our Slack Workspace! So I highly encourage you to be involved in the community! Thank you and Toodles! "
MEMBER_LOG_ID = "C06Q2RN2MTJ"  # Member log channel ID
TECH_NEWS_ID = "C06PPLGLV2T"  # Tech News Channel ID
COMMUNITY_MEMES_ID = "C06L8B2QFM2"  # Community Memes channel ID

# Global variables for debouncing and tracking users
welcomed_users = set()  # Track users who have been welcomed
last_event_timestamp = {}  # Track the last event timestamp for each user

# Handle user joining the channel and send welcome/onboarding messages
@slack_event_adapter.on("member_joined_channel")
def recognize_member_joined(event_data):
    event = event_data["event"]
    print(f"Received event: {event}")
    user_id = event.get("user")
    channel_id = event.get("channel")
    event_ts = event.get("event_ts")

    # Debounce logic to prevent duplicate messages
    if user_id in last_event_timestamp and event_ts <= last_event_timestamp[user_id]:
        return
    last_event_timestamp[user_id] = event_ts

    # Send welcome and onboarding messages if in the correct channel
    if channel_id == MEMBER_LOG_ID:
        if user_id not in welcomed_users:
            welcomed_users.add(user_id)
            send_channel_welcome_message(MEMBER_LOG_ID, user_id)
            send_direct_onboarding_message(user_id)

# Send onboarding message via direct message
def send_direct_onboarding_message(user_id):
    try:
        response = client.conversations_open(users=[user_id])
        channel_id = response["channel"]["id"]
        client.chat_postMessage(
            channel=channel_id,
            text=ONBOARDING_MESSAGE.format(user_id=user_id)
        )
    except SlackApiError as e:
        print(f"Error sending onboarding message: {e.response['error']}")

# Send welcome message to the channel
def send_channel_welcome_message(channel_id, user_id):
    try:
        client.chat_postMessage(
            channel=channel_id,
            text=WELCOME_MESSAGE.format(user_id=user_id)
        )
    except SlackApiError as e:
        print(f"Error sending welcome message: {e.response['error']}")

# Handle user leaving the channel
@slack_event_adapter.on("member_left_channel")
def recognize_member_left(event_data):
    event = event_data["event"]
    print(f"Received event: {event}")
    user_id = event.get("user")
    channel_id = event.get("channel")

    # Remove user from welcomed users set
    if channel_id == MEMBER_LOG_ID:
        if user_id in welcomed_users:
            welcomed_users.remove(user_id)

# Web scraping tech headlines from specified websites
WEBSITES = {
    "TechRadar": "https://www.techradar.com",
    "Wired": "https://www.wired.com/tag/technology/",
}

def find_articles():
    articles = []  # Store scraped articles
    # Iterate through each website
    for siteName, url in WEBSITES.items():
        try:
            httpResponse = requests.get(url)
            httpResponse.raise_for_status()  # Check for HTTP errors
            soup = BeautifulSoup(httpResponse.text, 'html.parser')
            articles_scraped = 0
            # Scrape headlines, links, and images
            for articleTag in soup.find_all(['h2', 'h3']):
                if articles_scraped >= 4:
                    break
                headlineTag = articleTag.get_text(strip=True)
                linkTag = articleTag.find_parent('a')
                imageTag = articleTag.find_previous('img')  # Find the image related to the article
                # Default values
                title = "No title available"
                link = "No link available"
                image_url = None
                if headlineTag and linkTag:
                    title = headlineTag
                    link = urljoin(url, linkTag['href'])
                    if imageTag and 'src' in imageTag.attrs:
                        image_url = urljoin(url, imageTag['src'])
                articles.append({
                    'title': title,
                    'link': link,
                    'image_url': image_url
                })
                articles_scraped += 1
        except requests.RequestException as e:
            print(f"Error fetching articles from {siteName}: {e}")
    return articles

# Format and compile weekly news messages
def compile_news_weekly(articles):
    messages = []
    for article in articles:
        # Format each article posting
        message_text = f"*Headline:* {article['title']}\n*Link:* {article['link']}\n"
        # Prepare attachment with image if available
        attachments = []
        if article['image_url']:
            attachments.append({
                "fallback": "Image not available.",
                "text": "Image Preview :)",
                "image_url": article['image_url'],
            })
        messages.append({
            "text": message_text,
            "attachments": attachments
        })
    return messages

# Post the compiled messages to the Tech News channel on Slack
def post_news_message_to_slack(messages):
    messageMax = 7  # Max number of messages to post
    messageCount = 0
    try:
        for message in messages:
            if messageCount >= messageMax:
                break
            client.chat_postMessage(
                channel=TECH_NEWS_ID,
                text=message["text"],
                attachments=message["attachments"]
            )
            messageCount += 1
    except SlackApiError as e:
        print(f"Error posting message to Slack: {e.response['error']}")

# Execute the news scraping and posting process
def run_news_weekly_job():
    articles = find_articles()
    messages = compile_news_weekly(articles)
    post_news_message_to_slack(messages)

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
                    'url': submission.url,
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
                text=f"*{meme['title']}*",
                attachments=attachments
            )
        except SlackApiError as e:
            print(f"Error posting meme to Slack: {e.response['error']}")

# Run the daily meme job to scrape and post memes
def run_daily_meme_job():
    memes = scrape_reddit_memes('ProgrammerHumor', limit=3)
    post_reddit_memes_to_slack(memes)

# Initialize APScheduler and add jobs
scheduler = BackgroundScheduler()
scheduler.add_job(run_news_weekly_job, 'interval', weeks=1, day_of_week='mon', hour=10)  # Every Monday at 10 AM
scheduler.add_job(run_daily_meme_job, 'interval', days=3)  # Every 3 days
scheduler.start()

if __name__ == "__main__":
    # Start the APScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_news_weekly_job, 'interval', weeks=1, day_of_week='mon', hour=10)  # Every Monday at 10 AM
    scheduler.add_job(run_daily_meme_job, 'interval', days=3)  # Every 3 days
    scheduler.start()

    # Get the port from environment variable or use default
    port = int(os.environ.get("PORT", 10000))
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=port)

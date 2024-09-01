# Import necessary python libraries and modules
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import schedule
import time

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
                articles_scraped +=1
        except requests.RequestException as e:
            print(f"Error fetching articles from {siteName}: {e}")

    return articles

# Format and compile weekly news messages
def compile_news_weekly(articles):
    messages = []
    for article in articles:  # Format each article posting
        message_text = f"*Headline:* {article['title']}\n*Link:* {article['link']}\n"
        
        # Prepare attachment with image if available
        attachments = []
        if article['image_url']:
            attachments.append({
                "fallback": "Image not available.",
                "text": "Image Preview :)",
                "image_url": article['image_url']
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

# Schedule the weekly news job to run every Monday
def schedule_news_weekly():
    schedule.every().monday.at("09:00").do(run_news_weekly_job)

    while True:
        schedule.run_pending()
        time.sleep(60)  

# Execute the news scraping and posting process
def run_news_weekly_job():
    articles = find_articles()
    messages = compile_news_weekly(articles)
    post_news_message_to_slack(messages)

if __name__ == "__main__":
    schedule_news_weekly()  # Schedule weekly news job
    app.run(port=3000)  # Run Flask app
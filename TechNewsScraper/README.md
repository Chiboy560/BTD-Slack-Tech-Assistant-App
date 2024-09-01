# BTD Slack Chatbot - Tech News Feature 

## Overview
The Tech News Feature of the BTD Slack Chatbot automatically scrapes and posts the latest tech headlines from popular websites like TechRadar and Wired. This feature keeps your Slack channel updated with the latest in tech news, making it easy for members to stay informed.

## Features
- **Web Scraping for Tech Headlines:** Automatically scrapes the latest tech headlines, along with links and images, from specified websites.
- **Weekly Tech News Updates:** Posts a curated list of tech headlines every Monday to the designated Slack channel.

## Installation

### Prerequisites
- Python 3.6 or higher
- Slack API Token
- pip for installing Python packages
- Gunicorn for running the bot script locally

### Setup
1. **Install required Python libraries:**
   Use `pip install` or `pip3 install` to download the necessary libraries:
   - `requests`
   - `beautifulsoup4`
   - `slack_sdk`
   - `schedule`
   
2. **Create a Slack Chatbot:**
   - Obtain your Slack API Token, which will be used to interact with the Slack API.

3. **Set up the environment:**
   - Store your Slack Token securely, typically in a `.env` file.
   - Ensure that your Slack App is integrated into the workspace and all OAuth permissions are properly configured.

## Usage

### Running the Tech News Feature:
To run the Tech News feature locally, you can use `ngrok` for tunneling and `gunicorn` for running the bot script in production.

1. **Start the bot using gunicorn:**
   ```bash
   gunicorn --bind 0.0.0.0:3000 bot:app

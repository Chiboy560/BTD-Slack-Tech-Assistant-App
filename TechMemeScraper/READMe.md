# TechMemeScraper

This module scrapes the latest tech-related memes from Reddit and posts them to a Slack channel. It uses the PRAW library to interact with Reddit and the Slack SDK to post the memes.

## Setup Instructions

1. **Install required libraries:**
   Use `pip install` or `pip3 install` to download the necessary libraries:
   - `praw`
   - `slack_sdk`
   - `schedule`
   - `Flask`

2. **Create a Reddit App:**
   - Set up a Reddit App through your personal Reddit account by following online instructions or guidance from ChatGPT.

3. **Set up environment variables:**
   - Ensure you have the following environment variables in your `.env` file:
     - `REDDIT_CLIENT_ID`
     - `REDDIT_SECRET`
     - `REDDIT_USER_AGENT`

4. **Set up your Slack app:**
   - Ensure all OAuth permissions are configured.
   - Confirm that your Slack app is integrated into your workspace.

5. **Run the script:**
   - Execute the script to scrape and post memes on a regular basis.

## Usage

### To Run the Meme Scraper
Call the function `run_daily_meme_job()` to start the meme scraping process.

### Continuous Deployment
- Deploy your app to a cloud platform like Heroku, Render, or AWS EC2 to ensure it runs continuously.
```

Feel free to copy and paste this directly into your VS Code for GitHub!
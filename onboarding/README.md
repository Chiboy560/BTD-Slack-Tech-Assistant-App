# Beyond the Dome Slack Chatbot - Onboarding Feature (Initial README)

## Overview
The Onboarding Feature of the BTD Slack Chatbot automatically welcomes members to the Slack Workspace upon first arrival and provides them with initial onboarding information necessary for a seamless introduction. This feature enhances the user experience by ensuring that new members receive a warm welcome and essential information to get started.

## Features
- **Slack Workspace Welcome Message:** Every member who joins the member-log channel, and therefore the Slack Workspace, will be sent a greeting message.
- **Direct Onboarding Message:** Sends a personalized onboarding message directly to the new Slack member's direct messages.

## Installation

### Prerequisites
- Python 3.6 or higher
- Slack API Token
- Slack Signing Secret
- pip for installing Python packages
- Gunicorn for running the bot script locally

### Set Up
1. **Install required libraries:**
   Use `pip install` or `pip3 install` to download the necessary libraries:
   - `slack_sdk`
   - `flask`
   - `slackeventsapi`
   - `python-dotenv`
   - `gunicorn`

2. **Create a Slack Chatbot:**
   - Collect your Slack Token and Slack Signing Secret from the Slack API website.

3. **Set up the Slack app:**
   - Ensure all OAuth permissions are configured.
   - Confirm that your Slack app is integrated into the workspace.

4. **Run the script:**
   - Ensure that the bot is set up to handle and respond to events.

## Usage

### To Run the Onboarding Feature
- To run it locally, you can use `ngrok` to tunnel events to your local server.
- Use Gunicorn to run the bot script in production mode:

For Example:
  ```bash
  gunicorn --bind 0.0.0.0
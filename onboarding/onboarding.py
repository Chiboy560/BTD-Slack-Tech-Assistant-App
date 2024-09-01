#Imported libraries necessary for chatbot's development 
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from slackeventsapi import SlackEventAdapter
import time

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Retrieve Slack Bot Token and Signing Secret from environment variables
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')

# Initialize the Slack Event Adapter with the signing secret and Flask app
slack_event_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, '/slack/events', app)

# Initialize the Slack client with the bot token
client = WebClient(token=SLACK_BOT_TOKEN)

# Define the welcome message template for new members
WELCOME_MESSAGE = "<@{user_id}> Welcome to the BTD Tech Community 🎉! Check your DMs to see the onboarding message I sent to you and then please provide a formal introduction in the #introductions channel!"
# Define the onboarding message template for direct messages
ONBOARDING_MESSAGE = "Hello <@{user_id}>, Beyond the Dome is a...."

# Define the channel IDs for the member log and tech news channels
MEMBER_LOG_ID = "C06Q2RN2MTJ"  # Member log channel ID
TECH_NEWS_ID = "C06PPLGLV2T"  # Tech News Channel ID

# A set to keep track of users who have been welcomed
welcomed_users = set()

# A dictionary to keep track of the last event timestamps to debounce repeated events
last_event_timestamp = {}

# Event listener for when a new member joins a channel
@slack_event_adapter.on("member_joined_channel")
def recognize_member_joined(event_data):
    event = event_data["event"]
    print(f"Received event: {event}")
    user_id = event.get("user")  # Get the user ID of the person who joined
    channel_id = event.get("channel")  # Get the channel ID where the event occurred
    event_ts = event.get("event_ts")  # Get the event timestamp

    # Debounce: Process the event only if it's newer than the last one for this user
    if user_id in last_event_timestamp and event_ts <= last_event_timestamp[user_id]:
        return
    
    # Update the last event timestamp for this user
    last_event_timestamp[user_id] = event_ts

    # Ensure the event is for the member log channel
    if channel_id == MEMBER_LOG_ID:
        # If the user hasn't been welcomed yet, send them a welcome message and onboarding message
        if user_id not in welcomed_users:
            welcomed_users.add(user_id)  # Add user to the welcomed set
            send_channel_welcome_message(MEMBER_LOG_ID, user_id)  # Send welcome message to the channel
            send_direct_onboarding_message(user_id)  # Send onboarding message via direct message

# Function to send a direct onboarding message to the user
def send_direct_onboarding_message(user_id):
    try:
        # Open a direct message conversation with the user
        response = client.conversations_open(users=[user_id])
        channel_id = response["channel"]["id"]  # Get the DM channel ID

        # Post the onboarding message to the DM channel
        client.chat_postMessage(
            channel=channel_id,
            text=ONBOARDING_MESSAGE.format(user_id=user_id)
        )
    except SlackApiError as e:
        # Print an error message if the API call fails
        print(f"Error sending onboarding message: {e.response['error']}")

# Function to send a welcome message to the member log channel
def send_channel_welcome_message(channel_id, user_id):
    try:
        # Post the welcome message to the specified channel
        client.chat_postMessage(
            channel=channel_id,
            text=WELCOME_MESSAGE.format(user_id=user_id)
        )
    except SlackApiError as e:
        # Print an error message if the API call fails
        print(f"Error sending welcome message: {e.response['error']}")

# Main entry point of the Flask application
if __name__ == "__main__":
    app.run(port=3000)  # Run the Flask app on port 3000

# Event listener for when a member leaves a channel
@slack_event_adapter("member_left_channel")
def recognize_member_left(event_data):
    event = event_data["event"]
    print(f"Received event: {event}")
    user_id = event.get("user")  # Get the user ID of the person who left
    channel_id = event.get("channel")  # Get the channel ID where the event occurred
    event_ts = event.get("event_ts")  # Get the event timestamp
    
    # If the event occurred in the member log channel, remove the user from the welcomed set
    if channel_id == MEMBER_LOG_ID:
        if user_id in welcomed_users:
            del welcomed_users[user_id]
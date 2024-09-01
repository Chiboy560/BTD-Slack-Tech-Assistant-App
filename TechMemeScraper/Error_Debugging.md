# Error Handling & Debugging

This document provides information on how errors are handled within the project and steps for debugging common issues.

## Imported Python Libraries:
For downloading python libraries, it is highly recommended to use a virtual environment.

To set up a virtual environment and  run your code locally,  use the commands "python3/python -m venv venv" then "source venv/bin/activate" to activate it. Finally type in "deactivate" when you're done. 

Do this in your Mac Terminal or Windows Command Prompt.

## Meme Posting Format
Please ensure that you set your posting correctly. I formatted mine in a specific way that looked pleasing for me. Ensure you find your own format or feel free to use mine. 

## Onboarding
There were intiially a lot of errors in the onboarding output and they mostly comprised of dual and triple posting of the same message. An important section of my code that solved this issue was adding a debouncing feature that kept slowed down the message posting 

## Slack API Errors
The script handles Slack API errors using the `SlackApiError` class. If an error occurs while posting a message, the script will print the error to the console:

```python
except SlackApiError as e:
    print(f"Error posting meme to Slack: {e.response['error']}")



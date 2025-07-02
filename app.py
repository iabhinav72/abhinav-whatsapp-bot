from flask import Flask, request, jsonify
import requests
import json # Import the json library

app = Flask(__name__)

# --- IMPORTANT ---
# Replace this with the correct API key from your Gupshup App Dashboard
GUPSHUP_API_KEY = 'sk_42b6378849dc41cc90ece33045e89ab3'

# Double-check these values in your Gupshup dashboard as well
GUPSHUP_SOURCE_NUMBER = '917834811114'
GUPSHUP_BOT_NAME = 'AbhinavBotGupShup'


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    This webhook receives incoming messages from Gupshup.
    """
    if request.method == 'GET':
        # Gupshup may send a GET request to verify the webhook URL
        return jsonify({"status": "ok"}), 200

    # Process incoming POST request (actual messages)
    data = request.get_json()
    print("Incoming Webhook Data:", json.dumps(data, indent=2))

    try:
        # Safely extract message details using .get() to avoid errors
        message_data = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [{}])[0]

        if message_data and message_data.get('from') and message_data.get('text'):
            sender = message_data['from']
            message_text = message_data['text']['body'].lower().strip()
            print(f"📩 Message received from {sender}: {message_text}")

            # Simple bot logic
            if "who are you" in message_text:
                send_reply(sender, "I am a bot created by Abhinav.")
            else:
                send_reply(sender, f"You said: {message_text}")

    except (IndexError, KeyError, TypeError) as e:
        print(f"⚠️ Error processing webhook data: {e}. Data might be in an unexpected format.")

    return jsonify({'status': 'ok'}), 200


def send_reply(to, message_text):
    """
    Sends a reply back to the user via the Gupshup API.
    """
    url = "https://api.gupshup.io/sm/api/v1/msg"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'apikey': GUPSHUP_API_KEY
    }

    # --- CODE CHANGE ---
    # The message payload should be a JSON object, converted to a string.
    # This is more robust and supports different message types.
    message_payload = {
        "type": "text",
        "text": message_text
    }

    payload = {
        'channel': 'whatsapp',
        'source': GUPSHUP_SOURCE_NUMBER,
        'destination': to,
        'message': json.dumps(message_payload), # Convert the dict to a JSON string
        'src.name': GUPSHUP_BOT_NAME
    }

    print("🚀 Sending POST to Gupshup with:")
    print("Headers:", headers)
    print("Payload:", payload)

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors (4xx or 5xx)
        print(f"✅ Message sent successfully to {to}: {message_text}")
        print("Gupshup response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send message to Gupshup: {e}")


if __name__ == '__main__':
    # Use 0.0.0.0 to make the server accessible from your network if needed for testing
    app.run(host='0.0.0.0', port=5000)

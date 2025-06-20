from flask import Flask, request
import requests
from Chatbot.bot import generate_response  # Import your existing function
import os

app = Flask(__name__)

# === Config ===
VERIFY_TOKEN = "vaibhavgarg"  # Same as what you set in Meta
ACCESS_TOKEN = "EAAJwQg2JkbgBO9ru9N4oepWfGWCwWTOg50TZBp74ktIHzYmd69tfZAaSEg3w4dlZCZC4B5V2dz5ieZATMpsa9ZAMKSRqaNxiJD1HZA9RJTVZAZBcijBI4xrZAmIPw50xkjSYeTTAuwoUk65R8Cu0BRPfShZAaOBYlWWTbr1V6Y5odJyNOQBH6lZBGJilJxJzsFmmRc9FJWMDcehCtjpNC6zJnMbZBdhrMUMOBvorF1pEZD"
PHONE_NUMBER_ID = "691257177404421"
PROJECT = "Krupal Habitat"  # Can be dynamic later
user_histories = {}  # Stores conversation history per user


# === Webhook Verification ===
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if (
            request.args.get("hub.mode") == "subscribe"
            and request.args.get("hub.verify_token") == VERIFY_TOKEN
        ):
            return request.args.get("hub.challenge"), 200
        return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("Incoming POST:", data)

        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender_id = message["from"]
            text = message["text"]["body"]

            # Store & update user history
            history = user_histories.get(sender_id, [])
            history.append({"role": "user", "content": text})
            response = generate_response(PROJECT, history)
            history.append({"role": "assistant", "content": response["text"]})
            user_histories[sender_id] = history

            send_whatsapp_message(sender_id, response["text"])

        except Exception as e:
            print("Error:", e)

        return "ok", 200


# === Send Message via WhatsApp API ===
def send_whatsapp_message(recipient, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message},
    }

    res = requests.post(url, headers=headers, json=payload)
    print("WhatsApp API response:", res.status_code, res.text)


if __name__ == "__main__":
    app.run(port=5000)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

sessions = {}

def generate_response(user_id, message):
    if user_id not in sessions:
        sessions[user_id] = {"step": "start"}

    state = sessions[user_id]
    message = message.lower()

    # EXIT
    if message in ["no", "exit"]:
        sessions[user_id] = {"step": "start"}
        return {"text": "👍 Have a great day! See you again."}

    # STEP 1
    if state["step"] == "start":
        state["step"] = "service"
        return {
            "text": "Hey 👋 I'm your AI assistant. How can I help you?",
            "options": ["Machine Bowling", "Turf Booking"]
        }

    # STEP 2
    if state["step"] == "service":
        state["service"] = message
        state["step"] = "duration"
        return {
            "text": f"Great! You selected {message}. Choose duration:",
            "options": ["1 hour", "2 hours"]
        }

    # STEP 3 (PRICE)
    if state["step"] == "duration":
        state["duration"] = message

        if "machine" in state["service"]:
            price = "₹900" if "1" in message else "₹1600"
        else:
            price = "₹1300" if "1" in message else "₹2600"

        state["price"] = price
        state["step"] = "confirm"

        return {
            "text": f"💰 Price: {price}\nConfirm booking?",
            "options": ["Confirm", "Cancel"]
        }

    # STEP 4
    if state["step"] == "confirm":
        if message == "confirm":
            state["step"] = "mobile"
            return {"text": "📱 Enter your mobile number:"}

        if message == "cancel":
            state["step"] = "start"
            return {
                "text": "Booking cancelled. Start again.",
                "options": ["Machine Bowling", "Turf Booking"]
            }

    # STEP 5
    if state["step"] == "mobile":
        state["mobile"] = message
        state["step"] = "payment_method"
        return {
            "text": "💳 Select payment method:",
            "options": ["Card", "PhonePe", "Paytm", "GPay", "Razorpay"]
        }

    # STEP 6
    if state["step"] == "payment_method":
        state["payment"] = message
        state["step"] = "qr"
        return {
            "text": f"📲 Scan QR using {message} to pay {state['price']}",
            "qr": True,
            "options": ["Payment Done"]
        }

    # STEP 7
    if state["step"] == "qr":
        state["step"] = "done"

        receipt = f"""
Booking Receipt
-----------------------
Service: {state['service']}
Duration: {state['duration']}
Price: {state['price']}
Payment: {state['payment']}
Mobile: {state['mobile']}
Status: Confirmed
"""

        with open("receipt.txt", "w") as f:
            f.write(receipt)

        return {
            "text": "✅ Payment successful!\n🎉 Booking confirmed!\nDownload receipt below:",
            "download": "/receipt"
        }

    # STEP 8
    if state["step"] == "done":
        state["step"] = "restart"
        return {
            "text": "🙏 Thanks for booking!\nNeed anything else?",
            "options": ["Yes", "No"]
        }

    # STEP 9
    if state["step"] == "restart":
        if message == "yes":
            state["step"] = "start"
            return {
                "text": "How can I help you again?",
                "options": ["Machine Bowling", "Turf Booking"]
            }
        else:
            sessions[user_id] = {"step": "start"}
            return {"text": "👍 Have a great day!"}

    return {"text": "Error occurred"}


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data["message"]

    user_id = request.remote_addr
    response = generate_response(user_id, user_message)

    return jsonify(response)


@app.route("/receipt")
def receipt():
    return send_file("receipt.txt", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
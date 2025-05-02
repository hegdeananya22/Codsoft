import random
from datetime import datetime
def get_response(user_input):
    user_input = user_input.lower()

    greetings = ["hi", "hello", "hey", "good morning", "good evening"]
    farewells = ["bye", "goodbye", "see you", "exit"]

    if any(greet in user_input for greet in greetings):
        return random.choice([
            "Hello there! ",
            "Hi! How can I assist you today?",
            "Hey! What can I do for you?"
        ])
    elif "how are you" in user_input:
        return "I'm just a bot, but I'm doing fine. Thanks for asking!"

    elif "your name" in user_input:
        return "I'm ChatBotty, your virtual assistant. "

    elif "help" in user_input:
        return "I can tell you the time, tell jokes, talk about weather, or just chat! Try saying 'time', 'joke' or 'weather'."

    elif "time" in user_input:
        now = datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}."

    elif "weather" in user_input:
        return "I can't fetch real-time weather yet, but I hope it's nice where you are! "

    elif "joke" in user_input:
        return random.choice([
            "Why don’t scientists trust atoms? Because they make up everything!",
            "I'm reading a book on anti-gravity. It's impossible to put down!",
            "Why was the math book sad? Because it had too many problems.",
            "Why don’t programmers like nature? It has too many bugs.",
            "What do you call 8 hobbits? A hobbyte."
        ])
    elif any(farewell in user_input for farewell in farewells):
        return "Goodbye! Take care and come back soon. "

    else:
        return "Hmm, I didn't quite get that. Try asking me something else!"
def chatbot():
    print(" ChatBotty: Hi there! I'm your friendly rule-based chatbot.")
    print("Type 'exit' to end the conversation.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("ChatBotty: It was nice talking to you. Goodbye!")
            break
        if not user_input:
            print("ChatBotty: You didn't say anything. Try asking something!")
            continue
        response = get_response(user_input)
        print(f"ChatBotty: {response}")
chatbot()

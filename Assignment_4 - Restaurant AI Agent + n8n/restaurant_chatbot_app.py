"""CLI entrypoint for the LangChain + SQLite restaurant chatbot."""

from dotenv import load_dotenv

from restaurant_chatbot import RestaurantChatbot
from restaurant_db      import initialize_database


def main() -> None:
    # Load OPENAI_API_KEY (or any other secrets) from the .env file.
    load_dotenv()

    db_path = "restaurant.sqlite"

    # Creates the SQLite file + tables if they don't exist yet,
    # then seeds the demo menu and restaurant info on the very first run.
    initialize_database(db_path)

    # The bot reads the API key from the environment automatically.
    bot = RestaurantChatbot(db_path=db_path)

    # Updated welcome message
    print("Welcome to Tasty Sea - Seafood! 🌊")
    print("I'm your digital assistant, here to help with menu details, recommendations, or our opening hours.")
    print("\nYou can try asking me things like:")
    print("- 'Do you have vegetarian dishes?'")
    print("- 'Can you recommend a meal?'")
    print("-" * 40)
    print("Type 'exit' to quit at any time.\n")

    # Memory state for CLI
    history = []

    while True:
        # input() blocks until the user presses Enter.
        user_input = input("You: ").strip()

        # Skip empty lines (user just pressed Enter without typing).
        if not user_input:
            continue

        # Graceful exit command.
        if user_input.lower() in {"exit", "quit"}:
            print("Bot: Goodbye! Hope to see you at Tasty Sea soon.")
            break

        # This single call does classify → fetch DB → generate answer.
        reply = bot.answer(user_input, history=history)

        # Save the conversation turn
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": reply})

        print(f"Bot: {reply}\n")


# Only run main() if this file is executed directly (not imported).
if __name__ == "__main__":
    main()
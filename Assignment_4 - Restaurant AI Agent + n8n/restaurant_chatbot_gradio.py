"""Gradio web UI for the SQLite + LangChain restaurant chatbot."""

from dotenv import load_dotenv
import gradio as gr

from restaurant_chatbot import RestaurantChatbot
from restaurant_db      import initialize_database


def create_bot(db_path: str = "restaurant.sqlite") -> RestaurantChatbot:
    """Load environment variables, ensure DB exists, then build chatbot."""
    load_dotenv()
    initialize_database(db_path)
    return RestaurantChatbot(db_path=db_path)


def build_demo(bot: RestaurantChatbot) -> gr.Blocks:
    """Construct the Gradio chat interface around the chatbot backend."""

    def chat_handler(message: str, history: list[dict]) -> tuple[list[dict], str]:
        """Append the user question and bot answer in Gradio messages format."""
        history = history or []
        user_text = (message or "").strip()
        if not user_text:
            return history, ""

        # Pass the Gradio history directly to the bot
        answer = bot.answer(user_text, history=history)

        updated_history = history + [
            {"role": "user",      "content": user_text},
            {"role": "assistant", "content": answer},
        ]
        return updated_history, ""

    with gr.Blocks(title="Tasty Sea Chatbot") as demo:
        # Updated welcome message to match the CLI branding
        gr.Markdown("## Welcome to Tasty Sea - Seafood! 🌊\nI'm your digital assistant, here to help with menu details, recommendations, or our opening hours.")

        chatbot = gr.Chatbot(label="Conversation", height=450)

        message_box = gr.Textbox(
            label="Your question",
            placeholder="e.g., Do you have vegetarian dishes?"
        )

        with gr.Row():
            send_btn  = gr.Button("Send", variant="primary")
            clear_btn = gr.Button("Clear")

        send_btn.click(chat_handler,
                       inputs=[message_box, chatbot],
                       outputs=[chatbot, message_box])

        message_box.submit(chat_handler,
                            inputs=[message_box, chatbot],
                            outputs=[chatbot, message_box])

        clear_btn.click(lambda: [], outputs=chatbot, queue=False)

        # Updated examples to match the requested style
        gr.Examples(
            examples=[
                "Do you have vegetarian dishes?",
                "Can you recommend a meal?",
                "What are your opening hours?",
            ],
            inputs=message_box,
        )

    return demo


def main() -> None:
    """Run the web app."""
    bot  = create_bot()
    demo = build_demo(bot)
    demo.launch(server_port=7861)


if __name__ == "__main__":
    main()
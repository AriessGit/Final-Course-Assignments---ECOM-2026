import os
import re
import json
import sqlite3
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from restaurant_db import (
    get_restaurant_details_and_hours,
    search_menu_items,
    get_menu_items,
    book_reservation,
    cancel_reservation,
    check_availability_and_alternatives
)


class RestaurantChatbot:
    """RAG-style restaurant assistant backed by SQLite tables."""

    def __init__(self, db_path: str, model_name: str = "gpt-4o-mini") -> None:
        self.db_path = db_path
        self.llm = None
        # State memory to hold booking ID for cancellations
        self.pending_cancellation_id: Optional[int] = None
        # State memory to hold reservation details for multi-turn confirmations
        self.pending_reservation: Optional[Dict] = None
        # Counter for failed cancellation attempts
        self.cancellation_attempts: int = 0
        # State flags for guest limit handling (> 8 guests)
        self.waiting_for_guest_choice: bool = False
        self.waiting_for_new_guest_count: bool = False

        if os.getenv("OPENAI_API_KEY", "").strip():
            self.llm = ChatOpenAI(model=model_name, temperature=0)

        # Classification prompt
        self.classifier_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a router for a restaurant chatbot. "
             "Classify the user message into exactly one of these categories:\n"
             "  reservation   — user wants to book a table, or is providing booking details (like time, date, name, guests, or answering questions about reservation modification)\n"
             "  cancellation  — user wants to cancel an existing booking\n"
             "  menu          — questions about food, drinks, or prices\n"
             "  hours         — questions about opening hours or location\n"
             "  general       — anything else\n"
             "Return ONLY the single category word. No punctuation, no explanation."),
            ("human", "Chat History:\n{history}\n\nLatest Question: {question}")
        ])

        # Answer prompt
        self.answer_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a helpful restaurant assistant. Use only the provided context to answer. "
             "If the user asks for a recommendation, pick the best dish from the context. "
             "If the user asks for an ingredient (like peanuts) and it's not in the context, explicitly say you don't have dishes with that ingredient."),
            ("human", "Chat History:\n{history}\n\nLatest Question: {question}\n\nContext:\n{context}")
        ])

        # General conversation prompt for human-like interaction
        self.general_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a warm, friendly, and human-like host at 'Tasty Sea - Seafood' restaurant. "
             "A customer is making general conversation or greeting you. "
             "Respond naturally and politely. If they say hello, greet them back warmly and gently "
             "ask how you can help them today (e.g., with the menu, booking a table, or opening hours). "
             "Do not say you are an AI, a bot, or an assistant. Act like a real human representative. "
             "Always respond in the same language the user is speaking."),
            ("human", "Chat History:\n{history}\n\nLatest Message: {question}")
        ])

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        if not history:
            return "No previous conversation."
        lines = []
        for msg in history[-6:]:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def classify_question(self, question: str, history_str: str) -> str:
        """Classify intent using LLM and keyword priority."""
        lower_q = question.lower()

        # Check for cancellation first
        if any(k in lower_q for k in ["cancel", "cancellation", "delete booking"]):
            return "cancellation"

        # Check for reservation keywords explicitly
        if any(k in lower_q for k in ["reserve", "book", "reservation", "table", "another", "new"]):
            return "reservation"

        # Catch numbers or yes/no inputs ONLY during an active reservation flow
        if self.pending_reservation or self.waiting_for_guest_choice or self.waiting_for_new_guest_count:
            if any(k in lower_q for k in ["yes", "no", "yep", "nope", "sure", "ok"]) or re.search(r'\b\d+\b', lower_q):
                return "reservation"

        # Check for menu
        if any(k in lower_q for k in ["menu", "dish", "food", "price", "cost", "have", "with", "contains",
                                      "vegan", "vegetarian", "spicy", "drink", "cocktail", "juice", "nut",
                                      "meal", "suggest", "recommend"]):
            return "menu"

        # Check for hours
        if any(k in lower_q for k in ["hour", "open", "close", "address",
                                      "phone", "location", "email", "website"]):
            return "hours"

        if not self.llm:
            return "general"

        chain = self.classifier_prompt | self.llm | StrOutputParser()
        result = chain.invoke({"question": question, "history": history_str}).strip().lower()
        valid = {"reservation", "cancellation", "menu", "hours", "general"}
        return result if result in valid else "general"

    def _handle_reservation(self, question: str, history_str: str) -> str:
        # Retrieve the real-time Israel clock
        israel_tz = ZoneInfo("Asia/Jerusalem")
        now = datetime.now(israel_tz)
        current_time_str = now.strftime("%Y-%m-%d %H:%M")

        # Explicitly reset state if user asks for a new/another reservation
        if any(word in question.lower() for word in ["new", "another", "start"]):
            self.pending_reservation = None
            self.waiting_for_guest_choice = False
            self.waiting_for_new_guest_count = False

        # Handle state where we are waiting for user to decide whether to change guest count after exceeding 8
        if self.waiting_for_guest_choice:
            lower_q = question.lower()

            # 1. Direct number input
            match = re.search(r'\b\d+\b', lower_q)
            if match:
                new_guests = int(match.group())
                self.waiting_for_guest_choice = False
                self.waiting_for_new_guest_count = False
                if self.pending_reservation:
                    self.pending_reservation["number_of_guests"] = new_guests
                # Explicitly override the question so the LLM doesn't extract the old number from history
                question = f"Change the number of guests to {new_guests}."

            # 2. Positive response
            elif any(w in lower_q for w in ["yes", "yeah", "sure", "ok", "yep"]):
                self.waiting_for_guest_choice = False
                self.waiting_for_new_guest_count = True
                return "Great! How many guests would you like to book for?"

            # 3. Negative response
            elif any(w in lower_q for w in ["no", "nope", "nah"]):
                self.waiting_for_guest_choice = False
                self.pending_reservation = None
                return "Is there anything else I can help you with?"

            # 4. Unrecognized input while waiting
            else:
                details_data, _ = get_restaurant_details_and_hours(self.db_path)
                phone = details_data.get("phone", "+972-540000000")
                return f"Sorry, it is not possible to book for more than 8 people. If you still wish to do so, please contact the restaurant at {phone}. Would you like to change the number of guests?"

        # Handle state where we are waiting for the new guest count after user agreed to change
        elif self.waiting_for_new_guest_count:
            match = re.search(r'\b\d+\b', question)
            if match:
                new_guests = int(match.group())
                self.waiting_for_new_guest_count = False
                if self.pending_reservation:
                    self.pending_reservation["number_of_guests"] = new_guests
                # Explicitly override the question so the LLM parses the new number
                question = f"Change the number of guests to {new_guests}."
            else:
                return "Please tell me how many guests you would like to book for (1 to 8)."

        # Prompt for extraction - explicitly telling the LLM to ignore history if creating a new reservation
        extract_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Extract reservation details. If the user asks for a 'new' or 'another' reservation, IGNORE previous reservation details from history. "
             "Otherwise, use history to fill in missing details. "
             "If the user is confirming a suggested alternative time, update the 'time' field accordingly. "
             "Return ONLY raw JSON with these keys: customer_name, date, time, number_of_guests, contact. "
             "The current date and time in Israel is " + current_time_str + ". "
                                                                            "If time is provided without AM/PM, use 24-hour format. "
                                                                            "Resolve relative dates like 'today' to exact YYYY-MM-DD format. "
                                                                            "Use null for fields that are missing."),
            ("human", "Chat History:\n{history}\n\nLatest Question: {question}")
        ])

        if not self.llm:
            return "Please call us directly to make a reservation!"

        chain = extract_prompt | self.llm | StrOutputParser()
        raw = chain.invoke({"question": question, "history": history_str})

        # Clean the output in case the LLM includes markdown formatting
        cleaned_raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            details = json.loads(cleaned_raw)
            # Merge with pending if exists (only for follow-up questions)
            if self.pending_reservation:
                for k, v in self.pending_reservation.items():
                    if not details.get(k): details[k] = v
            self.pending_reservation = details
        except json.JSONDecodeError:
            return "Sorry, I couldn't process your request. Please provide name, date, time, and number of guests."

        # Verify we have minimum required details
        details = self.pending_reservation
        if not details:
            return "Please provide your reservation details (name, date, time, and guests)."

        required = ["customer_name", "date", "time", "number_of_guests"]
        if not all(details.get(k) for k in required):
            return (
                "Please provide your full name, reservation date, time, and number of guests to book a table. "
                "Example: 'Table for 2, Sarah Connor, 01/01/2027 at 20:00'"
            )

        date_str = details["date"]
        time_str = details["time"]

        # --- GUEST LIMIT VALIDATION (MAX 8) ---
        try:
            num_guests = int(details.get("number_of_guests", 1))
        except (ValueError, TypeError):
            num_guests = 1

        if num_guests > 8:
            details_data, _ = get_restaurant_details_and_hours(self.db_path)
            phone = details_data.get("phone", "+972-540000000")
            self.waiting_for_guest_choice = True
            return (
                f"Sorry, it is not possible to book for more than 8 people. If you still wish to do so, please contact the restaurant at {phone}. "
                f"Would you like to change the number of guests?"
            )
        # --- END GUEST LIMIT VALIDATION ---

        # --- VALIDATION: Past Time and Opening Hours ---
        try:
            req_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            req_dt = req_dt.replace(tzinfo=israel_tz)

            # 1. Past Time Check
            if req_dt < now:
                return "Sorry, you cannot book a reservation in the past. Please choose a future date and time."

            # 2. Opening Hours Check
            _, hours = get_restaurant_details_and_hours(self.db_path)
            day_of_week = req_dt.strftime("%A")
            day_hours = next((h for h in hours if h["day_of_week"] == day_of_week), None)

            if not day_hours:
                return f"Sorry, the restaurant is closed on {day_of_week}s."

            req_h, req_m = map(int, time_str.split(':'))
            open_h, open_m = map(int, day_hours["open_time"].split(':'))
            close_h, close_m = map(int, day_hours["close_time"].split(':'))

            req_minutes = req_h * 60 + req_m
            open_minutes = open_h * 60 + open_m
            close_minutes = close_h * 60 + close_m

            if not (open_minutes <= req_minutes <= close_minutes):
                return f"Sorry, our operating hours on {day_of_week} are from {day_hours['open_time']} to {day_hours['close_time']}. Please choose a time within these hours."

        except ValueError:
            return "Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time."
        # --- END VALIDATION ---

        # Check availability
        is_free, alternatives = check_availability_and_alternatives(self.db_path, date_str, time_str)

        if not is_free:
            if alternatives:
                alt_text = " or ".join(alternatives)
                return (
                    f"Sorry, the time {time_str} is unavailable. "
                    f"Would you like to book one of these available times: {alt_text}?"
                )
            else:
                return f"Sorry, the time {time_str} is fully booked, and there are currently no nearby available alternative times."

        # Finalize Booking
        try:
            res_id = book_reservation(
                self.db_path,
                details["customer_name"],
                date_str,
                time_str,
                int(details["number_of_guests"]),
                details.get("contact")
            )

            # Clear state on success
            self.pending_reservation = None
            self.waiting_for_guest_choice = False
            self.waiting_for_new_guest_count = False
            self._notify_n8n({**details, "id": res_id}, event="reservation")

            return (
                f"✅ Reservation confirmed!\n"
                f"Name: {details['customer_name']}\n"
                f"Date: {details['date']} at {details['time']}\n"
                f"Number of guests: {details['number_of_guests']} · Reservation #{res_id}"
            )
        except Exception as e:
            return f"An error occurred while confirming your reservation: {str(e)}"

    def _handle_cancellation(self, question: str, history_str: str = "") -> str:
        """Handle cancellation flow with retry limits and history awareness."""
        extract_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Extract 'booking_id' (integer) and 'customer_name' (string) from the user message or conversation history. "
             "If 'booking_id' or 'customer_name' is missing or not explicitly stated, use null for that field. "
             "Return ONLY raw JSON with keys: id, name."),
            ("human", "Chat History:\n{history}\n\nLatest Question: {question}")
        ])

        if not self.llm:
            return "Please contact us directly to cancel a reservation."

        chain = extract_prompt | self.llm | StrOutputParser()
        try:
            raw = chain.invoke({"question": question, "history": history_str})
            cleaned_raw = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_raw)
            res_id = data.get("id")
            name = data.get("name")
        except Exception:
            res_id = None
            name = None

        if res_id:
            self.pending_cancellation_id = res_id
            self.cancellation_attempts = 0  # Reset counter on success
            if name:
                return self._execute_cancellation(res_id, name)
            else:
                return f"I found booking #{res_id}. Please provide your FULL NAME to verify and cancel."

        if name and self.pending_cancellation_id:
            res_id = self.pending_cancellation_id
            return self._execute_cancellation(res_id, name)

        # If we reached here, the user gave invalid or unexpected input
        self.cancellation_attempts += 1

        if self.cancellation_attempts >= 3:
            self.pending_cancellation_id = None
            self.cancellation_attempts = 0
            return "It seems we are having trouble processing your cancellation request. For further assistance, please contact the restaurant directly. How else can I help you today?"

        if self.pending_cancellation_id:
            return "I still need your FULL NAME to proceed with the cancellation."

        return "Sorry, I couldn't understand the cancellation request. Please provide your reservation number. It starts with # (e.g., #1)."

    def _get_reservation_details(self, res_id: int) -> dict:
        """Fetch reservation details from DB to include in the webhook payload."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Fetch reservation by ID - attempting a standard table name
                cursor.execute("SELECT * FROM reservations WHERE id = ?", (res_id,))
                row = cursor.fetchone()

                if row:
                    row_dict = dict(row)
                    # Gracefully handle common column names for date, time, and guests
                    date = row_dict.get("date") or row_dict.get("reservation_date")
                    time = row_dict.get("time") or row_dict.get("reservation_time")
                    guests = row_dict.get("number_of_guests") or row_dict.get("guests") or row_dict.get("party_size")

                    return {
                        "date": date,
                        "time": time,
                        "number_of_guests": guests
                    }
        except Exception as e:
            # If there's an error (e.g., table doesn't exist or diff schema), return empty dict
            pass
        return {}

    def _execute_cancellation(self, res_id: int, name: str) -> str:
        try:
            # 1. Fetch details BEFORE canceling (in case the record is deleted or modified)
            res_details = self._get_reservation_details(res_id)

            # 2. Cancel the reservation via DB helper
            cancel_reservation(self.db_path, res_id, name)

            # 3. Prepare payload with all available details
            payload = {"id": res_id, "name": name}
            if res_details:
                if res_details.get("date"): payload["date"] = res_details["date"]
                if res_details.get("time"): payload["time"] = res_details["time"]
                if res_details.get("number_of_guests"): payload["number_of_guests"] = res_details["number_of_guests"]

            self._notify_n8n(payload, event="cancellation")

            # Reset state variables after successful cancellation
            self.pending_cancellation_id = None
            self.cancellation_attempts = 0

            return f"✅ Reservation #{res_id} for {name} has been cancelled."

        except ValueError as e:
            # Name does not match booking ID - increment counter
            self.cancellation_attempts += 1

            if self.cancellation_attempts >= 3:
                self.pending_cancellation_id = None
                self.cancellation_attempts = 0
                return "For security reasons, I've stopped the cancellation process due to multiple mismatched details. Please contact the restaurant directly for help."

            # Return error message from database
            return str(e)

        except Exception:
            self.pending_cancellation_id = None
            self.cancellation_attempts = 0
            return "Something went wrong while cancelling."

    def _notify_n8n(self, data: dict, event: str) -> None:
        webhook_url = os.getenv("N8N_WEBHOOK_URL")
        if not webhook_url:
            print(f"[DEBUG] N8N_WEBHOOK_URL not configured, skipping webhook notification for event: {event}")
            return
        try:
            print(f"[DEBUG] Sending to n8n webhook: {webhook_url} with event={event}, data={data}")
            response = requests.post(webhook_url, json={**data, "event": event}, timeout=5)
            print(f"[DEBUG] n8n webhook response: {response.status_code} - {response.text}")
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to send webhook to n8n: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error in n8n webhook: {e}")

    def _build_menu_context(self, question: str) -> tuple[str, bool]:
        """Helper to build context for menu queries."""
        rows = search_menu_items(self.db_path, question)
        if rows:
            lines = [f"- {r['item_name']} ({r['category']}): {r['description']} | ${r['price']:.2f}" for r in rows]
            return "\n".join(lines), True

        rows = get_menu_items(self.db_path)
        lines = [f"- {r['item_name']} ({r['category']}): {r['description']} | ${r['price']:.2f}" for r in rows]
        return "\n".join(lines), True

    def _build_details_context(self) -> str:
        """Helper to build context for hours/details queries."""
        details, hours = get_restaurant_details_and_hours(self.db_path)
        if not details: return "No restaurant details found."
        details_text = f"Name: {details['name']}\nAddress: {details['address']}\nPhone: {details['phone']}"
        hours_lines = [f"- {h['day_of_week']}: {h['open_time']} to {h['close_time']}" for h in hours]
        return details_text + "\n\nOpening Hours:\n" + "\n".join(hours_lines)

    def answer(self, question: str, history: List[Dict[str, str]] = None) -> str:
        """Main method to route the question to the correct handler."""
        if history is None:
            history = []

        history_str = self._format_history(history)
        category = self.classify_question(question, history_str)

        if category == "reservation":
            return self._handle_reservation(question, history_str)
        elif category == "cancellation":
            return self._handle_cancellation(question, history_str)
        elif category == "menu":
            context, _ = self._build_menu_context(question)
            chain = self.answer_prompt | self.llm | StrOutputParser()
            return chain.invoke({"question": question, "history": history_str, "context": context})
        elif category == "hours":
            context = self._build_details_context()
            chain = self.answer_prompt | self.llm | StrOutputParser()
            return chain.invoke({"question": question, "history": history_str, "context": context})
        else:
            if self.llm:
                chain = self.general_prompt | self.llm | StrOutputParser()
                return chain.invoke({"question": question, "history": history_str})
            else:
                return "I can only help with menu questions, booking a table, or cancelling an existing reservation."
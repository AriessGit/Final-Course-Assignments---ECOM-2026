<div align="center">

# 🌊 Tasty Sea – Seafood | AI Restaurant Chatbot

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-OpenAI-1C3C3C?logo=langchain)](https://langchain.com)
[![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![n8n](https://img.shields.io/badge/Automation-n8n-FF6D5A?logo=n8n&logoColor=white)](https://n8n.io)
[![Gradio](https://img.shields.io/badge/UI-Gradio-F97316?logo=gradio&logoColor=white)](https://gradio.app)

**An intelligent restaurant assistant powered by LangChain + OpenAI, SQLite, and n8n automation.**

Handles menu queries, table reservations, and cancellations — with real-time notifications via Email, SMS, and Google Calendar.

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Environment Variables](#-environment-variables)
- [Usage](#-usage)
- [n8n Workflow](#-n8n-workflow)
- [Screenshots & Demo](#-screenshots--demo)
- [Conversation Examples](#-conversation-examples)
- [Testing Matrix](#-testing-matrix)

---

## 🎯 Overview

Tasty Sea is a full-stack AI chatbot for a seafood restaurant. It understands natural language, maintains conversational context, and automates end-to-end reservation workflows:

1. **User** chats via Gradio UI
2. **LangChain** classifies intent and extracts entities
3. **SQLite** stores reservations with validation
4. **n8n Webhook** triggers notifications on every booking/cancellation
5. **Email + SMS + Calendar** confirm the action in real time

---

## 🏗️ System Architecture

```
┌─────────────┐      ┌──────────────────────┐      ┌─────────────┐
│  Gradio UI  │─────▶│  LangChain Chatbot   │─────▶│  SQLite DB  │
│  (Frontend) │      │  • Intent Classifier │      │ • menu_items│
└─────────────┘      │  • Entity Extractor  │      │ • reservations
                     │  • Validation Logic  │      │ • opening_hours
                     └──────────┬───────────┘      └─────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   n8n Webhook       │
                     │   POST /restaurant  │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │ Google Calendar│  │    Email     │  │ Twilio SMS   │
      │  (Create/Del)  │  │  (SMTP)      │  │  (Send)      │
      └──────────────┘  └──────────────┘  └──────────────┘
```

**Flow:**
- **Reservation** → Create Calendar Event → Send Confirmation Email + SMS
- **Cancellation** → Delete Calendar Event → Send Cancellation Email + SMS

---

## ✨ Features

### 🤖 AI Conversational Engine
- **Intent Classification** — LLM-based routing between `menu`, `hours`, `reservation`, `cancellation`, and `general`
- **Entity Extraction** — Natural language parsing of names, dates, times, and guest counts
- **Context Memory** — Multi-turn conversations for collecting missing booking details
- **Human-like Responses** — Warm, friendly tone with restaurant-host personality

### 📅 Reservation System
- ✅ Real-time availability check (2-hour buffer between bookings)
- ✅ Opening hours validation
- ✅ Past-date blocking
- ✅ Guest limit enforcement (max 8 per table) with fallback options
- ✅ Alternative time suggestions when slot is taken

### 🔒 Secure Cancellation
- 🔐 Name verification against booking ID (case-insensitive)
- 🔐 3-attempt limit to prevent brute-force
- 🔐 Soft-delete (status = `cancelled`) for audit trail

### 📡 n8n Automation
- 🔗 Webhook trigger on every booking/cancellation
- 📧 HTML email confirmations (reservation + cancellation templates)
- 📱 Twilio SMS notifications
- 📅 Google Calendar event creation/deletion
- ⚖️ IF node splits flows by event type

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.10+ |
| **LLM Framework** | LangChain + OpenAI GPT-4o-mini |
| **Database** | SQLite3 |
| **UI** | Gradio |
| **Automation** | n8n (self-hosted) |
| **Notifications** | SMTP Email, Twilio SMS |
| **Calendar** | Google Calendar API |
| **Testing** | pytest / smoke tests |

---

## 🗃️ Database Schema

### Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `menu_items` | Restaurant menu | `item_name`, `category`, `price`, `is_vegetarian`, `is_spicy` |
| `reservations` | Booking records | `customer_name`, `date`, `time`, `number_of_guests`, `status` |
| `opening_hours` | Weekly schedule | `day_of_week`, `open_time`, `close_time` |
| `restaurant_details` | Business info | `name`, `address`, `phone`, `email`, `website` |

### Sample Data

**Menu Items (19 dishes):**
- Starters: Sea Bass Ceviche, Salmon Carpaccio, Crispy Calamari, Green Salad with Halloumi
- Mains: Grilled Sea Bass Fillet, Baked Whole Sea Bream, Seafood Pasta, Fish and Chips
- Desserts: Vanilla Creme Brulee, Crumb Cheesecake, Mixed Berry Sorbet
- Drinks: Chardonnay, Goldstar Beer, Margarita, Fresh Juices, Smoothies

**Opening Hours:**
| Day | Hours | Notes |
|-----|-------|-------|
| Mon–Wed | 12:00–22:00 | — |
| Thursday | 12:00–23:00 | — |
| Friday | 12:00–24:00 | Live music |
| Saturday | 11:00–24:00 | Weekend catch |
| Sunday | 12:00–21:00 | Family set menu |

---

## 📁 Project Structure

```
📦 restaurant-chatbot/
├── 📄 README.md                          # This file
├── 📄 .env                               # Environment configuration
├── 🐍 restaurant_chatbot.py              # Core chatbot engine (LangChain)
├── 🐍 restaurant_db.py                   # SQLite schema + query helpers
├── 🐍 restaurant_chatbot_app.py          # CLI entry point
├── 🐍 restaurant_chatbot_gradio.py       # Gradio web UI
├── 🐍 smoke_test_restaurant_chatbot.py   # Automated smoke tests
├── ⚙️ Class_Project.json                 # n8n workflow export
├── 🗃️ restaurant.sqlite                  # Local database (auto-created)
└── 📸 screenshots/                       # Demo images & video
    ├── main.png
    ├── n8n_diagram.jpg
    ├── webhook_parameters.jpg
    ├── IF_parameters.jpg
    ├── send_email_params.jpg
    ├── twilio_params.jpg
    ├── reservation_confirm.jpg
    ├── reservation_cancel.jpg
    ├── twilio_messege.jpg
    ├── calendarjpg.jpg
    ├── time_reservation.jpg
    ├── handal_pizza.jpg
    ├── canceling_1.jpg
    ├── canceling_2.jpg
    ├── DB_menu.jpg
    ├── DB_reservations.jpg
    └── Video.mp4
```

---

## 🚀 Setup & Installation

### 1. Clone & Install Dependencies

```bash
git clone <your-repo-url>
cd restaurant-chatbot
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Required packages:**
```
langchain>=0.2
langchain-openai>=0.1
gradio>=4.0
python-dotenv>=1.0
requests>=2.31
```

### 2. Configure Environment

The project includes a `.env` file with the required variable structure. You only need to fill in your actual API keys:

```bash
# The .env file is already included in the repo.
# Just edit it and replace the placeholder with your real OpenAI key:
```

**`.env` file contents:**
```env
OPENAI_API_KEY=your_openai_api_key_here

# n8n Webhook URL (Production)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/restaurant

# n8n Test URL (uncomment to use test webhook instead)
# N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/restaurant
```

**What to do:**
1. Open `.env` in your editor
2. Replace `your_openai_api_key_here` with your actual [OpenAI API key](https://platform.openai.com/api-keys)
3. Keep the `N8N_WEBHOOK_URL` as-is if running n8n locally on port 5678
4. If using n8n's test webhook (for development), uncomment the test URL and comment out the production one

> **Note:** The chatbot works in **offline fallback mode** without `OPENAI_API_KEY`, using keyword-based routing for basic menu/hours queries.

### 3. Initialize Database

The database auto-initializes on first run, seeding demo menu items, hours, and restaurant details.

### 4. Start n8n (in separate terminal)

```bash
docker run -it --rm   --name n8n   -p 5678:5678   -v ~/.n8n:/home/node/.n8n   n8nio/n8n
```

Import `Class_Project.json` into n8n and activate the workflow.

### 5. Launch the Chatbot

**Web UI (Gradio):**
```bash
python restaurant_chatbot_gradio.py
```
Open `http://127.0.0.1:7861`

**CLI Mode:**
```bash
python restaurant_chatbot_app.py
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API key for LLM classification & extraction |
| `N8N_WEBHOOK_URL` | ✅ | n8n webhook endpoint (e.g., `http://localhost:5678/webhook/restaurant`) |

> **Note:** The chatbot works in **offline fallback mode** without `OPENAI_API_KEY`, using keyword-based routing for basic menu/hours queries.

---

## 💬 Usage

### Example Interactions

**General conversation:**
```
User: Hello
Bot: Hello there! Welcome to Tasty Sea! How can I help you today?
```

**Menu query:**
```
User: Do you have vegetarian dishes?
Bot: Yes, we have a vegetarian dish: the Green Salad with Halloumi...
```

**Missing item handling:**
```
User: Do you have pizza?
Bot: I'm sorry, but we don't have pizza on the menu.
```

**Reservation:**
```
User: table for 4, Arie Ru, for today at 15:00
Bot: ✅ Reservation confirmed!
     Name: Arie Ru
     Date: 2026-07-27 at 15:00
     Number of guests: 4 · Reservation #15
```

**Cancellation:**
```
User: cancel reservation 15
Bot: Reservation ID #15 not found for 'null'. Please provide FULL NAME.
User: Arie Ru
Bot: ✅ Reservation #15 for Arie Ru has been cancelled.
```

---

## ⚙️ n8n Workflow

### Webhook Configuration
- **Method:** POST
- **Path:** `restaurant`
- **URL:** `http://localhost:5678/webhook/restaurant`
- **Authentication:** None

### IF Node Logic
```
Condition: {{ $json.body.event }}  equals  "reservation"
  ├─ TRUE  → Reservation Flow
  │           ├─ Create Google Calendar event
  │           ├─ Respond to Webhook
  │           ├─ Send Email (HTML confirmation)
  │           └─ Send Twilio SMS
  │
  └─ FALSE → Cancellation Flow
              ├─ Get Calendar events by Booking ID
              ├─ Delete Calendar event
              ├─ Respond to Webhook
              ├─ Send Email (HTML cancellation)
              └─ Send Twilio SMS
```

### Notification Channels

| Channel | Reservation | Cancellation |
|---------|-------------|--------------|
| **Email** | ✅ HTML confirmation (blue theme) | ✅ HTML cancellation (red theme) |
| **SMS** | ✅ Twilio confirmation | ✅ Twilio cancellation |
| **Calendar** | ✅ Create event | ✅ Delete event |
| **Webhook Response** | ✅ "Reservation confirmed..." | ✅ "Cancellation processed..." |

---

## 📸 Screenshots & Demo

### 🖥️ Gradio Chat Interface
![Main Chat UI](screenshots/main.png)

### 🏗️ n8n Workflow Diagram
![n8n Diagram](screenshots/n8n_diagram.jpg)

### 🔗 Webhook Node Parameters
![Webhook Params](screenshots/webhook_parameters.jpg)

### ⚖️ IF Node Parameters
![IF Params](screenshots/IF_parameters.jpg)

### 📧 Email Configuration
![Email Params](screenshots/send_email_params.jpg)

### 📱 Twilio SMS Configuration
![Twilio Params](screenshots/twilio_params.jpg)

### ✅ Reservation Confirmation Email
![Reservation Confirm](screenshots/reservation_confirm.jpg)

### ❌ Cancellation Email
![Reservation Cancel](screenshots/reservation_cancel.jpg)

### 📱 SMS Notifications (Phone)
![Twilio Message](screenshots/twilio_messege.jpg)

### 📅 Google Calendar Integration
![Calendar](screenshots/calendarjpg.jpg)

### ⏰ Time Validation (Past Date Blocked)
![Time Validation](screenshots/time_reservation.jpg)

### 🍕 Missing Item Handling
![Pizza Query](screenshots/handal_pizza.jpg)

### 🔐 Secure Cancellation Flow
![Cancel Step 1](screenshots/canceling_1.jpg)
![Cancel Step 2](screenshots/canceling_2.jpg)

### 🗃️ Database Browser
![DB Menu](screenshots/DB_menu.jpg)
![DB Reservations](screenshots/DB_reservations.jpg)

### 🎬 Full Demo Video
Watch the end-to-end demonstration:

https://github.com/user-attachments/assets/Video.mp4

*(Shows: greeting → menu query → hours → recommendation → reservation with validation → SMS/Email/Calendar confirmation → new reservation → cancellation with name verification → cancellation notifications)*

---

## 🎭 Conversation Examples

### Scenario 1: General Inquiry
```text
👤 User: Tell me about the place / restaurant
🤖 Bot: Absolutely! Tasty Sea is a cozy seafood restaurant where we pride ourselves 
        on serving the freshest catches from the ocean...
```

### Scenario 2: Opening Hours
```text
👤 User: What are your opening hours?
🤖 Bot: Our opening hours at Tasty Sea are as follows:
        • Monday: 12:00 to 22:00
        • Tuesday: 12:00 to 22:00
        • ...
```

### Scenario 3: Menu Recommendation
```text
👤 User: Can you recommend a meal?
🤖 Bot: I recommend trying the Grilled Sea Bass Fillet. It's a fresh sea bass fillet 
        served on a bed of root vegetables and cauliflower cream, and it's priced at $128.
```

### Scenario 4: Reservation with Past-Date Validation
```text
👤 User: table for 4, Arie Ru, for 24/07/2026, at 6pm
🤖 Bot: Sorry, you cannot book a reservation in the past. Please choose a future date and time.

👤 User: ohh sorry, i want to order for today, at 15:00
🤖 Bot: ✅ Reservation confirmed!
        Name: Arie Ru
        Date: 2026-07-27 at 15:00
        Number of guests: 4 · Reservation #15
```

### Scenario 5: New Reservation for a Friend
```text
👤 User: I want to make a new reservation for my friend
🤖 Bot: Please provide your full name, reservation date, time, and number of guests...

👤 User: Ilya Cohel, table for 2, for tomorrow, at 13 pm
🤖 Bot: ✅ Reservation confirmed!
        Name: Ilya Cohel
        Date: 2026-07-28 at 13:00
        Number of guests: 2 · Reservation #16
```

### Scenario 6: Secure Cancellation
```text
👤 User: I want to cancel order for Arie Ru
🤖 Bot: Reservation ID #16 not found for 'Arie Ru'. Please provide FULL NAME.

👤 User: Reservation #15 Arie Ru
🤖 Bot: Please provide your full name, reservation date, time, and number of guests...

👤 User: cancel reservation 15
🤖 Bot: Reservation ID #15 not found for 'null'. Please provide FULL NAME.

👤 User: Arie Ru
🤖 Bot: ✅ Reservation #15 for Arie Ru has been cancelled.
```

---

## 🧪 Testing Matrix

| # | Test Scenario | Expected Result | Status |
|---|---------------|-----------------|--------|
| 1 | Greeting / general chat | Friendly host response | ✅ Pass |
| 2 | Menu query (vegetarian) | Returns vegetarian items | ✅ Pass |
| 3 | Missing item (pizza) | Polite "not on menu" response | ✅ Pass |
| 4 | Opening hours request | Full weekly schedule | ✅ Pass |
| 5 | Meal recommendation | Best dish from context | ✅ Pass |
| 6 | Reservation with all details | Confirmed + webhook fired | ✅ Pass |
| 7 | Reservation in the past | Rejected with explanation | ✅ Pass |
| 8 | Reservation outside hours | Rejected with hour range | ✅ Pass |
| 9 | Overlapping reservation | Alternative times suggested | ✅ Pass |
| 10 | Guest limit > 8 | Offer to change count | ✅ Pass |
| 11 | Multi-turn reservation | Collects missing fields | ✅ Pass |
| 12 | Cancellation with wrong name | Error + retry prompt | ✅ Pass |
| 13 | Cancellation with correct name | Cancelled + webhook fired | ✅ Pass |
| 14 | n8n reservation branch | Email + SMS + Calendar created | ✅ Pass |
| 15 | n8n cancellation branch | Email + SMS + Calendar deleted | ✅ Pass |

---

## 📝 License

This project was built as a capstone assignment for an AI Advanced course.

## 🙋‍♂️ Author

Built with ❤️ for **Tasty Sea – Seafood**

---

<div align="center">

**[⬆ Back to Top](#-tasty-sea--seafood--ai-restaurant-chatbot)**

</div>

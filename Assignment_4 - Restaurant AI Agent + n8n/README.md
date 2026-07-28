# 🌊 Tasty Sea – Seafood Restaurant Chatbot

A full-stack AI-powered restaurant reservation and assistance system for **Tasty Sea – Seafood**, featuring a conversational chatbot built with LangChain & OpenAI, a Gradio web interface, SQLite database, and n8n workflow automation for calendar events, email confirmations, and SMS notifications.

---

## 🎬 Watch the Demo First

> 📹 **Please watch the video before reading the technical section - it shows the whole flow end to end 
(chat → database → calendar → email → SMS) and makes everything below much easier to follow.**
>
**The video showcases:**
> - General conversation and restaurant information
> - Menu queries and recommendations
> - Opening hours inquiries
> - **Reservation booking** with real-time validation
> - **Reservation cancellation** with security verification
> - Automated **email confirmations** via SMTP (Simple Mail Transfer Protocol)
> - Automated **SMS notifications** via Twilio
> - **Google Calendar** event creation and deletion
> - n8n workflow orchestration

>  https://github.com/user-attachments/assets/f3ae1f76-e7b2-4178-ac8d-3c3dff01f07c
>

---

## ✨ Features

### Chatbot Capabilities
| Feature | Description |
|---------|-------------|
| 💬 **General Chat** | Warm, human-like conversation about the restaurant |
| 🍽️ **Menu Queries** | Search dishes by name, category, dietary preferences (vegetarian, spicy) |
| ⭐ **Recommendations** | AI-powered meal recommendations based on menu data |
| 🕐 **Opening Hours** | Real-time answers about operating hours and location |
| 📅 **Reservations** | Book tables with validation (past dates, opening hours, availability, max 8 guests) |
| ❌ **Cancellations** | Secure cancellation with booking ID + full name verification |

### Automation (via n8n)
| Integration | Action |
|-------------|--------|
| 📧 **Email** | HTML confirmation & cancellation emails via SMTP |
| 📱 **SMS** | Text notifications via Twilio |
| 📆 **Google Calendar** | Auto-create events on booking, auto-delete on cancellation |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Gradio UI     │────▶│  Python Chatbot  │────▶│  SQLite DB      │
│  (Port 7861)    │     │  (LangChain+GPT) │     │  (reservations, │
└─────────────────┘     └──────────────────┘     │   menu, hours)  │
                            │                      └─────────────────┘
                            │                              │
                            ▼                              ▼
                    ┌───────────────┐              ┌───────────────┐
                    │   n8n Webhook │              │   Google      │
                    │  (Port 5678)  │─────────────▶│   Calendar    │
                    └───────┬───────┘              └───────────────┘
                            │
                    ┌───────┴───────┐
                    │  Twilio SMS   │
                    │  SMTP Email   │
                    └───────────────┘
```

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **LangChain** + **OpenAI GPT-4o-mini** for intent classification & entity extraction
- **SQLite** for local data persistence
- **Gradio** for the web chat interface
- **n8n** (Docker) for no-code workflow automation
- **Twilio API** for SMS notifications
- **SMTP** for transactional emails
- **Google Calendar API** for event management
- **Docker Compose** for n8n deployment

---

## 📁 Project Structure

```
.
├── restaurant_chatbot.py          # Core chatbot logic (RAG + state management)
├── restaurant_chatbot_gradio.py   # Gradio web UI entrypoint
├── restaurant_chatbot_app.py      # CLI entrypoint
├── restaurant_db.py               # SQLite helpers & seed data
├── Class_Project.json             # n8n workflow export (import into n8n)
├── docker-compose.yml             # n8n Docker setup
├── example.env                    # Environment variables template
└── restaurant.sqlite              # Auto-generated SQLite database
```

---

## 🚀 Setup & Installation

### 1. Clone & Install Dependencies

```bash
git clone <your-repo-url>
cd tasty-sea-chatbot
pip install -r requirements.txt  # langchain, langchain-openai, gradio, python-dotenv, requests
```

### 2. Configure Environment Variables

> ⚠️ **Important:** Rename `example.env` to `.env` by removing the word **"example"** from the filename:
> ```bash
> mv example.env .env
> ```

> 🔑 **Then, open `.env` and replace all placeholder values with your own API keys and credentials:**
> - `OPENAI_API_KEY` – Your OpenAI API key
> - `N8N_WEBHOOK_URL` – Your n8n webhook URL (local or production)
> - SMTP credentials in n8n
> - Twilio credentials in n8n
> - Google Calendar OAuth in n8n

### 3. Start n8n (Docker)

```bash
docker-compose up -d
```

n8n will be available at `http://localhost:5678`

### 4. Import the n8n Workflow

1. Open n8n at `http://localhost:5678`
2. Go to **Workflows** → **Import from File**
3. Select `Class_Project.json`
4. Configure your credentials (SMTP, Twilio, Google Calendar)

### 5. Launch the Chatbot

**Web UI (Gradio):**
```bash
python restaurant_chatbot_gradio.py
```
Open `http://127.0.0.1:7861` in your browser.

**CLI Mode:**
```bash
python restaurant_chatbot_app.py
```

---

## 🗄️ Database Schema

### `menu_items`
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `item_name` | TEXT | Dish name |
| `category` | TEXT | Starter / Main / Dessert / Drinks |
| `description` | TEXT | Dish description |
| `price` | REAL | Price in USD |
| `is_vegetarian` | INTEGER | 1 = vegetarian |
| `is_spicy` | INTEGER | 1 = spicy |
| `is_available` | INTEGER | 1 = available |

### `reservations`
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (Booking ID) |
| `customer_name` | TEXT | Full name |
| `date` | TEXT | Reservation date (YYYY-MM-DD) |
| `time` | TEXT | Reservation time (HH:MM) |
| `number_of_guests` | INTEGER | Party size (max 8) |
| `contact` | TEXT | Phone/email (optional) |
| `status` | TEXT | `confirmed` or `cancelled` |
| `created_at` | TIMESTAMP | Booking timestamp |

### `opening_hours`
Stores daily operating hours with special notes (e.g., "Live music in the evening").

---

## 🔗 n8n Workflow

The `Class_Project.json` workflow handles two event types:

### 🟢 Reservation Event (`event: "reservation"`)
1. **Webhook** receives booking data from the chatbot
2. **Create Google Calendar event** (2-hour duration, Asia/Jerusalem timezone)
3. **Respond to Webhook** with confirmation text
4. **Send Email** (HTML confirmation with booking details)
5. **Send SMS** (Twilio confirmation text)

### 🔴 Cancellation Event (`event: "cancellation"`)
1. **Webhook** receives cancellation data
2. **Get many events** from Google Calendar (search by Booking ID)
3. **Delete an event** from Google Calendar
4. **Respond to Webhook** with cancellation text
5. **Send Email** (HTML cancellation notice)
6. **Send SMS** (Twilio cancellation text)

---

## 📸 Screenshots

### Chatbot Interface
<img width="1333" height="733" alt="Image" src="https://github.com/user-attachments/assets/0f568d5e-6cf8-4b95-80b8-c1081493f47e" />

### Reservation Booking
<img width="679" height="721" alt="Image" src="https://github.com/user-attachments/assets/fbbeba34-ca92-44b8-9cb6-8f65826c238f" />

<img width="1159" height="724" alt="Image" src="https://github.com/user-attachments/assets/008153dd-952c-4535-a046-95b0b4985a70" />

### Cancellation Flow
<img width="693" height="573" alt="Image" src="https://github.com/user-attachments/assets/aece800d-79e8-49f1-b8e9-71d23b134188" />

<img width="648" height="589" alt="Image" src="https://github.com/user-attachments/assets/f0e32994-e159-4c8c-9267-c3a427382d15" />


### Email Notifications
<img width="884" height="560" alt="Image" src="https://github.com/user-attachments/assets/bebdd3cc-c35f-4040-b65a-5922f9b15eef" />

<img width="902" height="595" alt="Image" src="https://github.com/user-attachments/assets/b3f899c2-b953-4f3e-8821-c14f4d9fdf35" />


### SMS Notifications
<img width="276" height="610" alt="Image" src="https://github.com/user-attachments/assets/6b75d6d2-0203-4ad8-8dd1-a0dbb097e31c" />


### Google Calendar
<img width="424" height="452" alt="Image" src="https://github.com/user-attachments/assets/d2b9ecd8-02ad-42e0-b459-7fe7931002bf" />


### n8n Configuration
<img width="1113" height="540" alt="Image" src="https://github.com/user-attachments/assets/0cea05ca-a65b-4493-9b7d-a26ea39c3f62" />

<img width="935" height="580" alt="Image" src="https://github.com/user-attachments/assets/f4721309-30a3-43cc-8926-2c595e4e19c0" />

<img width="1024" height="671" alt="Image" src="https://github.com/user-attachments/assets/0d561a68-5f92-49c0-800c-10c0c2273b11" />

<img width="939" height="671" alt="Image" src="https://github.com/user-attachments/assets/43d99263-f788-4979-8e4a-88834d686908" />

<img width="939" height="668" alt="Image" src="https://github.com/user-attachments/assets/c735a719-392b-4517-9c8e-4ead75fd8fbd" />

### Database
<img width="1304" height="318" alt="Image" src="https://github.com/user-attachments/assets/5c2e9166-6989-4d93-9042-b1bd3e2c06f4" />

<img width="1308" height="624" alt="Image" src="https://github.com/user-attachments/assets/4efa3691-53e1-4fee-bdd2-ab4921e431de" />


---

## 💡 Usage Examples

### General Conversation
```
User: Hello
Bot: Hello there! Welcome to Tasty Sea! How can I help you today?

User: Tell me about the place
Bot: Absolutely! Tasty Sea is a cozy seafood restaurant...
```

### Menu Queries
```
User: Do you have vegetarian dishes?
Bot: Yes, we have a vegetarian dish: the Green Salad with Halloumi...

User: Do you have pizza?
Bot: I'm sorry, but we don't have pizza on the menu.
```

### Booking a Table
```
User: table for 4, Arie Ru, for today at 15:00
Bot: ✅ Reservation confirmed!
     Name: Arie Ru
     Date: 2026-07-27 at 15:00
     Number of guests: 4 · Reservation #15
```

### Cancelling a Reservation
```
User: cancel reservation 15
Bot: Reservation ID #15 not found. Please provide FULL NAME.

User: Arie Ru
Bot: ✅ Reservation #15 for Arie Ru has been cancelled.
```

---

## ⚙️ Validation Rules

The chatbot enforces several business rules:

1. **Past Date/Time** – Cannot book in the past
2. **Opening Hours** – Must be within operating hours for that day
3. **Availability** – 2-hour buffer between reservations; suggests alternatives if taken
4. **Guest Limit** – Maximum 8 guests per booking (suggests contacting restaurant for larger parties)
5. **Cancellation Security** – Requires both Booking ID and matching full name; 3-attempt limit

---

## 📝 License

This project was built as a class project for educational purposes.

---

**Made with 🐟🦐🌊 for Tasty Sea – Seafood**

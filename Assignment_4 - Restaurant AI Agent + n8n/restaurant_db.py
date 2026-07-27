"""SQLite setup and query helpers for the restaurant chatbot."""

import re
from typing import Any, Dict, List, Tuple, cast, Optional
from datetime import datetime, timedelta
import sqlite3

def initialize_database(db_path: str = "restaurant.sqlite") -> None:
    """Create tables and seed starter data if this is a new database."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS menu_items (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name     TEXT NOT NULL,
                category      TEXT NOT NULL,
                description   TEXT NOT NULL,
                price         REAL NOT NULL,
                is_vegetarian INTEGER NOT NULL DEFAULT 0,
                is_spicy      INTEGER NOT NULL DEFAULT 0,
                is_available  INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS restaurant_details (
                id      INTEGER PRIMARY KEY CHECK (id = 1),
                name    TEXT NOT NULL,
                address TEXT NOT NULL,
                phone   TEXT NOT NULL,
                email   TEXT NOT NULL,
                website TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS opening_hours (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                day_of_week TEXT NOT NULL UNIQUE,
                open_time   TEXT NOT NULL,
                close_time  TEXT NOT NULL,
                notes       TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                date          TEXT NOT NULL,
                time          TEXT NOT NULL,
                number_of_guests    INTEGER NOT NULL,
                contact       TEXT,
                status        TEXT NOT NULL DEFAULT 'confirmed',
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        _seed_if_empty(conn)


def _seed_if_empty(conn: sqlite3.Connection) -> None:
    """Insert a small demo dataset once, keeping reruns idempotent."""
    has_menu    = conn.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0] > 0
    has_details = conn.execute("SELECT COUNT(*) FROM restaurant_details").fetchone()[0] > 0
    has_hours   = conn.execute("SELECT COUNT(*) FROM opening_hours").fetchone()[0] > 0

    if not has_menu:
        menu_rows = [
            ("Sea Bass Ceviche", "Starter", "Fresh sea bass, red onion, cilantro, chili, and lime juice", 62.0, 0, 1, 1),
            ("Salmon Carpaccio", "Starter", "Thin salmon slices, olive oil, capers, and parmesan", 58.0, 0, 0, 1),
            ("Crispy Calamari", "Starter", "Fried calamari rings in a crispy coating with garlic aioli", 54.0, 0, 0, 1),
            ("Green Salad with Halloumi", "Starter", "Crispy lettuce, cherry tomatoes, candied pecans, and seared halloumi", 48.0, 1, 0, 1),
            ("Grilled Sea Bass Fillet", "Main", "Fresh sea bass fillet served on a bed of root vegetables and cauliflower cream", 128.0, 0, 0, 1),
            ("Baked Whole Sea Bream", "Main", "Oven-baked sea bream with herbs, lemon, and olive oil", 115.0, 0, 0, 1),
            ("Seafood Pasta", "Main", "Shrimp, calamari, and mussels in a butter, garlic, and white wine sauce", 98.0, 0, 0, 1),
            ("Fish and Chips", "Main", "Beer-battered cod pieces, served with fries and tartar sauce", 78.0, 0, 0, 1),
            ("Vanilla Creme Brulee", "Dessert", "Rich vanilla cream with a caramelized sugar layer", 48.0, 1, 0, 1),
            ("Crumb Cheesecake", "Dessert", "Classic cold cheesecake with buttery crumb topping", 45.0, 1, 0, 1),
            ("Mixed Berry Sorbet", "Dessert", "3 scoops of sweet and sour mixed berry sorbet", 36.0, 1, 0, 1),
            ("Glass of Chardonnay", "Drinks", "Dry white wine, Yiron vineyard", 42.0, 1, 0, 1),
            ("Draft Goldstar Beer", "Drinks", "1/3 or 1/2 liter of beloved Israeli beer", 32.0, 1, 0, 1),
            ("Margarita Cocktail", "Drinks", "Tequila, triple sec, lime juice served frozen", 48.0, 1, 0, 1),
            ("Fresh Orange Juice", "Drinks", "Freshly squeezed", 22.0, 1, 0, 1),
            ("Pomegranate Juice", "Drinks", "Freshly squeezed", 26.0, 1, 0, 1),
            ("Mint Lemonade Slush", "Drinks", "Lemonade with fresh mint leaves and crushed ice", 20.0, 1, 0, 1),
            ("Tropical Smoothie", "Drinks", "Mango, pineapple, and melon on a water or milk base", 32.0, 1, 0, 1),
            ("Strawberry Banana Smoothie", "Drinks", "Classic strawberry and banana on a milk or orange juice base", 30.0, 1, 0, 1),
        ]
        conn.executemany(
            """INSERT INTO menu_items (item_name, category, description, price, is_vegetarian, is_spicy, is_available) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            menu_rows,
        )

    if not has_details:
        conn.execute(
            """INSERT INTO restaurant_details (id, name, address, phone, email, website) VALUES (1, ?, ?, ?, ?, ?)""",
            ("Tasty Sea - Seafood", "364 Ben Yehuda , Tel-Aviv", "+972-540000000", "hello@tasty.sea.example.il", "www.tastysea.example.il"),
        )

    if not has_hours:
        hours_rows = [
            ("Monday", "12:00", "22:00", ""), ("Tuesday", "12:00", "22:00", ""), ("Wednesday", "12:00", "22:00", ""),
            ("Thursday", "12:00", "23:00", ""), ("Friday", "12:00", "24:00", "Live music in the evening"),
            ("Saturday", "11:00", "24:00", "Special weekend catch available"), ("Sunday", "12:00", "21:00", "Family set menu available"),
        ]
        conn.executemany(
            """INSERT INTO opening_hours (day_of_week, open_time, close_time, notes) VALUES (?, ?, ?, ?)""",
            hours_rows,
        )


def get_menu_items(db_path: str) -> List[Dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT item_name, category, description, price, is_vegetarian, is_spicy, is_available FROM menu_items ORDER BY category, item_name").fetchall()
    return [cast(Dict[str, Any], dict(row)) for row in rows]


def search_menu_items(db_path: str, query: str) -> List[Dict[str, Any]]:
    clean_query = re.sub(r'[^\w\s]', '', query)
    ignore_words = {"what", "which", "how", "you", "have", "are", "the", "in", "on", "menu", "dish", "dishes", "food", "list", "show", "me", "all", "can", "tell", "do", "options", "suggest", "recommend", "meal", "recommendation"}
    tokens = [t.strip().lower() for t in clean_query.split() if len(t.strip()) >= 3 and t.strip().lower() not in ignore_words]

    if not tokens: return get_menu_items(db_path)

    where_clauses = []
    params = []
    is_veg_req = False
    is_spicy_req = False

    for token in tokens[:6]:
        if token in ["vegetarian", "vegan", "veg"]: is_veg_req = True
        elif token in ["spicy", "hot"]: is_spicy_req = True
        else:
            where_clauses.append("(LOWER(item_name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(category) LIKE ?)")
            wildcard = f"%{token}%"
            params.extend([wildcard, wildcard, wildcard])

    sql = "SELECT item_name, category, description, price, is_vegetarian, is_spicy, is_available FROM menu_items"
    conditions = []
    if where_clauses: conditions.append("(" + " OR ".join(where_clauses) + ")")
    if is_veg_req: conditions.append("(is_vegetarian = 1)")
    if is_spicy_req: conditions.append("(is_spicy = 1)")
    if conditions: sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY category, item_name"

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
    return [cast(Dict[str, Any], dict(row)) for row in rows]


def get_restaurant_details_and_hours(db_path: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        details_row = conn.execute("SELECT name, address, phone, email, website FROM restaurant_details WHERE id = 1").fetchone()
        hours_rows = conn.execute("SELECT day_of_week, open_time, close_time, notes FROM opening_hours ORDER BY id").fetchall()
    details = cast(Dict[str, Any], dict(details_row)) if details_row else {}
    hours = [cast(Dict[str, Any], dict(row)) for row in hours_rows]
    return details, hours


def book_reservation(db_path: str, customer_name: str, date: str, time: str, number_of_guests: int, contact: str = None) -> int:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("INSERT INTO reservations (customer_name, date, time, number_of_guests, contact) VALUES (?, ?, ?, ?, ?)", (customer_name, date, time, number_of_guests, contact))
        return cursor.lastrowid

def find_cancellable_reservation(db_path: str, name: str, date: str, time: str) -> Optional[int]:
    """Finds a reservation ID matching name, date, and time."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        # Case-insensitive check for name
        cursor = conn.execute("""
            SELECT id FROM reservations 
            WHERE LOWER(customer_name) = LOWER(?) 
            AND date = ? 
            AND time = ?
            AND status = 'confirmed'
        """, (name, date, time))
        row = cursor.fetchone()
        return row['id'] if row else None


def cancel_reservation(db_path: str, res_id: int, customer_name: str) -> dict:
    """Cancels a reservation only if the booking ID and customer full name match and returns its details."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check if booking exists and name matches (case-insensitive)
    cursor.execute("""
        SELECT * FROM reservations 
        WHERE id = ? AND LOWER(customer_name) = LOWER(?)
    """, (res_id, customer_name))

    row = cursor.fetchone()

    if not row:
        conn.close()
        raise ValueError(f"Reservation ID #{res_id} not found for '{customer_name}'. Please provide FULL NAME.")

    res_data = dict(row)

    # Instead of deleting the reservation, mark it as cancelled so it can be removed manually later.
    cursor.execute("UPDATE reservations SET status = 'cancelled' WHERE id = ?", (res_id,))
    conn.commit()
    conn.close()

    return res_data


def get_reservations(db_path: str, customer_name: str = None) -> list:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        if customer_name:
            rows = conn.execute("SELECT * FROM reservations WHERE status='confirmed' AND customer_name LIKE ?", (f"%{customer_name}%",)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM reservations WHERE status='confirmed'").fetchall()
        return [dict(r) for r in rows]


def check_availability_and_alternatives(db_path: str, req_date: str, req_time: str) -> tuple[bool, list[str]]:
    """
    Checks if there is a two-hour overlap with an existing reservation.
    Returns (True, []) if available.
    Returns (False, [alt_time1, alt_time2]) if occupied, including suggestions for two hours before/after.
    """
    try:
        # Convert date and time into a datetime object for easier calculations
        req_dt = datetime.strptime(f"{req_date} {req_time}", "%Y-%m-%d %H:%M")
    except ValueError:
        return False, []

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        # Retrieve all confirmed reservations for the requested date
        rows = conn.execute(
            "SELECT time FROM reservations WHERE date = ? AND status = 'confirmed'",
            (req_date,)
        ).fetchall()

    conflicts = []
    for row in rows:
        try:
            existing_dt = datetime.strptime(f"{req_date} {row['time']}", "%Y-%m-%d %H:%M")
            # If the difference between reservations is less than 7200 seconds (two hours), there is a conflict
            if abs((req_dt - existing_dt).total_seconds()) < 7200:
                conflicts.append(existing_dt)
        except ValueError:
            continue

    # If there are no conflicts, the requested time is available
    if not conflicts:
        return True, []

    # If the time is occupied, calculate two hours before and two hours after alternatives
    alt_before = req_dt - timedelta(hours=2)
    alt_after = req_dt + timedelta(hours=2)

    # Helper function that checks whether a specific alternative time is available
    def is_time_free(check_dt: datetime) -> bool:
        for row in rows:
            try:
                ext_dt = datetime.strptime(f"{req_date} {row['time']}", "%Y-%m-%d %H:%M")
                if abs((check_dt - ext_dt).total_seconds()) < 7200:
                    return False
            except ValueError:
                pass
        return True

    suggestions = []
    if is_time_free(alt_before):
        suggestions.append(alt_before.strftime("%H:%M"))
    if is_time_free(alt_after):
        suggestions.append(alt_after.strftime("%H:%M"))

    return False, suggestions
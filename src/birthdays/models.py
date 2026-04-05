"""Birthday database operations."""

from datetime import date, datetime

from src.db import get_db

CATEGORIES = ["Family", "Friends", "Work", "Other"]


def get_all():
    """Get all birthdays sorted by days until next birthday."""
    with get_db("birthdays.db") as conn:
        rows = conn.execute("SELECT * FROM birthday ORDER BY date").fetchall()
    birthdays = [dict(row) for row in rows]
    for b in birthdays:
        b["date_obj"] = date.fromisoformat(b["date"])
        b["days_until"] = days_until_birthday(b["date_obj"])
        b["age_next"] = age_on_next_birthday(b["date_obj"])
        b["has_year"] = b["date_obj"].year != 1900
    birthdays.sort(key=lambda b: b["days_until"])
    return birthdays


def add(name, date_str, category="Other", notes=""):
    """Add a birthday. date_str: MM-DD or YYYY-MM-DD."""
    d = _parse_date(date_str)
    with get_db("birthdays.db") as conn:
        conn.execute(
            "INSERT INTO birthday (name, date, category, notes) VALUES (?, ?, ?, ?)",
            (name, d.isoformat(), category, notes),
        )


def edit(birthday_id, name=None, date_str=None, category=None, notes=None):
    """Edit an existing birthday."""
    with get_db("birthdays.db") as conn:
        if name is not None:
            conn.execute("UPDATE birthday SET name = ? WHERE id = ?", (name, birthday_id))
        if date_str is not None:
            d = _parse_date(date_str)
            conn.execute("UPDATE birthday SET date = ? WHERE id = ?", (d.isoformat(), birthday_id))
        if category is not None:
            conn.execute("UPDATE birthday SET category = ? WHERE id = ?", (category, birthday_id))
        if notes is not None:
            conn.execute("UPDATE birthday SET notes = ? WHERE id = ?", (notes, birthday_id))


def delete(birthday_id):
    """Delete a birthday."""
    with get_db("birthdays.db") as conn:
        conn.execute("DELETE FROM birthday WHERE id = ?", (birthday_id,))


def days_until_birthday(d):
    """Calculate days until next birthday."""
    today = datetime.today().date()
    this_year = d.replace(year=today.year)
    if this_year < today:
        this_year = d.replace(year=today.year + 1)
    return (this_year - today).days


def age_on_next_birthday(d):
    """Calculate age on next birthday. Returns None if year is 1900 (unknown)."""
    if d.year == 1900:
        return None
    today = datetime.today().date()
    this_year = d.replace(year=today.year)
    if this_year >= today:
        return today.year - d.year
    return today.year - d.year + 1


def _parse_date(date_str):
    """Parse MM-DD or YYYY-MM-DD into a date object. Uses 1900 for unknown year."""
    parts = date_str.split("-")
    try:
        if len(parts) == 2:
            month, day = int(parts[0]), int(parts[1])
            return date(1900, month, day)
        elif len(parts) == 3:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError as e:
        raise ValueError(f"Invalid date '{date_str}': {e}") from e
    raise ValueError(f"Invalid date format: {date_str}. Use MM-DD or YYYY-MM-DD.")

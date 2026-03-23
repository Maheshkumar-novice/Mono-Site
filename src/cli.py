"""Admin CLI for managing feeds and birthdays."""

import click

from src.db import init_feed_db, init_birthdays_db, seed_default_feeds


@click.group()
def main():
    """Mono-Site admin CLI."""
    pass


# ── Feed commands ──────────────────────────────────────────────

@main.group()
def feed():
    """Manage RSS feeds."""
    pass


@feed.command("list")
def feed_list():
    """List all feeds."""
    init_feed_db()
    from src.feed.models import get_all_feeds

    feeds = get_all_feeds()
    if not feeds:
        click.echo("No feeds. Run 'mono-cli feed seed' to add defaults.")
        return
    for f in feeds:
        click.echo(f"  [{f['id']}] {f['title'] or 'Untitled'} — {f['url']}")


@feed.command("add")
@click.argument("url")
def feed_add(url):
    """Add a new feed URL."""
    init_feed_db()
    import feedparser
    from src.feed.models import add_feed

    click.echo(f"Fetching feed metadata for {url}...")
    data = feedparser.parse(url)
    title = data.feed.get("title", "Untitled Feed")
    description = data.feed.get("description", data.feed.get("subtitle", ""))
    link = data.feed.get("link", "")

    feed_id = add_feed(url, title=title, description=description, link=link)
    click.echo(f"Added feed: {title} (ID: {feed_id})")


@feed.command("remove")
@click.argument("feed_id", type=int)
def feed_remove(feed_id):
    """Remove a feed by ID."""
    init_feed_db()
    from src.feed.models import remove_feed

    if not click.confirm(f"Remove feed {feed_id}?"):
        return
    remove_feed(feed_id)
    click.echo(f"Feed {feed_id} removed.")


@feed.command("seed")
def feed_seed():
    """Seed default feeds if database is empty."""
    init_feed_db()
    seed_default_feeds()
    click.echo("Default feeds seeded.")


# ── Birthday commands ──────────────────────────────────────────

@main.group()
def birthday():
    """Manage birthdays."""
    pass


@birthday.command("list")
def birthday_list():
    """List all birthdays sorted by upcoming."""
    init_birthdays_db()
    from src.birthdays.models import get_all

    birthdays = get_all()
    if not birthdays:
        click.echo("No birthdays.")
        return
    for b in birthdays:
        days = b["days_until"]
        age_str = f" (turning {b['age_next']})" if b["age_next"] is not None else ""
        click.echo(f"  [{b['id']}] {b['name']} — {b['date_obj'].strftime('%b %d')}{age_str} — {days} days away — {b['category']}")


@birthday.command("add")
@click.argument("name")
@click.argument("date_str")
@click.option("--category", "-c", default="Other", help="Category: Family, Friends, Work, Other")
@click.option("--notes", "-n", default="", help="Optional notes")
def birthday_add(name, date_str, category, notes):
    """Add a birthday. DATE_STR: MM-DD or YYYY-MM-DD."""
    init_birthdays_db()
    from src.birthdays.models import add

    add(name, date_str, category=category, notes=notes)
    click.echo(f"Added birthday: {name} ({date_str})")


@birthday.command("edit")
@click.argument("birthday_id", type=int)
@click.option("--name", default=None)
@click.option("--date", "date_str", default=None)
@click.option("--category", "-c", default=None)
@click.option("--notes", "-n", default=None)
def birthday_edit(birthday_id, name, date_str, category, notes):
    """Edit a birthday by ID."""
    init_birthdays_db()
    from src.birthdays.models import edit

    edit(birthday_id, name=name, date_str=date_str, category=category, notes=notes)
    click.echo(f"Birthday {birthday_id} updated.")


@birthday.command("delete")
@click.argument("birthday_id", type=int)
def birthday_delete(birthday_id):
    """Delete a birthday by ID."""
    init_birthdays_db()
    from src.birthdays.models import delete

    if not click.confirm(f"Delete birthday {birthday_id}?"):
        return
    delete(birthday_id)
    click.echo(f"Birthday {birthday_id} deleted.")


# ── Quote commands ──────────────────────────────────────────

@main.group()
def quote():
    """Manage quotes."""
    pass


@quote.command("list")
@click.option("--author", "-a", default=None, help="Filter by author")
def quote_list(author):
    """List all quotes."""
    import json
    from pathlib import Path

    quotes_file = Path(__file__).resolve().parent.parent / "data" / "quotes.json"
    if not quotes_file.exists():
        click.echo("No quotes file found.")
        return
    with open(quotes_file) as f:
        quotes = json.load(f)

    if author:
        quotes = [q for q in quotes if author.lower() in q.get("author", "").lower()]

    for i, q in enumerate(quotes, 1):
        src = f' — {q["source"]}' if q.get("source") else ""
        click.echo(f'  [{i}] "{q["text"][:80]}..." — {q["author"]}{src}')
    click.echo(f"\n  {len(quotes)} quotes total.")


@quote.command("add")
@click.argument("text")
@click.argument("author")
@click.option("--source", "-s", default=None, help="Book or work name")
def quote_add(text, author, source):
    """Add a new quote."""
    import json
    from pathlib import Path

    quotes_file = Path(__file__).resolve().parent.parent / "data" / "quotes.json"
    quotes = []
    if quotes_file.exists():
        with open(quotes_file) as f:
            quotes = json.load(f)

    entry = {"text": text, "author": author}
    if source:
        entry["source"] = source

    quotes.append(entry)
    with open(quotes_file, "w") as f:
        json.dump(quotes, f, indent=4, ensure_ascii=False)

    click.echo(f"Added quote by {author}. Total: {len(quotes)}")


@quote.command("remove")
@click.argument("index", type=int)
def quote_remove(index):
    """Remove a quote by index (1-based)."""
    import json
    from pathlib import Path

    quotes_file = Path(__file__).resolve().parent.parent / "data" / "quotes.json"
    if not quotes_file.exists():
        click.echo("No quotes file found.")
        return
    with open(quotes_file) as f:
        quotes = json.load(f)

    idx = index - 1
    if idx < 0 or idx >= len(quotes):
        click.echo(f"Invalid index. Must be 1-{len(quotes)}.")
        return

    if not click.confirm(f'Remove "{quotes[idx]["text"][:60]}..." by {quotes[idx]["author"]}?'):
        return

    removed = quotes.pop(idx)
    with open(quotes_file, "w") as f:
        json.dump(quotes, f, indent=4, ensure_ascii=False)

    click.echo(f"Removed quote by {removed['author']}. Remaining: {len(quotes)}")


if __name__ == "__main__":
    main()

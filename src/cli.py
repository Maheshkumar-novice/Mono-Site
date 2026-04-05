"""Admin CLI for managing feeds and birthdays."""

import click

from src.db import init_birthdays_db, init_feed_db, seed_default_feeds


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
        name = b["name"]
        date = b["date_obj"].strftime("%b %d")
        cat = b["category"]
        click.echo(f"  [{b['id']}] {name} — {date}{age_str} — {days} days away — {cat}")


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


if __name__ == "__main__":
    main()

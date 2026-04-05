"""Main build entry point — builds all sections."""

import logging


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Building feed...")
    from src.feed.builder import build as build_feed

    build_feed()

    logger.info("Building football...")
    from src.football.builder import build as build_football

    build_football()

    logger.info("Building F1...")
    from src.f1.builder import build as build_f1

    build_f1()

    logger.info("Building birthdays...")
    from src.birthdays.builder import build as build_birthdays

    build_birthdays()

    logger.info("All builders complete.")


if __name__ == "__main__":
    main()

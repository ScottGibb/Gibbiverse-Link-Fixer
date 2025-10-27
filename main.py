import yaml
import logging
from pathlib import Path
from argparse import ArgumentParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up argument parser
parser = ArgumentParser(description="Clean Markdown links.")
parser.add_argument(
    "--path",
    type=Path,
    help="Root directory containing Markdown files.",
    # required=True,
)
parser.add_argument(
    "--links",
    type=Path,
    help="Path to a file containing valid links (one per line).",
    required=True,
)
parser.add_argument(
    "--topics",
    type=Path,
    help="Path to a file containing valid topics (one per line).",
    required=True,
)
BLOG_DIR = parser.parse_args().path
LINKS_FILE_PATH = parser.parse_args().links
TOPICS_FILE_PATH = parser.parse_args().topics


def build_dictionaries() -> tuple[list[str], dict[str, str]]:
    with open(LINKS_FILE_PATH, "r") as f:
        valid_links = yaml.load(f, Loader=yaml.SafeLoader)

    with open(TOPICS_FILE_PATH, "r") as f:
        valid_topics = set(line.strip() for line in f if line.strip())
    logger.info(
        f"Loaded {len(valid_links)} valid links and {len(valid_topics)} valid topics."
    )
    logger.debug(f"Valid links: {valid_links}")
    logger.debug(f"Valid topics: {valid_topics}")
    return valid_links, valid_topics


def find_topics(topics: list[str], markdown_content: str):
    topic_count = 0
    found_topics = []
    for topic in topics:
        if topic in markdown_content:
            logger.debug(f"Topic '{topic}' found in markdown content.")
            topic_count += 1
            found_topics.append(topic)
    logger.info(f"Found {topic_count} topics in the markdown content.")
    return found_topics


def update_frontmatter(md_path: Path, topics: list[str]):
    try:
        logger.info(f"Opening markdown file: {md_path}")
        with md_path.open("r", encoding="utf-8") as f:
            content = f.read()
            found_topics = find_topics(topics, content)
            # Update YAML front matter
            ## TODO: Implement front matter update logic here
    except Exception:
        logger.exception(f"Failed to read {md_path}")      

def main():
    logger.info("Starting Link Fixer...")
    links, topics = build_dictionaries()
    for md_path in BLOG_DIR.rglob("*.md"):
        update_frontmatter(md_path, topics)
    logger.info("Link fixer completed.")


if __name__ == "__main__":
    main()

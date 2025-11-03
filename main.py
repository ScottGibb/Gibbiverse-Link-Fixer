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
    # required=True,
)
parser.add_argument(
    "--topics",
    type=Path,
    help="Path to a file containing valid topics (one per line).",
    # required=True,
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


def read_markdown_with_frontmatter(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.startswith("---"):
        # Split the front matter from the body
        parts = content.split("---", 2)
        if len(parts) >= 3:
            _, frontmatter, body = parts
        else:
            frontmatter, body = "", content
    else:
        frontmatter, body = "", content

    # Parse YAML
    yaml_data = yaml.safe_load(frontmatter) if frontmatter.strip() else {}

    return yaml_data, body.strip()

def write_markdown_with_frontmatter(path, yaml_data, body):
    frontmatter = yaml.dump(yaml_data, sort_keys=False)
    new_content = f"---\n{frontmatter}---\n\n{body}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)

def update_frontmatter(md_path: Path, topics: list[str]):
    font_matter, body = read_markdown_with_frontmatter(md_path)
    topics = find_topics(topics, body)
    current_topics = font_matter["tags"] if "tags" in font_matter else []

    if current_topics is not None:
        for topic in topics:
            if topic not in current_topics:
                current_topics.append(topic)
    else:
        current_topics = topics
    font_matter["tags"] = current_topics
    write_markdown_with_frontmatter(md_path, font_matter, body)

def change_wiki_links_to_markdown_links(md_path: Path, valid_links: list[str]):
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    for link in valid_links:
        wiki_link = f"[[{link}]]"
        markdown_link = f"[{link}]({valid_links[link]})"
        if wiki_link.lower() in content.lower():
            content = content.replace(wiki_link, markdown_link)
            logger.info(f"Replaced '{wiki_link}' with '{markdown_link}' in {md_path}")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

import re
from pathlib import Path

def replace_known_wikilinks_with_md_links(md_path: Path, blog_dir: Path):
    """Replace [[WikiLinks]] that match existing markdown files with [text](relative/path.md)."""
    
    # Step 1: Build a map from stem name -> full path
    known_posts = {p.stem: p for p in blog_dir.rglob("*.md")}

    # Step 2: Read file content
    content = md_path.read_text(encoding="utf-8")

    # Step 3: Regex to match [[WikiLinks]]
    wikilink_pattern = re.compile(r"\[\[([^\]]+)\]\]")

    # Step 4: Replacement logic
    def replace_link(match):
        link_name = match.group(1).strip()
        target_name = Path(link_name).name

        # Only replace if there's a corresponding markdown file
        if target_name in known_posts:
            target_path = known_posts[target_name]
            return f"[{target_name}](.{target_path.as_posix().removeprefix(str(blog_dir.as_posix()))})"
        
        # Otherwise leave as-is
        return match.group(0)

    # Step 5: Apply replacements
    new_content = wikilink_pattern.sub(replace_link, content)

    # Step 6: Write updated content
    md_path.write_text(new_content, encoding="utf-8")
        
def main():
    logger.info("Starting Link Fixer...")
    links, topics = build_dictionaries()
    for md_path in BLOG_DIR.rglob("*.md"):
        update_frontmatter(md_path, topics)
        change_wiki_links_to_markdown_links(md_path, links)
        replace_known_wikilinks_with_md_links(md_path, BLOG_DIR)
    logger.info("Link fixer completed.")


if __name__ == "__main__":
    main()

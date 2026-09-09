from pathlib import Path
import json
import re

from pypdf import PdfReader


PDF_PATH = Path("2024_BA_Beer_Style_Guidelines.pdf")
STYLE_SOURCE_PATH = Path(
    "knowledge/data/BA_2024_style_source.json"
)

FIELD_LABELS = [
    "Color",
    "Clarity",
    "Perceived Malt Aroma & Flavor",
    "Perceived Hop Aroma & Flavor",
    "Perceived bitterness",
    "Fermentation Characteristics",
    "Body",
    "Additional notes",
    "Original Gravity (°Plato)",
    "Apparent Extract/Final Gravity (°Plato)",
    "Alcohol by Weight (Volume)",
    "Hop Bitterness (IBU)",
    "Color SRM (EBC)",
]


def normalize_pdf_text(text):
    """Normalize common PDF extraction artifacts."""

    replacements = {
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "‐": "-",
        "-": "-",
        "‒": "-",
        "–": "-",
        "—": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Join words split by a line-ending hyphen.
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1-\2", text)

    # Convert remaining line breaks to spaces.
    text = re.sub(r"\s*\n\s*", " ", text)

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def parse_statistics(statistics_text):
    """Split the BA statistics section into individual fields."""

    if not statistics_text:
        return {
            "original_gravity": None,
            "final_gravity": None,
            "alcohol": None,
            "ibu": None,
            "srm": None,
        }

    text = statistics_text.strip()

    patterns = {
        "original_gravity": (
            r"Original Gravity \(°Plato\)\s*(.*?)"
            r"(?=•\s*Apparent Extract/Final Gravity)"
        ),
        "final_gravity": (
            r"Apparent Extract/Final Gravity \(°Plato\)\s*(.*?)"
            r"(?=•\s*Alcohol by Weight)"
        ),
        "alcohol": (
            r"Alcohol by Weight \(Volume\)\s*(.*?)"
            r"(?=•\s*Hop Bitterness)"
        ),
        "ibu": (
            r"Hop Bitterness \(IBU\)\s*(.*?)"
            r"(?=•\s*Color\s*SRM)"
        ),
        "srm": (
            r"Color\s*SRM \(EBC\)\s*(.*)$"
        ),
    }

    result = {}

    for field_name, pattern in patterns.items():
        match = re.search(pattern, text)

        if match:
            result[field_name] = match.group(1).strip()
        else:
            result[field_name] = None

    return result

def load_ba_style_names():
    """Load the official BA style names from the source index."""

    with open(STYLE_SOURCE_PATH, "r", encoding="utf-8") as file:
        styles = json.load(file)

    return [
        style["name"]
        for style in styles
    ]

def extract_style_from_page(page_text, style_name, style_names):
    """Extract one BA style entry from a single PDF page."""

    text = normalize_pdf_text(page_text)

    style_pattern = re.escape(style_name) + r"\s+Color:"

    match = re.search(style_pattern, text)

    if not match:
        return None

    start = match.start()
    content_start = match.end() - len("Color:")

    # Find the next known BA style heading.
    next_start = len(text)

    for candidate in style_names:
        if candidate == style_name:
            continue

        candidate_pattern = (
            re.escape(candidate)
            + r"\s+Color:"
        )

        candidate_match = re.search(
            candidate_pattern,
            text[match.end():],
        )

        if candidate_match:
            candidate_start = (
                match.end()
                + candidate_match.start()
            )

            if candidate_start < next_start:
                next_start = candidate_start

    style_text = text[
        content_start:next_start
    ].strip()

    result = {
        "name": style_name,
    }

    # Locate the statistics section.
    stats_marker = "Original Gravity (°Plato)"

    stats_start = style_text.find(stats_marker)

    if stats_start == -1:
        descriptive_text = style_text
        statistics_text = None
    else:
        descriptive_text = style_text[:stats_start].strip()
        statistics_text = style_text[stats_start:].strip()

        # Extract the labeled descriptive fields.
    field_positions = []

    for label in FIELD_LABELS:
        position = descriptive_text.find(label)

        if position != -1:
            field_positions.append((position, label))

    field_positions.sort()

    for index, (start_position, label) in enumerate(field_positions):
        value_start = start_position + len(label)

        if index + 1 < len(field_positions):
            value_end = field_positions[index + 1][0]
        else:
            value_end = len(descriptive_text)

        value = descriptive_text[
            value_start:value_end
        ].strip()

        result[label] = value.lstrip(":").strip()

        # Some BA styles contain unlabeled prose between the
    # Body field and the statistics section. Preserve it
    # as Additional notes rather than attaching it to Body.
    body_value = result.get("Body")

    body_value = result.get("Body")

    if body_value and "When using these guidelines" in body_value:
        body_text, notes_text = body_value.split(
            "When using these guidelines",
            1,
        )

        result["Body"] = body_text.strip()
        result["Additional notes"] = (
            "When using these guidelines" + notes_text
        ).strip()

    statistics = parse_statistics(statistics_text)

    result.update(statistics)

    return result

def extract_style_from_document(document_text, style_name, style_names):
    """Extract one BA style entry from the complete PDF text."""

    text = normalize_pdf_text(document_text)

    style_pattern = re.escape(style_name) + r"\s+Color:"
    match = re.search(style_pattern, text)

    if not match:
        return None

    content_start = match.end() - len("Color:")

    # Find the next known BA style heading.
    next_start = len(text)

    for candidate in style_names:
        if candidate == style_name:
            continue

        candidate_pattern = re.escape(candidate) + r"\s+Color:"
        candidate_match = re.search(
            candidate_pattern,
            text[match.end():],
        )

        if candidate_match:
            candidate_start = (
                match.end() + candidate_match.start()
            )

            if candidate_start < next_start:
                next_start = candidate_start

    style_text = text[content_start:next_start].strip()

    result = {"name": style_name}

    # Locate the statistics section.
    stats_marker = "Original Gravity (°Plato)"
    stats_start = style_text.find(stats_marker)

    if stats_start == -1:
        descriptive_text = style_text
        statistics_text = None
    else:
        descriptive_text = style_text[:stats_start].strip()
        statistics_text = style_text[stats_start:].strip()

    # Locate descriptive fields.
    field_positions = []

    for label in FIELD_LABELS:
        position = descriptive_text.find(label)

        if position != -1:
            field_positions.append((position, label))

    field_positions.sort()

    for index, (start_position, label) in enumerate(field_positions):
        value_start = start_position + len(label)

        if index + 1 < len(field_positions):
            value_end = field_positions[index + 1][0]
        else:
            value_end = len(descriptive_text)

        value = descriptive_text[value_start:value_end].strip()

        result[label] = value.lstrip(":").strip()

    # Separate the standard competition note when it follows Body.
    body_value = result.get("Body")

    if body_value and "When using these guidelines" in body_value:
        body_text, notes_text = body_value.split(
            "When using these guidelines",
            1,
        )

        result["Body"] = body_text.strip()

        result["Additional notes"] = (
            "When using these guidelines" + notes_text
        ).strip()

    statistics = parse_statistics(statistics_text)
    result.update(statistics)

    return result

def main():
    reader = PdfReader(PDF_PATH)

    style_names = load_ba_style_names()

    page = reader.pages[19]
    text = page.extract_text()

    result = extract_style_from_document(
        text,
        "West Coast-Style India Pale Ale",
        style_names,
    )

    if result is None:
        print("Style not found.")
        return

    print("=" * 80)
    print(result["name"])
    print("=" * 80)

    for key, value in result.items():
        if key == "name":
            continue

        print(f"\n{key}:")
        print(value)

if __name__ == "__main__":
    main()
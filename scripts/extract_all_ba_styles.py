from pathlib import Path
import json

from pypdf import PdfReader

from parse_ba_style import (
    extract_style_from_document,
    load_ba_style_names,
)


PDF_PATH = Path("2024_BA_Beer_Style_Guidelines.pdf")
STYLE_SOURCE_PATH = Path("knowledge/data/BA_2024_style_source.json")
OUTPUT_PATH = Path("knowledge/data/BA_2024_parsed_styles.json")


def load_source_styles():
    """Load the official BA style source index."""
    with open(STYLE_SOURCE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_all_styles():
    """Extract all known BA styles from the PDF."""

    reader = PdfReader(PDF_PATH)
    source_styles = load_source_styles()
    style_names = load_ba_style_names()

    parsed_styles = []
    warnings = []
    failures = []

    # Extract and normalize the complete PDF.
    page_texts = {}

    for page_number, page in enumerate(reader.pages, start=1):
        page_texts[page_number] = page.extract_text() or ""

    document_text = "\n".join(
        page_texts[page_number]
        for page_number in sorted(page_texts)
    )

    for source_style in source_styles:
        style_name = source_style["name"]

        result = extract_style_from_document(
            document_text,
            style_name,
            style_names,
        )

        found_on_page = source_style["page"]

        if result is None:
            failures.append(style_name)
            continue

        # Preserve source-index metadata.
        result["guideline_year"] = source_style["guideline_year"]
        result["page"] = source_style["page"]
        result["section"] = source_style["section"]
        result["subsection"] = source_style["subsection"]
        result["source"] = source_style["source"]
        result["pdf_page"] = found_on_page

        # Required descriptive fields.
        required_fields = [
            "Color",
            "Clarity",
            "Perceived Malt Aroma & Flavor",
            "Perceived Hop Aroma & Flavor",
            "Perceived bitterness",
            "Fermentation Characteristics",
            "Body",
        ]

        missing_fields = [
            field
            for field in required_fields
            if not result.get(field)
        ]

        if missing_fields:
            warnings.append(
                {
                    "style": style_name,
                    "type": "missing_fields",
                    "fields": missing_fields,
                }
            )

        parsed_styles.append(result)

    return parsed_styles, warnings, failures


def main():
    parsed_styles, warnings, failures = extract_all_styles()

    output = {
        "source": "Brewers Association Beer Style Guidelines",
        "guideline_year": 2024,
        "styles": parsed_styles,
        "validation": {
            "source_style_count": 161,
            "parsed_style_count": len(parsed_styles),
            "warning_count": len(warnings),
            "failure_count": len(failures),
            "warnings": warnings,
            "failures": failures,
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 80)
    print("BA STYLE EXTRACTION")
    print("=" * 80)
    print(f"Source styles:   {output['validation']['source_style_count']}")
    print(f"Parsed styles:   {output['validation']['parsed_style_count']}")
    print(f"Warnings:        {output['validation']['warning_count']}")
    print(f"Failures:        {output['validation']['failure_count']}")
    print(f"Output:          {OUTPUT_PATH}")

    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(
                f"- {warning['style']}: "
                f"{', '.join(warning['fields'])}"
            )

    if failures:
        print("\nFAILURES:")
        for style in failures:
            print(f"- {style}")


if __name__ == "__main__":
    main()
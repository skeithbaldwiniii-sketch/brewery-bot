from __future__ import annotations

import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
STYLES_FILE = ROOT / "styles.json"
BACKUP_FILE = ROOT / "styles.json.before_21b_fix"

PARENT_URL = "https://www.bjcp.org/style/2021/21/21B/specialty-ipa/"

CHILDREN = {
    "Belgian IPA": "https://www.bjcp.org/style/2021/21/21B/specialty-ipa-belgian-ipa/",
    "Black IPA": "https://www.bjcp.org/style/2021/21/21B/specialty-ipa-black-ipa/",
    "Brown IPA": "https://www.bjcp.org/style/2021/21/21B/specialty-ipa-brown-ipa/",
    "Red IPA": "https://www.bjcp.org/style/2021/21/21B/specialty-ipa-red-ipa/",
    "Rye IPA": "https://www.bjcp.org/style/2021/21/21B/specialty-ipa-rye-ipa/",
    "White IPA": "https://www.bjcp.org/style/2021/21/21B/specialty-ipa-white-ipa/",
    "Brut IPA": "https://www.bjcp.org/style/2021/21/21B/specialty-ipa-brut-ipa/",
}

EXPECTED_CHILDREN = [
    "Specialty IPA: Belgian IPA",
    "Specialty IPA: Black IPA",
    "Specialty IPA: Brown IPA",
    "Specialty IPA: Red IPA",
    "Specialty IPA: Rye IPA",
    "Specialty IPA: White IPA",
    "Specialty IPA: Brut IPA",
]


class BJCPParser(HTMLParser):
    """
    Purpose-built parser for the current BJCP 2021 style page structure.

    Extracts:
      - official style title
      - named style sections
      - vital statistics

    Uses only Python's standard-library HTMLParser.
    """

    SECTION_CLASSES = {
        "overall-impression": "overallimpression",
        "appearance": "appearance",
        "aroma": "aroma",
        "flavor": "flavor",
        "mouthfeel": "mouthfeel",
        "comments": "comments",
        "history": "history",
        "ingredients": "characteristicingredients",
        "style-comparison": "stylecomparison",
        "commercial-examples": "commercialexamples",
        "style-attributes": "tags",

        # Specialty IPA parent-page sections
        "currently-defined-types": "currentlydefinedtypes",
        "entry-instructions": "entryinstructions",
        "strength-classifications": "strengthclassifications",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)

        self.style_title = ""
        self.sections = {}
        self.vital_stats = {}

        # Track the HTML element structure explicitly.
        self._tag_stack = []

        # Title
        self._in_title = False

        # Main content container
        self._in_content = False
        self._content_depth = 0

        # Normal section
        self._current_section = None
        self._section_depth = 0
        self._section_parts = []
        self._in_heading = False

        # Vital statistics
        self._in_vital_table = False
        self._vital_row_active = False
        self._vital_cell_index = 0
        self._vital_label = ""
        self._vital_value = ""

    @staticmethod
    def _classes(attrs):
        attrs = dict(attrs)
        return set((attrs.get("class") or "").split())

    def handle_starttag(self, tag, attrs):
        classes = self._classes(attrs)

        # Record the tag and its classes so end-tag handling can
        # identify exactly which structural element is closing.
        self._tag_stack.append((tag, classes))

        # ------------------------------------------------------------
        # Style title
        # ------------------------------------------------------------
        if tag == "h1" and "entry-title" in classes:
            self._in_title = True
            return

        if self._in_title:
            return

        # ------------------------------------------------------------
        # Main BJCP content container
        # ------------------------------------------------------------
        if (
            tag == "div"
            and not self._in_content
            and "entry-content" in classes
            and "about-beer-style" in classes
        ):
            self._in_content = True
            self._content_depth = 1
            return

        if not self._in_content:
            return

        if tag == "div":
            self._content_depth += 1

        # ------------------------------------------------------------
        # Vital statistics
        # ------------------------------------------------------------
        if tag == "div" and "vital-statistics" in classes:
            self._in_vital_table = True
            return

        if self._in_vital_table:
            if tag == "div" and "row" in classes:
                self._vital_row_active = True
                self._vital_cell_index = 0
                self._vital_label = ""
                self._vital_value = ""
                return

            if (
                self._vital_row_active
                and tag == "div"
                and "cell" in classes
            ):
                self._vital_cell_index += 1
                return

            # Ignore other tags inside the vital statistics table.
            # Do NOT return from the entire parser state here.
            return

        # ------------------------------------------------------------
        # Section headings
        # ------------------------------------------------------------
        if tag in ("h2", "h3"):
            self._in_heading = True

        # ------------------------------------------------------------
        # Normal BJCP sections
        # ------------------------------------------------------------
        if tag == "div" and self._current_section is None:
            for css_class, key in self.SECTION_CLASSES.items():
                if css_class in classes:
                    self._current_section = key
                    self._section_depth = 1
                    self._section_parts = []
                    return

        if self._current_section and tag == "div":
            self._section_depth += 1

    def handle_endtag(self, tag):
        # Find the matching structural element from our tag stack.
        closing_classes = set()

        for index in range(len(self._tag_stack) - 1, -1, -1):
            open_tag, classes = self._tag_stack[index]

            if open_tag == tag:
                closing_classes = classes
                del self._tag_stack[index:]
                break

        # ------------------------------------------------------------
        # Title
        # ------------------------------------------------------------
        if self._in_title and tag == "h1":
            self._in_title = False
            return

        # ------------------------------------------------------------
        # Section heading
        # ------------------------------------------------------------
        if tag in ("h2", "h3"):
            self._in_heading = False
            return

        # ------------------------------------------------------------
        # Vital statistics
        # ------------------------------------------------------------
        if self._in_vital_table:

            # Finish a row only when the actual row <div> closes.
            if (
                tag == "div"
                and closing_classes
                and "row" in closing_classes
            ):
                self._finish_vital_row()
                return

            # Exit the vital-statistics container only when it closes.
            if (
                tag == "div"
                and closing_classes
                and "vital-statistics" in closing_classes
            ):
                self._in_vital_table = False
                return

            return

        # ------------------------------------------------------------
        # Normal style section
        # ------------------------------------------------------------
        if self._current_section and tag == "div":
            self._section_depth -= 1

            if self._section_depth == 0:
                self._finish_section()

            return

        # ------------------------------------------------------------
        # Main content container
        # ------------------------------------------------------------
        if self._in_content and tag == "div":
            self._content_depth -= 1

            if self._content_depth == 0:
                self._in_content = False

    def handle_data(self, data):
        text = " ".join(data.split())

        if not text:
            return

        if self._in_title:
            self.style_title += text
            return

        # Vital statistics
        # These labels are inside h3 elements, so this must be
        # checked before the general heading suppression below.
        if self._vital_row_active:
            if self._vital_cell_index == 1:
                self._vital_label += text
            elif self._vital_cell_index == 2:
                self._vital_value += text
            return

        # Do not capture h2/h3 section headings as section content.
        if self._in_heading:
            return

        # Normal section
        if self._current_section:
            self._section_parts.append(text)

    def _finish_section(self):
        if self._current_section:
            text = " ".join(self._section_parts).strip()

            if text:
                self.sections[self._current_section] = text

        self._current_section = None
        self._section_depth = 0
        self._section_parts = []

    def _finish_vital_row(self):
        label = " ".join(self._vital_label.split()).strip()
        value = " ".join(self._vital_value.split()).strip()

        if label and value:
            self.vital_stats[label.upper()] = value

        self._vital_row_active = False
        self._vital_cell_index = 0
        self._vital_label = ""
        self._vital_value = ""

def fetch_html(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Brews Springsteen BJCP importer)"
        },
    )

    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")

def parse_page(url):
    html = fetch_html(url)

    parser = BJCPParser()
    parser.feed(html)
    parser.close()

    if not parser.style_title:
        raise RuntimeError(f"Could not find style title: {url}")

    if not parser.sections:
        raise RuntimeError(f"Could not find style sections: {url}")

    return parser


def parse_range(value, percent=False):
    """
    Convert BJCP ranges such as:

        40 - 70
        1.056 - 1.070
        5.5% - 7.5%

    into (minimum, maximum).
    """
    numbers = re.findall(r"\d+(?:\.\d+)?", value)

    if len(numbers) < 2:
        raise ValueError(f"Could not parse range: {value!r}")

    minimum = float(numbers[0])
    maximum = float(numbers[1])

    return minimum, maximum


def build_style(parser, *, parent=False, child_name=None):
    title = parser.style_title.strip()

    match = re.match(r"21B\.\s*(.+)", title)

    if not match:
        raise RuntimeError(f"Unexpected BJCP title: {title!r}")

    official_name = match.group(1).strip()

    if parent:
        name = "Specialty IPA"
    else:
        name = official_name

        expected = f"Specialty IPA: {child_name}"
        if name != expected:
            raise RuntimeError(
                f"Expected {expected!r}, but BJCP page reports {name!r}"
            )

    sections = parser.sections
    stats = parser.vital_stats

    def section(key):
        return sections.get(key)

    style = {
        "name": name,
        "number": "21B" if parent else None,
        "category": "Ipa",
        "categorynumber": "21",

        "overallimpression": section("overallimpression"),
        "aroma": section("aroma"),
        "appearance": section("appearance"),
        "flavor": section("flavor"),
        "mouthfeel": section("mouthfeel"),

        "comments": section("comments"),
        "history": section("history"),
        "characteristicingredients": section("characteristicingredients"),
        "stylecomparison": section("stylecomparison"),

        "commercialexamples": section("commercialexamples"),
        "tags": section("tags"),

        "ibumin": None,
        "ibumax": None,
        "srmmin": None,
        "srmmax": None,
        "ogmin": None,
        "ogmax": None,
        "fgmin": None,
        "fgmax": None,
        "abvmin": None,
        "abvmax": None,
    }

    if not parent:
        required_stats = ["IBU", "SRM", "OG", "FG", "ABV"]

        for stat in required_stats:
            if stat not in stats:
                raise RuntimeError(
                    f"{name}: missing vital statistic {stat!r}. "
                    f"Found: {sorted(stats)}"
                )

        style["ibumin"], style["ibumax"] = parse_range(stats["IBU"])
        style["srmmin"], style["srmmax"] = parse_range(stats["SRM"])
        style["ogmin"], style["ogmax"] = parse_range(stats["OG"])
        style["fgmin"], style["fgmax"] = parse_range(stats["FG"])
        style["abvmin"], style["abvmax"] = parse_range(stats["ABV"])

    if parent:
        required_sections = [
            "overallimpression",
            "aroma",
            "appearance",
            "flavor",
            "mouthfeel",
            "comments",
        ]
    else:
        required_sections = [
            "overallimpression",
            "aroma",
            "appearance",
            "flavor",
            "mouthfeel",
            "comments",
            "history",
            "characteristicingredients",
            "stylecomparison",
            "commercialexamples",
            "tags",
        ]

    for key in required_sections:
        if not style[key]:
            raise RuntimeError(f"{name}: missing required section {key!r}")

    return style


def main():
    print("=" * 70)
    print("21B SPECIALTY IPA SOURCE MIGRATION")
    print("=" * 70)

    if not STYLES_FILE.exists():
        raise FileNotFoundError(STYLES_FILE)

    if BACKUP_FILE.exists():
        raise FileExistsError(
            f"Backup already exists: {BACKUP_FILE}\n"
            "Refusing to overwrite it."
        )

    print("\nLoading styles.json...")
    with STYLES_FILE.open("r", encoding="utf-8") as f:
        styles = json.load(f)

    if not isinstance(styles, list):
        raise RuntimeError("styles.json does not contain a top-level list.")

    print(f"Existing style count: {len(styles)}")

    specialty = [
        style for style in styles
        if style.get("name") == "Specialty IPA"
    ]

    if len(specialty) != 1:
        raise RuntimeError(
            f"Expected exactly one existing Specialty IPA record; "
            f"found {len(specialty)}."
        )

    print("Existing Specialty IPA record found.")

    print("\nFetching official BJCP parent page...")
    parent_parser = parse_page(PARENT_URL)
    parent_style = build_style(parent_parser, parent=True)

    print(f"  Parsed: {parent_style['name']}")

    child_styles = []

    for child_name, url in CHILDREN.items():
        print(f"Fetching official BJCP page: {child_name}...")
        parser = parse_page(url)
        style = build_style(
            parser,
            parent=False,
            child_name=child_name,
        )
        child_styles.append(style)

        print(
            f"  Parsed: {style['name']} "
            f"(IBU {style['ibumin']}-{style['ibumax']}, "
            f"SRM {style['srmmin']}-{style['srmmax']}, "
            f"ABV {style['abvmin']}-{style['abvmax']})"
        )

    # ------------------------------------------------------------
    # Validate the complete replacement before modifying anything.
    # ------------------------------------------------------------

    replacement_names = [parent_style["name"]] + [
        style["name"] for style in child_styles
    ]

    if replacement_names != [
        "Specialty IPA",
        *EXPECTED_CHILDREN,
    ]:
        raise RuntimeError(
            "Unexpected Specialty IPA family names:\n"
            + "\n".join(replacement_names)
        )

    # Replace the malformed Specialty IPA record in-place.
    # This preserves the existing position in styles.json.
    new_styles = []

    for style in styles:
        if style.get("name") == "Specialty IPA":
            new_styles.append(parent_style)
            new_styles.extend(child_styles)
        else:
            new_styles.append(style)

    expected_count = len(styles) + 7

    if len(new_styles) != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} styles after migration; "
            f"got {len(new_styles)}."
        )

    names = [style.get("name") for style in new_styles]

    for expected_name in ["Specialty IPA", *EXPECTED_CHILDREN]:
        count = names.count(expected_name)

        if count != 1:
            raise RuntimeError(
                f"Expected exactly one {expected_name!r}; found {count}."
            )

    # Parent should have no universal vital statistics.
    for key in [
        "ibumin", "ibumax",
        "srmmin", "srmmax",
        "ogmin", "ogmax",
        "fgmin", "fgmax",
        "abvmin", "abvmax",
    ]:
        if parent_style[key] is not None:
            raise RuntimeError(
                f"Parent Specialty IPA unexpectedly has {key}="
                f"{parent_style[key]!r}"
            )

    if parent_style["number"] != "21B":
        raise RuntimeError("Parent Specialty IPA does not have BJCP number 21B.")

    # Child records must not claim the parent BJCP number.
    for style in child_styles:
        if style["number"] is not None:
            raise RuntimeError(
                f"{style['name']} unexpectedly has BJCP number "
                f"{style['number']!r}"
            )

    print("\nAll validation checks passed.")
    print(f"New style count: {len(new_styles)}")

    # ------------------------------------------------------------
    # Only now modify files.
    # ------------------------------------------------------------

    print(f"\nCreating backup: {BACKUP_FILE.name}")
    shutil.copy2(STYLES_FILE, BACKUP_FILE)

    print("Writing updated styles.json...")
    with STYLES_FILE.open("w", encoding="utf-8") as f:
        json.dump(new_styles, f, indent=4, ensure_ascii=False)
        f.write("\n")

    print("\n" + "=" * 70)
    print("MIGRATION COMPLETE")
    print("=" * 70)
    print(f"Backup: {BACKUP_FILE}")
    print(f"Updated: {STYLES_FILE}")
    print(f"Styles: {len(styles)} -> {len(new_styles)}")
    print("\nAdded:")
    for name in EXPECTED_CHILDREN:
        print(f"  + {name}")


if __name__ == "__main__":
    main()

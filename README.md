# Brews Springsteen 🍺

## Brewery Operations Intelligence Platform

Brews Springsteen is a Python-based brewery operations intelligence platform built to automate and simplify day-to-day brewery and cellar operations.

The system connects an existing Google Sheets production workflow with a SQLite knowledge database, external brewery systems, and Slack, allowing brewery staff to access schedules, task information, beer knowledge, operational data, and reports through a natural-language interface.

> Built as a real-world brewery automation project to reduce repetitive administrative work and make operational information easier to access.

---

## Current Capabilities

### 📋 Schedule & Task Intelligence

Brews Springsteen reads the brewery's operational board from Google Sheets and interprets tasks organized by weekday.

Users can ask questions such as:

```text
What's on Wednesday?
What's left today?
When are we kegging Festbier?
What day are deliveries?
When is the event?
```

The system identifies the relevant schedule or task information and returns the appropriate answer.

The Google Sheet remains the operational source of truth, allowing the brewery to continue using its existing workflow without requiring staff to learn a new scheduling system.

---

### ✅ Daily Operations Reporting

Task completion is determined from the existing Google Sheets workflow using **strikethrough formatting**.

The system can generate daily reports and end-of-day reports that separate completed work from tasks that still need to be addressed.

Example:

```text
END OF DAY - TUESDAY
------------------------

COMPLETED
- stack barrels
- pull deliveries
- make sixtel of beach, haze & juice for delivery
- update sales sheets
- tally ferry log

NEEDS RESCHEDULING
- brewing:
- keg off festbier
- flip bt1 for thc bev
- sani bt2 for thc bev

SUMMARY: 7 completed / 4 remaining
```

---

### 💬 Slack Integration

Brews Springsteen integrates with Slack using **Slack Bolt** and Socket Mode.

Staff can mention the bot and ask questions directly from the brewery's existing communication environment.

```text
@Brews Springsteen What's on Wednesday?
```

Questions are routed through the appropriate intelligence and knowledge layers based on their content and the user's channel permissions.

---

## 🍺 Beer Knowledge System

Brews Springsteen includes a structured SQLite-based beer knowledge system designed to keep different sources of beer information separate while allowing them to work together.

The system currently incorporates:

- BJCP 2021 Beer Style Guidelines
- Brewers Association 2024 Beer Style Guidelines
- General brewing knowledge
- Brewery-specific beer information

### BJCP Style Database

The BJCP database contains structured style information including:

- Style name
- BJCP category and number
- Country of origin
- Historical period
- History
- Overall description
- Aroma
- Appearance
- Flavor
- Mouthfeel
- Ingredients
- Brewing notes
- Typical ABV
- Typical IBU
- Typical OG
- Typical FG
- Typical SRM

BJCP-specific questions are answered directly from the BJCP database.

Example:

```text
What does BJCP say about Festbier?
```

returns the BJCP style information without replacing it with another organization's specifications.

---

### Brewers Association Style Database

The project also contains the **2024 Brewers Association Beer Style Guidelines**, parsed into structured database records.

The BA dataset currently contains **161 beer styles**.

Each style can include:

- Style name
- Guideline year
- Section
- Subsection
- Color
- Perceived malt aroma & flavor
- Perceived hop aroma & flavor
- Perceived bitterness
- Fermentation characteristics
- Body
- Additional notes
- Original gravity
- Final gravity
- Alcohol
- IBU
- SRM
- Source page

Brewers Association-specific questions are routed directly to the BA database.

Example:

```text
What does the Brewers Association say about Festbier?
```

returns the Brewers Association guideline information independently of the BJCP data.

---

## 🔀 BJCP / Brewers Association Style Crosswalk

Because BJCP and Brewers Association style names and specifications do not always correspond directly, the project uses a separate **style crosswalk** rather than merging the two databases.

The crosswalk records relationships such as:

```text
BJCP:
Festbier

        │
        │ equivalent_to
        ▼

Brewers Association:
German-Style Oktoberfest/Festbier
```

Relationships include a confidence level so that uncertain mappings can remain distinguishable from high-confidence equivalents.

This architecture preserves the original source data while allowing the system to understand that different organizations may describe the same or related beer styles differently.

---

## 🧠 Style Synthesis

General style questions can combine information from both sources through a deterministic synthesis layer.

For example:

```text
What is a Festbier?
```

can return a combined overview using:

```text
BJCP 2021
     │
     ├── Style description
     ├── OG / FG
     ├── ABV
     ├── IBU
     └── SRM

Brewers Association 2024
     │
     ├── Style characteristics
     ├── OG / FG
     ├── Alcohol
     ├── IBU
     └── SRM
```

The sources remain explicitly separated.

This is intentional: **conflicting specifications are not averaged, overwritten, or presented as though they came from a single authority.**

The system therefore distinguishes between:

```text
General question
        ↓
BJCP + BA synthesis

BJCP-specific question
        ↓
BJCP source

Brewers Association-specific question
        ↓
BA source
```

The current synthesis system is deterministic and does not require an LLM to generate the underlying style facts.

---

## 🍺 Beer30 Integration

Brews Springsteen includes a REST API integration with Beer30 for brewery production and tank-management data.

Current functionality includes:

- Beer30 API connectivity
- WIP report retrieval
- WIP snapshot storage in SQLite
- Tank and batch queries
- Fermentation and cellaring queries
- Historical snapshot timestamps
- Natural-language WIP queries through Slack
- Beer30 inventory data retrieval and snapshot infrastructure

The current Beer30 integration uses sandbox data for development and testing.

Because sandbox data may not represent current brewery operations, Beer30 WIP responses identify the source report date and local retrieval timestamp rather than presenting the information as live operational data.

Live production integration will be expanded once current API access and data are available.

---

## 🧠 Natural-Language Intelligence

The intelligence layer interprets natural-language questions rather than requiring rigid commands.

It can distinguish between questions involving:

- Schedule information
- Remaining tasks
- Task timing
- Beer releases
- Brewery events
- Brewery operations
- Beer knowledge
- BJCP style information
- Brewers Association style information
- General style questions
- Beer30 WIP information

The goal is to allow brewery staff to ask questions naturally rather than learn a collection of application-specific commands.

---

## 🎸 Springsteen Easter Egg

Brews Springsteen includes a small personality feature that responds to requests such as:

```text
@Brews Springsteen play me something
```

The bot randomly selects a short Bruce Springsteen lyric snippet and song title, adding a bit of personality to the conversational interface.

---

## 🗄️ Database Architecture

SQLite provides structured local storage for brewery knowledge, operational data, production records, and external-system snapshots.

Current database components include:

```text
beer_styles
ba_styles
encyclopedia_entries
brewery_beers
batches
fermentation_readings
beer30_inventory
beer30_sync_runs
beer30_wip
```

The database architecture is intentionally modular.

Source-specific beer-style information remains separated so that provenance can be preserved when multiple knowledge sources are used together.

---

## 🔌 Integrations

### Current Integrations

- Google Sheets
- Google Drive API
- Slack
- Slack Bolt / Socket Mode
- SQLite
- Beer30 REST API
- BJCP style data
- Brewers Association style data

### Planned / Pending Integrations

- Beer30 live production integration
- Upserve / Breadcrumb
- Sales analytics
- Additional brewery operational systems

Planned sales analytics include:

- Weekly beer and cider rankings
- Monthly beer and cider rankings
- Individual product performance
- Packaged/canned product performance
- Automated weekly sales reports
- Automated monthly business intelligence reports

---

## 🛠️ Technology

### Language

- Python

### Data & Storage

- SQLite
- Google Sheets
- JSON

### APIs & Integrations

- Google Sheets API
- Google Drive API
- Slack API
- Slack Bolt / Socket Mode
- Beer30 REST API

### Python Libraries

- `gspread`
- `google-auth`
- `python-dotenv`
- `requests`
- `slack-bolt`
- `slack-sdk`
- `pytest`

### Development Tools

- VS Code
- Python virtual environments
- Git
- GitHub

---

## 📁 Project Structure

```text
brewery_bot/
│
├── integrations/
│   ├── __init__.py
│   ├── board_reader.py
│   ├── google_sheets.py
│   ├── beer30.py
│   └── slack.py
│
├── intelligence/
│   ├── task_queries.py
│   ├── beer30_queries.py
│   └── springsteen.py
│
├── knowledge/
│   ├── ask.py
│   ├── database.py
│   ├── encyclopedia.py
│   ├── beer_queries.py
│   ├── style_crosswalk.py
│   ├── style_synthesis.py
│   ├── import_styles.py
│   ├── seed_encyclopedia.py
│   ├── seed_styles.py
│   └── data/
│       ├── style_crosswalk.json
│       ├── BJCP style data
│       └── BA style data
│
├── reports/
│   ├── __init__.py
│   ├── daily_report.py
│   ├── daily_tasks.py
│   ├── eod_report.py
│   └── schedule.py
│
├── scripts/
│   ├── sync_beer30_inventory.py
│   └── data import / processing scripts
│
├── tests/
│   ├── test_ba_question_routing.py
│   ├── test_ba_style_lookup.py
│   ├── test_ba_style_formatting.py
│   ├── test_style_crosswalk.py
│   ├── test_style_synthesis.py
│   ├── test_slack_build_answer.py
│   └── ...
│
├── main.py
├── eod_main.py
├── daily_report_main.py
├── requirements.txt
├── run_daily_report.bat
├── run_eod_report.bat
├── .gitignore
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/skeithbaldwiniii-sketch/brewery-bot.git
cd brewery-bot
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure credentials

The application uses environment variables and local credential files for external services.

Create a `.env` file containing the required Slack credentials:

```text
SLACK_BOT_TOKEN=your_bot_token
SLACK_APP_TOKEN=your_app_token
```

Beer30 credentials should also be stored locally rather than committed to source control.

Place Google service-account credentials in:

```text
credentials.json
```

Credentials and private operational data are intentionally excluded from the public repository.

### 5. Initialize the database

```powershell
python -m knowledge.database
```

The local SQLite database will be created under:

```text
data/
```

---

## ▶️ Running the Application

### Slack Bot

```powershell
python -m integrations.slack
```

The bot uses Slack Socket Mode to receive events.

### Daily Report

```powershell
python main.py
```

### End-of-Day Report

```powershell
python eod_main.py
```

Windows batch files are also included for scheduled execution:

```text
run_daily_report.bat
run_eod_report.bat
```

---

## 🧪 Testing

The project uses `pytest` for automated testing.

Run the complete test suite with:

```powershell
pytest
```

Targeted tests can be run during development:

```powershell
pytest tests/test_ba_question_routing.py tests/test_style_synthesis.py tests/test_slack_build_answer.py
```

The BJCP/BA style synthesis feature currently has regression coverage for:

- BA style lookup
- BA style formatting
- BA-specific question routing
- BJCP-specific question routing
- BJCP/BA style crosswalks
- General style synthesis
- Slack answer generation

---

## 🔐 Security

Private credentials and operational data are intentionally excluded from version control.

The repository ignores:

```text
.env
credentials.json
.venv/
__pycache__/
*.pyc
data/
```

No API tokens, Google service-account credentials, or local operational databases should be committed to the repository.

### Data & Privacy

Brewery-specific operational data is treated as private and is not included in the public source repository.

External service credentials are loaded through environment variables or local credential files.

The public repository contains application code, configuration examples, development infrastructure, and non-sensitive reference data rather than brewery credentials or private operational datasets.

---

## 🚧 Project Status

**Active development**

The project currently has operational components for:

- Schedule intelligence
- Task intelligence
- Slack integration
- Daily reporting
- End-of-day reporting
- Beer knowledge
- BJCP style information
- Brewers Association style information
- BJCP/BA style crosswalking
- Deterministic BJCP/BA style synthesis
- Beer30 sandbox integration

The Beer30 live-data expansion is currently pending access to current production data.

Upserve / Breadcrumb integration is pending API information and access.

The project is being developed incrementally toward a broader brewery operations and analytics platform.

---

## 🎯 Future Development

Potential future capabilities include:

- Expanded BJCP/BA style crosswalk
- Style aliases and alternate terminology
- Additional beer knowledge sources
- Beer30 live production integration
- Upserve / Breadcrumb sales integration
- Production and batch tracking
- Fermentation analytics
- Inventory analysis
- Beer and cider sales rankings
- Packaged product performance
- Weekly management reports
- Monthly business intelligence reports
- Automated operational alerts
- Historical production analytics
- Natural-language access to brewery data
- Additional brewery-system integrations

---

## 💡 Why I Built It

This project was developed to solve a real operational problem in a working brewery environment.

Rather than replacing the brewery's existing processes, Brews Springsteen is designed to connect to the tools already being used and automate the repetitive work around them.

The project provides hands-on experience with:

- API integration
- Data modeling
- Database design
- Automation
- Natural-language interfaces
- Data parsing
- Knowledge representation
- Source reconciliation
- Operational reporting
- Python application architecture
- Real-world system integration
- Automated testing

The long-term goal is to create a centralized brewery operations assistant capable of connecting **production, cellar operations, inventory, sales, scheduling, and brewery knowledge through a single interface.**

# Brews Springsteen 🍺

## Brewery Operations Intelligence Platform

Brews Springsteen is a Python-based brewery operations intelligence platform built to automate and simplify day-to-day brewery and cellar operations.

The system connects an existing Google Sheets production workflow with a SQLite knowledge database, external brewery systems, Gmail, and Slack, allowing brewery staff to access schedules, task information, beer knowledge, operational data, sales reports, and automated workflows through a natural-language interface.

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

Brews Springsteen integrates with Slack using **Slack Bolt**, Socket Mode, and the Slack API.

Staff can mention the bot and ask questions directly from the brewery's existing communication environment.

```text
@Brews Springsteen What's on Wednesday?
```

Questions are routed through the appropriate intelligence and knowledge layers based on their content and the user's channel permissions.

Slack can also serve as the destination for automated operational reports, including weekly Upserve sales reports.

---

## 🍺 Beer Knowledge System

Brews Springsteen includes a structured SQLite-based beer knowledge system designed to keep different sources of beer information separate while allowing them to work together.

The system currently incorporates:

- BJCP 2021 Beer Style Guidelines
- Brewers Association 2024 Beer Style Guidelines
- Structured hop information
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

### BJCP Category Structure

BJCP category structure is preserved in the source data rather than flattening categories into individual beer styles.

For example:

```text
21B Specialty IPA
├── Belgian IPA
├── Black IPA
├── Brown IPA
├── Brut IPA
├── Red IPA
├── Rye IPA
└── White IPA
```

`21B Specialty IPA` is treated as the parent competition category. The defined Specialty IPA types retain their own specifications rather than inheriting statistics from the parent category.

This preserves source accuracy and allows questions about either the category or an individual subtype to be handled appropriately.

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

## 🌿 Hop Intelligence

Brews Springsteen includes a structured hop knowledge and intelligence layer.

Current functionality includes:

- Structured hop profiles
- Hop characteristics and descriptors
- Hop queries
- Hop comparisons
- Hop recommendations
- Natural-language hop routing
- Hop intelligence based on brewing characteristics
- Hop product-form information
- Hop aliases
- Base-variety relationships
- Alpha-acid information
- Hop inventory infrastructure

The goal is to allow questions such as:

```text
Compare Citra and Mosaic.
What are the characteristics of Citra?
Give me hops similar to this one.
```

Hop intelligence is designed to interpret structured hop data rather than relying solely on free-form generated knowledge.

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

The synthesis system is deterministic and does not require an LLM to generate the underlying style facts.

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
- Connection and retry handling
- Tank-status reporting

The current Beer30 integration uses sandbox data for development and testing.

Because sandbox data may not represent current brewery operations, Beer30 WIP responses identify the source report date and local retrieval timestamp rather than presenting the information as live operational data.

Live production integration will be expanded once current API access and production data are available.

---

## 📊 Upserve Sales Automation

Brews Springsteen now includes an operational weekly Upserve sales-report workflow.

The current workflow uses the existing brewery Gmail account rather than requiring a separate Upserve API integration.

```text
Upserve Weekly Email
        │
        ▼
      Gmail
        │
        ▼
Find Product Mix CSV
        │
        ▼
Download Attachment
        │
        ▼
Parse CSV
        │
        ▼
Filter B - Full / C - Full
        │
        ▼
Rank by Units Sold
        │
        ▼
Format Weekly Report
        │
        ▼
Slack Staff Channel
        │
        ▼
Record Processed Report
```

### Report Filtering

The system extracts products belonging to:

```text
B - Full
C - Full
```

Products are ranked by the Upserve `Sold` field.

The number of products is dynamic; the report does not depend on a fixed number of products.

### Idempotency

Successfully processed Upserve emails are recorded in SQLite.

A report that has already been processed will not be sent to Slack again.

This protects against:

- Scheduler retries
- Duplicate task executions
- Manual reruns
- Temporary infrastructure failures followed by retries

The database stores the source Gmail message ID and reporting period.

### Automated Runner

The production runner is:

```text
scripts/run_upserve_weekly.py
```

The runner:

1. Initializes the database.
2. Searches Gmail for the latest matching Upserve report.
3. Downloads the CSV attachment.
4. Parses and ranks the report.
5. Sends the formatted report to the brewery staff Slack channel.
6. Records successful processing.
7. Logs the result and any errors.

### Windows Task Scheduler

The Upserve runner is configured as a Windows Task Scheduler job.

It executes:

```powershell
.venv\Scripts\python.exe -m scripts.run_upserve_weekly
```

The production task runs hourly on Mondays during the expected Upserve reporting window.

Repeated execution is safe because of the SQLite idempotency check.

### Logging

Upserve execution logs are written to:

```text
data/logs/upserve_weekly.log
```

The runner records:

- Start time
- Processing status
- Reporting period
- Slack timestamp when a report is sent
- Processing failures

The scheduler is configured to return a failure exit code when processing fails so that Windows Task Scheduler can correctly identify failed executions.

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
- Hop information and recommendations
- Beer30 WIP information

The goal is to allow brewery staff to ask questions naturally rather than learn a collection of application-specific commands.

---

## 🎸 Springsteen Easter Egg

Brews Springsteen includes a small personality feature that responds to requests such as:

```text
@Brews Springsteen play me something
```

The bot can randomly select a short Bruce Springsteen lyric snippet and song title, adding a bit of personality to the conversational interface.

---

## 🗄️ Database Architecture

SQLite provides structured local storage for brewery knowledge, operational data, production records, external-system snapshots, and workflow state.

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
hop_varieties
upserve_processed_reports
```

The database architecture is intentionally modular.

Source-specific beer-style information remains separated so that provenance can be preserved when multiple knowledge sources are used together.

The `upserve_processed_reports` table provides persistent state for automated Upserve report processing and duplicate protection.

---

## 🔌 Integrations

### Current Integrations

- Google Sheets
- Google Drive API
- Gmail API
- Slack API
- Slack Bolt / Socket Mode
- SQLite
- Beer30 REST API
- BJCP style data
- Brewers Association style data
- Windows Task Scheduler

### Completed Automated Workflows

- Google Sheets schedule intelligence
- Google Sheets task completion
- Daily operational reporting
- End-of-day reporting
- Beer30 WIP reporting
- Upserve weekly sales reporting
- Slack delivery of operational reports

### Planned / Pending Integrations

- Beer30 live production integration
- Additional brewery operational systems
- Expanded sales analytics

Potential sales analytics include:

- Weekly beer and cider rankings
- Monthly beer and cider rankings
- Individual product performance
- Packaged/canned product performance
- Historical sales trends
- Automated weekly management reports
- Automated monthly business intelligence reports

---

## 🛠️ Technology

### Language

- Python

### Data & Storage

- SQLite
- Google Sheets
- JSON
- CSV

### APIs & Integrations

- Google Sheets API
- Google Drive API
- Gmail API
- Slack API
- Slack Bolt / Socket Mode
- Beer30 REST API

### Python Libraries

- `gspread`
- `google-auth`
- `google-api-python-client`
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
- Windows Task Scheduler

---

## 📁 Project Structure

```text
brewery_bot/
│
├── integrations/
│   ├── board_reader.py
│   ├── google_sheets.py
│   ├── gmail.py
│   ├── beer30.py
│   ├── slack.py
│   └── upserve.py
│
├── intelligence/
│   ├── task_queries.py
│   ├── schedule_commands.py
│   ├── beer30_queries.py
│   └── ...
│
├── knowledge/
│   ├── database.py
│   ├── encyclopedia.py
│   ├── beer_queries.py
│   ├── upserve.py
│   ├── hop_intelligence.py
│   ├── hop_queries.py
│   ├── hop_comparison.py
│   ├── style_crosswalk.py
│   ├── style_synthesis.py
│   └── ...
│
├── reports/
│   ├── daily_report.py
│   ├── daily_tasks.py
│   ├── eod_report.py
│   ├── schedule.py
│   └── upserve_report.py
│
├── scripts/
│   ├── run_upserve_weekly.py
│   ├── sync_beer30_inventory.py
│   └── data import / processing scripts
│
├── tests/
│   ├── test_ba_question_routing.py
│   ├── test_ba_style_lookup.py
│   ├── test_ba_style_formatting.py
│   ├── test_style_crosswalk.py
│   ├── test_style_synthesis.py
│   ├── test_upserve.py
│   ├── test_upserve_processing.py
│   ├── test_upserve_idempotency.py
│   ├── test_upserve_report.py
│   ├── test_run_upserve_weekly.py
│   └── ...
│
├── styles.json
├── requirements.txt
├── pytest.ini
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

### 4. Configure Credentials

The application uses environment variables and local credential files for external services.

Create a `.env` file containing the required Slack credentials and other environment-specific configuration.

Example:

```text
SLACK_BOT_TOKEN=your_bot_token
SLACK_APP_TOKEN=your_app_token
BREWS_STAFF_CHANNEL_ID=your_staff_channel_id
```

Beer30 credentials should also be stored locally rather than committed to source control.

Google credentials should be stored locally in the appropriate credential file.

Credentials and private operational data are intentionally excluded from the public repository.

### 5. Initialize the Database

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

### Upserve Weekly Report

```powershell
python -m scripts.run_upserve_weekly
```

The Upserve runner can be executed manually at any time. If the latest report has already been processed, the runner exits without sending another Slack message.

---

## 🧪 Testing

The project uses `pytest` for automated testing.

The current regression suite contains **97 tests** covering:

- Schedule and task workflows
- Task completion
- Slack integration and routing
- Daily reporting
- Tank status
- Beer30 integration
- Beer knowledge
- BJCP style lookup and routing
- Brewers Association style lookup and routing
- BJCP/BA crosswalking
- Style synthesis
- Hop intelligence
- Hop comparisons and recommendations
- Upserve parsing
- Upserve report formatting
- Upserve processing
- Upserve idempotency
- Upserve scheduled execution

Run the complete test suite with:

```powershell
pytest
```

Current baseline:

```text
97 passed
```

Targeted Upserve tests:

```powershell
pytest tests/test_upserve_processing.py tests/test_run_upserve_weekly.py
```

---

## 🔐 Security

Private credentials and operational data are intentionally excluded from version control.

The repository ignores sensitive/local files such as:

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
- Natural-language task completion
- Slack integration
- Daily reporting
- End-of-day reporting
- Tank and fermentation status
- Beer knowledge
- BJCP style information
- Brewers Association style information
- BJCP/BA style crosswalking
- Deterministic BJCP/BA style synthesis
- Hop intelligence
- Hop comparisons and recommendations
- Beer30 sandbox integration
- Beer30 WIP and inventory infrastructure
- Upserve weekly sales automation
- Gmail-based report ingestion
- Automated Slack sales reporting
- Persistent report idempotency
- Windows Task Scheduler execution

### Current Development Priorities

Beer30 live-data expansion remains dependent on access to current production data.

The Upserve weekly reporting workflow is operational and has been tested through the complete Gmail → CSV → parsing → Slack → SQLite pipeline.

The broader project continues toward a centralized brewery operations and analytics platform.

---

## 🎯 Future Development

Potential future capabilities include:

- Expanded BJCP/BA style crosswalk
- Style aliases and alternate terminology
- Additional beer knowledge sources
- Beer30 live production integration
- Production and batch tracking
- Fermentation analytics
- Inventory analysis
- Beer and cider sales rankings
- Historical sales analytics
- Packaged product performance
- Weekly management reports
- Monthly business intelligence reports
- Automated operational alerts
- Historical production analytics
- Natural-language access to brewery data
- Additional brewery-system integrations
- Cloud-hosted automation

---

## 💡 Why I Built It

This project was developed to solve a real operational problem in a working brewery environment.

Rather than replacing the brewery's existing processes, Brews Springsteen is designed to connect to the tools already being used and automate the repetitive work around them.

The project provides hands-on experience with:

- API integration
- Data modeling
- Knowledge-source migration
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
- Workflow automation
- External-system integration

The long-term goal is to create a centralized brewery operations assistant capable of connecting **production, cellar operations, inventory, sales, scheduling, and brewery knowledge through a single interface.**

---

## 🍺 The Goal

```text
Production
    │
Cellar ───────┐
    │         │
Inventory ────┤
    │         │
Sales ────────┤
    │         │
Scheduling ───┤
    │         │
Knowledge ────┘
       │
       ▼
Brews Springsteen
       │
       ▼
One conversational interface
for brewery operations
```

**Brew beer. Let Springsteen handle the paperwork.** 🍺

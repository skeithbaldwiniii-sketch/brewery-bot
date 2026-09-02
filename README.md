# Brews Springsteen 🍺

## Brewery Operations Intelligence Platform

Brews Springsteen is a Python-based brewery operations intelligence platform
built to automate and simplify day-to-day brewery and cellar operations.

The system connects an existing Google Sheets production workflow with a SQLite
knowledge database, external brewery systems, and Slack, allowing brewery staff
to access schedules, task information, beer knowledge, operational data, and
reports through a natural-language interface.

> Built as a real-world brewery automation project to reduce repetitive administrative work and make operational information easier to access.

---

## Current Capabilities

### 📋 Schedule & Task Intelligence

Brews Springsteen reads the brewery's operational board from Google Sheets and
interprets tasks organized by weekday.

Users can ask questions such as:

- "What's on Wednesday?"
- "What's left today?"
- "When are we kegging Festbier?"
- "What day are deliveries?"
- "When is the event?"

The system identifies the relevant schedule or task information and returns the
appropriate answer.

The Google Sheet remains the operational source of truth, allowing the brewery
to continue using its existing workflow without requiring staff to learn a new
scheduling system.

### ✅ Daily Operations Reporting

Task completion is determined from the existing Google Sheets workflow using
**strikethrough formatting**.

The system can generate daily reports and end-of-day reports that separate
completed work from tasks that still need to be addressed.

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
- ferry steins for ofest release (10 cases)
- pull wajito & sunchaser from dugout & clean lines

NEEDS RESCHEDULING
- brewing:
- keg off festbier (6 sixtels, all halves)
- flip bt1 for thc bev
- sani bt2 for thc bev

SUMMARY: 7 completed / 4 remaining
```

### 💬 Slack Integration

Brews Springsteen integrates with Slack using **Slack Bolt** and Socket Mode.

Staff can mention the bot and ask questions directly from the brewery's
existing communication environment.

Example:

```text
@Brews Springsteen What's on Wednesday?
```

Schedule and task questions are routed through the task-intelligence layer
first. Questions that are not recognized as schedule-related can fall back to
the brewery knowledge system.

### 🍺 Beer30 Integration

Brews Springsteen includes a REST API integration with Beer30 for brewery
production and tank-management data.

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
Because sandbox data may not represent current brewery operations, Beer30 WIP
responses identify the source report date and local retrieval timestamp rather
than presenting the information as live operational data.

Live production integration will be expanded once current API access and data
are available.

### 🍺 Beer Knowledge Database

The project includes a SQLite-based brewery knowledge database containing
structured beer-style information and general brewing knowledge.

The beer-style database includes:

- Beer style
- BJCP category
- History
- Description
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

Beer-style information is based on the **BJCP 2021 Beer Style Guidelines**.

### 🧠 Natural-Language Task Intelligence

The task intelligence layer interprets natural-language questions rather than
requiring rigid commands.

It can distinguish between questions involving:

- A specific day's schedule
- Remaining tasks
- Task timing
- Beer releases
- Brewery events
- Specific brewery operations
- Beer knowledge
- Beer30 WIP information

The system searches schedule information learned from the brewery's operational
board instead of relying on a hard-coded list of brewery tasks.

### 🎸 Springsteen Easter Egg

Brews Springsteen includes a small personality feature that responds to requests
such as:

```text
@Brews Springsteen play me something
```

The bot randomly selects a short Bruce Springsteen lyric snippet and song title,
adding a bit of personality to the conversational interface.

---

## 🗄️ Database Architecture

SQLite provides structured local storage for brewery knowledge and establishes a
foundation for production and analytics functionality.

Current database tables include:

- `beer_styles`
- `encyclopedia_entries`
- `brewery_beers`
- `batches`
- `fermentation_readings`
- `beer30_inventory`
- `beer30_sync_runs`
- `beer30_wip`

The database architecture is designed to support brewery knowledge,
production records, fermentation data, external system snapshots, historical
analytics, and future brewery-specific integrations.

---

## 🔌 Integrations

### Current Integrations

- Google Sheets
- Google Drive API
- Slack
- SQLite
- Beer30 REST API (sandbox)

### Planned / Pending Integrations

- Beer30 live production integration
- Upserve / Breadcrumb

Planned sales analytics will include:

- Weekly beer and cider pint-sales rankings
- Monthly beer and cider sales rankings
- Individual product performance
- Packaged/canned product performance
- Automated weekly sales reports
- Automated monthly sales reports

These integrations will expand the project from an operations assistant into a
broader brewery operations and analytics platform.

---

## 🛠️ Technology

### Language

- Python

### Data & Storage

- SQLite
- Google Sheets

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
│   ├── import_styles.py
│   ├── seed_encyclopedia.py
│   ├── seed_styles.py
│   └── task_knowledge.py
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
│   └── [Beer30 test scripts]
│
├── main.py
├── eod_main.py
├── requirements.txt
├── styles.json
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

The application uses environment variables and local credential files for
external services.

Create a `.env` file containing the required Slack credentials:

```text
SLACK_BOT_TOKEN=your_bot_token
SLACK_APP_TOKEN=your_app_token
```

Beer30 credentials should also be stored in the local environment rather than
committed to source control.

Place the Google service-account credentials in:

```text
credentials.json
```

Credentials and private operational data are intentionally excluded from this
repository.

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

## 🔐 Security

Private credentials and operational data are intentionally excluded from
version control.

The repository ignores:

```text
.env
credentials.json
.venv/
__pycache__/
*.pyc
data/
```

No API tokens, Google service-account credentials, or local operational databases
should be committed to the repository.

### Data & Privacy

Brewery-specific operational data is treated as private and is not included in
the public source repository.

External service credentials are loaded through environment variables or local
credential files. Local databases and operational data are excluded from
version control.

The public repository contains application code, configuration examples, and
development/test infrastructure rather than brewery credentials or private
operational datasets.

---

## 🚧 Project Status

**Active development**

The core schedule intelligence, Slack integration, beer knowledge database,
daily reporting, end-of-day reporting, and Beer30 sandbox integration are
operational.

The Beer30 live-data expansion is currently pending access to current
production data.

Upserve / Breadcrumb integration is pending API information and access.

The project is being developed incrementally as a broader brewery operations
and analytics platform.

---

## 🎯 Future Development

Potential future capabilities include:

- Beer30 live production integration
- Upserve / Breadcrumb sales integration
- Production and batch tracking
- Fermentation data
- Inventory analysis
- Beer and cider sales rankings
- Packaged product performance
- Weekly management reports
- Monthly business intelligence reports
- Automated operational alerts
- Historical production analytics
- Natural-language access to brewery data

---

## 💡 Why I Built It

This project was developed to solve a real operational problem in a working
brewery environment.

Rather than replacing the brewery's existing processes, Brews Springsteen is
designed to connect to the tools already being used and automate the repetitive
work around them.

The project provides hands-on experience with:

- API integration
- Data modeling
- Database design
- Automation
- Natural-language interfaces
- Data parsing
- Operational reporting
- Python application architecture
- Real-world system integration

The long-term goal is to create a centralized brewery operations assistant
capable of connecting production, cellar operations, sales, and brewery
knowledge through a single interface.

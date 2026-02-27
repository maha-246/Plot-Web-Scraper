# Zameen Listings Tracker Scraper

A Python Selenium scraper (using undetected chromedriver) that reads Zameen listing URLs from a Google Sheet, extracts key listing details, and writes the results back to the same sheet.

## What it does
- Reads rows from **Zameen_Listings_Tracker** worksheet
- Skips rows where `Status` is `Done`
- Opens each `URL` and scrapes listing fields
- Extracts:
  - Price (PKR)
  - Marla size
  - Agent name, agency name, phone number (via Call button)
- Updates the Google Sheet row with scraped values
- Marks each row as `Done` (or `Failed` if the page does not load)

## Google Sheet Columns
Expected headers (case sensitive):
- URL
- Purpose
- Property Type
- Price
- Down Payment
- Installment Amount
- Number of Installments
- Marla Size
- Added Date
- Location
- Agency Name
- Agent Name
- Phone Number
- Scraped On
- Status

## Requirements
- Python 3.10+
- Google Chrome installed
- A Google Service Account JSON key with access to the target Google Sheet

## Setup

### 1) Install dependencies
Create a virtual environment and install requirements:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Google credentials (IMPORTANT)

This project uses a Google Service Account JSON file.

✅ Do NOT upload credentials.json to GitHub.

Steps:

- Create a Service Account in Google Cloud Console
- Download the JSON key file
- Share your Google Sheet with the Service Account email (Editor permission)
- Place the JSON file locally in the project folder as credentials.json

### Configuration

Update these values in the script if needed:

- Google Sheet key: ``client.open_by_key("YOUR_SHEET_KEY")``
- Worksheet name: ``.worksheet("Zameen_Listings_Tracker")``
- Chrome settings (Windows paths): ``user-data-dir=E:\ZameenChromeProfile`` and ``disk-cache-dir=E:\uc_cache``
- Chrome major version: ``version_main=144`` (must match your installed Chrome major version)

### Run 

``python scraper.py``

The script will process all rows that have a URL and are not marked Done.
Chrome will stay open until you press ENTER in the terminal.

### Notes

- Website layout can change, so XPaths may need updates.
- If the Call button / phone number does not appear, the listing may require login or may be restricted.
- For better performance and fewer Google API requests, consider switching per-cell updates to batch_update.

### Security

- Never commit credentials.json
- If you accidentally upload it, delete it immediately and rotate the key in Google Cloud
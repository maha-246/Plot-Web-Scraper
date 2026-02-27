# Zameen Listings Tracker Scraper

A Python automation tool that reads Zameen listing URLs from a Google Sheet, extracts key property details, and writes the results back to the same sheet for tracking and reporting.

## What it does
- Reads rows from the `Zameen_Listings_Tracker` worksheet
- Skips rows where `Status` is `Done`
- Opens each listing URL and extracts listing fields
- Writes scraped values back into the same row
- Marks each row as `Done` (or `Failed` if the page does not load)

## Data extracted
- Price (PKR)
- Marla size
- Agent name
- Agency name
- Phone number (via the Call button when available)

## Google Sheet columns
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

## Tech stack
Python, Selenium, pandas, Google Sheets API (gspread)

## Requirements
- Python 3.10+
- Google Chrome installed
- A Google Service Account JSON key with access to the target Google Sheet

## Setup

### 1) Install dependencies
Create and activate a virtual environment, then install requirements:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2) Google credentials

This project uses a Google Service Account JSON file.

Important: Do not upload credentials.json to GitHub.

Steps:

1. Create a Service Account in Google Cloud Console
2. Download the JSON key file
3. Share your Google Sheet with the Service Account email (give Editor access)
4. Place the JSON file locally in the project folder as credentials.json

## Configuration

- Update these values in scraper.py if needed:
- Google Sheet key: ```client.open_by_key("YOUR_SHEET_KEY")```
- Worksheet name: ```.worksheet("Zameen_Listings_Tracker")```
- If you are using custom Chrome profile and cache paths, update them based on your system.

## Run
```python scraper.py```

The script processes all rows that have a URL and are not marked Done. If a page fails to load or data cannot be captured, the row is marked Failed.

## Notes

- Website layout can change, so selectors/XPaths may need updates over time.
- If the Call button or phone number does not appear, the listing may require login or be restricted.
- For better performance and fewer Google API requests, consider switching from per cell updates to a batch_update.

## Security

-  Never commit credentials.json
- If you accidentally upload credentials, delete them immediately and rotate the key in Google Cloud
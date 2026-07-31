"""
Syncs newly-found jobs into a Google Sheet. Only APPENDS new rows -- it never
overwrites a row that already exists, so your manual "Status" / "Notes"
edits (and any color-highlighting you've done) are always safe.
"""
import gspread
from google.oauth2.service_account import Credentials

import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def get_worksheet():
    creds = Credentials.from_service_account_file(config.SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    try:
        sheet = client.open(config.GOOGLE_SHEET_NAME)
    except gspread.SpreadsheetNotFound:
        sheet = client.create(config.GOOGLE_SHEET_NAME)
        print(f"Created new spreadsheet '{config.GOOGLE_SHEET_NAME}'. "
              f"Share it with yourself from Google Drive if you can't see it.")

    try:
        ws = sheet.worksheet(config.GOOGLE_WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(config.GOOGLE_WORKSHEET_NAME, rows=1000, cols=len(config.SHEET_HEADERS))
        ws.append_row(config.SHEET_HEADERS)

    if ws.row_values(1) != config.SHEET_HEADERS:
        ws.update("A1", [config.SHEET_HEADERS])

    return ws


def append_jobs(ws, rows: list[list]):
    if not rows:
        return
    ws.append_rows(rows, value_input_option="USER_ENTERED")

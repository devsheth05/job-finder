import gspread
from google.oauth2.service_account import Credentials

creds = Credentials.from_service_account_file(
    "service_account.json",
    scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",]
)
client = gspread.authorize(creds)

sheets = client.openall()
if not sheets:
    print("The service account can't see ANY spreadsheets. It's not shared correctly.")
else:
    print("The service account can see these spreadsheets:")
    for s in sheets:
        print(f"  '{s.title}'")
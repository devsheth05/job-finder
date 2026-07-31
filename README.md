# Job Finder

Searches Greenhouse, Lever, and Ashby boards directly (public APIs, no
scraping) plus SimplifyJobs' New-Grad and Internship repos, scores every
posting, deduplicates across sources, and appends new matches to a Google
Sheet. Runs automatically every 6 hours via GitHub Actions.

## 1. One-time setup

### A. Google Sheets API access

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → create
   a project (or use an existing one).
2. Enable the **Google Sheets API** and **Google Drive API**
   (APIs & Services → Library → search each → Enable).
3. APIs & Services → Credentials → **Create Credentials → Service Account**.
   Give it any name (e.g. `job-finder-bot`).
4. Open the new service account → **Keys** tab → **Add Key → Create new key
   → JSON**. This downloads a `.json` file — keep it secret, never commit it.
5. Copy the service account's email address (looks like
   `job-finder-bot@your-project.iam.gserviceaccount.com`).
6. Create a Google Sheet named **"Job Search Tracker"** (must match
   `GOOGLE_SHEET_NAME` in `config.py`) and **share it with that service
   account email** (Editor access). The script will create the "Jobs" tab
   and headers automatically on first run.

### B. Push this project to GitHub

```bash
cd job-finder
git init
git add .
git commit -m "Initial commit"
gh repo create job-finder --private --source=. --push
# or create the repo on github.com and `git remote add origin <url>` + push
```

### C. Add the service account key as a GitHub secret

Repo → **Settings → Secrets and variables → Actions → New repository
secret**:
- Name: `GOOGLE_SERVICE_ACCOUNT_JSON`
- Value: paste the *entire contents* of the JSON key file downloaded in step A4.

That's it — the workflow in `.github/workflows/job-search.yml` will now run
every 6 hours automatically. You can also trigger it manually anytime from
the repo's **Actions** tab → "Job Search" → **Run workflow**.

## 2. Running it locally (to test before pushing)

```bash
pip install -r requirements.txt

# quick test without touching Google Sheets:
python main.py --no-sheets

# full run, writes to your Sheet (needs service_account.json in this folder):
python main.py
```

## 3. Tuning it to your search

Everything you'd want to adjust lives in **`config.py`**:

- `POSITIVE_KEYWORDS` / `NEGATIVE_KEYWORDS` — what makes a posting score
  higher or lower.
- `LOCATION_TIERS` — which cities/regions are worth bonus points.
- `SCORE_THRESHOLD` — postings scoring below this never make it to the sheet.
- `GREENHOUSE_COMPANIES` / `LEVER_COMPANIES` / `ASHBY_COMPANIES` — the seed
  list of companies polled directly. Add any company by finding its careers
  URL slug (e.g. `boards.greenhouse.io/**stripe**` → `"stripe"`).

## 4. How dedup works

Every job gets a fingerprint from `company + title + location`. If the same
job shows up on both Simplify and a direct Greenhouse poll, it collapses
into **one row**, with a combined `Source(s)` column — you never get
duplicate rows. `jobs.db` (SQLite) is the source of truth and is committed
back to the repo after each run so history/dedup persists forever; it also
becomes a useful longitudinal dataset over time.

## 5. The sheet

Columns: `Company, Title, Location, Remote, Posted, First Seen, Score,
Stars, Apply Link, Source(s), Status, Notes`.

The script only **appends** new rows — it never rewrites existing ones, so
your manual edits (Status, Notes, row highlighting/coloring) are always
safe across runs.

## 6. Extending it later

- Add more ATS sources by copying the pattern in `sources/greenhouse.py`
  (Workable, SmartRecruiters, Jobvite all have similar public APIs).
- Add a resume-match score by embedding your resume + each job description
  and computing cosine similarity (OpenAI/Anthropic embeddings work well).
- Add notifications (Discord/Slack webhook, email) by calling a small
  function at the end of `main.py` with the `top` matches list.
- Swap Status automation for AI-assisted triage once volume gets high.

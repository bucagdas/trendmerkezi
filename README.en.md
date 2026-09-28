# TrendMerkezi - Current Trends on X

*[Türkçe](README.md)*

TrendMerkezi is a Python bot that automatically collects Turkey's current
search trends and posts them to
**[@trendmerkezi](https://x.com/trendmerkezi)**, along with a friendly comment
and an image/video. It's fully automated: it posts 4 times a day, at times
when social media usage is high.

## How it works

Each run, the script follows these steps:

1. **Fetches trends:** Pulls fresh/rising trends from Google's "Trending Now"
   data (last 24 hours, `geo=TR`) via [`trendspy`](https://pypi.org/project/trendspy/);
   filters out finished, low-volume, or overly long (news-query-like) entries,
   sorts by rise percentage + volume, and picks the top **5**.
2. **Picks a comment:** A random, warm/witty opening line from `comments.txt`.
3. **Adds hashtags:** Up to 3 random tags from `hashtags.txt`.
4. **Picks media:** A random image/video (`.webp`, `.png`, `.jpg`, `.jpeg`,
   `.mp4`) from the `images/` folder.
5. **Builds the text safely:** To stay within X's weighted character limit of
   278: **trends are always preserved**; if needed, hashtag count is reduced
   first (3→0), then a shorter comment is picked if still too long.
6. **Posts:** Uploads media via `tweepy` (v1.1) and posts the tweet via the v2
   API; if media upload fails, continues as **text-only** so the post doesn't
   get dropped entirely.
7. **Logs:** Writes key steps and errors to both a log file and the run
   output.

## Automation (scheduling)

The bot runs on GitHub Actions (`.github/workflows/main.yml`,
`workflow_dispatch`). Since GitHub's own `schedule` triggers with delay,
scheduling is handled by an **external Cloudflare Worker cron**. **4 posts**
a day:

| UTC | Turkey (UTC+3) |
| --- | --- |
| 06:00 | 09:00 |
| 10:00 | 13:00 |
| 15:00 | 18:00 |
| 19:00 | 22:00 |

Cloudflare triggers the workflow with `dry_run: false`; the default for
manual runs is `dry_run: true`, so tweets are never posted by accident.

## Setup

Requirements are in `requirements.txt`:

- [`trendspy`](https://pypi.org/project/trendspy/): Google Trends "Trending Now" data
- [`tweepy`](https://pypi.org/project/tweepy/): X/Twitter API client

### Steps

1. Clone the repo.
2. `pip install -r requirements.txt`
3. Provide your X API credentials as **environment variables** (or GitHub
   Actions secrets):
   - `CONSUMER_KEY`
   - `CONSUMER_SECRET`
   - `ACCESS_TOKEN`
   - `ACCESS_TOKEN_SECRET`
   - `BEARER_TOKEN`
4. Prepare content files: images/videos in `images/`, one entry per line in
   `comments.txt` and `hashtags.txt`.
5. Run: `python trendmerkezi.py`

### Local testing (without tweeting)

`DRY_RUN=1 python trendmerkezi.py`: fetches trends, **prints** the tweet that
would be sent, but **does not post it live**. (Accepted values for
`DRY_RUN`: `1`, `true`, `yes`.)

## File structure

| File | Purpose |
| --- | --- |
| `trendmerkezi.py` | Main script |
| `comments.txt` | Randomly picked opening comments (one per line) |
| `hashtags.txt` | Randomly picked hashtag pool |
| `images/` | Pool of images/videos to post |
| `requirements.txt` | Python dependencies |
| `.github/workflows/main.yml` | GitHub Actions workflow |

## License

This project is licensed under the [MIT License](LICENSE).

## Author

[bucagdas](https://github.com/bucagdas)

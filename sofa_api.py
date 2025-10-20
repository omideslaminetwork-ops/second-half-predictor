import requests

LIVE_URL = "https://api.sofascore.com/api/v1/sport/football/events/live"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9"
}

def get_live_matches(debug=False):
    try:
        r = requests.get(LIVE_URL, headers=HEADERS, timeout=10)
        status = r.status_code
        if status != 200:
            return [], {"status": status, "error": "non-200"}
        data = r.json()
        events = data.get("events", [])
        matches = []
        for ev in events:
            matches.append({
                "id": ev.get("id"),
                "home_team": ev.get("homeTeam", {}).get("name"),
                "away_team": ev.get("awayTeam", {}).get("name"),
                "home_score": ev.get("homeScore", {}).get("current", 0),
                "away_score": ev.get("awayScore", {}).get("current", 0),
                "time": ev.get("status", {}).get("description"),
                "minute": ev.get("status", {}).get("minute")
            })
        meta = {"status": status, "count": len(matches)}
        return matches, meta
    except Exception as e:
        return [], {"status": "exception", "error": str(e)}

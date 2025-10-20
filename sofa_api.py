import requests

WORKER_URL = "https://sofa-relay.omideslami-network.workers.dev

"  # آدرس Worker خودت

def get_live_matches(debug=False):
    try:
        r = requests.get(WORKER_URL, timeout=12)
        status = r.status_code
        text_head = r.text[:300] if r.text else ""
        if status != 200:
            return [], {"status": status, "error": "non-200", "response_head": text_head}

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
        meta = {"status": status, "count": len(matches), "response_head": text_head}
        return matches, meta
    except Exception as e:
        return [], {"status": "exception", "error": str(e)}

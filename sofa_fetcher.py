# sofa_fetcher.py
import requests
import time

SOFA_LIVE_URL = "https://api.sofascore.com/api/v1/sport/football/events/live"
EVENT_STATS_URL = "https://api.sofascore.com/api/v1/event/{}/statistics"
EVENT_LINEUP_URL = "https://api.sofascore.com/api/v1/event/{}/lineups"
EVENT_TIMELINE_URL = "https://api.sofascore.com/api/v1/event/{}/timeline"

def fetch_live_events():
    try:
        r = requests.get(SOFA_LIVE_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("events", [])
    except Exception as e:
        print("Error fetching sofascore live:", e)
        return []

def parse_event_minimal(ev):
    try:
        return {
            "id": ev.get("id"),
            "home_name": ev.get("homeTeam", {}).get("name"),
            "away_name": ev.get("awayTeam", {}).get("name"),
            "home_score": ev.get("homeScore", {}).get("current", 0),
            "away_score": ev.get("awayScore", {}).get("current", 0),
            "status": ev.get("status", {}).get("description"),
            "minute": ev.get("status", {}).get("minute") if ev.get("status") else None,
            "tournament": ev.get("tournament", {}).get("name")
        }
    except Exception as e:
        return {"id": ev.get("id")}

def fetch_event_stats(event_id):
    """Fetch statistics and lineup for an event id (may return empty dict on error)."""
    stats = {}
    try:
        r = requests.get(EVENT_STATS_URL.format(event_id), timeout=8)
        if r.ok:
            stats_json = r.json()
            stats["raw_stats"] = stats_json
    except Exception as e:
        print("stats fetch error", e)

    try:
        r2 = requests.get(EVENT_LINEUP_URL.format(event_id), timeout=8)
        if r2.ok:
            stats["raw_lineup"] = r2.json()
    except Exception as e:
        print("lineup fetch error", e)

    try:
        r3 = requests.get(EVENT_TIMELINE_URL.format(event_id), timeout=8)
        if r3.ok:
            stats["raw_timeline"] = r3.json()
    except Exception as e:
        print("timeline fetch error", e)

    # add small sleep to be polite
    time.sleep(0.2)
    return stats

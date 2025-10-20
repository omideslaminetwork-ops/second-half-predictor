# app.py
import streamlit as st
import pandas as pd
from sofa_fetcher import fetch_live_events, parse_event_minimal, fetch_event_stats
from rules import apply_rules
from translations import TRANSLATIONS
from googletrans import Translator
import csv
from datetime import datetime, timedelta
import os

translator = Translator()

def t(key, lang="fa"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["fa"]).get(key, key)

st.set_page_config(page_title="2nd Half Predictor", layout="wide")
lang = st.sidebar.selectbox("Language / زبان / اللغة / Dil", ["fa","en","ar","tr"], index=0)
st.title(t("title", lang))
st.markdown(t("trial_info", lang))

# Simple user signup & trial (CSV based)
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

st.sidebar.header("Account")
email = st.sidebar.text_input("Email")
if st.sidebar.button("Start Free Trial"):
    if email:
        # append to users.csv
        if not os.path.exists("users.csv"):
            with open("users.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["email","start_date","status"])  # header
        with open("users.csv", "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([email, datetime.utcnow().isoformat(), "free"])
        st.sidebar.success("Trial started for " + email)
        st.session_state["user_email"] = email
    else:
        st.sidebar.warning("Enter email to start trial")

# check user status
def is_user_active(email):
    if not email:
        return False, None
    if not os.path.exists("users.csv"):
        return False, None
    dfu = pd.read_csv("users.csv")
    row = dfu[dfu["email"] == email]
    if row.empty:
        return False, None
    row = row.iloc[-1]
    start = datetime.fromisoformat(row["start_date"])
    status = row["status"]
    days = (datetime.utcnow() - start).days
    return (status == "paid") or (days < 3 and status == "free"), days

active, days = is_user_active(st.session_state.get("user_email", email))
if not active:
    st.warning("You are not active or trial expired. Start trial or pay subscription.")
    st.stop()

# Fetch live events
with st.spinner(t("loading", lang)):
    events = fetch_live_events()

if not events:
    st.info(t("no_matches", lang))
    st.stop()

parsed = [parse_event_minimal(ev) for ev in events]

st.subheader("Live Matches")
for ev in parsed:
    home = ev.get("home_name", "HOME")
    away = ev.get("away_name", "AWAY")
    status = ev.get("status", "")
    score = f"{ev.get('home_score',0)} - {ev.get('away_score',0)}"
    cols = st.columns([3,1])
    with cols[0]:
        st.markdown(f"**{home}  {score}  {away}**  —  {status}")
    with cols[1]:
        if st.button(t("analyze", lang) + f"  |  {home} vs {away}", key=f"btn_{ev.get('id')}"):
            st.info("Analyzing... fetching event details")
            stats_raw = fetch_event_stats(ev.get("id"))
            # parse minimal stats safely (you can expand this based on sofascore outputs)
            stats = {}
            # try to extract some fields if present
            try:
                rs = stats_raw.get("raw_stats", {})
                # structure differs; here we attempt safe extraction
                for item in rs.get("statistics", []):
                    # each item may contain 'home' and 'away' values
                    k = item.get("name")
                    home_val = item.get("home", {}).get("value") if item.get("home") else None
                    away_val = item.get("away", {}).get("value") if item.get("away") else None
                    if k and home_val is not None:
                        stats[f"{k}_home"] = home_val
                    if k and away_val is not None:
                        stats[f"{k}_away"] = away_val
            except Exception as e:
                print("parse stats error", e)

       # fallback simple fields
            stats["home_goals"] = ev.get("home_score",0)
            stats["away_goals"] = ev.get("away_score",0)
            stats["goal_minutes"] = []  # could be extracted from timeline
            stats["competition_type"] = ev.get("tournament", "league")
            stats["has_live_broadcast"] = True

            res = apply_rules(ev, stats)
            if res["allowed"]:
                st.success(t("allowed", lang))
            else:
                st.error(t("forbidden", lang))
            st.write(t("reasons", lang) + ":", res["reasons"])
            st.write(t("signals", lang) + ":")
            st.json(res["signals"])

            sentence_en = "High chance of second-half goal" if res["allowed"] else "Forbidden by rules"
            if lang != "en":
                try:
                    tr = translator.translate(sentence_en, dest=lang).text
                except:
                    tr = sentence_en
                st.markdown(f"**{tr}**")

# -*- coding: utf-8 -*-
import streamlit as st
from sofa_api import get_live_matches

st.set_page_config(page_title="AI Football Predictor", layout="wide")

st.title("⚽ Football Live AI Predictions")
st.caption("اگر چیزی نمایش داده نشد، یک‌بار Refresh بزن یا VPN اروپا (DE/NL/UK/CH) امتحان کن.")

if st.button("🔄 Refresh"):
    st.experimental_rerun()

matches, meta = get_live_matches(debug=False)

with st.expander("🔧 Debug info"):
    st.write(meta)

if not matches:
    st.warning("هیچ بازی زنده‌ای یافت نشد یا پاسخ خالی است. (احتمالاً نیاز به VPN یا هدر مرورگر)")
else:
    for m in matches:
        line = f"**{m['home_team']}** {m['home_score']} - {m['away_score']} **{m['away_team']}**"
        if m.get("time"):
            line += f" | {m['time']}"
        if m.get("minute") is not None:
            line += f" | min {m['minute']}"
        st.write(line)

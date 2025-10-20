# rules.py
def apply_rules(parsed_event, stats):
    reasons = []
    allowed = True
    signals = {}

    # safe getters
    h = stats.get("home_goals", parsed_event.get("home_score", 0))
    a = stats.get("away_goals", parsed_event.get("away_score", 0))
    goal_minutes = stats.get("goal_minutes", [])
    comp_type = stats.get("competition_type", parsed_event.get("tournament", "league"))
    has_broadcast = stats.get("has_live_broadcast", True)

    # Forbidden rules
    if h == 0 and a == 0:
        allowed = False
        reasons.append("First half 0-0 (forbidden)")

    stronger = stats.get("stronger_team")  # 'home'/'away'/None
    if stronger:
        if stronger == "home" and (h - a) >= 2:
            allowed = False
            reasons.append("Stronger team leading by 2+ (forbidden)")
        if stronger == "away" and (a - h) >= 2:
            allowed = False
            reasons.append("Stronger team leading by 2+ (forbidden)")

    if stats.get("red_home", 0) > 0 or stats.get("red_away", 0) > 0:
        allowed = False
        reasons.append("Red card in first half (forbidden)")

    if (h == 3 and a == 0) or (a == 3 and h == 0):
        allowed = False
        reasons.append("Score 3-0 at halftime (forbidden)")

    # early goal rule minute 0-10 one goal and finished 1-0
    early_goals = [m for m in goal_minutes if 0 <= m <= 10]
    if len(early_goals) == 1 and (h + a) == 1:
        allowed = False
        reasons.append("Single early goal 0-10 and no other goals (forbidden)")

    # penalty or own goal 40-45
    pen_min = stats.get("penalty_minute")
    if pen_min and 40 <= pen_min <= 45:
        allowed = False
        reasons.append("Penalty/own-goal between 40-45 (forbidden)")

    # top scorers presence
    if stats.get("top_scorer_present_home") is False or stats.get("top_scorer_present_away") is False:
        allowed = False
        reasons.append("Top scorer missing from lineup (forbidden)")

    # competition type forbidden
    if comp_type in ["youth", "cup_minor", "noncompetitive"]:
        allowed = False
        reasons.append("Low quality / youth / minor cup (forbidden)")

    if not has_broadcast:
        reasons.append("No live broadcast (higher manipulation risk)")

    # Signals (probabilistic heuristics)
    if abs(h - a) <= 1:
        signals["diff_one_or_draw"] = 0.80
    if stats.get("stronger_team") and ((stats.get("stronger_team") == "home" and (a-h) == 1) or (stats.get("stronger_team") == "away" and (h-a) == 1)):
        signals["stronger_behind_by_one"] = 0.95
    if (stats.get("big_chances_home", 0) + stats.get("big_chances_away", 0)) > max(1, (h + a)):
        signals["big_chances_vs_goals"] = 0.95

    signals["market_value_diff"] = stats.get("team_market_value_home",0) - stats.get("team_market_value_away",0)
    signals["height_diff"] = stats.get("avg_height_home",0) - stats.get("avg_height_away",0)
    signals["keeper_home_short"] = stats.get("keeper_height_home",999) < 190
    signals["keeper_away_short"] = stats.get("keeper_height_away",999) < 190
    signals["same_lineup_home"] = stats.get("same_lineup_home", False)
    signals["same_lineup_away"] = stats.get("same_lineup_away", False)
    signals["home_defensive_formation"] = str(stats.get("formation_home","")).startswith("3-5") or str(stats.get("formation_home","")).startswith("5-")
    signals["away_defensive_formation"] = str(stats.get("formation_away","")).startswith("3-5") or str(stats.get("formation_away","")).startswith("5-")
    signals["no_broadcast"] = not has_broadcast
    signals["high_ratings_diff"] = stats.get("home_players_rating_over_7",0) - stats.get("away_players_rating_over_7",0)
    signals["attack_profile_home"] = stats.get("attack_profile_home", 0.5)

    return {"allowed": allowed, "reasons": reasons, "signals": signals}

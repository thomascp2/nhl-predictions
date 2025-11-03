"""
RECOMMENDED EXPANDED STARS LIST (50 Players)
Based on database analysis Oct 31 - Nov 2, 2025

Sources:
  - Players with 2+ T1-ELITE picks in recent games
  - Known NHL superstars (McDavid, MacKinnon, etc.)
  - High-volume rookies/young stars (Bedard, Celebrini, Carlsson)
  - Consistent 75%+ average probability players

Organized by tier for easy filtering.
"""

# Tier 1: SUPERSTARS (Must-bet when favorable) - 15 players
TIER_1_SUPERSTARS = [
    # The Elite 5
    "Connor McDavid",       # EDM - 2 elite, 82.6% avg
    "Nathan MacKinnon",     # COL - 4 elite, 91.8% avg ⭐ BEST
    "Auston Matthews",      # TOR - 2 elite, 76.1% avg
    "Leon Draisaitl",       # EDM - 2 elite, 79.2% avg
    "David Pastrnak",       # BOS - 2 elite, 90.5% avg

    # Elite Playmakers
    "Nikita Kucherov",      # TBL - Reigning Art Ross winner
    "Kirill Kaprizov",      # MIN - 1 elite, 85.6% avg
    "Matthew Tkachuk",      # FLA - Top power forward
    "Artemi Panarin",       # NYR - Elite scorer
    "Jack Hughes",          # NJD - 1 elite, 79.9% avg

    # Elite Two-Way + Defense
    "Cale Makar",           # COL - 2 elite, 81.9% avg (D)
    "Sidney Crosby",        # PIT - 2 elite, 61.0% avg (veteran)
    "Jack Eichel",          # VGK - 2 elite, 92.7% avg ⭐
    "Elias Pettersson",     # VAN - Elite center
    "Jason Robertson",      # DAL - Elite goal scorer
]

# Tier 2: ELITE SCORERS (Very reliable) - 18 players
TIER_2_ELITE_SCORERS = [
    # Established Stars
    "William Nylander",     # TOR - 2 elite, 55.4% avg
    "Mitch Marner",         # TOR - 1 elite, 53.8% avg
    "Kyle Connor",          # WPG - 1 elite, 89.8% avg
    "Mark Scheifele",       # WPG - 1 elite, 82.3% avg
    "Sebastian Aho",        # CAR - 1 elite, 71.6% avg
    "Mark Stone",           # VGK - 1 elite, 87.5% avg
    "Mikko Rantanen",       # COL - Elite winger
    "Tim Stutzle",          # OTT - 0 elite, 78.1% avg
    "John Tavares",         # TOR - 2 elite, 81.8% avg
    "Brayden Point",        # TBL - Elite center
    "Tage Thompson",        # BUF - High-volume shooter

    # Rising Stars
    "Cole Caufield",        # MTL - 1 elite, 83.0% avg (sniper)
    "Adrian Kempe",         # LAK - 1 elite, 84.9% avg
    "Seth Jarvis",          # CAR - 1 elite, 84.5% avg
    "Matt Boldy",           # MIN - 0 elite, 77.7% avg
    "Alex DeBrincat",       # DET - 0 elite, 78.1% avg
    "Matthew Knies",        # TOR - 2 elite, 75.9% avg
    "Pavel Dorofeyev",      # VGK - 0 elite, 80.8% avg
]

# Tier 3: YOUNG STARS & HIGH-VOLUME (Good for specific props) - 17 players
TIER_3_YOUNG_STARS = [
    # Generational Talents
    "Connor Bedard",        # CHI - 1 elite, 74.3% avg - GENERATIONAL
    "Macklin Celebrini",    # SJS - 2 elite, 84.8% avg - ROOKIE ⭐
    "Leo Carlsson",         # ANA - 2 elite, 81.0% avg
    "Cutter Gauthier",      # ANA - 2 elite, 82.5% avg

    # High-Volume Vets (Good for Shots)
    "Alex Ovechkin",        # WSH - All-time great
    "Evgeni Malkin",        # PIT - 2 elite, 66.1% avg
    "Brad Marchand",        # BOS - Elite two-way
    "Dylan Larkin",         # DET - 2 elite, 75.6% avg
    "Bo Horvat",            # NYI - 0 elite, 75.2% avg
    "Nick Suzuki",          # MTL - 1 elite, 78.6% avg

    # Emerging/Consistent
    "Kirill Marchenko",     # CBJ - 2 elite, 79.7% avg
    "Troy Terry",           # ANA - 2 elite, 68.4% avg
    "William Eklund",       # SJS - 0 elite, 71.8% avg
    "Zach Werenski",        # CBJ - 1 elite, 75.1% avg (D)
    "Filip Forsberg",       # NSH - Veteran scorer
    "Jake Guentzel",        # TBL - Elite winger
    "Valeri Nichushkin",    # COL - When healthy
]

# COMBINED LIST (All 50 players)
ALL_STARS = TIER_1_SUPERSTARS + TIER_2_ELITE_SCORERS + TIER_3_YOUNG_STARS

# Export for use in stars_only_filter.py
STARS_EXPANDED = ALL_STARS

print(f"Total Stars: {len(ALL_STARS)}")
print(f"  Tier 1 (Superstars): {len(TIER_1_SUPERSTARS)}")
print(f"  Tier 2 (Elite Scorers): {len(TIER_2_ELITE_SCORERS)}")
print(f"  Tier 3 (Young Stars): {len(TIER_3_YOUNG_STARS)}")

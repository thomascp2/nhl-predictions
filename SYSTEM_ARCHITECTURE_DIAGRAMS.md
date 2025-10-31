# NHL Betting System - Architecture Diagrams

**Date:** October 30, 2025
**Version:** 3.0 (with TOI & Goalie Saves integration)

---

## 📊 Diagram Index

1. [High-Level System Architecture](#1-high-level-system-architecture)
2. [Detailed Workflow Swim Lanes](#2-detailed-workflow-swim-lanes)
3. [Daily Automation Timeline](#3-daily-automation-timeline)
4. [Data Flow Diagram](#4-data-flow-diagram)
5. [Prediction Model Architecture](#5-prediction-model-architecture)
6. [Edge Detection & Optimization](#6-edge-detection--optimization)

---

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph External["🌐 External Data Sources"]
        NHL_API["NHL API<br/>(Player/Team/Goalie Stats)"]
        ODDS_API["The Odds API<br/>(Game Totals)"]
        PP_API["PrizePicks API<br/>(Lines & Odds)"]
    end

    subgraph DataLayer["💾 Data Layer"]
        DB[(SQLite Database<br/>nhl_predictions.db)]
        DB_Tables["Tables:<br/>• player_stats<br/>• team_stats<br/>• goalie_stats<br/>• player_game_logs<br/>• predictions<br/>• prizepicks_edges<br/>• gto_parlays"]
    end

    subgraph PredictionEngine["🧠 Prediction Engine"]
        StatModel["Statistical Model<br/>Points & Shots"]
        MLModel["ML Ensemble Model<br/>XGBoost + Calibration"]
        TOIModel["TOI Model<br/>Linear Probability"]
        GoalieModel["Goalie Saves Model<br/>Linear Probability"]
    end

    subgraph Optimization["⚡ Optimization Layer"]
        MultiLine["Multi-Line EV<br/>Optimizer"]
        GTO["GTO Parlay<br/>Builder"]
        Correlation["Correlation<br/>Detector"]
        Bankroll["Bankroll<br/>Manager"]
    end

    subgraph Output["📤 Output"]
        Files["Files:<br/>• LATEST_PICKS.txt<br/>• LATEST_PICKS.csv<br/>• GTO_PARLAYS_*.csv<br/>• MULTI_LINE_EDGES_*.csv"]
        GitHub["GitHub<br/>Auto-Commit"]
        Dashboard["Streamlit<br/>Dashboard"]
    end

    subgraph Automation["🤖 Automation"]
        Scheduler["Task Scheduler<br/>4x Daily"]
        Workflow["run_complete_workflow_gto.py"]
    end

    %% External to Data
    NHL_API -->|Fetch Stats| DB
    ODDS_API -->|Game Totals| DB
    PP_API -->|Lines & Odds| MultiLine

    %% Data to Predictions
    DB -->|Player/Team Stats| StatModel
    DB -->|All Features| MLModel
    DB -->|TOI History| TOIModel
    DB -->|Goalie Stats| GoalieModel

    %% Predictions to DB
    StatModel -->|Save Predictions| DB
    MLModel -->|Save Predictions| DB
    TOIModel -->|Save Predictions| DB
    GoalieModel -->|Save Predictions| DB

    %% DB to Optimization
    DB -->|Load Predictions| MultiLine
    MultiLine -->|Edges| GTO
    GTO -->|Check Correlation| Correlation
    GTO -->|Calculate Sizing| Bankroll

    %% Optimization to Output
    MultiLine -->|Save Edges| DB
    GTO -->|Save Parlays| DB
    DB -->|Generate Files| Files
    Files -->|Commit| GitHub
    DB -->|Display| Dashboard

    %% Automation
    Scheduler -->|Trigger 4x Daily| Workflow
    Workflow -->|Orchestrates| PredictionEngine
    Workflow -->|Orchestrates| Optimization
    Workflow -->|Orchestrates| Output

    style External fill:#e1f5ff
    style DataLayer fill:#fff4e1
    style PredictionEngine fill:#e8f5e9
    style Optimization fill:#f3e5f5
    style Output fill:#fce4ec
    style Automation fill:#fff9c4
```

---

## 2. Detailed Workflow Swim Lanes

```mermaid
flowchart TB
    subgraph DataSources["🌐 DATA SOURCES"]
        direction TB
        DS1["NHL API"]
        DS2["The Odds API"]
        DS3["PrizePicks API"]
    end

    subgraph DataRefresh["📥 DATA REFRESH (Smart Cache)"]
        direction TB
        Check["Check Data Age<br/>(>2 hours old?)"]
        Fetch["Fetch Fresh Data:<br/>• Player Stats<br/>• Team Stats<br/>• Goalie Stats<br/>• Game Logs"]
        UseCache["Use Cached Data"]

        Check -->|Yes| Fetch
        Check -->|No| UseCache
    end

    subgraph Predictions["🎯 PREDICTION MODELS (4 Models)"]
        direction TB

        subgraph StatModel["Statistical Model"]
            SP1["Points Prediction<br/>(Piecewise Linear)"]
            SP2["Shots Prediction<br/>(Normal Distribution)"]
        end

        subgraph MLModel["ML Ensemble Model"]
            ML1["Load XGBoost Models<br/>(Points & Shots)"]
            ML2["Extract 33 Features"]
            ML3["Predict Probabilities"]
            ML4["Calibrate (Isotonic)"]
            ML5["Ensemble 70/30 Weight"]

            ML1 --> ML2 --> ML3 --> ML4 --> ML5
        end

        subgraph TOIModel["TOI Model"]
            TOI1["Fetch TOI History"]
            TOI2["Classify Player Roles"]
            TOI3["Predict TOI"]
            TOI4["Generate Multi-Lines<br/>(13.5 - 23.5 min)"]

            TOI1 --> TOI2 --> TOI3 --> TOI4
        end

        subgraph GoalieModel["Goalie Saves Model"]
            GS1["Get Goalie SV%"]
            GS2["Get Team Defense"]
            GS3["Get Opp Offense"]
            GS4["Predict Shots Against"]
            GS5["Predict Saves<br/>(Shots × SV%)"]
            GS6["Generate Multi-Lines<br/>(21.5 - 31.5 saves)"]

            GS1 --> GS2 --> GS3 --> GS4 --> GS5 --> GS6
        end
    end

    subgraph Database["💾 DATABASE"]
        direction TB
        SavePreds["Save All Predictions<br/>to predictions table"]
        CountPreds["Expected:<br/>• Points: 40-50<br/>• Shots: 40-50<br/>• TOI: 10-20<br/>• Saves: 15-30<br/>TOTAL: 105-135"]

        SavePreds --> CountPreds
    end

    subgraph EdgeDetection["💰 EDGE DETECTION"]
        direction TB
        FetchPP["Fetch PrizePicks Lines<br/>(150-200 props)"]
        Match["Match Against<br/>Our Predictions"]
        Extrapolate["Extrapolate Probabilities<br/>(Exponential Decay)"]
        CalcEV["Calculate EV:<br/>EV = (prob × multiplier) - 1"]
        FilterEV["Filter Edges<br/>(EV ≥ 7%)"]
        SaveEdges["Save to<br/>prizepicks_edges table"]

        FetchPP --> Match --> Extrapolate --> CalcEV --> FilterEV --> SaveEdges
    end

    subgraph GTOOptimization["🎲 GTO PARLAY OPTIMIZATION"]
        direction TB
        LoadEdges["Load Edges<br/>(EV ≥ 7%)"]
        Priority["Prioritize:<br/>GOBLIN > STANDARD > DEMON"]
        Correlate["Check Correlations:<br/>• Same game?<br/>• Same team?<br/>• Same player?"]
        Build["Build Parlays:<br/>2-leg, 3-leg, 4-leg"]
        RankEV["Rank by Combined EV"]
        Top10["Select Top 10-15"]
        SaveParlays["Save to<br/>gto_parlays table"]

        LoadEdges --> Priority --> Correlate --> Build --> RankEV --> Top10 --> SaveParlays
    end

    subgraph Output["📤 OUTPUT"]
        direction TB
        GenFiles["Generate Files:<br/>• LATEST_PICKS.txt<br/>• LATEST_PICKS.csv<br/>• GTO_PARLAYS_*.csv<br/>• MULTI_LINE_EDGES_*.csv"]
        Commit["Git Commit & Push<br/>to GitHub"]

        GenFiles --> Commit
    end

    subgraph UserActions["👤 USER ACTIONS"]
        direction TB
        Review["Review Picks<br/>(Dashboard or GitHub)"]
        CalcBets["Calculate Bet Sizes<br/>(Bankroll Manager)"]
        PlaceBets["Place Bets on<br/>PrizePicks"]
        TrackResults["Track Results<br/>(After Games)"]

        Review --> CalcBets --> PlaceBets --> TrackResults
    end

    %% Main flow
    DataSources --> DataRefresh
    DataRefresh --> Predictions
    Predictions --> Database
    Database --> EdgeDetection
    EdgeDetection --> GTOOptimization
    GTOOptimization --> Output
    Output --> UserActions

    style DataSources fill:#e1f5ff
    style DataRefresh fill:#e8f5e9
    style Predictions fill:#fff4e1
    style Database fill:#f3e5f5
    style EdgeDetection fill:#fce4ec
    style GTOOptimization fill:#e1f5ff
    style Output fill:#fff9c4
    style UserActions fill:#f3e5f5
```

---

## 3. Daily Automation Timeline

```mermaid
gantt
    title NHL Betting System - Daily Automation Schedule
    dateFormat HH:mm
    axisFormat %H:%M

    section Morning
    Wake Up & Coffee                    :milestone, m1, 07:00, 0m
    Review Yesterday Results            :a1, 07:30, 30m
    🤖 WORKFLOW #1 (8 AM)              :crit, w1, 08:00, 5m
    Grade Yesterday (if 6-11 AM)        :a2, 08:00, 3m
    Fetch Fresh Data (if >2hr old)      :a3, 08:03, 2m
    Generate 4 Prediction Models        :a4, 08:05, 3m
    Find Edges                          :a5, 08:08, 2m
    Build GTO Parlays                   :a6, 08:10, 1m
    Commit to GitHub                    :a7, 08:11, 1m
    Review Generated Picks              :a8, 08:15, 15m
    Calculate Bet Sizes                 :a9, 08:30, 15m
    Place Morning Bets                  :a10, 09:00, 60m

    section Midday
    Monitor Line Movement               :a11, 10:00, 120m
    🤖 WORKFLOW #2 (12 PM)             :crit, w2, 12:00, 5m
    Refresh Edges                       :a12, 12:00, 3m
    Rebuild Parlays                     :a13, 12:03, 2m
    Midday Strategy Session             :a14, 12:30, 90m

    section Afternoon
    🤖 WORKFLOW #3 (3 PM)              :crit, w3, 15:00, 5m
    Final Pre-Game Data Refresh         :a15, 15:00, 2m
    Update Predictions                  :a16, 15:02, 3m
    Final Betting Window                :a17, 17:00, 60m

    section Evening
    🤖 WORKFLOW #4 (6 PM) - FINAL      :crit, w4, 18:00, 5m
    Last Update Before Games            :a18, 18:00, 3m
    Finalize Parlays                    :a19, 18:03, 2m
    Pre-Game Review                     :a20, 18:30, 30m
    Games Start                         :milestone, m2, 19:00, 0m
    Live Monitoring (Optional)          :a21, 19:00, 180m
    Most Games End                      :milestone, m3, 21:00, 0m
    Record Results                      :a22, 21:00, 60m
    Day Wrap-Up                         :a23, 23:00, 30m
```

---

## 4. Data Flow Diagram

```mermaid
flowchart LR
    subgraph External["External APIs"]
        NHL["NHL API<br/>📊"]
        ODDS["The Odds API<br/>💰"]
        PP["PrizePicks API<br/>🎯"]
    end

    subgraph Storage["Database Tables"]
        PS[("player_stats<br/>Season & Recent")]
        TS[("team_stats<br/>Defense/Offense")]
        GS[("goalie_stats<br/>SV%, GAA")]
        GL[("player_game_logs<br/>Historical Results")]
        PREDS[("predictions<br/>All Models")]
        EDGES[("prizepicks_edges<br/>+EV Opportunities")]
        PARLAYS[("gto_parlays<br/>Optimized Combos")]
    end

    subgraph Models["Prediction Models"]
        STAT["Statistical<br/>Model"]
        ML["ML Ensemble<br/>Model"]
        TOI["TOI<br/>Model"]
        GOALIE["Goalie Saves<br/>Model"]
    end

    subgraph Optimizer["Optimization"]
        MULTI["Multi-Line<br/>EV Calc"]
        GTO["GTO Parlay<br/>Builder"]
    end

    subgraph Files["Output Files"]
        TXT["LATEST_PICKS.txt"]
        CSV["LATEST_PICKS.csv"]
        GTOCSV["GTO_PARLAYS_*.csv"]
        EDGECSV["MULTI_LINE_EDGES_*.csv"]
    end

    %% External to Storage
    NHL -->|Fetch| PS
    NHL -->|Fetch| TS
    NHL -->|Fetch| GS
    NHL -->|Fetch| GL
    ODDS -->|Game Totals| TS

    %% Storage to Models
    PS -->|Season Stats| STAT
    PS -->|33 Features| ML
    PS -->|TOI History| TOI
    GS -->|Goalie Stats| GOALIE
    TS -->|Team Stats| STAT
    TS -->|Team Stats| ML
    TS -->|Defense/Offense| GOALIE
    GL -->|Historical| ML

    %% Models to Storage
    STAT -->|Points/Shots| PREDS
    ML -->|Ensemble| PREDS
    TOI -->|TOI Props| PREDS
    GOALIE -->|Save Props| PREDS

    %% Storage to Optimizer
    PREDS -->|All Predictions| MULTI
    PP -->|PrizePicks Lines| MULTI
    MULTI -->|Edges| EDGES
    EDGES -->|High EV| GTO
    GTO -->|Parlays| PARLAYS

    %% Optimizer to Files
    PREDS -->|Format| TXT
    PREDS -->|Format| CSV
    EDGES -->|Export| EDGECSV
    PARLAYS -->|Export| GTOCSV

    %% Files to GitHub
    TXT -.->|Commit| GH["GitHub<br/>🐙"]
    CSV -.->|Commit| GH
    GTOCSV -.->|Commit| GH
    EDGECSV -.->|Commit| GH

    style External fill:#e1f5ff
    style Storage fill:#fff4e1
    style Models fill:#e8f5e9
    style Optimizer fill:#f3e5f5
    style Files fill:#fce4ec
```

---

## 5. Prediction Model Architecture

```mermaid
flowchart TB
    subgraph Input["📥 INPUT DATA"]
        direction TB
        I1["Player Season Stats<br/>(PPG, SOG, TOI, Sh%)"]
        I2["Rolling Stats<br/>(L5, L10 averages)"]
        I3["Team Stats<br/>(GA, SA per game)"]
        I4["Goalie Stats<br/>(SV%, GAA)"]
        I5["Game Context<br/>(Home/Away, O/U Total)"]
    end

    subgraph Features["🔧 FEATURE ENGINEERING"]
        direction TB
        F1["Season Features (8)<br/>PPG, SOG, GPG, APG, TOI, Sh%, GP, Position"]
        F2["Rolling Features (10)<br/>L10 PPG/SOG/Std/Z-score<br/>L5 PPG/SOG/Std/Z-score"]
        F3["Form Indicators (4)<br/>Recent vs Season<br/>L5 vs L10 trends"]
        F4["Consistency Metrics (2)<br/>PPG/SOG consistency"]
        F5["Opponent Factors (7)<br/>GA/SA normalized<br/>Goalie difficulty"]
        F6["Context (2)<br/>Home advantage<br/>Position indicator"]

        Total["TOTAL: 33 Features"]
        F1 & F2 & F3 & F4 & F5 & F6 --> Total
    end

    subgraph StatModel["📊 STATISTICAL MODEL"]
        direction TB

        subgraph Points["Points Prediction"]
            P1["Expected Points =<br/>PPG × Home/Away × Game Total"]
            P2["Piecewise Linear:<br/>PPG ≥1.5 → 95%<br/>PPG 1.0-1.5 → 70-95%<br/>PPG 0.5-1.0 → 50-70%<br/>PPG <0.5 → linear"]
            P3["Probability (OVER 0.5)"]

            P1 --> P2 --> P3
        end

        subgraph Shots["Shots Prediction"]
            S1["Expected Shots =<br/>SOG × Home/Away × Game Total"]
            S2["Std Dev = Expected × 0.40"]
            S3["Normal Distribution:<br/>P(X > 2.5) = 1 - CDF(2.5)"]
            S4["Probability (OVER 2.5)"]

            S1 --> S2 --> S3 --> S4
        end
    end

    subgraph MLModel["🤖 ML ENSEMBLE MODEL"]
        direction TB

        XGB1["XGBoost Classifier<br/>(200 trees, depth 5)"]
        XGB2["Trained on Historical<br/>Game Logs with Results"]
        CAL["Calibrated Classifier<br/>(Isotonic Regression)"]
        PRED["Calibrated Probability<br/>(Points & Shots)"]

        XGB1 --> XGB2 --> CAL --> PRED
    end

    subgraph TOIModel["⏱️ TOI MODEL"]
        direction TB

        T1["Classify Player Role:<br/>Elite/Top/Middle/Bottom"]
        T2["Predict Average TOI"]
        T3["Dynamic Std Dev:<br/>Elite: 1.5 min<br/>Top: 2.0 min<br/>Middle: 2.5 min<br/>Bottom: 3.0 min"]
        T4["Linear Probability:<br/>P = 0.5 + distance/(4×σ)"]
        T5["Generate Lines:<br/>13.5, 15.5, 17.5, 19.5, 21.5, 23.5"]

        T1 --> T2 --> T3 --> T4 --> T5
    end

    subgraph GoalieModel["🥅 GOALIE SAVES MODEL"]
        direction TB

        G1["Goalie SV%<br/>Team Defense (SA/G)<br/>Opponent Offense (SF/G)"]
        G2["Predict Shots Against:<br/>50% Team + 50% Opp"]
        G3["Home/Away Adjustment:<br/>Home: -3% shots<br/>Away: +3% shots"]
        G4["Predict Saves:<br/>Shots × SV%"]
        G5["Dynamic Std Dev:<br/>Elite (≥.920): 4.0<br/>Good (≥.910): 5.0<br/>Avg (<.910): 6.0"]
        G6["Linear Probability:<br/>P = 0.5 + distance/(4×σ)"]
        G7["Generate Lines:<br/>21.5, 23.5, 25.5, 27.5, 29.5, 31.5"]

        G1 --> G2 --> G3 --> G4 --> G5 --> G6 --> G7
    end

    subgraph Ensemble["🎯 ENSEMBLE COMBINATION"]
        direction TB

        E1["Weighted Average:<br/>70% Statistical + 30% ML"]
        E2["Assign Tier:<br/>≥70% = T1-ELITE<br/>≥60% = T2-STRONG<br/><60% = T3-MARGINAL"]

        E1 --> E2
    end

    subgraph Output["📤 OUTPUT"]
        direction TB

        O1["Save to predictions table:<br/>• Player, Team, Opponent<br/>• Prop Type, Line<br/>• Probability, Tier<br/>• Reasoning"]
    end

    %% Flow
    Input --> Features
    Features --> StatModel
    Features --> MLModel
    Features --> TOIModel
    Features --> GoalieModel

    StatModel --> Ensemble
    MLModel --> Ensemble
    TOIModel --> Output
    GoalieModel --> Output
    Ensemble --> Output

    style Input fill:#e1f5ff
    style Features fill:#fff4e1
    style StatModel fill:#e8f5e9
    style MLModel fill:#e8f5e9
    style TOIModel fill:#e8f5e9
    style GoalieModel fill:#e8f5e9
    style Ensemble fill:#f3e5f5
    style Output fill:#fce4ec
```

---

## 6. Edge Detection & Optimization

```mermaid
flowchart TB
    subgraph Predictions["📊 OUR PREDICTIONS"]
        direction TB
        P1["Points: 40-50 picks<br/>Shots: 40-50 picks<br/>TOI: 10-20 picks<br/>Saves: 15-30 picks"]
        P2["For each pick:<br/>• Player, Prop Type<br/>• Line (e.g., O0.5 points)<br/>• Our Probability (e.g., 75%)"]

        P1 --> P2
    end

    subgraph PrizePicks["🎯 PRIZEPICKS LINES"]
        direction TB
        PP1["Fetch All Lines<br/>(150-200 props)"]
        PP2["For each line:<br/>• Player, Prop Type<br/>• Line (may differ from ours)<br/>• Odds Type (GOBLIN/STANDARD/DEMON)"]

        PP1 --> PP2
    end

    subgraph Matching["🔗 LINE MATCHING"]
        direction TB
        M1["Match by Player + Prop Type"]
        M2["Find PP line in our predictions"]

        M1 --> M2
    end

    subgraph Extrapolation["📈 PROBABILITY EXTRAPOLATION"]
        direction TB

        EX1{"Line Exact Match?"}
        EX2["Use Exact Probability"]
        EX3{"Line Between Two<br/>Predictions?"}
        EX4["Linear Interpolation"]
        EX5["Exponential Extrapolation"]

        EX1 -->|Yes| EX2
        EX1 -->|No| EX3
        EX3 -->|Yes| EX4
        EX3 -->|No| EX5

        subgraph Decay["Decay Rates by Prop"]
            D1["Points: 0.60 (aggressive)<br/>Goals: 0.55 (very aggressive)<br/>Assists: 0.65<br/>Shots: 0.72<br/>TOI: varies by tier<br/>Saves: varies by tier"]
        end

        EX5 --> Decay
    end

    subgraph EVCalc["💰 EV CALCULATION"]
        direction TB

        EV1["Get Individual Multiplier:<br/>GOBLIN: ~1.44x<br/>STANDARD: ~1.73x<br/>DEMON: ~2.0x"]
        EV2["PrizePicks Implied Prob:<br/>1 / multiplier"]
        EV3["Our Edge:<br/>(Our Prob - PP Prob) × 100"]
        EV4["Expected Value:<br/>(Our Prob × Multiplier) - 1"]
        EV5{"EV ≥ 7%?"}
        EV6["KEEP - This is an edge!"]
        EV7["DISCARD - No edge"]

        EV1 --> EV2 --> EV3 --> EV4 --> EV5
        EV5 -->|Yes| EV6
        EV5 -->|No| EV7
    end

    subgraph Edges["📋 EDGE PLAYS"]
        direction TB

        ED1["Typical Results:<br/>25-50 edge plays found"]
        ED2["Save to prizepicks_edges table"]
        ED3["Export to MULTI_LINE_EDGES_*.csv"]

        ED1 --> ED2 --> ED3
    end

    subgraph GTOInput["🎲 GTO PARLAY INPUTS"]
        direction TB

        G1["Filter: EV ≥ 7%"]
        G2["Prioritize:<br/>1. GOBLIN (most reliable)<br/>2. STANDARD<br/>3. DEMON (last resort)"]
        G3["Typical: 25-50 candidates"]

        G1 --> G2 --> G3
    end

    subgraph Correlation["🔗 CORRELATION CHECKS"]
        direction TB

        C1{"Same Game?"}
        C2{"Same Team?"}
        C3{"Same Player<br/>Different Props?"}
        C4{"Known Correlation<br/>(e.g., SOG + Points)?"}
        C5["AVOID - Correlated"]
        C6["OK - Independent"]

        C1 -->|Yes| C5
        C1 -->|No| C2
        C2 -->|Yes| C5
        C2 -->|No| C3
        C3 -->|Yes| C4
        C3 -->|No| C6
        C4 -->|Yes| C5
        C4 -->|No| C6
    end

    subgraph ParlayBuild["🏗️ PARLAY CONSTRUCTION"]
        direction TB

        PB1["Generate Combinations:<br/>2-leg, 3-leg, 4-leg"]
        PB2["For each parlay:<br/>Combined Prob = Prob1 × Prob2 × ..."]
        PB3["Parlay Multiplier:<br/>Mult1 × Mult2 × ..."]
        PB4["Parlay EV:<br/>(Combined Prob × Parlay Mult) - 1"]
        PB5["Rank by EV"]
        PB6["Select Top 10-15"]

        PB1 --> PB2 --> PB3 --> PB4 --> PB5 --> PB6
    end

    subgraph ParlayOutput["📤 PARLAY OUTPUT"]
        direction TB

        PO1["Save to gto_parlays table"]
        PO2["Export to GTO_PARLAYS_*.csv"]
        PO3["Display in Dashboard"]

        PO1 --> PO2 --> PO3
    end

    %% Main flow
    Predictions --> Matching
    PrizePicks --> Matching
    Matching --> Extrapolation
    Extrapolation --> EVCalc
    EVCalc --> Edges
    Edges --> GTOInput
    GTOInput --> Correlation
    Correlation --> ParlayBuild
    ParlayBuild --> ParlayOutput

    style Predictions fill:#e8f5e9
    style PrizePicks fill:#e1f5ff
    style Matching fill:#fff4e1
    style Extrapolation fill:#f3e5f5
    style EVCalc fill:#fce4ec
    style Edges fill:#e1f5ff
    style GTOInput fill:#fff9c4
    style Correlation fill:#f3e5f5
    style ParlayBuild fill:#e8f5e9
    style ParlayOutput fill:#fce4ec
```

---

## 7. Key Decision Points

```mermaid
flowchart TB
    Start([Start Workflow]) --> CheckTime{What Time<br/>Is It?}

    CheckTime -->|6-11 AM| GradeYesterday["Grade Yesterday's Picks"]
    CheckTime -->|Other| SkipGrade["Skip Grading"]

    GradeYesterday --> CheckData{Data Age<br/>>2 Hours?}
    SkipGrade --> CheckData

    CheckData -->|Yes| FetchFresh["Fetch Fresh Data:<br/>• NHL API<br/>• The Odds API"]
    CheckData -->|No| UseCached["Use Cached Data"]

    FetchFresh --> GenPreds["Generate Predictions:<br/>4 Models"]
    UseCached --> GenPreds

    GenPreds --> CheckModels{All Models<br/>Succeeded?}

    CheckModels -->|4/4| AllGood["✅ All Models Working"]
    CheckModels -->|3/4 or 2/4| Partial["⚠️ Partial Success<br/>(Core models OK)"]
    CheckModels -->|1/4 or 0/4| Failed["❌ Critical Failure"]

    AllGood --> FetchPP["Fetch PrizePicks Lines"]
    Partial --> FetchPP
    Failed --> Alert["Alert User<br/>Check Logs"]

    FetchPP --> CheckLines{Found<br/>PP Lines?}

    CheckLines -->|Yes| MatchLines["Match Against<br/>Predictions"]
    CheckLines -->|No| NoPP["⚠️ No PrizePicks Data<br/>Use Cached"]

    MatchLines --> CalcEV["Calculate EV"]
    NoPP --> CalcEV

    CalcEV --> CheckEV{Found Edges<br/>≥7% EV?}

    CheckEV -->|Yes| BuildParlays["Build GTO Parlays"]
    CheckEV -->|No| NoEdges["⚠️ No Edges Found<br/>Lower Threshold?"]

    BuildParlays --> CheckParlays{Built<br/>Parlays?}

    CheckParlays -->|Yes| Output["Generate Output Files"]
    CheckParlays -->|No| NoParlays["⚠️ No Valid Parlays<br/>Too Correlated?"]
    NoEdges --> Output

    Output --> CommitGH["Commit to GitHub"]
    NoParlays --> Output

    CommitGH --> Done([Workflow Complete])
    Alert --> Done

    style Start fill:#e8f5e9
    style Done fill:#e8f5e9
    style AllGood fill:#c8e6c9
    style Partial fill:#fff9c4
    style Failed fill:#ffcdd2
    style Alert fill:#ffcdd2
    style NoPP fill:#fff9c4
    style NoEdges fill:#fff9c4
    style NoParlays fill:#fff9c4
```

---

## 📝 Diagram Legend

### Colors
- 🟦 **Blue** - External data sources, inputs
- 🟨 **Yellow** - Data storage, cache, database
- 🟩 **Green** - Prediction models, processing
- 🟪 **Purple** - Optimization, analysis
- 🟥 **Pink** - Output, results, exports
- 🟡 **Light Yellow** - Automation, scheduling

### Symbols
- `( )` - Start/End points
- `{ }` - Decision points
- `[ ]` - Process steps
- `[( )]` - Database storage
- `-->` - Data flow
- `-.->` - Optional/async flow

---

## 🎯 How to Read These Diagrams

### System Architecture (Diagram 1)
Shows the **big picture** - all major components and how they connect. Start here to understand overall structure.

### Workflow Swim Lanes (Diagram 2)
Shows **sequential flow** through different system layers. Read top-to-bottom to follow the process.

### Daily Timeline (Diagram 3)
Shows **when things happen** throughout the day. The yellow bars are automated workflows.

### Data Flow (Diagram 4)
Shows **where data comes from** and **where it goes**. Follow the arrows to trace data movement.

### Model Architecture (Diagram 5)
Shows **how predictions are made** in detail. Each model has its own logic flow.

### Edge Detection (Diagram 6)
Shows **how we find betting opportunities** and build parlays. Critical for understanding profit generation.

---

## 🚀 Quick Navigation

**Want to understand...**
- Overall system? → See Diagram 1
- Step-by-step process? → See Diagram 2
- Daily schedule? → See Diagram 3
- Data sources? → See Diagram 4
- How predictions work? → See Diagram 5
- How we make money? → See Diagram 6

---

**END OF ARCHITECTURE DIAGRAMS**

These diagrams are rendered automatically in Markdown viewers that support Mermaid (GitHub, VS Code, etc.)

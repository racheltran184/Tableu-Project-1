# 🚗 Victoria Road Crash Analysis (2012–2024)
**Data-to-decision road safety analytics using R + Tableau .**

This repository analyses Victorian road crash records (2012–2024) to identify **where crashes concentrate, when risk peaks, who is most impacted, and which vehicle characteristics correlate with severity**. The work is designed to support practical decision-making, including targeted enforcement, infrastructure prioritisation, and fleet safety initiatives, alongside clear descriptive reporting.

---

## Why this project matters
Road safety is not a single problem, it is usually **two problems at once**:

- **Frequency problem (Metro):** high volumes driven by traffic density and exposure
- **Severity problem (Regional):** lower volumes, but disproportionately higher fatality risk once a crash occurs

This repo makes that split visible so interventions can be designed correctly.

---

## Dashboards & Key Insights (with visuals)

### 1) Strategic Gap: Are we on track for 2030 targets?
The chart below frames crashes against the required downward trajectory and highlights structural breaks (e.g., COVID-era dip, post-2021 rebound).

![Strategic Gap Analysis](https://github.com/racheltran184/Tableu-Project-1/blob/main/visualizations/strategic_gap_analysis.png)

**Insights**
- Crashes peaked mid-decade, dropped sharply during COVID mobility restrictions, then **rebounded and stabilised above the required glide path**.
- The “gap to target” framing turns trend lines into a **delivery problem**: how large the reduction must be, not just whether it increased/decreased.

---

### 2) Beyond the Hotspots: Metro vs Regional risk is not the same thing
This dashboard contrasts **crash counts** with **fatality rate per 1,000 residents**, plus a combined view comparing crash volume to fatality rate by LGA.

![Metro vs Regional Risk](https://github.com/racheltran184/Tableu-Project-1/blob/main/visualizations/metro_vs_regional_risk.png)

**Insights**
- Metro LGAs dominate crash *volume* (exposure + congestion).
- Regional/Country LGAs can show **higher per-capita fatality risk**, even with fewer crashes.
- The combined chart prevents a common policy mistake: **funding only where crashes are most numerous**, rather than where crashes are most lethal.

---

### 3) Operational Targeting: When do crashes spike and who is most affected?
This view supports deployment decisions by combining **year trend, weekday, hour category, and demographic breakdown** in one place.

![Crash Frequency by Hour, Day, and Gender](https://github.com/racheltran184/Tableu-Project-1/blob/main/visualizations/temporal_demographics_dashboard.png)

**Insights**
- Clear operational peaks: **late-week afternoon periods (afternoon rush)** dominate crash frequency.
- Demographics confirm the burden distribution (e.g., adult cohorts contribute the largest absolute counts), enabling targeted messaging/enforcement windows.

---

### 4) Vehicle Factors: Which vehicle attributes show different severity patterns?
This dashboard connects vehicle involvement and severity with **vehicle type mix, road user role, and vehicle age patterns**.

![Influence of Vehicle Characteristics on Crash Severity](https://github.com/racheltran184/Tableu-Project-1/blob/main/visualizations/vehicle_characteristics_dashboard.png)

**Insights**
- Passenger vehicles dominate totals due to exposure, but certain categories (e.g., motorcycles/utility-style vehicles) can exhibit **different severity compositions**.
- Vehicle age comparison provides a simple lens for the role of **fleet renewal and safety feature availability**.

---

## 🎯 Policy Solutions and Implementation Plan

### 1) Metropolitan Victoria (high crash volume: frequency problem)

**Objective:** Reduce crash occurrence by lowering conflict exposure, improving compliance, and limiting distraction during peak urban travel.

**A. Intersection conflict reduction (engineering-led)**

* Implement targeted intersection upgrades at high-crash sites: protected right-turn phases, raised safety platforms near activity centres, improved line-marking and turning bays, and roundabout conversions where feasible.
* Prioritise sites using a ranked list of metro LGAs and corridors with consistently high crash counts.
* **Success measures:** reduction in crashes at treated intersections relative to matched untreated sites (before–after with comparison).

**B. Speed compliance (enforcement + road design)**

* Expand automated enforcement on arterial corridors (point-to-point and high-visibility mobile operations), aligned to peak travel windows.
* Apply “self-explaining road” treatments (gateway designs, lane narrowing, improved signage consistency) where speeding risk is structural.
* **Success measures:** improved speed compliance rates and reduced serious-injury crashes on treated corridors.

**C. Congestion and distraction management**

* Improve signal coordination/adaptive control on commuter routes to reduce stop–start conflict.
* Increase mobile phone detection and seatbelt enforcement in high-volume corridors.
* **Success measures:** reduction in peak-period crash rate per exposure proxy (e.g., crashes per day/hour window) and declining share of distraction-related incidents.

---

### 2) Regional and Country Victoria (lower volume, higher lethality: severity problem)

**Objective:** Reduce fatal and serious-injury outcomes by preventing high-energy impact types and improving post-crash survivability.

**A. Median barriers and shoulder safety**

* Install wire-rope median barriers on high-speed undivided routes with head-on risk.
* Expand shoulder sealing and rumble strips to reduce run-off-road crashes linked to fatigue and inattention.
* Add overtaking lanes and improved delineation on corridors with risky passing demand.
* **Success measures:** reductions in head-on/run-off-road fatal and serious-injury crashes per treated corridor length.

**B. Speed management on high-speed routes**

* Conduct corridor-level “Safe System” speed reviews to align posted limits with roadside risk and crash severity potential.
* Deploy point-to-point enforcement on long regional corridors to address sustained speeding.
* **Success measures:** reduced mean/free-flow speeds and reduced fatal/serious injury rates on targeted corridors.

**C. Strengthened trauma response coverage**

* Optimise dispatch and coverage planning for high-risk regional LGAs and long travel-time areas.
* Improve first-responder capability (training and equipment) where access to definitive care is structurally delayed.
* **Success measures:** reduced time-to-scene and time-to-trauma transfer in priority areas; improved survivability indicators for serious crashes.

**D. Safer vehicle adoption (regional targeting)**

* Prioritise incentives for vehicles equipped with modern safety features (e.g., AEB, ESC, lane support systems) in LGAs showing high per-capita fatality rates and older fleet profiles.
* **Success measures:** declining share of crashes involving older vehicles and reduced severity conditional on crash occurrence.

---

### 3) Temporal Targeting (Friday afternoon peak)

**Objective:** Reduce incidents during the identified highest-risk operational window.

**A. Focused enforcement deployment**

* Establish recurring enforcement operations during Friday afternoon peak periods, prioritising speeding, mobile phone use, and seatbelt compliance on commuter corridors.
* **Success measures:** year-over-year reduction in crash counts within the Friday peak window and improvements in compliance indicators.

**B. Behaviour-specific risk communication**

* Deliver short, repeated messages tied to the peak window (fatigue, haste, distraction) through employers, freight/logistics partners, and commuter channels.
* **Success measures:** reduction in peak-window crashes; optional supporting measures include campaign reach and engagement.

---

### 4) Vehicle Safety and Vulnerable Road Users

**Objective:** Reduce severity by addressing vehicle risk mechanisms and protecting high-risk road users.

**A. Fleet renewal (targeted)**

* Implement scrappage/upgrade incentives focused on older vehicles in high-risk LGAs, linked to minimum safety feature thresholds in replacement vehicles.
* **Success measures:** reduction in fatal/serious injuries where older vehicle involvement is overrepresented.

**B. Motorcycle severity reduction**

* Improve safety on high-risk motorcycle corridors (curve warning systems, skid-resistant surfacing, safer roadside barriers).
* Support protective gear adoption through incentives and compliance campaigns.
* **Success measures:** reduced motorcycle fatal/serious injury rate per crash.

**C. Utility vehicle rollover risk**

* Address rollover risk through load-limit enforcement, modification compliance checks, and fleet safety requirements (ESC/stability features).
* Improve shoulders and clear zones on regional routes where rollover risk is elevated.
* **Success measures:** reduced rollover crash share and reduced severity outcomes for utility vehicles.

---

## Governance and Evaluation

* Establish a Road Safety Delivery Scorecard with a small set of outcome and operational KPIs:

  * fatalities and serious injuries (overall and per-capita),
  * metro crash frequency (volume proxy),
  * regional fatality rate per population,
  * Friday peak crash rate,
  * speed and distraction compliance indicators,
  * share of crashes involving older vehicles.
* Evaluate interventions using before–after designs with comparison corridors/LGAs to improve attribution.
* Review quarterly to reallocate effort based on measured outcomes and emerging risk patterns.
---
## Tool Used: R & Tableu
---

## Data assets
This project integrates multiple datasets (typical star/relational structure):

- `crash1.csv` — crash-level incident records (time, location, severity, etc.)
- `vehicle1.csv` — vehicle-level attributes involved in crashes
- `person1.csv` — person/casualty-level demographics and road user role
- `hour.csv` — time-based crash aggregation inputs (hour / bins)
- `LGA_POLYGON.shp` — LGA boundaries for spatial enrichment
- `LGA_Year_Population_Victoria.csv` — population denominators for rate calculations
- `data_dictionary.xlsx` — field definitions / metadata

**Join logic (high level)**
- Crash ↔ Vehicle ↔ Person linked via accident/entity identifiers
- Spatial join maps crash points to LGA polygons
- Population join enables **rates**, not just counts

---
## Repository structure

```text
victoria-road-crash-analysis/
│
├── Data/
│   ├── LGA_POLYGON.shp
│   ├── crash1.csv.gz
│   ├── person1.csv.gz
│   ├── vehicle1.csv.gz
│   ├── hour.csv
│   └── data_dictionary.xlsx
│
├── visualizations/
│   ├── metro_vs_regional_risk.png
│   ├── strategic_gap_analysis.png
│   ├── temporal_demographics_dashboard.png
│   └── vehicle_characteristics_dashboard.png
│
├── Victoria Car Crash Analysis.twb
├── Victoria Road Crash Trend.R
├── Report.pdf
└── README.md

```


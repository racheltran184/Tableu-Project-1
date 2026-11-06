# ==============================================================================
# R Visualisation 4: Victoria Road Crashes - Advanced Policy Diagnostics
# (Includes 'Trend Reversal' Annotation)
# ==============================================================================

# --- 1. Libraries ---
library(dplyr)
library(lubridate)
library(ggplot2)
library(purrr)
library(zoo)
library(readr)
library(scales) 

# --- 2. Load Data ---
# Run from the repository root; read_csv() reads the gzipped file directly
crash <- read_csv("Data/crash1.csv.gz")

# --- 3. Data Cleaning ---
crash_clean <- crash %>%
  mutate(
    ACCIDENT_DATE = as.Date(lubridate::parse_date_time(ACCIDENT_DATE,
                                                       orders = c("Y-m-d","d/m/Y","Y/m/d","d-b-Y"))),
    Year_numeric = year(ACCIDENT_DATE),
    Month_numeric = month(ACCIDENT_DATE)
  ) %>%
  filter(!is.na(Year_numeric), !is.na(Month_numeric),
         Year_numeric >= 2012, Year_numeric <= 2024) %>%
  mutate(Date = make_date(year = Year_numeric, month = Month_numeric, day = 1))

# --- 4. Policy Events Setup ---
policy_events <- data.frame(
  Date = as.Date(c("2011-01-01", "2016-05-15", "2023-03-31", "2021-12-01")),
  Policy_Short = c(" National Road Safety\n Strategy 2011-20",
                   " Towards Zero\n Victoria 2016-20",
                   " Mobile Detection\n Cameras Enforcement", 
                   " National Road Safety\n Strategy 2021-30"),
  y_position = c(1250, 950, 550, 1050),
  LineColor = c("#2980B9", "#1ABC9C", "#E67E22", "#8E44AD"),
  stringsAsFactors = FALSE
)

# --- 5. Aggregation & Advanced Statistics ---
monthly_data <- crash_clean %>%
  group_by(Date, Year_numeric, Month_numeric) %>%
  summarise(Crashes = n(), .groups = "drop") %>%
  arrange(Date) %>%
  mutate(
    Crashes_MA12 = zoo::rollmean(Crashes, k = 12, fill = NA, align = "right"),
    Crashes_SD12 = zoo::rollapply(Crashes, width = 12, FUN = sd, fill = NA, align = "right")
  )

# --- 6. Dynamic Targets & Gap Analysis ---
# Baseline
baseline_2018_2020 <- monthly_data %>%
  filter(Year_numeric >= 2018, Year_numeric <= 2020) %>%
  summarise(avg = mean(Crashes, na.rm = TRUE)) %>%
  pull(avg)

target_2030 <- baseline_2018_2020 * 0.7

# Glide Path
glide_path <- data.frame(
  Date = seq(as.Date("2021-01-01"), as.Date("2030-01-01"), by = "month")
) %>%
  mutate(
    Target_Trajectory = seq(from = baseline_2018_2020, to = target_2030, length.out = n())
  )

# --- NEW ANALYTICS ---

# A. Find Historical Min/Max Points
max_point <- monthly_data %>% filter(Crashes_MA12 == max(Crashes_MA12, na.rm=T)) %>% head(1)
min_point <- monthly_data %>% filter(Crashes_MA12 == min(Crashes_MA12, na.rm=T)) %>% head(1)

# B. Calculate "Gap to Target" for the Latest Data Point
last_data <- tail(monthly_data %>% filter(!is.na(Crashes_MA12)), 1)
target_at_last_date <- glide_path %>% 
  filter(Date == last_data$Date) %>% 
  pull(Target_Trajectory)

if(length(target_at_last_date) == 0) {
  target_at_last_date <- approx(glide_path$Date, glide_path$Target_Trajectory, xout=last_data$Date)$y
}

gap_value <- last_data$Crashes_MA12 - target_at_last_date
gap_color <- ifelse(gap_value > 0, "#C0392B", "#27AE60") # Red/Green
gap_label <- paste0("Current Gap:\n", ifelse(gap_value>0, "+", ""), round(gap_value,0), " vs Target")

# C. Calculate Recent Trend Slope (Post 2021)
recent_data <- monthly_data %>% filter(Year_numeric >= 2021)
trend_model <- lm(Crashes ~ Date, data = recent_data)
slope_yearly <- coef(trend_model)[2] * 365 
trend_desc <- ifelse(slope_yearly > 0, "Rising", "Falling")

# --- 7. The Plot ---
p4 <- ggplot() + 
  
  # 1. Backgrounds
  annotate("rect", xmin = as.Date("2011-01-01"), xmax = as.Date("2020-12-31"), ymin = -Inf, ymax = Inf, alpha = 0.05, fill = "#2980B9") +
  annotate("rect", xmin = as.Date("2021-01-01"), xmax = as.Date("2024-12-31"), ymin = -Inf, ymax = Inf, alpha = 0.05, fill = "#8E44AD") +
  annotate("rect", xmin = as.Date("2020-03-01"), xmax = as.Date("2021-09-01"), ymin = -Inf, ymax = Inf, alpha = 0.1, fill = "#F1C40F") +
  
  # 2. Target Trajectory (Glide Path)
  geom_line(data = glide_path, aes(x = Date, y = Target_Trajectory), linetype = "dotted", color = "#C0392B", size = 0.8) +
  
  # 3. Volatility Ribbon
  geom_ribbon(data = monthly_data, aes(x = Date, ymin = Crashes_MA12 - Crashes_SD12, ymax = Crashes_MA12 + Crashes_SD12), fill = "#2C3E50", alpha = 0.1) +
  
  # 4. Data Lines
  geom_line(data = monthly_data, aes(x = Date, y = Crashes), color = "#BDC3C7", alpha = 0.6, size = 0.3) +
  geom_line(data = monthly_data, aes(x = Date, y = Crashes_MA12), color = "#2C3E50", size = 1.2) +
  
  # 5. Policy Interventions
  geom_vline(data = policy_events, aes(xintercept = Date, color = LineColor), linetype = "dashed", size = 0.8) +
  geom_text(data = policy_events, aes(x = Date, y = y_position, label = Policy_Short), color = "#2C3E50", size = 3, fontface = "bold", hjust = 0, vjust = 0.5) +
  
  # 6. ENHANCED ANNOTATIONS
  
  # A. Trend Reversal (ADDED BACK)
  annotate("curve", x = as.Date("2019-06-01"), xend = as.Date("2019-01-01"),
           y = 1250, yend = 1100, color = "#C0392B", size = 0.8,
           arrow = arrow(length = unit(0.2, "cm")), curvature = 0.2) +
  annotate("text", x = as.Date("2019-12-01"), y = 1300,
           label = "Trend Reversal\n in 2019", color = "#C0392B",
           size = 3, fontface = "bold", hjust = 0.5) +
  
  # B. Historical High
  geom_point(data = max_point, aes(x = Date, y = Crashes_MA12), color = "#E74C3C", size = 2) +
  geom_text(data = max_point, aes(x = Date, y = Crashes_MA12, label = paste0("Peak: ", round(Crashes_MA12))), vjust = -1.5, size = 3, color = "#E74C3C", fontface="bold") +
  
  # C. Historical Low (COVID)
  geom_point(data = min_point, aes(x = Date, y = Crashes_MA12), color = "#27AE60", size = 2) +
  geom_text(data = min_point, aes(x = Date, y = Crashes_MA12, label = paste0("Low: ", round(Crashes_MA12))), vjust = 1.5, size = 3, color = "#27AE60", fontface="bold") +
  
  # D. "Gap to Target" Indicator (The Red Arrow)
  geom_segment(aes(x = last_data$Date, xend = last_data$Date, y = last_data$Crashes_MA12, yend = target_at_last_date), arrow = arrow(length = unit(0.2, "cm")), color = gap_color, size = 1) +
  annotate("text", x = last_data$Date - 150, y = mean(c(last_data$Crashes_MA12, target_at_last_date)), label = gap_label, color = gap_color, size = 3, fontface = "bold", hjust = 1) +
  
  # E. Trend Slope Label
  annotate("label", x = as.Date("2022-06-01"), y = 400, 
           label = paste0("Recent Trend (2021+): ", trend_desc, "\n(", round(slope_yearly, 1), " crashes/year)"),
           color = "#2C3E50", size = 3, fill = "white", alpha = 0.8) +
  
  # 7. Scales & Theme
  scale_color_identity(guide = "none") +
  scale_x_date(date_breaks = "2 years", date_labels = "%Y", limits = c(as.Date("2011-01-01"), as.Date("2026-06-01"))) +
  labs(
    title = "Victoria Road Crashes: Strategic Gap Analysis",
    subtitle = "Are we on track for 2030? Comparing current trends against the required trajectory.",
    x = NULL, y = "Monthly Crashes (Smoothed)",
    caption = paste0("Source: Victoria Crash DB | Gap calculated as difference between 12-mth MA and linear Glide Path.\nTarget: ", round(target_2030,0), " crashes/month (-30% from 2018-20 baseline).")
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(size = 18, face = "bold", color = "#2C3E50"),
    plot.subtitle = element_text(size = 12, color = "#7F8C8D"),
    panel.grid.minor = element_blank()
  )

print(p4)
ggsave("victoria_crashes_diagnostic_v2.png", plot = p4, width = 14, height = 8, dpi = 300, bg = "white")
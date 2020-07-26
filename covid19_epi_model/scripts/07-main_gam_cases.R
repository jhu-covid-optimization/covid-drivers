# libraries
library(tidyverse)
library(mgcv) # for gam 
library(dlnm)
library(foreach)
library(doParallel)
library(parallel)

rucc <- 1

# Read analysis dataframe
analysis_df <- read_csv(
  file = sprintf('./data/05-analysis_df_rucc_%s.csv', rucc),
  col_types = cols(
    'trips_count' = col_double(),
    'trips_count_baseline' = col_double(),
    'trips_count_pct_change' = col_double(),
    'trips_count_per_capita' = col_double(),
    'trips_count_log' = col_double(),
    'trips_count_per_capita_log' = col_double(),
    'Beds' = col_double(),
    'HospCt' = col_double(),
    'beds_log' = col_double(),
    'hospct_log' = col_double()
  )
) %>%
  # starting at 30 days prior to time since first death in order to get lagged
  # values 30 days prior
  filter(time_since_first_case >= (-30)) %>%
  #drop_na(trips_count_pct_change) %>%
  # code metro_state_county as factor
  mutate(metro_state_county = as.factor(metro_state_county)) %>%
  # enough for lag
  drop_na(hospct_log) %>%
  group_by(fips) %>% filter(n() > 30)# %>%


# build crossbasis for gam model for 30 day lagged mobility of retail and rec
# called cbgam
cbgam <- crossbasis(
  #analysis_df$retail_and_recreation_percent_change_from_baseline,
  analysis_df$trips_count_pct_change,
  lag = 30,
  argvar = list(fun='cr', df=4), # using penalized spline 'cr'
  arglag = list(fun='cr', df=4),
  group = analysis_df$fips # makes sure I lag appropriately by metro/county
)


# penalize the crossbasis splines
cbgamPen <- cbPen(cbgam)


# Uncomment to load model if saved previously
# dlnm.main.gam <- readRDS(sprintf("./results/07-main_gam_rucc_%s_cases.rds", rucc))


# 1. Fit GAM -------------------------------------------------------------
dlnm.main.gam <- gam(
  daily_cases ~
    cbgam + # this is the lag matrix 
    s(time_since_first_case) + 
    s(time_since_first_case, metro_state_county, bs=c("fs")) + # global smoother
    s(PC1, bs="cr", k=5) +
    s(PC2, bs="cr", k=5) +
    s(PC3, bs="cr", k=5) +
    s(PC4, bs="cr", k=5) +
    s(beds_log, bs="cr", k=5) +
    s(hospct_log, bs="cr", k=5) +
    offset(log(population_v051)), 
  data=analysis_df,
  paraPen=list(cbgam=cbgamPen),# this applies the penalty to the lagged matrix
  family="quasipoisson",
  method="REML"
)

# Save model
saveRDS(dlnm.main.gam, file = sprintf("./results/07-main_gam_rucc_%s_cases.rds", rucc))

# Before saving final, add same results from main GAM to list for plots
png(sprintf("./results/07-gam_partial_plots-rucc_%s_cases.png", rucc),width=10, height=7, units="in", res=300)
plot(dlnm.main.gam, pages=1, residuals=FALSE, seWithMean = TRUE)
dev.off()

# Check autocorrelation
original <- plot(dlnm.main.gam, pages=1, residuals=TRUE, seWithMean = TRUE)
pacf(residuals(dlnm.main.gam, type="scaled.pearson"))
pacf(residuals(dlnm.main.gam)) # basically the same

# png partial autocorrelation (PACF) plots
png(sprintf("./results/07-pacf_mainmod-rucc_%s_cases.png", rucc),width=10, height=7, units="in", res=300)
pacf(residuals(dlnm.main.gam, type="scaled.pearson"))
dev.off()

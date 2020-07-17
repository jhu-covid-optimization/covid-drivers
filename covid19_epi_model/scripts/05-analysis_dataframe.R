# ------------------------------------------------------------------------------
# Title: Make smaller study area dataframe based on counties of interest
# Author: Sarah McGough and Ryan Gan
# Purpose: Builds dataframe for analysis in GAM models; this script runs after 
# PCA in 04
# ------------------------------------------------------------------------------

# library 
library(tidyverse)
library(yaml)

# Read data --------------------------------------------------------------------
# load config file
config <- read_yaml('./scripts/config.yaml')
rucc_code <- 3

# read in pc
pc_df <- read_csv(
  file = './data/04-rucc_3_pca.csv'
  ) %>%
  # using only some variables
  select(fips, metro_area, metro_state_county, PC1:PC4)
  
# read in master time series dataframe 
master_ts <- read_csv(
  file = './data/03-nyt_us_county_timeseries_daily.csv',
  col_types = cols(
    'trips_count' = col_double(),
    'trips_count_baseline' = col_double(),
    'trips_count_pct_change' = col_double(),
    'trips_count_per_capita' = col_double(),
    'trips_count_log' = col_double(),
    'trips_count_per_capita_log' = col_double()
  )
)

# read nyt time series and limit to study fips
analysis_df <- master_ts %>% 
  # filter/subset to study fips
  # filter(fips %in% config$study_fips) %>% 
  filter(fips %in% pc_df$fips) %>%
  left_join(pc_df, by = 'fips') %>% 
  # study window ends at date 2020-05-13; for reproducibility 
  filter(date <= config$study_window$end_date) %>% 
  # impute early portion of time series using imputeTS function
  arrange(fips,date) %>%
  group_by(fips) #%>%
  # mutate_at(
  #   vars(
  #     # retail_and_recreation_percent_change_from_baseline
  #     trips_count
  #   ),
  #   list(
  #     ~ imputeTS::na_ma(., k = 5, weighting = "linear")
  #   )
  # )

# Read in hospitals and beds
acute_care <- read_csv('./data/acute_care.csv') %>%
  rename(fips = FIPS) %>%
  mutate(fips = as.character(fips))

acute_care <- acute_care %>% 
  # exclude nyc counties
  filter(!(fips %in% c('36005','36047','36061', '36081','36085'))) %>% 
  # bind in nyc aggregates
  bind_rows(
    acute_care %>%
      subset(
        fips %in% c('36005','36047','36061', '36081','36085')
      ) %>%
      summarize_at(
        vars(Beds, HospCt), 
        sum # sum of values across nyc
      ) %>%
      mutate(fips = '36061')
  ) %>%
  mutate(
    beds_log = log(Beds + 1),
    hospct_log = log(HospCt + 1)
  )

analysis_df <- analysis_df %>%
  left_join(acute_care, by = 'fips')

# save study df
write_csv(analysis_df, './data/05-analysis_df_rucc_3.csv')

# Storing summary information --------------------------------------------------
sink("./results/05-analysis_df_meta_info.txt")
print('#######################################################################')
# print out names of study areas
print('Study counties:')

print(unique(analysis_df$metro_state_county))

print('#######################################################################')
# print out study date window
print('Study date summary:')
print(summary(analysis_df$date))

# print dims of dataframe
print('#######################################################################')
print('n observations and columns: ')
print(dim(analysis_df))

sink()

# Exlusion of New York City sensivity dataframe --------------------------------
# read in pc
nonyc_pc_df <- read_csv(
  file = './data/04-study_fips_nonyc_pca.csv'
  ) %>%
  # using only some variables
  select(fips, metro_area, metro_state_county, PC1:PC4)

# read nyt time series and limit to study fips
nonyc_df <- master_ts %>%
  # filter/subset to study fips
  filter(fips %in% config$study_fips) %>% 
  right_join(nonyc_pc_df, by = 'fips') %>% 
  # study window ends at date 2020-05-13; for reproducibility 
  filter(date <= config$study_window$end_date) %>% 
  # impute early portion of time series using imputeTS function
  arrange(fips,date) %>%
  group_by(fips) #%>%
  # mutate_at(
  #   vars(
  #     # retail_and_recreation_percent_change_from_baseline
  #     trips_count
  #   ),
  #   list(
  #     ~ imputeTS::na_ma(., k = 5, weighting = "linear")
  #   )
  # ) 

# quick unit check; make sure new york is not present
if (!('New York' %in% unique(nonyc_df$state))) {
  'New York exlcuded from sensitivity dataframe'
} else {
  'Check, New York still in sensivity dataframe'
}

# write dataframe
write_csv(nonyc_df, './data/05-sensitivity_analysis_nonyc_df.csv')


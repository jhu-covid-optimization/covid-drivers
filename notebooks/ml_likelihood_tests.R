datafile = read.csv("../data/processed/ml_r_analysis_dataset_seed_0_std.tsv", sep='\t')

# Calculate Goodness of Fit for a linear model with DV of death difference and IV of Hospital Difference
lm_just_hosp <- lm(death_diff ~ Beds_diff,  data=datafile)
print(lm_just_hosp$coefficients)
print(summary(lm_just_hosp)$r.squared)


# Test if adding Hospital Difference as an IV significantly improves a model using
# Mobility Difference + Nursing Home Ct as an IV
lm_no_hosp <- lm(death_diff ~ TWOwk_prior_intra_diff + Nurse_diff,  data=datafile)
lm_hosp <- lm(death_diff ~ TWOwk_prior_intra_diff + Nurse_diff + Beds_diff,  data=datafile)

anova(lm_no_hosp, lm_hosp)
print(lm_hosp$coefficients)
print(summary(lm_no_hosp)$r.squared)
print(summary(lm_hosp)$r.squared)

# Test if adding Hospital Difference as an IV significantly improves a model using
# all possible IVs
lm_no_hosp <- lm(death_diff ~ TWOwk_prior_intra_diff +
                   RUCC_diff + area_diff + elderly_diff + hispanic_diff + black_diff ,  data=datafile)
lm_hosp <- lm(death_diff ~ TWOwk_prior_intra_diff +
                RUCC_diff + area_diff + elderly_diff + hispanic_diff + black_diff  + Beds_diff,  data=datafile)

print(summary(lm_no_hosp))
anova(lm_no_hosp, lm_hosp)
print(lm_hosp$coefficients)
print(summary(lm_no_hosp)$r.squared)
print(summary(lm_hosp)$r.squared)

# Test if adding Hospital Difference as an IV significantly improves a model using
# just significant IVs
lm_no_hosp <- lm(death_diff ~ TWOwk_prior_intra_diff +
                   RUCC_diff + elderly_diff  + hispanic_diff + black_diff + Nurse_diff,  data=datafile)
lm_hosp <- lm(death_diff ~ TWOwk_prior_intra_diff +
                RUCC_diff + elderly_diff + hispanic_diff + black_diff + Nurse_diff + Beds_diff,  data=datafile)

print(summary(lm_no_hosp))
anova(lm_no_hosp, lm_hosp)
print(lm_hosp$coefficients)
print(summary(lm_no_hosp)$r.squared)
print(summary(lm_hosp)$r.squared)

# Test if adding Hospital Difference as an IV significantly improves a Logistic Regression using
# Mobility Difference + Nursing Home Ct as an IV using a Likelihood Ratio Test (Which is a ChiSq test)
glm_no_hosp <- glm(More_Deaths ~ TWOwk_prior_intra_diff  + Nurse_diff, data = datafile, family = "binomial")
glm_hosp <- glm(More_Deaths ~ TWOwk_prior_intra_diff  + Nurse_diff + Beds_diff, data = datafile, family = "binomial")

print(summary.glm(glm_no_hosp))
print(summary.glm(glm_hosp))
print(glm_hosp$coefficients)


anova(glm_no_hosp, glm_hosp, test="Chisq")

# Test if adding Hospital Difference as an IV significantly improves a Logistic Regression using
# all IV's
glm_no_hosp <- glm(More_Deaths ~ TWOwk_prior_intra_diff +
                     RUCC_diff + area_diff + elderly_diff + hispanic_diff + black_diff + Nurse_diff, data = datafile, family = "binomial")
glm_hosp <- glm(More_Deaths ~ TWOwk_prior_intra_diff + 
                  RUCC_diff + area_diff + elderly_diff + hispanic_diff + black_diff + Nurse_diff + Beds_diff, data = datafile, family = "binomial")

print(summary.glm(glm_no_hosp))
print(summary.glm(glm_hosp))
print(glm_hosp$coefficients)

anova(glm_no_hosp, glm_hosp, test="Chisq")

# Test if adding Hospital Difference as an IV significantly improves a Logistic Regression using
# only significant IVs
glm_no_hosp <- glm(More_Deaths ~ TWOwk_prior_intra_diff +
                     RUCC_diff + elderly_diff + hispanic_diff + black_diff + Nurse_diff, data = datafile, family = "binomial")
glm_hosp <- glm(More_Deaths ~  TWOwk_prior_intra_diff +
                  RUCC_diff + elderly_diff + hispanic_diff + black_diff + Nurse_diff + Beds_diff, data = datafile, family = "binomial")

print(summary.glm(glm_no_hosp))
print(summary.glm(glm_hosp))
print(glm_hosp$coefficients)

anova(glm_no_hosp, glm_hosp, test="Chisq")

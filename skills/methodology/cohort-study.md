---
name: cohort-study
category: methodology
discipline: medical
description: "Prospective and retrospective cohort study design with STROBE checklist and confounding control"
---

# Cohort Study

## When to Use
When investigating the association between an exposure and an outcome over time, where randomization is not feasible or ethical. Cohort studies follow groups of individuals defined by exposure status and observe them for the occurrence of outcomes. Use prospective cohorts for incident exposures with precise measurement; use retrospective cohorts when suitable historical data (registries, medical records) already exist.

## Protocol

### Step 1: Define the Research Question
- Formulate using the PECO framework:
  - **P**opulation: Define the source population and eligibility criteria
  - **E**xposure: Define the exposure or risk factor (binary, categorical, or continuous), including dose, duration, and timing
  - **C**omparator: Define the unexposed or reference group
  - **O**utcome: Define the outcome(s) of interest with precise diagnostic criteria or case definitions
- Specify the hypothesized direction and magnitude of association
- Determine whether the study is etiologic (causal) or prognostic (predictive)

### Step 2: Choose Prospective vs Retrospective Design

**Prospective cohort:**
- Participants are enrolled at a defined time point and followed forward
- Advantages: direct exposure measurement, temporal sequence is clear, can collect data tailored to the study, can measure incidence
- Disadvantages: expensive, time-consuming (especially for rare or long-latency outcomes), loss to follow-up
- Best for: common outcomes, modifiable exposures, biomarker measurement

**Retrospective (historical) cohort:**
- Uses existing records to identify a cohort at a past time point and determines outcomes that have already occurred
- Advantages: faster, cheaper, feasible for rare exposures in occupational/registry settings
- Disadvantages: limited to available data, potential for information bias, exposure/outcome definitions constrained by existing records
- Best for: occupational exposures, rare exposures, registry-based studies

**Ambidirectional cohort:**
- Begins with retrospective data and continues with prospective follow-up
- Useful for extending existing cohorts

### Step 3: Define the Study Population
- Define the source population (geographic, institutional, or registry-based)
- Establish clear inclusion and exclusion criteria:
  - Include: age range, sex, clinical characteristics, exposure window
  - Exclude: prevalent cases of the outcome (for incidence studies), conditions that preclude follow-up
- Define the entry point (cohort inception): date of exposure onset, date of enrollment, or index date
- Calculate the required sample size:
  - For Cox regression: events per variable (EPV) rule — minimum 10-20 events per predictor
  - For incidence comparison: use Kelsey formula or equivalent
  - Account for expected loss to follow-up (inflate by 10-20%)
  - Account for potential confounders in the model

### Step 4: Measure the Exposure
- Define the exposure precisely:
  - Binary (yes/no), categorical (low/medium/high), continuous, or time-varying
  - Timing: current, cumulative, peak, time-weighted average
  - Source: questionnaire, interview, medical records, biomarker, administrative data, environmental monitoring
- Assess exposure validity:
  - Sensitivity and specificity of the exposure measurement
  - Misclassification: differential (related to outcome — biased) vs non-differential (unrelated to outcome — biases toward null)
- For retrospective studies: define the exposure window relative to the index date
- Document exposure ascertainment methods identically for exposed and unexposed groups

### Step 5: Measure the Outcome
- Define the outcome with objective, reproducible criteria:
  - Clinical diagnosis with specified criteria (e.g., ICD codes, lab thresholds)
  - Validated instruments or composite endpoints
  - Hard endpoints (death, disease) preferred over soft endpoints (symptoms, self-report)
- Ensure outcome ascertainment is independent of exposure status:
  - Blinded outcome adjudication when possible
  - Identical follow-up procedures for exposed and unexposed
- Multiple outcome sources improve completeness: medical records, registries (cancer, death), insurance claims, linkage to national databases
- Define the outcome ascertainment period and censoring rules

### Step 6: Identify and Control Confounders
- A confounder must: (1) be associated with the exposure, (2) be associated with the outcome, and (3) NOT be on the causal pathway between exposure and outcome
- Identify potential confounders from:
  - Directed Acyclic Graphs (DAGs) — preferred method for confounder identification
  - Literature review of known risk factors
  - Clinical knowledge and biological plausibility
- Common confounders: age, sex, smoking, BMI, socioeconomic status, comorbidities

**Confounding control strategies:**

*At the design stage:*
- **Restriction:** Limit enrollment to a specific subgroup (e.g., non-smokers only) — reduces generalizability but eliminates confounding by the restricted variable
- **Matching:** Match exposed and unexposed on key confounders (individual or frequency matching) — must use matched analysis methods (conditional logistic regression, stratified Cox)
- **Propensity score matching:** Match on the probability of being exposed given measured covariates

*At the analysis stage:*
- **Stratification:** Analyze within strata of confounders (Mantel-Haenszel method) — limited by sparse data with many strata
- **Multivariable regression:** Include confounders as covariates in the regression model — most common approach
- **Propensity score methods:**
  - Matching, stratification, weighting (IPTW — Inverse Probability of Treatment Weighting), or covariate adjustment
  - Check balance of covariates after propensity score application (standardized mean differences < 0.10)
- **Instrumental variable analysis:** Uses a variable associated with exposure but not outcome except through the exposure — addresses unmeasured confounding
- **Difference-in-differences:** For policy or time-based exposures with pre-post data

*Residual confounding:*
- Always acknowledge that unmeasured confounders may exist
- Quantify potential impact: E-value (minimum strength of an unmeasured confounder needed to explain away the observed association)
- Sensitivity analysis: Rosenbaum bounds or bias analysis (quantitative bias analysis, probabilistic bias analysis)

### Step 7: Plan Follow-Up and Handle Attrition
- Define the follow-up period (start date, end date, minimum required follow-up)
- Specify censoring events:
  - Administrative censoring (study end date)
  - Loss to follow-up
  - Competing events (death from other causes)
  - Treatment crossover
- Minimize loss to follow-up:
  - Multiple contact methods (phone, email, postal, home visits)
  - Tracking through administrative databases (vital statistics, national registries)
  - Regular follow-up intervals
  - Retention incentives
- Report the proportion lost to follow-up; >20% threatens validity
- Compare baseline characteristics of those lost vs retained to assess selection bias
- Sensitivity analysis: best-case/worst-case scenarios for missing outcomes

### Step 8: Analyze the Data

**Descriptive analysis:**
- Table 1: Baseline characteristics by exposure group
  - Continuous variables: mean (SD) or median (IQR)
  - Categorical variables: n (%)
  - Report standardized mean differences (SMD) rather than p-values for balance assessment
- Report person-time at risk and follow-up duration (median with IQR)
- Report outcome rates (incidence rate, cumulative incidence) by exposure group

**Primary analysis — Cox proportional hazards regression:**
- Models time to event, accounts for censoring and variable follow-up
- Produces Hazard Ratios (HR) with 95% CI
- **Proportional hazards assumption:**
  - Check with: Schoenfeld residuals test (global and per-variable), log-log plots, time-interaction terms
  - If violated: stratify the Cox model by the offending variable, use time-varying coefficients, or use restricted mean survival time (RMST)
- Model building:
  - Include confounders identified from the DAG (not stepwise selection based on p-values)
  - Report crude (unadjusted) and adjusted HRs
  - Check for multicollinearity (VIF < 5)
  - Assess linearity for continuous variables (fractional polynomials, restricted cubic splines)
  - Test for interactions (effect modification) for pre-specified variables
- Present Kaplan-Meier survival curves (with number at risk table) and log-rank test

**Alternative analysis methods:**
- **Logistic regression:** When follow-up is fixed and complete (no censoring) — produces OR
- **Poisson/negative binomial regression:** For incidence rates (events per person-time) — produces IRR
- **Competing risks analysis:** Fine-Gray model or cause-specific hazards when competing events exist
- **Time-varying exposure:** Extended Cox model with time-dependent covariates
- **Marginal structural models:** For time-varying confounding affected by prior exposure (uses IPTW)
- **Landmark analysis:** To avoid immortal time bias — define a fixed time point after which survival is analyzed

**Missing data:**
- Report the proportion of missing data for each variable
- Assess the missing data mechanism: MCAR, MAR, MNAR
- Use multiple imputation (MICE) for MAR data; perform complete-case analysis as sensitivity
- Do NOT use single imputation (mean, LOCF) as the primary method

### Step 9: Address Common Biases
- **Selection bias:** Ensure the exposed and unexposed groups come from the same source population
- **Immortal time bias:** Ensure the exposure definition does not require survival to a future time point; use time-varying exposure or landmark analysis
- **Information bias:** Standardize data collection across groups; blind assessors to exposure status
- **Healthy worker effect:** Compare to an appropriate reference group (not general population) in occupational cohorts
- **Reverse causation:** Exclude early follow-up (lag period) or prevalent cases
- **Collider bias:** Do not condition on variables that are consequences of both exposure and outcome (check with DAGs)
- **Time-related biases:** Align time zero across exposure groups; avoid prevalent user designs (prefer new-user designs)

### Step 10: Report Following STROBE
- Follow the STROBE checklist (see below)
- Include: flow diagram of participant selection, Table 1, crude and adjusted estimates, sensitivity analyses, DAG (recommended)
- Be transparent about limitations, particularly unmeasured confounding

## Checklist: STROBE (22 Items for Cohort Studies)

### Title and Abstract
1. (a) Indicate the study design in the title or abstract. (b) Provide an informative and balanced summary of what was done and found.

### Introduction
2. Explain the scientific background and rationale for the investigation being reported.
3. State specific objectives, including any pre-specified hypotheses.

### Methods
4. Present key elements of study design early in the paper.
5. Describe the setting, locations, and relevant dates (enrollment, exposure, follow-up, data collection).
6. (a) Give the eligibility criteria, and the sources and methods of selection of participants. Describe methods of follow-up. (b) For matched studies, give matching criteria and number of exposed and unexposed.
7. Clearly define all outcomes, exposures, predictors, potential confounders, and effect modifiers. Give diagnostic criteria where applicable.
8. For each variable of interest, give sources of data and details of methods of assessment (measurement). Describe comparability of assessment methods if there is more than one group.
9. Describe any efforts to address potential sources of bias.
10. Explain how the study size was arrived at.
11. Explain how quantitative variables were handled in the analyses. If applicable, describe which groupings were chosen and why.
12. (a) Describe all statistical methods, including those used to control for confounding. (b) Describe any methods used to examine subgroups and interactions. (c) Explain how missing data were addressed. (d) If applicable, explain how loss to follow-up was addressed. (e) Describe any sensitivity analyses.

### Results
13. (a) Report numbers of individuals at each stage of study — e.g., numbers potentially eligible, examined for eligibility, confirmed eligible, included in the study, completing follow-up, and analysed. (b) Give reasons for non-participation at each stage. (c) Consider use of a flow diagram.
14. (a) Give characteristics of study participants (e.g., demographic, clinical, social) and information on exposures and potential confounders. (b) Indicate number of participants with missing data for each variable of interest. (c) Summarise follow-up time (e.g., average and total amount).
15. Report numbers of outcome events or summary measures over time.
16. (a) Give unadjusted estimates and, if applicable, confounder-adjusted estimates and their precision (e.g., 95% confidence interval). Make clear which confounders were adjusted for and why they were included. (b) Report category boundaries when continuous variables were categorized. (c) If relevant, consider translating estimates of relative risk into absolute risk for a meaningful time period.
17. Report other analyses done — e.g., analyses of subgroups and interactions, and sensitivity analyses.

### Discussion
18. Summarise key results with reference to study objectives.
19. Discuss limitations of the study, taking into account sources of potential bias or imprecision. Discuss both direction and magnitude of any potential bias.
20. Give a cautious overall interpretation of results considering objectives, limitations, multiplicity of analyses, results from similar studies, and other relevant evidence.
21. Discuss the generalisability (external validity) of the study results.

### Other Information
22. Give the source of funding and the role of the funders. If applicable, give the registration number of the study.

## References
- von Elm E, Altman DG, Egger M, et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) Statement: guidelines for reporting observational studies. Lancet. 2007;370(9596):1453-1457
- Vandenbroucke JP, von Elm E, Altman DG, et al. Strengthening the Reporting of Observational Studies in Epidemiology (STROBE): Explanation and Elaboration. PLoS Med. 2007;4(10):e297
- Hernan MA, Robins JM. Causal Inference: What If. Chapman & Hall/CRC; 2020. Available from: www.hsph.harvard.edu/miguel-hernan/causal-inference-book/
- Rothman KJ, Greenland S, Lash TL. Modern Epidemiology. 3rd ed. Lippincott Williams & Wilkins; 2008
- VanderWeele TJ, Ding P. Sensitivity Analysis in Observational Research: Introducing the E-Value. Ann Intern Med. 2017;167(4):268-274
- Hernan MA, Hernandez-Diaz S, Robins JM. A structural approach to selection bias. Epidemiology. 2004;15(5):615-625
- Suissa S. Immortal time bias in pharmacoepidemiology. Am J Epidemiol. 2008;167(4):492-499
- Textor J, van der Zander B, Gilthorpe MS, Liskiewicz M, Ellison GT. Robust causal inference using directed acyclic graphs: the R package 'dagitty'. Int J Epidemiol. 2016;45(6):1887-1894

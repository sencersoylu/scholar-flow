---
name: meta-analysis
category: methodology
discipline: general
description: "Meta-analysis protocol with effect size calculation, heterogeneity analysis, and GRADE assessment"
---

# Meta-Analysis

## When to Use
When quantitatively synthesizing results from multiple studies that address the same research question. Requires at least 2 studies with comparable interventions, populations, and outcomes, though more studies improve precision and allow assessment of heterogeneity. Meta-analysis is typically conducted within a systematic review. Do NOT pool results if studies are too clinically or methodologically heterogeneous — use narrative synthesis instead.

## Protocol

### Step 1: Confirm Appropriateness of Quantitative Synthesis
- Verify that included studies are sufficiently similar in:
  - Population and setting
  - Intervention and comparator
  - Outcome definition and measurement
  - Study design
- If substantial clinical heterogeneity exists, prefer narrative synthesis or limit pooling to homogeneous subgroups
- Plan the synthesis approach: which outcomes will be pooled, which will be summarized narratively

### Step 2: Define Eligibility Criteria for Pooling
- Specify which studies from the systematic review will enter the meta-analysis
- Define minimum data requirements for inclusion (e.g., must report mean and SD, or event counts)
- Pre-specify subgroup analyses and sensitivity analyses to avoid data-driven decisions

### Step 3: Extract or Calculate Effect Sizes
- Select the appropriate effect measure based on outcome type:

**Dichotomous outcomes:**
  - Risk Ratio (RR): ratio of event probability in treatment vs control
  - Odds Ratio (OR): ratio of odds of event in treatment vs control
  - Risk Difference (RD): absolute difference in event probability
  - Number Needed to Treat (NNT): 1/RD
  - For rare events (< 5%), OR approximates RR; for common events, they diverge

**Continuous outcomes:**
  - Mean Difference (MD): when studies use the same measurement scale
  - Standardized Mean Difference (SMD): when studies use different scales measuring the same construct
    - Cohen's d = (M1 - M2) / SDpooled
    - Hedges' g = d * (1 - 3/(4(n1+n2) - 9))  [correction for small samples]
  - If SD not reported, estimate from SE, CI, IQR, range, or p-value

**Time-to-event outcomes:**
  - Hazard Ratio (HR): from Cox proportional hazards models
  - If HR not directly reported, estimate using methods by Tierney et al. (2007)

**Correlation outcomes:**
  - Fisher's z transformation of Pearson's r for pooling; back-transform for reporting

- Extract: effect estimate, variance/SE/CI, sample size per group, number of events (for dichotomous)
- Contact authors for missing data; consider imputation methods as last resort

### Step 4: Choose the Statistical Model

**Fixed-effect model (common-effect model):**
  - Assumes all studies estimate the SAME true effect
  - Appropriate when: studies are clinically and methodologically homogeneous, or conducting a sensitivity analysis
  - Methods: inverse-variance, Mantel-Haenszel (for sparse data), Peto (for very rare events with balanced groups)
  - Weights based on study precision (inverse of variance)

**Random-effects model:**
  - Assumes true effects VARY across studies, following a distribution
  - Appropriate when: clinical or methodological heterogeneity is expected (most common scenario)
  - Estimates the MEAN of the distribution of true effects
  - Methods: DerSimonian-Laird (most common, but can underestimate variance), REML (recommended), Paule-Mandel, Hartung-Knapp-Sidik-Jonkman (HKSJ — recommended for CIs, especially with few studies)
  - Weights include both within-study variance and between-study variance (tau-squared)
  - Gives relatively more weight to smaller studies compared to fixed-effect

**Practical recommendation:** Use random-effects as the default in most reviews, with fixed-effect as a sensitivity analysis. Always report the model choice with justification.

### Step 5: Calculate the Pooled Effect Estimate
- Compute the weighted average effect size using the selected model
- Calculate the 95% confidence interval for the pooled estimate
- For random-effects, also report the 95% prediction interval (range within which the true effect of a future study is expected to fall)
- Report the pooled estimate with its CI: e.g., "OR = 0.72, 95% CI [0.58, 0.89]"

### Step 6: Assess Statistical Heterogeneity
- **Cochran's Q test:**
  - Tests whether observed variability exceeds sampling error
  - Low power with few studies; significant Q indicates heterogeneity but non-significant Q does not confirm homogeneity
  - Report Q statistic and its p-value

- **I-squared (I2):**
  - Percentage of total variability due to true heterogeneity (not chance)
  - Interpretation (Higgins et al.):
    - 0-40%: might not be important
    - 30-60%: may represent moderate heterogeneity
    - 50-90%: may represent substantial heterogeneity
    - 75-100%: considerable heterogeneity
  - Interpretation depends on the context (magnitude of effects, strength of evidence for heterogeneity)

- **Tau-squared (tau2):**
  - Estimate of the between-study variance in random-effects models
  - Expressed on the scale of the effect measure
  - Used to calculate prediction intervals

- **H-squared:**
  - Ratio of Q to its degrees of freedom; H2 = 1 indicates no heterogeneity

- If heterogeneity is substantial (I2 > 50% or Q p < 0.10), explore sources through subgroup analysis and meta-regression

### Step 7: Create the Forest Plot
- Display for each study:
  - Study identifier (author, year)
  - Effect estimate with 95% CI (horizontal line)
  - Weight (square proportional to weight, or percentage)
  - Raw data (events/total for each group, or mean/SD/N)
- Display the pooled estimate as a diamond at the bottom
- Include the line of no effect (RR=1, OR=1, MD=0, SMD=0)
- Report heterogeneity statistics below the plot (I2, tau2, Q test)
- If using random-effects, optionally display the prediction interval
- Order studies by year, effect size, or subgroup
- Use a log scale for ratio measures (RR, OR, HR)

### Step 8: Assess Publication Bias
- **Visual assessment:**
  - Funnel plot: scatter plot of effect size vs precision (SE or sample size)
  - Symmetric funnel suggests no bias; asymmetry may indicate publication bias, small-study effects, or heterogeneity
  - Requires at least 10 studies for meaningful interpretation

- **Statistical tests:**
  - Egger's regression test: regresses standardized effect on precision; p < 0.10 suggests asymmetry (for continuous outcomes and OR)
  - Begg and Mazumdar rank correlation test: Kendall's tau between effect size and variance
  - Peters' test: recommended alternative for OR (regresses 1/n on effect)
  - Harbord's test: modified test for dichotomous outcomes
  - Arcsine test: for risk differences

- **Adjustment methods (if bias detected):**
  - Trim-and-fill: imputes missing studies and recalculates pooled estimate
  - Selection models (Copas, Vevea-Hedges): model the selection process
  - P-curve analysis: examines distribution of significant p-values
  - Limit meta-analysis: extrapolates to infinitely precise study

### Step 9: Conduct Sensitivity Analyses
- Test robustness of results by:
  - Excluding studies one at a time (leave-one-out analysis)
  - Excluding studies at high risk of bias
  - Comparing fixed-effect vs random-effects results
  - Excluding outliers (studies with residuals > 2 SD)
  - Varying inclusion criteria (e.g., including/excluding conference abstracts)
  - Using different effect measures (OR vs RR)
  - Using different estimation methods (DL vs REML)
  - Comparing complete-case vs imputed data
- Report whether conclusions change; if they do, note which studies or decisions drive the results

### Step 10: Conduct Subgroup Analyses and Meta-Regression
- **Subgroup analysis:**
  - Pre-specified groupings based on clinical or methodological variables
  - Compare pooled effects between subgroups using interaction test (not separate significance tests)
  - Minimum 2 studies per subgroup; interpret cautiously with few studies
  - Examples: by population age, intervention dose, study quality, geographic region

- **Meta-regression:**
  - Extends subgroup analysis to continuous moderators
  - Use random-effects meta-regression (method of moments or REML)
  - Requires at least 10 studies per covariate (rule of thumb)
  - Report regression coefficient, 95% CI, p-value, R2 analog (proportion of heterogeneity explained)
  - Beware of ecological fallacy: study-level associations may not hold at patient level
  - Use permutation tests for p-values with few studies

### Step 11: Assess Certainty of Evidence (GRADE)
- For each outcome, rate the certainty of evidence:
  - Start at HIGH for RCTs, LOW for observational studies
  - **Rate down for:**
    1. Risk of bias (limitations in study design/execution)
    2. Inconsistency (unexplained heterogeneity, wide prediction intervals)
    3. Indirectness (differences in PICO from review question)
    4. Imprecision (wide CIs, few events, optimal information size not met)
    5. Publication bias (funnel plot asymmetry, registry-publication discrepancy)
  - **Rate up for (observational studies only):**
    1. Large effect (RR > 2 or < 0.5 with no plausible confounding)
    2. Dose-response gradient
    3. All plausible confounding would reduce the effect
  - Final rating: High / Moderate / Low / Very Low
- Present in a Summary of Findings (SoF) table with: outcome, number of studies and participants, effect estimate with CI, certainty rating, plain-language interpretation

### Step 12: Report the Meta-Analysis
- Follow PRISMA 2020 (see systematic-review skill)
- Additionally report:
  - Effect measure used and justification
  - Statistical model (fixed/random) and estimation method
  - Software and packages used (e.g., R metafor, RevMan, Stata metan)
  - All heterogeneity statistics (Q, I2, tau2)
  - Forest plot for each pooled outcome
  - Funnel plot and publication bias tests (if >= 10 studies)
  - All sensitivity and subgroup analyses (pre-specified vs post hoc)
  - GRADE SoF table

## Checklist: Meta-Analysis Reporting

1. State whether fixed-effect or random-effects model was used, with justification
2. Report the estimation method (e.g., DerSimonian-Laird, REML, HKSJ)
3. Report the effect measure (OR, RR, MD, SMD, HR) with justification
4. Present forest plot(s) for all primary and key secondary outcomes
5. Report pooled effect estimate with 95% CI
6. Report prediction interval for random-effects analyses
7. Report Cochran's Q statistic and p-value
8. Report I-squared with its 95% CI
9. Report tau-squared
10. Present funnel plot if 10 or more studies are included
11. Report result of publication bias statistical test (Egger's or appropriate alternative)
12. Report all pre-specified subgroup analyses with interaction test
13. Report meta-regression results if conducted
14. Report sensitivity analyses and whether conclusions changed
15. Report leave-one-out analysis results
16. Present GRADE Summary of Findings table
17. Report the software and version used for all analyses
18. Distinguish pre-specified analyses from post hoc explorations
19. Report how missing data (e.g., missing SDs) were handled
20. Provide raw data or summary statistics for each study in a table or appendix

## References
- Higgins JPT, Thomas J, Chandler J, et al., editors. Cochrane Handbook for Systematic Reviews of Interventions version 6.4. Cochrane, 2023. Available from www.training.cochrane.org/handbook
- Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021
- Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. BMJ. 2008;336:924-926
- IntHout J, Ioannidis JPA, Borm GF. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. BMC Med Res Methodol. 2014;14:25
- Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. BMJ. 1997;315:629-634
- Tierney JF, Stewart LA, Ghersi D, Burdett S, Sydes MR. Practical methods for incorporating summary time-to-event data into meta-analysis. Trials. 2007;8:16
- Viechtbauer W. Conducting Meta-Analyses in R with the metafor Package. Journal of Statistical Software. 2010;36(3):1-48
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ. 2021;372:n71

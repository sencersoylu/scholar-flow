---
name: statistical-review
category: quality
discipline: general
description: "Statistical review protocol checking for p-hacking, multiple comparison correction, and effect size reporting"
---

# Statistical Review

Protocol for evaluating the statistical quality of a manuscript. Covers test selection, assumption verification, result reporting, common pitfalls, and p-hacking detection.

## When to Use

- Loaded by the Peer Reviewer agent for statistical accuracy verification
- As part of internal peer review before journal submission
- When reviewing a manuscript with quantitative results
- When auditing statistical analyses for rigor and completeness

---

## Protocol

### 1. Appropriateness of Statistical Tests

Review each statistical test used against the following criteria:

| Question | What to Check |
|----------|--------------|
| Does the test match the outcome variable type? | Continuous outcome with t-test/ANOVA, categorical with chi-square/Fisher's, time-to-event with log-rank/Cox |
| Does the test match the number of groups? | Two groups: t-test/Mann-Whitney. Three or more: ANOVA/Kruskal-Wallis |
| Is the test appropriate for the data structure? | Paired data requires paired tests. Clustered data requires mixed models or GEE. Repeated measures requires RM-ANOVA or mixed models |
| Is a parametric test justified? | Check if normality was assessed and reported |
| Is the test two-sided? | One-sided tests require strong a priori justification |

Common errors:
- Using independent t-test on paired/matched data
- Using parametric tests on heavily skewed data without justification
- Using chi-square when expected cell counts are below 5 (should use Fisher's exact)
- Using Pearson correlation on non-linear relationships
- Using repeated t-tests instead of ANOVA (inflates Type I error)
- Treating ordinal data as continuous without justification

### 2. Assumption Verification

For each statistical test, verify that assumptions are checked:

#### Parametric Tests (t-test, ANOVA, linear regression)
- [ ] Normality assessed (Shapiro-Wilk, Q-Q plot, or central limit theorem invoked for large n)
- [ ] Method of normality assessment stated
- [ ] Homogeneity of variance tested (Levene's test) and reported
- [ ] Action taken when assumptions violated (non-parametric alternative, transformation, or robust method)

#### Regression Models
- [ ] Linear regression: linearity, normality of residuals, homoscedasticity, independence, VIF for multicollinearity
- [ ] Logistic regression: linearity of continuous predictors with log-odds, adequate events per variable (EPV >= 10)
- [ ] Cox regression: proportional hazards assumption tested (Schoenfeld residuals, log-log plot)

#### Non-parametric Tests
- [ ] Justified by violation of parametric assumptions (not just by default)
- [ ] Appropriate non-parametric test selected

### 3. Multiple Testing Correction

| Scenario | Expected Action |
|----------|----------------|
| Multiple primary outcomes | Alpha adjustment (Bonferroni, Holm) or clearly designated single primary outcome |
| Multiple pairwise comparisons after ANOVA | Post-hoc test (Tukey, Dunnett, Games-Howell) |
| Subgroup analyses | Interaction test before subgroup comparisons; label as exploratory |
| Multiple secondary outcomes | FDR correction (Benjamini-Hochberg) or state as exploratory |
| Correlation matrices | FDR correction for number of comparisons |

Red flags:
- Multiple comparisons without any correction mentioned
- Selective reporting of only "significant" comparisons from a larger set
- Subgroup analyses presented as confirmatory without pre-specification
- P-values reported for dozens of comparisons without correction

### 4. Effect Size Reporting

Every comparison or association should report an effect size alongside the p-value.

| Analysis Type | Expected Effect Size | Interpretation Aid |
|--------------|---------------------|-------------------|
| Two-group comparison (continuous) | Cohen's d or mean difference with CI | Small: 0.2, Medium: 0.5, Large: 0.8 |
| ANOVA | Eta-squared or partial eta-squared | Small: 0.01, Medium: 0.06, Large: 0.14 |
| Correlation | r or rho (already an effect size) | Small: 0.1, Medium: 0.3, Large: 0.5 |
| Chi-square | Cramer's V or phi | Depends on df |
| Logistic regression | Odds ratio with CI | Meaningful thresholds context-dependent |
| Cox regression | Hazard ratio with CI | Meaningful thresholds context-dependent |
| Linear regression | R-squared, standardized beta | Report adjusted R-squared for model |

Red flags:
- Only p-values reported, no effect sizes
- Statistically significant p-value with trivially small effect size (especially in large samples)
- Effect sizes reported without confidence intervals
- No discussion of clinical or practical significance

### 5. Confidence Intervals

- [ ] 95% CIs reported for primary outcome measures
- [ ] CIs reported for effect sizes (not just point estimates)
- [ ] CIs interpreted correctly (the interval, not the point estimate, conveys precision)
- [ ] CIs consistent with reported p-values (CI crossing null should correspond to non-significant p)

### 6. Sample Size Justification

- [ ] A priori power analysis performed and reported
- [ ] Effect size used in power analysis justified (pilot data, literature, or MCID)
- [ ] Alpha, power, and calculated N stated
- [ ] Actual sample size meets or exceeds calculated requirement
- [ ] If sample is smaller than calculated, acknowledged as a limitation
- [ ] Software used for power calculation stated

Red flags:
- No power analysis mentioned anywhere in the manuscript
- Post-hoc power analysis presented as if it were a priori
- Power analysis based on observed effect size (circular reasoning)
- Impossibly small sample for the claimed power level

### 7. Missing Data Handling

- [ ] Amount of missing data reported per variable
- [ ] Pattern of missingness assessed (MCAR, MAR, MNAR)
- [ ] Missing data mechanism discussed
- [ ] Handling method stated (complete case, imputation, maximum likelihood)
- [ ] If imputation used: method described (MICE, single imputation, last observation carried forward)
- [ ] Sensitivity analysis comparing complete-case and imputed results

Red flags:
- No mention of missing data at all
- Complete-case analysis without reporting how much data was lost
- Last observation carried forward (LOCF) without justification (generally discouraged)
- Listwise deletion resulting in substantial sample reduction without discussion

### 8. P-Hacking and Selective Reporting Red Flags

P-hacking is the practice of manipulating data analysis to produce statistically significant results. Watch for:

#### Analysis Red Flags
- [ ] **Suspicious p-value clustering** -- many p-values just below 0.05 (e.g., 0.048, 0.043, 0.049)
- [ ] **Outcome switching** -- primary outcome in registration differs from primary outcome in paper
- [ ] **Flexible exclusion criteria** -- post-hoc exclusion of participants that changes results
- [ ] **Unplanned subgroups** -- subgroup analyses not pre-specified but presented as primary findings
- [ ] **Optional stopping** -- data collection appears to have stopped when significance was reached
- [ ] **Transformation shopping** -- multiple transformations tried until one yields significance
- [ ] **Covariate fishing** -- adding/removing covariates until the desired result appears
- [ ] **Rounding down** -- reporting p = 0.05 when actual value is slightly above (e.g., p = 0.054)

#### Reporting Red Flags
- [ ] **Selective outcome reporting** -- registered outcomes missing from the paper
- [ ] **Absence of non-significant results** -- only significant findings reported from multiple tests
- [ ] **HARKing** (Hypothesizing After Results are Known) -- exploratory findings presented as confirmatory hypotheses
- [ ] **Narrative spinning** -- emphasizing subgroup results or secondary outcomes when primary outcome is non-significant
- [ ] **Vague methods** -- analysis plan described in vague terms that could accommodate multiple approaches

#### What to Do
1. Check trial/study registration (ClinicalTrials.gov, PROSPERO, OSF) for pre-registered outcomes and analysis plan
2. Compare registered outcomes with reported outcomes
3. Look for discrepancies between methods and results sections
4. Examine whether non-significant results are reported and discussed
5. Check if the number of reported comparisons matches what the design would produce

### 9. Additional Statistical Quality Checks

- [ ] **Baseline comparisons in RCTs** -- p-values for baseline characteristics are unnecessary (randomization ensures comparability in expectation). If present, they should not drive covariate selection.
- [ ] **Percentage precision** -- percentages with excessive decimal places for small samples (e.g., "33.33%" when N = 3)
- [ ] **Standard deviation vs. standard error** -- SD used for describing data, SE (or CI) for describing precision of estimates. Verify correct usage.
- [ ] **Appropriate denominators** -- percentages calculated from the correct denominator (ITT population vs. completers)
- [ ] **Consistency** -- numbers in text match numbers in tables and figures
- [ ] **Degrees of freedom** -- reported and consistent with sample sizes

---

## Output Format

```
## Statistical Review Report

### Overall Statistical Quality: [Adequate / Needs Improvement / Serious Concerns]

### Test Appropriateness
| Analysis | Test Used | Appropriate? | Issue (if any) |
|----------|----------|-------------|----------------|
| [description] | [test] | Yes/No | [issue] |

### Assumption Verification
- [Finding 1]
- [Finding 2]

### Effect Size and CI Reporting
- [Finding]

### Multiple Testing
- [Finding]

### Sample Size Adequacy
- [Finding]

### Missing Data
- [Finding]

### P-Hacking Indicators
- [None detected / Concerns identified: ...]

### Recommendations
1. **Critical:** [...]
2. **Major:** [...]
3. **Minor:** [...]
```

---

## Checklist

### Test Selection and Assumptions
- [ ] Each statistical test appropriate for the data type and design
- [ ] Parametric assumptions checked and reported
- [ ] Non-parametric alternatives used when assumptions violated
- [ ] Correct handling of paired/clustered data

### Reporting Quality
- [ ] Effect sizes reported for all comparisons
- [ ] 95% confidence intervals provided
- [ ] Exact p-values reported (not "NS" or "p < 0.05")
- [ ] Multiple testing correction applied and stated
- [ ] Sample size justified with power analysis

### Data Integrity
- [ ] Missing data quantified and handled appropriately
- [ ] Numbers consistent across text, tables, and figures
- [ ] Denominators correct for all percentages
- [ ] SD vs. SE used correctly

### Bias Assessment
- [ ] No evidence of p-hacking or selective reporting
- [ ] Registered outcomes match reported outcomes
- [ ] Non-significant results reported
- [ ] Subgroup analyses labeled as exploratory (unless pre-specified)

---

## References

- Wasserstein RL, Lazar NA. The ASA's Statement on p-Values: Context, Process, and Purpose. The American Statistician. 2016;70(2):129-133. doi:10.1080/00031305.2016.1154108
- Wasserstein RL, Schirm AL, Lazar NA. Moving to a World Beyond "p < 0.05." The American Statistician. 2019;73(sup1):1-19. doi:10.1080/00031305.2019.1583913
- Simmons JP, Nelson LD, Simonsohn U. False-Positive Psychology: Undisclosed Flexibility in Data Collection and Analysis Allows Presenting Anything as Significant. Psychological Science. 2011;22(11):1359-1366. doi:10.1177/0956797611417632
- Head ML, Holman L, Lanfear R, Kahn AT, Jennions MD. The Extent and Consequences of P-Hacking in Science. PLoS Biol. 2015;13(3):e1002106. doi:10.1371/journal.pbio.1002106
- Kerr NL. HARKing: Hypothesizing After the Results are Known. Pers Soc Psychol Rev. 1998;2(3):196-217. doi:10.1207/s15327957pspr0203_4
- Lang TA, Altman DG. Basic Statistical Reporting for Articles Published in Biomedical Journals: The "Statistical Analyses and Methods in the Published Literature" or The SAMPL Guidelines. Int J Nurs Stud. 2015;52(1):5-9. doi:10.1016/j.ijnurstu.2014.09.006
- Greenland S, Senn SJ, Rothman KJ, et al. Statistical tests, P values, confidence intervals, and power: a guide to misinterpretations. Eur J Epidemiol. 2016;31(4):337-350. doi:10.1007/s10654-016-0149-3

---
name: inferential-statistics
category: statistics
discipline: general
description: "Inferential test selection and execution including t-test, ANOVA, chi-square, and non-parametric alternatives"
---

# Inferential Statistics

Complete protocol for selecting and executing hypothesis tests, including parametric and non-parametric tests, assumption checking, effect size calculation, and multiple comparison correction.

## When to Use

- When testing hypotheses about group differences or associations
- When comparing treatment outcomes between groups
- When determining if observed differences are statistically significant
- After completing descriptive statistics (see descriptive-statistics skill)

---

## Protocol

### 1. Test Selection Decision Tree

#### Continuous Outcome

| Groups | Related? | Parametric | Non-Parametric |
|--------|----------|-----------|----------------|
| 2 | Independent | Independent t-test | Mann-Whitney U |
| 2 | Paired/matched | Paired t-test | Wilcoxon signed-rank |
| >2 | Independent | One-way ANOVA | Kruskal-Wallis |
| >2 | Repeated measures | Repeated measures ANOVA | Friedman test |

#### Categorical Outcome

| Expected counts | Groups | Test |
|----------------|--------|------|
| All >= 5 | 2+ | Chi-square test of independence |
| Any < 5, 2x2 table | 2 | Fisher's exact test |
| Any < 5, larger table | 2+ | Fisher-Freeman-Halton exact test |
| Paired/matched | 2 | McNemar's test |

#### Correlation

| Data type | Test |
|-----------|------|
| Both continuous, normal | Pearson correlation (r) |
| Ordinal or non-normal | Spearman rank correlation (rho) |
| Both ordinal, small n | Kendall's tau |

### 2. Assumption Checking

#### 2.1 Assumptions for Parametric Tests

**Independent t-test and one-way ANOVA:**
1. **Independence** -- observations are independent (study design)
2. **Normality** -- outcome variable is approximately normally distributed in each group
3. **Homogeneity of variance** -- equal variances across groups (Levene's test)

```python
from scipy import stats
import pandas as pd
import numpy as np

# Example: comparing outcome between two groups
group1 = df[df['group'] == 'treatment']['outcome']
group2 = df[df['group'] == 'control']['outcome']

# Normality (per group)
for name, data in [('Treatment', group1), ('Control', group2)]:
    stat, p = stats.shapiro(data.dropna())
    print(f"{name}: Shapiro-Wilk W={stat:.4f}, p={p:.4f}")

# Homogeneity of variance
stat, p = stats.levene(group1.dropna(), group2.dropna())
print(f"Levene's test: F={stat:.4f}, p={p:.4f}")
```

**Decision rules:**
- If normality violated: use non-parametric alternative
- If normality OK but variance unequal: use Welch's t-test (does not assume equal variances)
- For ANOVA with unequal variances: use Welch's ANOVA or Games-Howell post-hoc

### 3. Test Execution

#### 3.1 Independent Samples t-test

```python
from scipy import stats

# Standard t-test (assumes equal variances)
t_stat, p_value = stats.ttest_ind(group1, group2)

# Welch's t-test (does not assume equal variances -- generally preferred)
t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)

print(f"t = {t_stat:.3f}, p = {p_value:.4f}")

# Effect size: Cohen's d
def cohens_d(g1, g2):
    n1, n2 = len(g1), len(g2)
    var1, var2 = g1.var(), g2.var()
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (g1.mean() - g2.mean()) / pooled_std

d = cohens_d(group1.dropna(), group2.dropna())
print(f"Cohen's d = {d:.3f}")
```

#### 3.2 Mann-Whitney U Test

```python
# Non-parametric alternative to independent t-test
u_stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')
print(f"U = {u_stat:.1f}, p = {p_value:.4f}")

# Effect size: rank-biserial correlation
n1, n2 = len(group1), len(group2)
r_rb = 1 - (2 * u_stat) / (n1 * n2)
print(f"Rank-biserial r = {r_rb:.3f}")
```

#### 3.3 Paired t-test

```python
# Paired data (e.g., pre-post measurements)
t_stat, p_value = stats.ttest_rel(pre_scores, post_scores)
print(f"t = {t_stat:.3f}, p = {p_value:.4f}")

# Effect size: Cohen's d for paired data
diff = post_scores - pre_scores
d_paired = diff.mean() / diff.std()
print(f"Cohen's d (paired) = {d_paired:.3f}")
```

#### 3.4 Wilcoxon Signed-Rank Test

```python
# Non-parametric alternative to paired t-test
stat, p_value = stats.wilcoxon(pre_scores, post_scores)
print(f"W = {stat:.1f}, p = {p_value:.4f}")

# Effect size: r = Z / sqrt(N)
n = len(pre_scores)
z = stats.norm.ppf(p_value / 2)
r = abs(z) / np.sqrt(n)
print(f"Effect size r = {r:.3f}")
```

#### 3.5 One-Way ANOVA

```python
# Parametric: one-way ANOVA
group_a = df[df['group'] == 'A']['outcome']
group_b = df[df['group'] == 'B']['outcome']
group_c = df[df['group'] == 'C']['outcome']

f_stat, p_value = stats.f_oneway(group_a, group_b, group_c)
print(f"F = {f_stat:.3f}, p = {p_value:.4f}")

# Effect size: eta-squared
import statsmodels.api as sm
from statsmodels.formula.api import ols

model = ols('outcome ~ C(group)', data=df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
ss_between = anova_table['sum_sq']['C(group)']
ss_total = anova_table['sum_sq'].sum()
eta_sq = ss_between / ss_total
print(f"Eta-squared = {eta_sq:.3f}")

# Post-hoc pairwise comparisons (Tukey HSD)
from statsmodels.stats.multicomp import pairwise_tukeyhsd

tukey = pairwise_tukeyhsd(df['outcome'], df['group'], alpha=0.05)
print(tukey)
```

#### 3.6 Welch's ANOVA (unequal variances)

```python
from scipy import stats

# Welch's ANOVA (does not assume equal variances)
stat, p_value = stats.alexandergovern(group_a, group_b, group_c)
print(f"Welch's ANOVA: statistic={stat:.3f}, p={p_value:.4f}")

# Post-hoc: Games-Howell (for unequal variances)
# Use pingouin library
import pingouin as pg
posthoc = pg.pairwise_gameshowell(data=df, dv='outcome', between='group')
print(posthoc)
```

#### 3.7 Kruskal-Wallis Test

```python
# Non-parametric alternative to one-way ANOVA
h_stat, p_value = stats.kruskal(group_a, group_b, group_c)
print(f"H = {h_stat:.3f}, p = {p_value:.4f}")

# Effect size: epsilon-squared
n = len(df)
k = df['group'].nunique()
epsilon_sq = (h_stat - k + 1) / (n - k)
print(f"Epsilon-squared = {epsilon_sq:.3f}")

# Post-hoc: Dunn's test with Bonferroni correction
from scikit_posthocs import posthoc_dunn
dunn = posthoc_dunn(df, val_col='outcome', group_col='group', p_adjust='bonferroni')
print(dunn)
```

#### 3.8 Chi-Square Test of Independence

```python
# Contingency table
contingency = pd.crosstab(df['exposure'], df['outcome'])
print(contingency)

# Chi-square test
chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
print(f"Chi-square = {chi2:.3f}, df = {dof}, p = {p_value:.4f}")

# Check expected counts
print(f"Minimum expected count: {expected.min():.1f}")
if expected.min() < 5:
    print("WARNING: Expected counts < 5. Consider Fisher's exact test.")

# Effect size: Cramer's V
n = contingency.sum().sum()
min_dim = min(contingency.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))
print(f"Cramer's V = {cramers_v:.3f}")
```

#### 3.9 Fisher's Exact Test

```python
# For 2x2 tables with small expected counts
contingency_2x2 = pd.crosstab(df['exposure'], df['outcome'])
odds_ratio, p_value = stats.fisher_exact(contingency_2x2)
print(f"Odds Ratio = {odds_ratio:.3f}, p = {p_value:.4f}")
```

#### 3.10 Correlation

```python
# Pearson correlation (parametric)
r, p_value = stats.pearsonr(df['var1'], df['var2'])
print(f"Pearson r = {r:.3f}, p = {p_value:.4f}")

# Spearman correlation (non-parametric)
rho, p_value = stats.spearmanr(df['var1'], df['var2'])
print(f"Spearman rho = {rho:.3f}, p = {p_value:.4f}")
```

### 4. Effect Size Interpretation

| Effect Size | Small | Medium | Large |
|-------------|-------|--------|-------|
| Cohen's d | 0.2 | 0.5 | 0.8 |
| Pearson r | 0.1 | 0.3 | 0.5 |
| Eta-squared | 0.01 | 0.06 | 0.14 |
| Cramer's V (df=1) | 0.1 | 0.3 | 0.5 |
| Cramer's V (df=2) | 0.07 | 0.21 | 0.35 |
| Cramer's V (df=3) | 0.06 | 0.17 | 0.29 |
| Odds Ratio | 1.5 | 2.5 | 4.3 |

Note: These are Cohen's conventions. Context-specific interpretation is always preferred -- a "small" effect may be clinically meaningful.

### 5. Multiple Comparison Correction

When performing multiple tests, the family-wise error rate inflates. Apply correction:

| Method | Description | When to Use |
|--------|------------|-------------|
| Bonferroni | Divide alpha by number of tests | Conservative; few comparisons |
| Holm (step-down) | Sequential Bonferroni | Less conservative than Bonferroni; general use |
| Benjamini-Hochberg (FDR) | Controls false discovery rate | Many comparisons; exploratory analyses |
| Tukey HSD | For all pairwise ANOVA comparisons | Post-hoc after significant ANOVA |
| Dunnett | Compare all groups to one control | Multiple treatment groups vs. one control |

```python
from statsmodels.stats.multitest import multipletests

# Example: correcting multiple p-values
p_values = [0.01, 0.03, 0.04, 0.15, 0.22]

# Bonferroni
reject_bonf, pvals_bonf, _, _ = multipletests(p_values, method='bonferroni')

# Holm
reject_holm, pvals_holm, _, _ = multipletests(p_values, method='holm')

# Benjamini-Hochberg (FDR)
reject_fdr, pvals_fdr, _, _ = multipletests(p_values, method='fdr_bh')

for i, p in enumerate(p_values):
    print(f"p={p:.3f} | Bonf={pvals_bonf[i]:.4f} ({reject_bonf[i]}) | "
          f"Holm={pvals_holm[i]:.4f} ({reject_holm[i]}) | "
          f"FDR={pvals_fdr[i]:.4f} ({reject_fdr[i]})")
```

### 6. Reporting Results

**Standard reporting format (APA-like):**

- t-test: *t*(df) = X.XX, *p* = .XXX, *d* = X.XX
- Mann-Whitney: *U* = X.XX, *p* = .XXX, *r* = X.XX
- ANOVA: *F*(df_between, df_within) = X.XX, *p* = .XXX, eta-sq = X.XX
- Chi-square: chi-sq(df) = X.XX, *p* = .XXX, Cramer's *V* = X.XX
- Correlation: *r*(df) = X.XX, *p* = .XXX

**Always report:**
1. Test statistic and degrees of freedom
2. Exact p-value (not just "p < 0.05", unless p < 0.001)
3. Effect size with interpretation
4. 95% confidence interval where possible
5. Sample sizes per group
6. Whether one-tailed or two-tailed (default: two-tailed)

---

## Checklist

### Test Selection
- [ ] Outcome variable type identified (continuous, categorical, ordinal)
- [ ] Number of groups identified
- [ ] Independence vs. paired/repeated measures determined
- [ ] Appropriate test selected from decision tree

### Assumptions
- [ ] Normality assessed (Shapiro-Wilk + visual inspection)
- [ ] Homogeneity of variance tested (Levene's test)
- [ ] Independence of observations verified by study design
- [ ] Sample size adequate for chosen test
- [ ] Non-parametric alternative used when assumptions violated

### Execution
- [ ] Correct test applied with proper parameters
- [ ] Two-tailed test used (unless one-tailed justified a priori)
- [ ] Effect size calculated for each comparison
- [ ] Confidence intervals computed

### Multiple Comparisons
- [ ] Family-wise error rate addressed if multiple tests performed
- [ ] Correction method stated and justified
- [ ] Corrected p-values reported alongside uncorrected

### Reporting
- [ ] Test statistic, df, and exact p-value reported
- [ ] Effect size reported with interpretation
- [ ] Group means/medians and SDs/IQRs reported
- [ ] Sample sizes per group stated
- [ ] Results narrative matches statistical output

---

## References

- Cohen J. Statistical Power Analysis for the Behavioral Sciences. 2nd ed. Lawrence Erlbaum Associates; 1988.
- Field A. Discovering Statistics Using IBM SPSS Statistics. 5th ed. SAGE Publications; 2018.
- Wasserstein RL, Lazar NA. The ASA Statement on p-Values: Context, Process, and Purpose. The American Statistician. 2016;70(2):129-133. doi:10.1080/00031305.2016.1154108
- Benjamini Y, Hochberg Y. Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. JRSS-B. 1995;57(1):289-300.
- Fritz CO, Morris PE, Richler JJ. Effect Size Estimates: Current Use, Calculations, and Interpretation. Journal of Experimental Psychology: General. 2012;141(1):2-18. doi:10.1037/a0024338
- scipy.stats documentation. https://docs.scipy.org/doc/scipy/reference/stats.html
- statsmodels documentation. https://www.statsmodels.org/stable/

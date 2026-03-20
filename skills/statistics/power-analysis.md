---
name: power-analysis
category: statistics
discipline: general
description: "Sample size and power analysis with effect size estimation and Type I/II error control"
---

# Power Analysis

Protocol for a priori sample size calculation, effect size estimation, and power determination for common study designs. Ensures studies are adequately powered to detect clinically or scientifically meaningful effects.

## When to Use

- During study design, before data collection begins
- When writing a grant proposal or protocol
- When justifying sample size to an IRB/ethics committee
- When performing post-hoc power analysis for negative studies (with caveats)
- When planning replication studies

---

## Protocol

### 1. Core Concepts

**Statistical power** is the probability of correctly rejecting a false null hypothesis (1 - beta).

Four interrelated quantities (knowing any three determines the fourth):

| Parameter | Symbol | Description | Typical Value |
|-----------|--------|------------|---------------|
| Significance level | alpha | Probability of Type I error (false positive) | 0.05 |
| Power | 1 - beta | Probability of detecting a true effect | 0.80 or 0.90 |
| Effect size | d, r, f, w, etc. | Magnitude of the effect to detect | Study-specific |
| Sample size | N or n | Number of participants needed | Calculated |

### 2. Effect Size Estimation

The most critical and often most difficult step. Sources for effect size estimates (in order of preference):

1. **Pilot study data** -- calculate effect size from your own preliminary data
2. **Published literature** -- meta-analyses or large studies on similar outcomes
3. **Clinical significance** -- the minimum difference that would be clinically meaningful (MCID)
4. **Conventions** -- Cohen's benchmarks (use only as a last resort)

#### 2.1 Effect Size Conventions (Cohen, 1988)

| Effect Size Measure | Small | Medium | Large | Used With |
|-------------------|-------|--------|-------|-----------|
| Cohen's d | 0.2 | 0.5 | 0.8 | Two-group mean comparisons |
| Cohen's f | 0.10 | 0.25 | 0.40 | ANOVA |
| Cohen's w | 0.10 | 0.30 | 0.50 | Chi-square tests |
| Pearson r | 0.10 | 0.30 | 0.50 | Correlation |
| Cohen's f-squared | 0.02 | 0.15 | 0.35 | Multiple regression |
| Odds Ratio | 1.5 | 2.5 | 4.3 | Logistic regression |
| Hazard Ratio | 1.3 | 1.7 | 2.5 | Survival analysis |

#### 2.2 Converting Between Effect Sizes

```python
import numpy as np

# Cohen's d to r
def d_to_r(d):
    return d / np.sqrt(d**2 + 4)

# r to Cohen's d
def r_to_d(r):
    return 2 * r / np.sqrt(1 - r**2)

# Cohen's d to f (for ANOVA with 2 groups)
def d_to_f(d):
    return d / 2

# Odds ratio to Cohen's d
def or_to_d(odds_ratio):
    return np.log(odds_ratio) * np.sqrt(3) / np.pi

# Cohen's d to odds ratio
def d_to_or(d):
    return np.exp(d * np.pi / np.sqrt(3))

# Eta-squared to Cohen's f
def eta_sq_to_f(eta_sq):
    return np.sqrt(eta_sq / (1 - eta_sq))
```

### 3. Sample Size Calculations

#### 3.1 Two-Sample t-test

```python
from statsmodels.stats.power import TTestIndPower

analysis = TTestIndPower()

# Parameters
effect_size = 0.5    # Cohen's d
alpha = 0.05         # significance level
power = 0.80         # desired power
ratio = 1.0          # n2/n1 ratio (1.0 = equal groups)

# Calculate required sample size per group
n_per_group = analysis.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power,
    ratio=ratio,
    alternative='two-sided'
)
print(f"Required n per group: {np.ceil(n_per_group):.0f}")
print(f"Total N: {np.ceil(n_per_group) * 2:.0f}")

# Generate power curve
import matplotlib.pyplot as plt

sample_sizes = np.arange(10, 200)
powers = analysis.power(effect_size=effect_size, nobs1=sample_sizes,
                        alpha=alpha, ratio=ratio, alternative='two-sided')

plt.figure(figsize=(8, 5))
plt.plot(sample_sizes, powers)
plt.axhline(y=0.80, color='r', linestyle='--', label='Power = 0.80')
plt.axvline(x=n_per_group, color='g', linestyle='--', label=f'n = {np.ceil(n_per_group):.0f}')
plt.xlabel('Sample Size per Group')
plt.ylabel('Power')
plt.title(f'Power Curve (d={effect_size}, alpha={alpha})')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('power_curve_ttest.png', dpi=150, bbox_inches='tight')
```

#### 3.2 Paired t-test

```python
from statsmodels.stats.power import TTestPower

analysis = TTestPower()

effect_size = 0.5    # Cohen's d for paired differences
alpha = 0.05
power = 0.80

n = analysis.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power,
    alternative='two-sided'
)
print(f"Required n (pairs): {np.ceil(n):.0f}")
```

#### 3.3 Chi-Square Test of Independence

```python
from statsmodels.stats.power import GofChisquarePower

# For chi-square goodness of fit
analysis = GofChisquarePower()

effect_size = 0.3    # Cohen's w
alpha = 0.05
power = 0.80
n_bins = 4           # degrees of freedom + 1

n = analysis.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power,
    n_bins=n_bins
)
print(f"Required total N: {np.ceil(n):.0f}")

# Alternative: using proportion difference (2x2 table)
from statsmodels.stats.power import NormalIndPower

# Two proportions
p1 = 0.30  # expected proportion in group 1
p2 = 0.45  # expected proportion in group 2
# Cohen's h for two proportions
h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))

analysis = NormalIndPower()
n_per_group = analysis.solve_power(
    effect_size=abs(h),
    alpha=alpha,
    power=power,
    ratio=1.0,
    alternative='two-sided'
)
print(f"Required n per group (proportions): {np.ceil(n_per_group):.0f}")
```

#### 3.4 One-Way ANOVA

```python
from statsmodels.stats.power import FTestAnovaPower

analysis = FTestAnovaPower()

effect_size = 0.25   # Cohen's f
alpha = 0.05
power = 0.80
k_groups = 3         # number of groups

n_per_group = analysis.solve_power(
    effect_size=effect_size,
    alpha=alpha,
    power=power,
    k_groups=k_groups
)
print(f"Required n per group: {np.ceil(n_per_group):.0f}")
print(f"Total N: {np.ceil(n_per_group) * k_groups:.0f}")
```

#### 3.5 Correlation

```python
from statsmodels.stats.power import NormalIndPower
import numpy as np

def power_correlation(r, alpha=0.05, power=0.80):
    """Sample size for testing Pearson correlation != 0.
    Uses Fisher's z transformation approach.
    """
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    z_r = 0.5 * np.log((1 + r) / (1 - r))  # Fisher's z
    n = ((z_alpha + z_beta) / z_r) ** 2 + 3
    return int(np.ceil(n))

from scipy import stats

r = 0.30  # expected correlation
n = power_correlation(r, alpha=0.05, power=0.80)
print(f"Required N for r={r}: {n}")

# Multiple effect sizes
for r in [0.10, 0.20, 0.30, 0.40, 0.50]:
    n = power_correlation(r)
    print(f"r = {r:.2f}: N = {n}")
```

#### 3.6 Multiple Regression

```python
from statsmodels.stats.power import FTestPower

analysis = FTestPower()

# Parameters
f2 = 0.15           # Cohen's f-squared (medium effect)
alpha = 0.05
power = 0.80
n_predictors = 5    # number of predictors in full model
n_tested = 2        # number of predictors being tested

# df_num = n_tested (predictors being tested)
# df_denom = N - n_predictors - 1

# Iterative solution
from scipy.optimize import brentq

def power_equation(n):
    df_num = n_tested
    df_denom = n - n_predictors - 1
    if df_denom <= 0:
        return -1
    noncentrality = f2 * n
    power_calc = analysis.power(
        effect_size=np.sqrt(f2),
        df_num=df_num,
        df_denom=df_denom,
        alpha=alpha
    )
    return power_calc - power

n_required = int(np.ceil(brentq(power_equation, n_predictors + 2, 10000)))
print(f"Required N for {n_predictors} predictors (f2={f2}): {n_required}")
```

### 4. Adjustments

#### 4.1 Dropout and Loss to Follow-up

```python
def adjust_for_dropout(n_calculated, dropout_rate):
    """Inflate sample size to account for expected dropout."""
    return int(np.ceil(n_calculated / (1 - dropout_rate)))

n_base = 64  # calculated sample size per group
dropout = 0.20  # 20% expected dropout

n_adjusted = adjust_for_dropout(n_base, dropout)
print(f"Adjusted n per group (for {dropout*100:.0f}% dropout): {n_adjusted}")
```

#### 4.2 Unequal Group Sizes

When randomization ratios are not 1:1 (e.g., 2:1 treatment:control):

```python
from statsmodels.stats.power import TTestIndPower

analysis = TTestIndPower()

# 2:1 allocation ratio
n_smaller_group = analysis.solve_power(
    effect_size=0.5,
    alpha=0.05,
    power=0.80,
    ratio=2.0,  # n_treatment / n_control
    alternative='two-sided'
)
print(f"Control group n: {np.ceil(n_smaller_group):.0f}")
print(f"Treatment group n: {np.ceil(n_smaller_group * 2):.0f}")
print(f"Total N: {np.ceil(n_smaller_group) + np.ceil(n_smaller_group * 2):.0f}")
```

#### 4.3 Multiple Primary Outcomes

When testing multiple primary outcomes, adjust alpha for multiplicity:

```python
# Bonferroni-adjusted alpha
n_outcomes = 3
alpha_adjusted = 0.05 / n_outcomes

n_per_group = TTestIndPower().solve_power(
    effect_size=0.5,
    alpha=alpha_adjusted,
    power=0.80,
    alternative='two-sided'
)
print(f"Adjusted alpha: {alpha_adjusted:.4f}")
print(f"Required n per group (Bonferroni-adjusted): {np.ceil(n_per_group):.0f}")
```

### 5. Sample Size Table (Quick Reference)

Pre-computed sample sizes per group for two-sample t-test, alpha=0.05, two-sided:

| Cohen's d | Power 0.80 | Power 0.90 | Power 0.95 |
|-----------|-----------|-----------|-----------|
| 0.2 (small) | 394 | 527 | 651 |
| 0.3 | 176 | 235 | 290 |
| 0.4 | 100 | 133 | 164 |
| 0.5 (medium) | 64 | 86 | 105 |
| 0.6 | 45 | 60 | 74 |
| 0.7 | 33 | 44 | 55 |
| 0.8 (large) | 26 | 34 | 42 |
| 1.0 | 17 | 23 | 28 |
| 1.2 | 12 | 16 | 20 |

### 6. Post-Hoc Power Analysis (Caution)

Post-hoc (observed) power analysis using the observed effect size is generally discouraged because:
- Observed power is a monotonic function of the p-value, providing no additional information
- It conflates the effect size estimate with sample size
- A non-significant result with low post-hoc power does not mean the study was "underpowered" -- it means the observed effect was small

**Acceptable alternatives for negative studies:**
- Report the minimum detectable effect size at 80% power given the actual sample size
- Report confidence intervals for the effect size
- Conduct sensitivity analysis showing the range of effects the study could detect

```python
# Sensitivity analysis: what effect could we detect?
from statsmodels.stats.power import TTestIndPower

analysis = TTestIndPower()
actual_n = 50  # actual sample size per group

detectable_d = analysis.solve_power(
    nobs1=actual_n,
    alpha=0.05,
    power=0.80,
    alternative='two-sided'
)
print(f"With n={actual_n} per group, the study could detect d >= {detectable_d:.3f} at 80% power")
```

---

## Checklist

### Planning
- [ ] Primary outcome measure identified
- [ ] Study design specified (independent groups, paired, etc.)
- [ ] Significance level chosen and justified (typically alpha = 0.05)
- [ ] Desired power specified (typically 0.80 or 0.90)

### Effect Size
- [ ] Effect size estimated from pilot data, literature, or MCID
- [ ] Source of effect size estimate documented and justified
- [ ] Cohen's conventions used only as last resort (with justification)

### Calculation
- [ ] Appropriate formula or software used for the study design
- [ ] Sample size per group and total N reported
- [ ] Adjustment made for expected dropout/loss to follow-up
- [ ] Adjustment made for multiple primary outcomes (if applicable)
- [ ] Adjustment made for unequal allocation (if applicable)

### Documentation
- [ ] All parameters reported: alpha, power, effect size, N
- [ ] Software and version used for calculation stated
- [ ] Power curve or sensitivity analysis included (recommended)
- [ ] Sample size calculation included in protocol/grant application

---

## References

- Cohen J. Statistical Power Analysis for the Behavioral Sciences. 2nd ed. Lawrence Erlbaum Associates; 1988.
- Faul F, Erdfelder E, Lang AG, Buchner A. G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. Behavior Research Methods. 2007;39(2):175-191. doi:10.3758/BF03193146
- Hoenig JM, Heisey DM. The Abuse of Power: The Pervasive Fallacy of Power Calculations for Data Analysis. The American Statistician. 2001;55(1):19-24. doi:10.1198/000313001300339897
- Lakens D. Calculating and reporting effect sizes to facilitate cumulative science: a practical primer for t-tests and ANOVAs. Frontiers in Psychology. 2013;4:863. doi:10.3389/fpsyg.2013.00863
- statsmodels.stats.power documentation. https://www.statsmodels.org/stable/stats.html#power-and-sample-size-calculations

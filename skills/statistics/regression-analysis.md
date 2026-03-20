---
name: regression-analysis
category: statistics
discipline: general
description: "Regression analysis protocols for linear, logistic, and Cox regression with model selection and assumption checks"
---

# Regression Analysis

Protocols for linear, logistic, and Cox proportional hazards regression, including assumption verification, model diagnostics, and interpretation guidelines.

## When to Use

- When modeling the relationship between an outcome and one or more predictors
- Linear regression: continuous outcome variable
- Logistic regression: binary, ordinal, or multinomial outcome
- Cox regression: time-to-event (survival) outcome
- When adjusting for confounders in observational studies

---

## Protocol

### 1. Linear Regression

#### 1.1 Assumptions (LINE)

1. **Linearity** -- linear relationship between each predictor and the outcome
2. **Independence** -- observations are independent (study design)
3. **Normality** -- residuals are normally distributed
4. **Equal variance (homoscedasticity)** -- residual variance is constant across fitted values

#### 1.2 Model Fitting and Diagnostics

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.outliers_influence import variance_inflation_factor
import matplotlib.pyplot as plt

# Fit model
model = ols('outcome ~ predictor1 + predictor2 + predictor3', data=df).fit()
print(model.summary())

# Key outputs to report:
# - R-squared and adjusted R-squared
# - F-statistic and its p-value
# - Coefficients, standard errors, 95% CI, p-values
```

#### 1.3 Assumption Diagnostics

```python
import scipy.stats as stats

# 1. Linearity: partial regression plots
fig = sm.graphics.plot_partregress_grid(model)
plt.tight_layout()
plt.savefig('partial_regression.png', dpi=150, bbox_inches='tight')

# 2. Normality of residuals
residuals = model.resid
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].hist(residuals, bins=30, edgecolor='black', density=True)
axes[0].set_title('Residual Distribution')
stats.probplot(residuals, plot=axes[1])
axes[1].set_title('Q-Q Plot of Residuals')
plt.tight_layout()
plt.savefig('residual_normality.png', dpi=150, bbox_inches='tight')

# Shapiro-Wilk test on residuals
w, p = stats.shapiro(residuals)
print(f"Shapiro-Wilk: W={w:.4f}, p={p:.4f}")

# 3. Homoscedasticity: residuals vs fitted values
fitted = model.fittedvalues
plt.figure(figsize=(8, 6))
plt.scatter(fitted, residuals, alpha=0.5)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Fitted Values')
plt.ylabel('Residuals')
plt.title('Residuals vs Fitted Values')
plt.savefig('residuals_vs_fitted.png', dpi=150, bbox_inches='tight')

# Breusch-Pagan test for homoscedasticity
from statsmodels.stats.diagnostic import het_breuschpagan
bp_stat, bp_p, _, _ = het_breuschpagan(residuals, model.model.exog)
print(f"Breusch-Pagan: statistic={bp_stat:.4f}, p={bp_p:.4f}")

# 4. Multicollinearity: Variance Inflation Factor (VIF)
X = df[['predictor1', 'predictor2', 'predictor3']]
X = sm.add_constant(X)
vif_data = pd.DataFrame()
vif_data['Variable'] = X.columns
vif_data['VIF'] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
print(f"\nVIF:\n{vif_data}")
# VIF > 5: moderate concern; VIF > 10: serious multicollinearity
```

#### 1.4 Influential Observations

```python
# Cook's distance
influence = model.get_influence()
cooks_d = influence.cooks_distance[0]
n = len(df)
threshold = 4 / n  # common threshold

plt.figure(figsize=(10, 5))
plt.stem(range(n), cooks_d, markerfmt=',')
plt.axhline(y=threshold, color='r', linestyle='--', label=f'Threshold = {threshold:.4f}')
plt.xlabel('Observation Index')
plt.ylabel("Cook's Distance")
plt.title("Cook's Distance")
plt.legend()
plt.savefig('cooks_distance.png', dpi=150, bbox_inches='tight')

influential = np.where(cooks_d > threshold)[0]
print(f"Influential observations (Cook's d > {threshold:.4f}): {influential}")
```

#### 1.5 Model Selection

```python
# Stepwise using AIC/BIC
# Forward selection example
from statsmodels.formula.api import ols

def forward_selection(data, target, candidates, criterion='aic'):
    """Simple forward selection based on AIC or BIC."""
    selected = []
    remaining = list(candidates)
    current_score = float('inf')

    while remaining:
        scores = []
        for var in remaining:
            formula = f"{target} ~ {' + '.join(selected + [var])}"
            model = ols(formula, data=data).fit()
            score = model.aic if criterion == 'aic' else model.bic
            scores.append((score, var))

        best_score, best_var = min(scores)
        if best_score < current_score:
            selected.append(best_var)
            remaining.remove(best_var)
            current_score = best_score
        else:
            break

    return selected

# Usage:
# selected = forward_selection(df, 'outcome',
#     ['predictor1', 'predictor2', 'predictor3', 'predictor4'],
#     criterion='aic')
```

#### 1.6 Reporting Linear Regression

Report in a table:
| Predictor | B (95% CI) | SE | Beta | p |
|-----------|-----------|-----|------|---|
| (Intercept) | value | value | -- | value |
| Predictor 1 | value (lower, upper) | value | value | value |

Also report: R-squared, adjusted R-squared, F-statistic, residual SE, N.

### 2. Logistic Regression

#### 2.1 Model Fitting

```python
import statsmodels.api as sm
from statsmodels.formula.api import logit

# Binary logistic regression
model = logit('outcome ~ predictor1 + predictor2 + predictor3', data=df).fit()
print(model.summary())

# Odds ratios with 95% CI
params = model.params
conf = model.conf_int()
odds_ratios = pd.DataFrame({
    'OR': np.exp(params),
    'Lower 95% CI': np.exp(conf[0]),
    'Upper 95% CI': np.exp(conf[1]),
    'p-value': model.pvalues
})
print(f"\nOdds Ratios:\n{odds_ratios}")
```

#### 2.2 Odds Ratio Interpretation

- **OR = 1**: no association
- **OR > 1**: increased odds of outcome with higher predictor value
- **OR < 1**: decreased odds of outcome with higher predictor value
- For continuous predictors: OR represents the change in odds for a 1-unit increase
- For categorical predictors: OR represents the odds relative to the reference category
- Report as: "Each 1-unit increase in X was associated with Y-fold higher odds of the outcome (OR = Z, 95% CI: A-B)"

#### 2.3 Model Performance

```python
from sklearn.metrics import roc_auc_score, roc_curve, classification_report
from sklearn.metrics import confusion_matrix

# Predicted probabilities
y_pred_prob = model.predict(df)
y_pred = (y_pred_prob >= 0.5).astype(int)
y_true = df['outcome']

# ROC curve and AUC
fpr, tpr, thresholds = roc_curve(y_true, y_pred_prob)
auc = roc_auc_score(y_true, y_pred_prob)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
plt.plot([0, 1], [0, 1], 'k--', label='Random')
plt.xlabel('1 - Specificity (FPR)')
plt.ylabel('Sensitivity (TPR)')
plt.title('ROC Curve')
plt.legend()
plt.savefig('roc_curve.png', dpi=150, bbox_inches='tight')

print(f"AUC = {auc:.3f}")
print(f"\nClassification Report:\n{classification_report(y_true, y_pred)}")
```

#### 2.4 Goodness of Fit

```python
# Hosmer-Lemeshow test
from statsmodels.stats.diagnostic import acorr_ljungbox

def hosmer_lemeshow(y_true, y_pred_prob, n_groups=10):
    """Hosmer-Lemeshow goodness-of-fit test."""
    data = pd.DataFrame({'y': y_true, 'prob': y_pred_prob})
    data['decile'] = pd.qcut(data['prob'], n_groups, duplicates='drop')

    observed = data.groupby('decile')['y'].sum()
    expected = data.groupby('decile')['prob'].sum()
    n_group = data.groupby('decile')['y'].count()

    hl_stat = (((observed - expected)**2) /
               (expected * (1 - expected / n_group))).sum()
    df = len(observed) - 2
    p_value = 1 - stats.chi2.cdf(hl_stat, df)

    return hl_stat, p_value, df

hl_stat, hl_p, hl_df = hosmer_lemeshow(y_true, y_pred_prob)
print(f"Hosmer-Lemeshow: chi2({hl_df}) = {hl_stat:.3f}, p = {hl_p:.4f}")
# p > 0.05 indicates adequate fit
```

#### 2.5 Reporting Logistic Regression

Report in a table:
| Predictor | OR (95% CI) | p |
|-----------|------------|---|
| Predictor 1 | value (lower-upper) | value |

Also report: AUC, Hosmer-Lemeshow p-value, N (events/non-events), pseudo R-squared.

### 3. Cox Proportional Hazards Regression

#### 3.1 Model Fitting

```python
from lifelines import CoxPHFitter

# Prepare data: time, event (1=event, 0=censored), predictors
cox = CoxPHFitter()
cox.fit(df[['time', 'event', 'predictor1', 'predictor2', 'predictor3']],
        duration_col='time', event_col='event')

cox.print_summary()

# Hazard ratios with 95% CI
print(f"\nHazard Ratios:\n{np.exp(cox.params_)}")
print(f"\n95% CI:\n{np.exp(cox.confidence_intervals_)}")
```

#### 3.2 Proportional Hazards Assumption

The PH assumption states that the hazard ratio between groups is constant over time. Violation means the effect of a predictor changes over follow-up time.

```python
# Test PH assumption
# Method 1: Schoenfeld residuals test
ph_test = cox.check_assumptions(df[['time', 'event', 'predictor1',
                                     'predictor2', 'predictor3']],
                                 p_value_threshold=0.05,
                                 show_plots=True)

# Method 2: Log-log survival plot (for categorical predictors)
from lifelines import KaplanMeierFitter
kmf = KaplanMeierFitter()

plt.figure(figsize=(8, 6))
for group_val in df['predictor1_cat'].unique():
    mask = df['predictor1_cat'] == group_val
    kmf.fit(df[mask]['time'], df[mask]['event'], label=str(group_val))
    # Log-log plot: lines should be parallel if PH holds
    plt.plot(np.log(kmf.survival_function_.index),
             np.log(-np.log(kmf.survival_function_.values)), label=str(group_val))

plt.xlabel('log(Time)')
plt.ylabel('log(-log(S(t)))')
plt.title('Log-Log Survival Plot (PH Check)')
plt.legend()
plt.savefig('ph_check.png', dpi=150, bbox_inches='tight')
```

**If PH assumption is violated:**
- Stratify by the violating variable: `cox.fit(..., strata=['violating_var'])`
- Include a time-varying covariate (interaction with time)
- Use accelerated failure time (AFT) model instead
- Restrict analysis to a time period where PH holds

#### 3.3 Hazard Ratio Interpretation

- **HR = 1**: no effect on hazard
- **HR > 1**: increased hazard (worse survival)
- **HR < 1**: decreased hazard (better survival)
- Report as: "Predictor X was associated with a Y% increase in hazard of the event (HR = Z, 95% CI: A-B, p = C)"
- HR = 1.25 means 25% higher hazard; HR = 0.75 means 25% lower hazard

#### 3.4 Reporting Cox Regression

Report in a table:
| Predictor | HR (95% CI) | p |
|-----------|------------|---|
| Predictor 1 | value (lower-upper) | value |

Also report: concordance index (C-statistic), number of events/total, median follow-up time, PH assumption test results.

---

## Checklist

### Linear Regression
- [ ] Linearity assessed (partial regression plots, scatter plots)
- [ ] Normality of residuals checked (Q-Q plot, Shapiro-Wilk)
- [ ] Homoscedasticity verified (residuals vs. fitted, Breusch-Pagan)
- [ ] Multicollinearity assessed (VIF < 5 for all predictors)
- [ ] Influential observations identified (Cook's distance)
- [ ] R-squared, adjusted R-squared, and F-statistic reported
- [ ] Coefficients reported with 95% CIs and p-values
- [ ] Model selection justified (AIC/BIC or theory-driven)

### Logistic Regression
- [ ] Sufficient events per predictor (minimum 10 EPV guideline)
- [ ] Linearity of continuous predictors with log-odds checked (Box-Tidwell)
- [ ] No multicollinearity (VIF < 5)
- [ ] Odds ratios reported with 95% CIs
- [ ] Model discrimination assessed (AUC/ROC)
- [ ] Calibration assessed (Hosmer-Lemeshow or calibration plot)
- [ ] Classification performance reported (sensitivity, specificity)

### Cox Regression
- [ ] Proportional hazards assumption tested (Schoenfeld residuals)
- [ ] Violations addressed (stratification, time-varying covariates)
- [ ] Hazard ratios reported with 95% CIs
- [ ] Concordance index reported
- [ ] Number of events and total N reported
- [ ] Median follow-up time reported
- [ ] Kaplan-Meier curves provided for key predictors

### General
- [ ] Sample size adequate for number of predictors
- [ ] Missing data handled appropriately
- [ ] Confounders identified and adjusted for
- [ ] Interaction terms considered where biologically plausible
- [ ] Model assumptions documented in methods section

---

## References

- Hosmer DW, Lemeshow S, Sturdivant RX. Applied Logistic Regression. 3rd ed. Wiley; 2013.
- Vittinghoff E, Glidden DV, Shiboski SC, McCulloch CE. Regression Methods in Biostatistics. 2nd ed. Springer; 2012.
- Kleinbaum DG, Klein M. Survival Analysis: A Self-Learning Text. 3rd ed. Springer; 2012.
- Peduzzi P, Concato J, Kemper E, Holford TR, Feinstein AR. A simulation study of the number of events per variable in logistic regression analysis. J Clin Epidemiol. 1996;49(12):1373-1379.
- Harrell FE. Regression Modeling Strategies. 2nd ed. Springer; 2015.
- lifelines documentation. https://lifelines.readthedocs.io/
- statsmodels documentation. https://www.statsmodels.org/stable/

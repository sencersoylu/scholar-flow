---
name: descriptive-statistics
category: statistics
discipline: general
description: "Descriptive statistics procedures including central tendency, distribution analysis, normality tests, and data visualization"
---

# Descriptive Statistics

Comprehensive protocol for summarizing and characterizing data before hypothesis testing. Covers data inspection, central tendency, dispersion, distribution assessment, visualization, and Table 1 generation for clinical studies.

## When to Use

- As the first step in any quantitative analysis
- When characterizing a study sample
- When assessing data quality and distribution assumptions
- When generating Table 1 (baseline characteristics) for clinical or epidemiological studies
- Before selecting appropriate inferential statistical tests

---

## Protocol

### 1. Data Inspection

Examine data types, ranges, completeness, and plausibility before any analysis.

```python
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv("data.csv")

# Basic structure
print(f"Shape: {df.shape}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")

# Missing data summary
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_summary = pd.DataFrame({
    'missing_count': missing,
    'missing_pct': missing_pct.round(2)
})
print(f"\nMissing data:\n{missing_summary[missing_summary['missing_count'] > 0]}")

# Unique values for categorical variables
for col in df.select_dtypes(include=['object', 'category']).columns:
    print(f"\n{col}: {df[col].nunique()} unique values")
    print(df[col].value_counts())

# Range check for numeric variables
print(f"\nNumeric summary:\n{df.describe().T}")
```

**Key checks:**
- Identify variable types (continuous, ordinal, nominal, binary)
- Flag implausible values (negative ages, percentages > 100)
- Assess missing data patterns (MCAR, MAR, MNAR)
- Check for duplicate records
- Verify sample size matches expected enrollment

### 2. Central Tendency

Choose the appropriate measure based on data distribution and type.

| Data Type | Distribution | Recommended Measure |
|-----------|-------------|-------------------|
| Continuous | Normal (symmetric) | Mean |
| Continuous | Skewed | Median |
| Ordinal | Any | Median |
| Nominal | Any | Mode |

```python
# Central tendency for numeric variables
for col in df.select_dtypes(include=[np.number]).columns:
    print(f"\n--- {col} ---")
    print(f"  Mean:   {df[col].mean():.3f}")
    print(f"  Median: {df[col].median():.3f}")
    print(f"  Mode:   {df[col].mode().values}")
```

### 3. Dispersion

| Data Type | Distribution | Recommended Measures |
|-----------|-------------|---------------------|
| Continuous | Normal | Mean +/- SD |
| Continuous | Skewed | Median (IQR) or Median (Q1-Q3) |
| Ordinal | Any | IQR, range |

```python
for col in df.select_dtypes(include=[np.number]).columns:
    print(f"\n--- {col} ---")
    print(f"  SD:    {df[col].std():.3f}")
    print(f"  IQR:   {df[col].quantile(0.75) - df[col].quantile(0.25):.3f}")
    print(f"  Q1:    {df[col].quantile(0.25):.3f}")
    print(f"  Q3:    {df[col].quantile(0.75):.3f}")
    print(f"  Range: {df[col].min():.3f} - {df[col].max():.3f}")
    print(f"  CV:    {(df[col].std() / df[col].mean() * 100):.1f}%")
```

### 4. Distribution Assessment

#### 4.1 Normality Testing

```python
from scipy import stats

for col in df.select_dtypes(include=[np.number]).columns:
    # Shapiro-Wilk test (best for n < 5000)
    if len(df[col].dropna()) < 5000:
        stat, p = stats.shapiro(df[col].dropna())
        print(f"{col}: Shapiro-Wilk W={stat:.4f}, p={p:.4f}")

    # D'Agostino-Pearson test (for larger samples)
    if len(df[col].dropna()) >= 20:
        stat, p = stats.normaltest(df[col].dropna())
        print(f"{col}: D'Agostino-Pearson K2={stat:.4f}, p={p:.4f}")

    # Skewness and kurtosis
    skew = df[col].skew()
    kurt = df[col].kurtosis()  # excess kurtosis (0 for normal)
    print(f"{col}: Skewness={skew:.3f}, Kurtosis={kurt:.3f}")
```

**Interpretation guidelines:**
- Shapiro-Wilk: preferred for n < 5000; p < 0.05 suggests non-normality
- For large samples (n > 300), normality tests are overly sensitive -- rely on visual inspection and skewness/kurtosis values instead
- Rule of thumb: |skewness| < 2 and |kurtosis| < 7 suggest acceptable normality (Curran et al., 1996)
- Always combine statistical tests with visual assessment (Q-Q plots, histograms)

#### 4.2 Q-Q Plot

```python
import matplotlib.pyplot as plt
from scipy import stats

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

col = "variable_name"  # replace with your variable

# Histogram with normal curve overlay
axes[0].hist(df[col].dropna(), bins=30, density=True, alpha=0.7, edgecolor='black')
x = np.linspace(df[col].min(), df[col].max(), 100)
axes[0].plot(x, stats.norm.pdf(x, df[col].mean(), df[col].std()), 'r-', lw=2)
axes[0].set_title(f'Histogram: {col}')
axes[0].set_xlabel(col)
axes[0].set_ylabel('Density')

# Q-Q plot
stats.probplot(df[col].dropna(), dist="norm", plot=axes[1])
axes[1].set_title(f'Q-Q Plot: {col}')

plt.tight_layout()
plt.savefig(f'normality_{col}.png', dpi=150, bbox_inches='tight')
plt.show()
```

### 5. Visualization

#### 5.1 Continuous Variables

```python
import matplotlib.pyplot as plt
import seaborn as sns

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Box plots for all numeric variables
fig, axes = plt.subplots(1, len(numeric_cols), figsize=(4*len(numeric_cols), 5))
if len(numeric_cols) == 1:
    axes = [axes]
for ax, col in zip(axes, numeric_cols):
    sns.boxplot(y=df[col], ax=ax)
    ax.set_title(col)
plt.tight_layout()
plt.savefig('boxplots.png', dpi=150, bbox_inches='tight')
plt.show()

# Correlation matrix (for continuous variables)
corr = df[numeric_cols].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            square=True, linewidths=0.5)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig('correlation_matrix.png', dpi=150, bbox_inches='tight')
plt.show()
```

#### 5.2 Categorical Variables

```python
# Bar charts for categorical variables
cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

for col in cat_cols:
    plt.figure(figsize=(8, 5))
    counts = df[col].value_counts()
    sns.barplot(x=counts.index, y=counts.values)
    plt.title(f'Distribution: {col}')
    plt.xlabel(col)
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'barplot_{col}.png', dpi=150, bbox_inches='tight')
    plt.show()
```

### 6. Table 1 Generation (Baseline Characteristics)

Table 1 summarizes participant characteristics, typically stratified by study groups.

**Formatting conventions:**
- Normal continuous variables: mean (SD)
- Skewed continuous variables: median (IQR) or median [Q1, Q3]
- Categorical variables: n (%)
- Report p-values for group comparisons (though some journals discourage this in RCTs)

```python
from scipy import stats

def generate_table1(df, group_col, continuous_vars, categorical_vars):
    """Generate Table 1 with group comparisons."""
    groups = df[group_col].unique()
    results = []

    # Header
    header = ['Variable', 'Overall (N={})'.format(len(df))]
    for g in groups:
        n = (df[group_col] == g).sum()
        header.append(f'{g} (n={n})')
    header.append('p-value')

    # Continuous variables
    for var in continuous_vars:
        # Test normality
        _, p_norm = stats.shapiro(df[var].dropna().sample(min(len(df[var].dropna()), 5000)))
        is_normal = p_norm > 0.05

        if is_normal:
            # Mean (SD)
            overall = f"{df[var].mean():.1f} ({df[var].std():.1f})"
            group_vals = []
            group_data = []
            for g in groups:
                subset = df[df[group_col] == g][var].dropna()
                group_vals.append(f"{subset.mean():.1f} ({subset.std():.1f})")
                group_data.append(subset)

            # t-test or ANOVA
            if len(groups) == 2:
                _, p = stats.ttest_ind(group_data[0], group_data[1])
            else:
                _, p = stats.f_oneway(*group_data)

            row = [f'{var}, mean (SD)', overall] + group_vals + [f'{p:.3f}']
        else:
            # Median (IQR)
            q1, med, q3 = df[var].quantile([0.25, 0.5, 0.75])
            overall = f"{med:.1f} ({q1:.1f}-{q3:.1f})"
            group_vals = []
            group_data = []
            for g in groups:
                subset = df[df[group_col] == g][var].dropna()
                gq1, gmed, gq3 = subset.quantile([0.25, 0.5, 0.75])
                group_vals.append(f"{gmed:.1f} ({gq1:.1f}-{gq3:.1f})")
                group_data.append(subset)

            # Mann-Whitney or Kruskal-Wallis
            if len(groups) == 2:
                _, p = stats.mannwhitneyu(group_data[0], group_data[1])
            else:
                _, p = stats.kruskal(*group_data)

            row = [f'{var}, median (IQR)', overall] + group_vals + [f'{p:.3f}']

        results.append(row)

    # Categorical variables
    for var in categorical_vars:
        categories = df[var].dropna().unique()
        # Chi-square test
        contingency = pd.crosstab(df[var], df[group_col])
        if contingency.min().min() < 5:
            # Fisher's exact for 2x2, or note small expected counts
            if contingency.shape == (2, 2):
                _, p = stats.fisher_exact(contingency)
            else:
                _, p, _, _ = stats.chi2_contingency(contingency)
                # Flag: expected counts < 5
        else:
            _, p, _, _ = stats.chi2_contingency(contingency)

        # First row with variable name and p-value
        results.append([f'{var}, n (%)', '', *['' for _ in groups], f'{p:.3f}'])
        for cat in categories:
            overall_n = (df[var] == cat).sum()
            overall_pct = overall_n / df[var].notna().sum() * 100
            group_vals = []
            for g in groups:
                subset = df[df[group_col] == g]
                n = (subset[var] == cat).sum()
                pct = n / subset[var].notna().sum() * 100
                group_vals.append(f"{n} ({pct:.1f}%)")
            results.append([f'  {cat}', f'{overall_n} ({overall_pct:.1f}%)']
                          + group_vals + [''])

    table1 = pd.DataFrame(results, columns=header)
    return table1

# Usage example:
# table1 = generate_table1(
#     df, group_col='treatment_group',
#     continuous_vars=['age', 'bmi', 'systolic_bp'],
#     categorical_vars=['sex', 'smoking_status', 'diabetes']
# )
# print(table1.to_string(index=False))
# table1.to_csv('table1.csv', index=False)
```

---

## Checklist

### Data Quality
- [ ] Data types correctly identified and coded
- [ ] Implausible or out-of-range values investigated
- [ ] Missing data quantified and patterns assessed
- [ ] Duplicate records checked and handled
- [ ] Sample size verified against study records

### Summary Statistics
- [ ] Central tendency reported (mean for normal, median for skewed data)
- [ ] Dispersion reported (SD for normal, IQR for skewed data)
- [ ] Categorical variables summarized as n (%)
- [ ] Denominators clear for all percentages

### Distribution Assessment
- [ ] Normality tested (Shapiro-Wilk or visual inspection)
- [ ] Q-Q plots generated for key variables
- [ ] Skewness and kurtosis calculated
- [ ] Distribution shape documented to inform test selection

### Visualization
- [ ] Histograms or density plots for continuous variables
- [ ] Box plots for group comparisons
- [ ] Bar charts for categorical variables
- [ ] Outliers identified and documented

### Table 1
- [ ] All baseline characteristics included
- [ ] Stratified by study groups
- [ ] Correct summary statistics used (mean/SD vs. median/IQR)
- [ ] Statistical tests appropriate for variable type
- [ ] Missing data counts reported per variable

---

## References

- Field A. Discovering Statistics Using IBM SPSS Statistics. 5th ed. SAGE Publications; 2018.
- Curran PJ, West SG, Finch JF. The robustness of test statistics to nonnormality and specification error in confirmatory factor analysis. Psychological Methods. 1996;1(1):16-29. doi:10.1037/1082-989X.1.1.16
- Altman DG. Practical Statistics for Medical Research. Chapman & Hall/CRC; 1991.
- Vittinghoff E, Glidden DV, Shiboski SC, McCulloch CE. Regression Methods in Biostatistics. 2nd ed. Springer; 2012.
- pandas documentation. https://pandas.pydata.org/docs/
- scipy.stats documentation. https://docs.scipy.org/doc/scipy/reference/stats.html

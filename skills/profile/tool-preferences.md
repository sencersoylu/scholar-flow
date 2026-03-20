---
name: tool-preferences
category: profile
discipline: general
description: "Preferred tools for statistics (R/Python/SPSS), reference management (Zotero/Mendeley), and databases"
---

# Tool Preferences

## When to Use
Loaded by the Statistician agent to generate code in the preferred language, by the Citation Manager to use the correct reference manager format, and by the Literature Agent to search the right databases.

## Preferences Template

Fill in each field below. Where options are listed, select one or specify your own.

### Statistics and Data Analysis

- **Primary Statistics Tool:** (Python / R / SPSS / Stata / SAS / JASP / Julia)
- **Secondary Statistics Tool:** (if applicable)
- **Python Environment:** (conda / venv / poetry / pip)
- **Python Version:** (e.g., 3.11)
- **R Version:** (e.g., 4.3)
- **Preferred Python Libraries:**
  - Statistics: (scipy / statsmodels / pingouin)
  - Data manipulation: (pandas / polars)
  - Machine learning: (scikit-learn / PyTorch / TensorFlow / JAX)
  - Visualization: (matplotlib / seaborn / plotly / altair)
  - Meta-analysis: (PythonMeta / custom)
- **Preferred R Packages:**
  - Statistics: (stats / lme4 / survival / brms)
  - Data manipulation: (dplyr / data.table)
  - Visualization: (ggplot2 / plotly)
  - Meta-analysis: (meta / metafor / netmeta)
  - Reporting: (rmarkdown / knitr / Quarto)

### Reference Management

- **Reference Manager:** (Zotero / Mendeley / EndNote / Paperpile / JabRef / BibDesk / None)
- **Export Format:** (BibTeX / BibLaTeX / RIS / EndNote XML / CSL JSON)
- **Library Sync:** (Cloud / Local / Both)
- **Auto-Import DOIs:** (Yes / No)
- **PDF Organization:** (Managed by reference manager / Manual folder structure)

### Literature Databases

- **Primary Databases:** (select all that apply)
  - Medical: PubMed, MEDLINE, Embase, Cochrane Library, CINAHL
  - Multidisciplinary: Scopus, Web of Science, Google Scholar
  - Computer Science: IEEE Xplore, ACM Digital Library, DBLP, Semantic Scholar
  - Preprints: arXiv, medRxiv, bioRxiv, SSRN
  - Regional: LILACS, CNKI, J-STAGE
- **Preferred Search Order:** (list in priority order)
- **Full-Text Access:** (Institutional / OpenAccess preferred / Both)
- **Interlibrary Loan Available:** (Yes / No)

### Document Preparation

- **Primary Writing Tool:** (LaTeX / Microsoft Word / Google Docs / Typst / Quarto)
- **LaTeX Distribution:** (TeX Live / MiKTeX / Overleaf / N/A)
- **LaTeX Editor:** (Overleaf / VS Code / TeXstudio / Emacs / Vim / N/A)
- **LaTeX Document Class:** (article / IEEEtran / elsarticle / amsart / custom)
- **Word Template:** (journal-provided / custom / default)
- **Collaboration Platform:** (Overleaf / Google Docs / SharePoint / Git)

### Figures and Graphics

- **Figure Creation Tool:** (matplotlib / ggplot2 / GraphPad Prism / Inkscape / Adobe Illustrator / BioRender / draw.io)
- **Figure Format:** (PDF / SVG / PNG / EPS / TIFF)
- **Figure DPI:** (300 / 600 / 1200)
- **PRISMA Flow Diagram Tool:** (draw.io / Lucidchart / PRISMA Flow Generator / manual)
- **Forest Plot Tool:** (RevMan / R metafor / Python forestplot / Stata)

### Data Management

- **Data Storage:** (Institutional server / Cloud storage / Local / GitHub)
- **Data Format:** (CSV / Excel / Parquet / HDF5 / JSON / SPSS .sav)
- **Version Control:** (Git / None / Other)
- **Code Repository:** (GitHub / GitLab / Bitbucket / None)
- **Data Sharing Platform:** (Zenodo / Figshare / Dryad / Mendeley Data / institutional repository)
- **Reproducibility Tool:** (Docker / Singularity / conda-lock / renv / None)

### Computation

- **Hardware Available:** (Local workstation / University HPC / Cloud GPU / Colab)
- **GPU Type:** (if applicable, e.g., NVIDIA A100, RTX 4090)
- **Max RAM:** (e.g., 32 GB, 128 GB)
- **Cluster Scheduler:** (SLURM / PBS / SGE / N/A)

## How Agents Use These Preferences

- **Statistician:** Generates analysis code in the preferred language using preferred libraries
- **Literature Agent:** Searches databases in the specified priority order
- **Citation Manager:** Exports references in the correct format for the reference manager
- **Academic Writer:** Formats output for the preferred writing tool (LaTeX commands vs Word formatting)
- **Methodology Agent:** Recommends PRISMA/forest plot tools based on figure preferences

## References
- N/A (user-provided)

---
name: systematic-review
category: methodology
discipline: general
description: "PRISMA 2020 systematic review protocol with database search strategy and bias assessment"
---

# Systematic Review

## When to Use
When conducting a systematic review of existing literature to answer a clearly defined research question. Applicable across disciplines but most commonly used in healthcare, social sciences, and evidence synthesis. Use this protocol whether performing a standalone systematic review or as the search phase of a meta-analysis.

## Protocol

### Step 1: Define the Research Question
- Formulate a focused question using the PICO(S) framework:
  - **P**opulation: Who is being studied?
  - **I**ntervention / Exposure: What is the treatment, exposure, or phenomenon?
  - **C**omparator: What is the alternative (placebo, standard care, no exposure)?
  - **O**utcome: What is being measured?
  - **S**tudy design (optional): What study types are eligible?
- Ensure the question is specific enough to guide search terms and eligibility criteria
- Register the question to check for existing or ongoing reviews (PROSPERO, Cochrane Library, JBI)

### Step 2: Register the Protocol
- Register on PROSPERO (for health-related reviews) or OSF (for other disciplines)
- Registration should occur BEFORE screening begins
- Include: objectives, eligibility criteria, search strategy, data extraction plan, risk of bias tool, synthesis method
- Record the registration number for manuscript reporting
- Consider publishing a protocol paper (e.g., in BMJ Open, Systematic Reviews)

### Step 3: Develop the Search Strategy
- Build search strings using a combination of:
  - **Controlled vocabulary:** MeSH terms (PubMed), Emtree (Embase), Subject Headings (CINAHL)
  - **Free-text keywords:** synonyms, related terms, variant spellings, abbreviations
  - **Boolean operators:** AND (combine concepts), OR (combine synonyms), NOT (use sparingly)
  - **Proximity operators:** ADJ, NEAR, W/n (database-specific)
  - **Truncation and wildcards:** * for variable endings, ? for single characters
- Structure the search by PICO concept blocks connected with AND
- Pilot the search in one database, then adapt syntax for each additional database
- Have a librarian or information specialist peer-review the search strategy (PRESS checklist)
- Document the full search string for each database

### Step 4: Search Multiple Databases
- Search a minimum of 3 databases (more for comprehensive reviews):
  - Medical: PubMed/MEDLINE, Embase, Cochrane CENTRAL
  - Multidisciplinary: Scopus, Web of Science
  - Subject-specific: CINAHL (nursing), PsycINFO (psychology), IEEE Xplore (engineering), ACM DL (CS)
- Supplement with:
  - Grey literature: OpenGrey, ProQuest Dissertations, conference proceedings
  - Trial registries: ClinicalTrials.gov, WHO ICTRP
  - Citation searching: forward (cited-by) and backward (reference lists) of included studies
  - Hand-searching: key journals in the field
  - Contact with authors for unpublished data
- Record the date of each search
- Export all results to a reference manager and deduplicate

### Step 5: Screen Titles and Abstracts
- Import deduplicated records into a screening tool (Covidence, Rayyan, ASReview, or spreadsheet)
- Apply predefined inclusion and exclusion criteria
- At least 2 independent reviewers screen all records
- Calculate inter-rater reliability (Cohen's kappa) on a pilot sample (aim for kappa > 0.80)
- Resolve disagreements by discussion or a third reviewer
- Record reasons for exclusion at this stage (aggregate counts)
- Err on the side of inclusion — uncertain records proceed to full-text review

### Step 6: Full-Text Review
- Retrieve full texts of all potentially eligible records
- At least 2 independent reviewers assess each full text against eligibility criteria
- Record specific reasons for exclusion for each excluded study
- Resolve disagreements by discussion or a third reviewer
- Contact authors if key information is missing from the paper
- Document the number of studies at each stage for the PRISMA flow diagram

### Step 7: Data Extraction
- Develop a standardized data extraction form (pilot on 3-5 studies first)
- Extract from each included study:
  - Study identifiers: author, year, country, journal, DOI
  - Study design and setting
  - Participant characteristics: sample size, demographics, inclusion/exclusion criteria
  - Intervention/exposure details: type, dose, duration, delivery
  - Comparator details
  - Outcome definitions and measurement tools
  - Results: effect estimates, confidence intervals, p-values, raw data where available
  - Funding source and conflicts of interest
- At least 2 reviewers extract data independently; reconcile discrepancies
- Contact study authors for missing or unclear data

### Step 8: Assess Risk of Bias / Quality
- Select the appropriate tool based on study design:
  - **RCTs:** Cochrane Risk of Bias tool (RoB 2) — 5 domains: randomization, deviations from intervention, missing data, outcome measurement, selective reporting
  - **Non-randomized studies of interventions:** ROBINS-I — 7 domains: confounding, selection, classification of interventions, deviations, missing data, measurement, selective reporting
  - **Observational studies:** Newcastle-Ottawa Scale (NOS) — selection, comparability, outcome/exposure
  - **Cross-sectional:** JBI Critical Appraisal Checklist
  - **Qualitative:** CASP Qualitative Checklist or JBI
  - **Diagnostic accuracy:** QUADAS-2
- At least 2 reviewers assess quality independently
- Present results in a risk-of-bias summary figure and traffic-light table
- Do NOT use quality scores to exclude studies; instead, use in sensitivity analysis

### Step 9: Synthesize Results
- **Narrative synthesis:** Organize findings by outcome, population subgroup, or thematic category
- Create summary of findings (SoF) tables
- If quantitative synthesis is appropriate, proceed to meta-analysis (see meta-analysis skill)
- Consider vote counting based on direction of effect (not statistical significance) as a minimal synthesis
- Use harvest plots or albatross plots for visual synthesis without pooling
- Address heterogeneity in study designs, populations, interventions, and outcomes narratively

### Step 10: Assess Certainty of Evidence
- Apply GRADE (Grading of Recommendations, Assessment, Development and Evaluations):
  - Start at "high" for RCTs, "low" for observational studies
  - Rate down for: risk of bias, inconsistency, indirectness, imprecision, publication bias
  - Rate up for: large effect, dose-response, plausible confounding
  - Assign final rating: High / Moderate / Low / Very Low
- Present GRADE assessment in a Summary of Findings table

### Step 11: Create the PRISMA Flow Diagram
- Document the flow of records through each phase:
  - Identification: records from databases, registers, and other sources
  - Screening: records screened, records excluded
  - Eligibility: reports sought for retrieval, reports not retrieved, reports assessed, reports excluded with reasons
  - Included: studies included in review, studies included in meta-analysis (if applicable)
- Use the PRISMA 2020 flow diagram template (available at prisma-statement.org)

### Step 12: Write the Manuscript
- Follow the PRISMA 2020 checklist for reporting (see below)
- Include: structured abstract, registered protocol reference, complete search strategy (appendix), PRISMA flow diagram, characteristics of included studies table, risk of bias assessment, synthesis results, GRADE SoF table
- Report deviations from the registered protocol with justification

## Checklist: PRISMA 2020 (27 Items)

### Title
1. Identify the report as a systematic review

### Abstract
2. Provide a structured abstract (background, objectives, data sources, study eligibility, participants, interventions, study appraisal and synthesis methods, results, limitations, conclusions, registration number)

### Introduction
3. Describe the rationale for the review in the context of existing knowledge
4. Provide an explicit statement of the objective(s) or question(s) the review addresses

### Methods
5. Indicate whether a review protocol exists, where it can be accessed, and registration information
6. Specify the eligibility criteria (inclusion and exclusion) with rationale
7. Describe all information sources (databases, registers, websites, organizations, reference lists) with dates of coverage
8. Present the complete search strategy for at least one database so it could be repeated
9. Describe the selection process (screening method, number of reviewers, software used)
10. Describe the data extraction process (methods, whether done independently, from how many reviewers)
11. List and define all outcome variables sought, distinguishing primary from secondary
12. Describe methods for assessing risk of bias in individual studies, including which domains were assessed
13. Describe any methods used to synthesize results (statistical methods, handling of heterogeneity, sensitivity analyses, meta-regression, subgroup analyses)
14. Describe any methods used to assess the certainty or confidence in the body of evidence (e.g., GRADE)
15. State the principal summary measures (e.g., risk ratio, mean difference) and describe methods of handling data and combining results

### Results
16. Report the number of studies screened, assessed for eligibility, and included, with reasons for exclusion at each stage (ideally with a flow diagram)
17. For each included study, present key characteristics (cite each study) and risk of bias assessments
18. Present results of all statistical syntheses conducted. If meta-analysis was performed, present for each the pooled estimate with confidence interval and heterogeneity measures
19. Present results of any assessment of risk of bias across studies
20. Present results of any sensitivity analysis or subgroup analysis

### Discussion
21. Provide a general interpretation of the results in the context of other evidence
22. Discuss any limitations of the evidence included in the review
23. Discuss any limitations of the review process
24. Provide a general interpretation and implications for practice, policy, and future research

### Other Information
25. Describe sources of funding for the review and the role of funders
26. Report any conflicts of interest of review authors
27. Report availability of data, code, and other materials used in the review

## References
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ. 2021;372:n71. doi:10.1136/bmj.n71
- Higgins JPT, Thomas J, Chandler J, et al., editors. Cochrane Handbook for Systematic Reviews of Interventions version 6.4. Cochrane, 2023. Available from www.training.cochrane.org/handbook
- Rethlefsen ML, Kirtley S, Waffenschmidt S, et al. PRISMA-S: an extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews. Systematic Reviews. 2021;10:39
- McGowan J, Sampson M, Salzwedel DM, et al. PRESS Peer Review of Electronic Search Strategies: 2015 Guideline Statement. Journal of Clinical Epidemiology. 2016;75:40-46
- Sterne JAC, Savovic J, Page MJ, et al. RoB 2: a revised tool for assessing risk of bias in randomised trials. BMJ. 2019;366:l4898
- Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. BMJ. 2008;336:924-926

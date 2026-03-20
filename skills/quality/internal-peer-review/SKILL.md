---
name: internal-peer-review
category: quality
discipline: general
description: "Internal peer review protocol checking methodology consistency, result interpretation, and logical fallacies"
---

# Internal Peer Review

Structured protocol for conducting a comprehensive internal review of a manuscript before journal submission. Covers all major sections with severity-rated feedback.

## When to Use

- Loaded by the Peer Reviewer agent for every manuscript review
- Before submitting a manuscript to a journal
- When a co-author requests a critical review
- When revising a manuscript after external peer review
- As a quality gate in the Scholar Flow pipeline

---

## Protocol

### 1. Title and Abstract Review

#### 1.1 Title

Evaluate the title for:
- **Accuracy** -- does it reflect the study design, population, and main finding?
- **Clarity** -- is it understandable without reading the paper?
- **Conciseness** -- is it free of unnecessary words? (Avoid "A study of...", "Investigation into...")
- **Informativeness** -- does it convey the key result (for results-based titles) or the scope (for descriptive titles)?
- **Keywords** -- does it contain terms that aid discoverability?
- **Study design** -- is the design named in the title? (Required by some journals: "A Randomized Controlled Trial", "A Systematic Review")

#### 1.2 Abstract

Evaluate for completeness based on structure (most biomedical journals require structured abstracts):

| Section | Required Elements |
|---------|------------------|
| Background/Objective | Research question or objective; why the study was done |
| Methods | Study design, setting, participants, interventions, main outcomes |
| Results | Key quantitative results with effect sizes and CIs or p-values |
| Conclusions | Main finding; clinical/practical implications; limitations acknowledged |

Check:
- [ ] Word count within journal limit (typically 250-300 words)
- [ ] All results in the abstract appear in the main text
- [ ] No citations in the abstract (unless journal permits)
- [ ] No abbreviations not defined in the abstract
- [ ] Trial registration number included (if applicable)
- [ ] Conclusions supported by the reported results (no overstatement)

### 2. Introduction Review

Evaluate using the "funnel" structure (broad to specific):

1. **Context and background** -- is the topic introduced clearly? Is the scope appropriate (not too broad, not too narrow)?
2. **Literature review** -- is the relevant literature summarized accurately and fairly? Are key studies cited? Are gaps identified?
3. **Knowledge gap** -- is a clear gap in current knowledge identified and justified?
4. **Rationale** -- does the study logically follow from the identified gap?
5. **Objective/hypothesis** -- is the study objective clearly stated? Is the hypothesis specific and testable?

Common issues:
- Citing outdated or retracted studies
- Selective citation (omitting contradictory evidence)
- Overstating the gap ("No study has ever..." -- usually incorrect)
- Objective that does not match the methods or results
- Introduction too long (typically 3-5 paragraphs)

### 3. Methods Review

The most critical section for scientific rigor. Evaluate:

#### 3.1 Study Design
- [ ] Design clearly stated (RCT, cohort, cross-sectional, case-control, etc.)
- [ ] Design appropriate for the research question
- [ ] Prospective registration mentioned (if applicable)

#### 3.2 Setting and Participants
- [ ] Study setting described (single/multi-center, geographic location, time period)
- [ ] Eligibility criteria clearly defined (inclusion and exclusion)
- [ ] Sampling method described
- [ ] Sample size justified with power analysis
- [ ] Recruitment process described
- [ ] Participant flow documented (or CONSORT diagram provided)

#### 3.3 Variables and Measurements
- [ ] Primary outcome clearly defined
- [ ] Secondary outcomes listed
- [ ] Exposure/intervention described in reproducible detail
- [ ] Measurement instruments validated or reliability reported
- [ ] Blinding described (who was blinded, how)

#### 3.4 Bias and Confounding
- [ ] Potential sources of bias identified and addressed
- [ ] Confounders identified and adjustment strategy described
- [ ] Randomization method described (if applicable)
- [ ] Allocation concealment described (if applicable)

#### 3.5 Statistical Analysis
- [ ] Analysis plan matches study design
- [ ] Statistical tests named and justified
- [ ] Software and version specified
- [ ] Significance threshold stated
- [ ] Missing data handling described
- [ ] Sensitivity analyses planned
- [ ] Multiple comparison correction addressed

#### 3.6 Ethics
- [ ] Ethics approval stated with reference number
- [ ] Informed consent described
- [ ] Data privacy measures mentioned

### 4. Results Review

#### 4.1 Participant Flow
- [ ] Number screened, enrolled, analyzed reported
- [ ] Reasons for exclusion documented
- [ ] Flow diagram provided (if applicable)
- [ ] Baseline characteristics table (Table 1) included

#### 4.2 Main Findings
- [ ] Results address the primary objective
- [ ] Results presented in logical order (primary outcome first)
- [ ] Effect sizes reported (not just p-values)
- [ ] Confidence intervals provided
- [ ] Exact p-values reported (not "p < 0.05" except when p < 0.001)
- [ ] Results consistent with Methods section (same tests, same outcomes)

#### 4.3 Tables and Figures
- [ ] Tables are self-explanatory (title, headers, footnotes)
- [ ] Figures are clear, properly labeled, with legends
- [ ] Data in tables/figures matches data in text
- [ ] No data duplication between tables, figures, and text
- [ ] Appropriate visualization type chosen

#### 4.4 Additional Analyses
- [ ] Subgroup analyses pre-specified or clearly labeled as exploratory
- [ ] Sensitivity analyses support main findings
- [ ] Negative results reported (not just significant findings)

### 5. Discussion Review

#### 5.1 Interpretation
- [ ] Key findings summarized without repeating Results verbatim
- [ ] Findings interpreted in context of existing literature
- [ ] Results compared with prior studies (agreements and disagreements explained)
- [ ] Biological or theoretical mechanism discussed

#### 5.2 Strengths and Limitations
- [ ] Study strengths identified
- [ ] Limitations honestly acknowledged
- [ ] Impact of limitations on interpretation discussed
- [ ] Common limitations not omitted (selection bias, measurement error, confounding, generalizability)

#### 5.3 Logical Soundness
- [ ] Conclusions supported by the data (no overstatement)
- [ ] Correlation not presented as causation (in observational studies)
- [ ] Generalizability appropriately scoped
- [ ] Clinical or practical significance discussed (not just statistical significance)
- [ ] No ecological fallacy (applying group-level findings to individuals)
- [ ] No post-hoc reasoning presented as a priori hypotheses

#### 5.4 Implications and Future Directions
- [ ] Practical/clinical implications stated
- [ ] Future research directions suggested
- [ ] Implications proportionate to the evidence

### 6. References Review

- [ ] All citations verified (spot-check 3-5 for accuracy)
- [ ] Key landmark studies cited
- [ ] Recent literature included (within last 3-5 years)
- [ ] Self-citation not excessive
- [ ] No retracted articles cited
- [ ] Citation style consistent with journal requirements
- [ ] All in-text citations appear in reference list and vice versa

### 7. Language and Presentation

- [ ] Writing is clear and concise
- [ ] Passive vs. active voice consistent with journal norms
- [ ] Abbreviations defined at first use
- [ ] Terminology used consistently throughout
- [ ] No jargon that would be unclear to the target audience
- [ ] Paragraphs have clear topic sentences
- [ ] Logical transitions between sections and paragraphs

---

## Output Format

Structure the review output as follows:

```
## Internal Peer Review Report

### Summary Assessment
[1-2 sentence overall assessment: ready for submission / needs minor revisions /
needs major revisions / fundamental issues]

### Critical Issues (Must Address Before Submission)
1. **[Section]:** [Description of issue]
   - Impact: [Why this matters]
   - Recommendation: [Specific fix]

### Major Issues (Strongly Recommended)
1. **[Section]:** [Description of issue]
   - Impact: [Why this matters]
   - Recommendation: [Specific fix]

### Minor Issues (Suggestions for Improvement)
1. **[Section]:** [Description of issue]
   - Recommendation: [Specific fix]

### Strengths
- [Notable strength 1]
- [Notable strength 2]

### Reporting Checklist Compliance
- [ ] Appropriate guideline identified: [CONSORT/STROBE/PRISMA/etc.]
- [ ] Checklist completed: [Yes/No/Partial]
- [ ] Key missing items: [List]
```

### Severity Definitions

| Severity | Definition | Examples |
|----------|-----------|---------|
| **Critical** | Fundamental flaw that invalidates conclusions or prevents publication | Wrong statistical test for data type; undisclosed conflict of interest; fabricated data indicators; missing ethics approval |
| **Major** | Significant issue that weakens the paper substantially | Missing power analysis; no effect sizes reported; selective reporting of outcomes; important confounders not addressed |
| **Minor** | Issue that should be fixed but does not threaten validity | Inconsistent abbreviations; minor formatting issues; unclear figure labels; redundant text |

---

## Checklist

### Before Starting Review
- [ ] Read the entire manuscript once without taking notes
- [ ] Identify the study design and applicable reporting guideline
- [ ] Note the target journal and its scope/requirements

### During Review
- [ ] Each section reviewed systematically using the protocol above
- [ ] Issues categorized by severity (critical/major/minor)
- [ ] Specific recommendations provided for each issue
- [ ] Strengths acknowledged alongside weaknesses
- [ ] Cross-references checked (methods match results, abstract matches text)

### After Review
- [ ] Review report organized by severity
- [ ] Constructive tone maintained throughout
- [ ] Actionable recommendations provided
- [ ] Reporting checklist compliance verified
- [ ] Statistical review completed (see statistical-review skill)

---

## References

- COPE (Committee on Publication Ethics). Ethical Guidelines for Peer Reviewers. 2017. https://publicationethics.org/resources/guidelines-new/cope-ethical-guidelines-peer-reviewers
- Stahel PF, Moore EE. Peer review for biomedical publications: we can improve the system. BMC Med. 2014;12:179. doi:10.1186/s12916-014-0179-1
- Provenzale JM, Stanley RJ. A systematic guide to reviewing a manuscript. AJR Am J Roentgenol. 2005;185(4):848-854. doi:10.2214/AJR.05.0782
- EQUATOR Network. Reporting guidelines for main study types. https://www.equator-network.org/

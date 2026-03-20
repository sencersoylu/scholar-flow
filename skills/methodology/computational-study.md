---
name: computational-study
category: methodology
discipline: cs
description: "Computational study protocol with algorithm design, benchmarking, and ablation study methodology"
---

# Computational Study

## When to Use
When evaluating algorithms, models, or computational systems. This covers empirical CS research including machine learning experiments, algorithm benchmarks, systems evaluations, and computational analyses. Use this protocol whenever claims are supported by experimental results on computational tasks.

## Protocol

### Step 1: Define the Research Problem and Claims
- State the problem clearly: what task, what input/output, what constraints
- Articulate the specific claims to be evaluated:
  - Performance claim: "Method X outperforms baselines on metric Y"
  - Efficiency claim: "Method X achieves comparable performance with Z% fewer resources"
  - Generalization claim: "Method X works across domains/datasets/scales"
  - Ablation claim: "Component Z contributes N% to overall performance"
- Distinguish between theoretical contributions (proofs, bounds) and empirical contributions (experiments)
- Define the scope: which settings, scales, domains, and data types the claims apply to

### Step 2: Select or Design the Method
- Clearly describe the proposed algorithm, model, or system:
  - Architecture and components
  - Input/output specification with data types and shapes
  - Hyperparameters and their roles
  - Computational complexity (time and space) — theoretical Big-O analysis
  - Training procedure (for learning-based methods): optimizer, learning rate schedule, batch size, epochs, convergence criteria
- Provide pseudocode or algorithmic description for novel methods
- Discuss design decisions and their rationale
- Identify the novel contribution relative to prior work

### Step 3: Select Baselines
- Include baselines that represent:
  - **State-of-the-art (SOTA):** Current best-performing methods on the same task
  - **Classical baselines:** Established, well-understood methods (even if not SOTA)
  - **Ablated versions:** Variants of the proposed method with components removed
  - **Simple baselines:** Trivial approaches (random, majority class, nearest neighbor) to establish a floor
- Use the same evaluation protocol for all methods:
  - Same data splits
  - Same preprocessing
  - Same evaluation metrics
  - Same hardware (or normalize for hardware differences)
- Re-run baselines rather than copying numbers from papers when possible (different implementations, data versions, or hardware can cause discrepancies)
- If re-running is not feasible, clearly state the source of baseline numbers and any known differences in evaluation setup

### Step 4: Select Benchmarks and Datasets
- Use established, widely-used benchmarks when available:
  - NLP: GLUE, SuperGLUE, SQuAD, WMT, MMLU
  - Vision: ImageNet, COCO, CIFAR-10/100, CelebA
  - Tabular: UCI repository, OpenML
  - Graphs: OGB, TU datasets
  - Reinforcement learning: Atari, MuJoCo, Gymnasium
  - Systems: SPEC, TPC, MLPerf
- Report dataset characteristics:
  - Size (samples, features, classes)
  - Class distribution and imbalance
  - Train/validation/test splits (use standard splits; if creating new splits, specify the random seed)
  - Any preprocessing, filtering, or augmentation applied
  - Version number or download date
  - License and terms of use
- Include multiple datasets to demonstrate generalization
- Address potential data leakage: ensure test data was not seen during training or hyperparameter tuning
- For new datasets: describe the collection process, annotation protocol (inter-annotator agreement), and release plan

### Step 5: Define Evaluation Metrics
- Select metrics appropriate to the task and aligned with the claims:
  - **Classification:** accuracy, precision, recall, F1, AUC-ROC, AUC-PR (prefer AUC-PR for imbalanced data)
  - **Regression:** MSE, RMSE, MAE, R-squared, MAPE
  - **Ranking:** NDCG, MAP, MRR, Precision@k, Recall@k
  - **Generation:** BLEU, ROUGE, METEOR, BERTScore, human evaluation
  - **Clustering:** NMI, ARI, silhouette score
  - **Efficiency:** wall-clock time, FLOPs, parameter count, memory usage, throughput (samples/sec)
  - **Fairness:** demographic parity, equalized odds, disparate impact
- Report multiple metrics — do not cherry-pick the one where your method wins
- Specify how metrics are computed: macro/micro/weighted averaging, confidence level for intervals
- For generative tasks: include human evaluation alongside automatic metrics

### Step 6: Design the Experimental Setup
- **Hyperparameter tuning:**
  - Specify the search space for all hyperparameters (ranges, distributions)
  - Specify the search method: grid search, random search (preferred over grid), Bayesian optimization, manual tuning
  - Specify the budget: number of trials, total GPU hours
  - Tune on the validation set, NEVER on the test set
  - Report the selected hyperparameters for the final model
  - Apply the same tuning budget/effort to baselines (fair comparison)

- **Cross-validation (if applicable):**
  - k-fold (typically k=5 or k=10) for small datasets
  - Stratified k-fold for imbalanced classification
  - Leave-one-out for very small datasets
  - Time-series split for temporal data (no future leakage)
  - Nested cross-validation for simultaneous model selection and evaluation

- **Random seeds and repetition:**
  - Run experiments with multiple random seeds (minimum 3, preferably 5-10)
  - Report mean and standard deviation (or standard error) across runs
  - Fix and report the random seeds used for reproducibility
  - Set seeds for: data splitting, weight initialization, data shuffling, dropout

- **Statistical significance testing:**
  - Paired t-test or Wilcoxon signed-rank test (for paired comparisons across datasets/folds)
  - McNemar's test (for comparing two classifiers on the same test set)
  - Bootstrap confidence intervals (for single test set comparisons)
  - Corrected resampled t-test (Nadeau and Bengio) for cross-validation comparisons
  - Report p-values AND effect sizes (Cohen's d or similar)
  - Apply Bonferroni or Holm correction for multiple comparisons
  - Do NOT claim "significant" without a formal statistical test

### Step 7: Design Ablation Studies
- Systematically remove or modify components to quantify their contribution:
  - Remove one component at a time (leave-one-out ablation)
  - Add components incrementally (leave-one-in / additive ablation)
  - Vary key design choices (e.g., attention type, normalization, activation function)
- For each ablation:
  - Change only one thing at a time (isolate the variable)
  - Use the same evaluation protocol as the main experiment
  - Report the performance delta and its statistical significance
- Present ablation results in a clear table with rows for each variant
- Address interactions: if components interact, consider factorial ablation (2^k design) for key components
- Ablation studies should directly support the claims made in the paper

### Step 8: Report Computational Resources
- **Hardware:**
  - GPU model and count (e.g., 4x NVIDIA A100 80GB)
  - CPU model and core count
  - RAM
  - Storage type (SSD/HDD)
  - Interconnect (for distributed training: NVLink, InfiniBand)
- **Software:**
  - OS, CUDA version, driver version
  - Framework and version (PyTorch 2.1, TensorFlow 2.15, JAX 0.4)
  - Key library versions (transformers, numpy, scipy)
  - Compiler and optimization flags (for systems papers)
- **Training cost:**
  - Wall-clock time per run
  - Total GPU hours (for all experiments including failed runs and hyperparameter search)
  - Estimated cloud cost (AWS/GCP/Azure equivalent)
  - Energy consumption in kWh if measurable (use tools like CodeCarbon, experiment-impact-tracker)
  - CO2 equivalent emissions (optional but increasingly expected)
- **Inference cost:**
  - Latency (ms per sample, p50/p95/p99)
  - Throughput (samples/second)
  - Memory footprint at inference
  - Model size (parameters, disk size)

### Step 9: Ensure Reproducibility
- **Code:**
  - Release all code used for experiments (training, evaluation, plotting)
  - Use a public repository (GitHub, GitLab) with a clear README
  - Include a requirements file (requirements.txt, environment.yml, pyproject.toml)
  - Provide setup instructions and verify they work on a clean environment
  - Include scripts to reproduce all tables and figures in the paper
  - Tag the exact code version used for the paper's results
  - License the code (MIT, Apache 2.0, or GPL — specify clearly)

- **Data:**
  - Release datasets or provide download scripts with checksums
  - If data cannot be shared (privacy, licensing): describe the data generation process in enough detail to recreate it, or provide synthetic/anonymized versions
  - Upload to a persistent repository (Zenodo, Figshare, Hugging Face) with a DOI
  - Include data documentation: datasheet (Gebru et al.) or data card

- **Models:**
  - Release trained model weights when feasible (Hugging Face, Zenodo)
  - Include model cards (Mitchell et al.) documenting: intended use, limitations, training data, evaluation results, ethical considerations

- **Experiment tracking:**
  - Use experiment tracking tools (Weights & Biases, MLflow, TensorBoard)
  - Log all hyperparameters, metrics, and system info automatically
  - Archive raw experiment logs alongside the paper

- **Containerization:**
  - Provide a Dockerfile or Singularity definition for full environment reproducibility
  - Pin all dependency versions (no floating versions)

### Step 10: Address Ethical Considerations
- **Dataset bias:** Analyze and report demographic biases in training data; evaluate model fairness across subgroups
- **Dual use:** Consider potential misuse of the method; discuss safeguards
- **Environmental impact:** Report compute costs and carbon footprint (see Step 8)
- **Privacy:** If using personal data, describe consent, anonymization, and compliance with regulations (GDPR, HIPAA)
- **Broader impact:** Include a broader impact statement discussing potential positive and negative societal effects
- Follow venue-specific ethics guidelines (NeurIPS checklist, ACM Code of Ethics)

### Step 11: Write the Paper
- Follow the standard CS paper structure:
  1. Abstract (problem, method, key results, impact)
  2. Introduction (motivation, problem, contribution summary, paper outline)
  3. Related Work (organized thematically, positioning the contribution)
  4. Method (formal description, pseudocode, complexity analysis)
  5. Experimental Setup (datasets, baselines, metrics, implementation details)
  6. Results (main results, ablations, analysis)
  7. Discussion / Limitations (failure cases, assumptions, scope)
  8. Conclusion (summary, future work)
  9. References
  10. Appendix (additional results, proofs, implementation details)
- Key writing principles:
  - Lead with the main result — do not bury findings
  - Every claim must be supported by evidence (experiment, proof, or citation)
  - Distinguish contributions from prior work clearly
  - Discuss negative results and failure cases honestly
  - Present limitations before or alongside strengths

## Checklist: Computational Study Reporting

### Problem and Method
1. State the problem definition formally with input/output specification
2. Describe the proposed method with sufficient detail for reimplementation
3. Provide pseudocode or algorithmic description for novel components
4. State the computational complexity (time and space)
5. Clearly articulate the novel contribution vs prior work

### Experimental Design
6. List all datasets with versions, sizes, splits, and sources
7. List all baselines with implementation sources and versions
8. Define all evaluation metrics with precise formulas or library references
9. Describe the hyperparameter search procedure and budget
10. Report the number of random seeds and repetitions
11. Report the selected hyperparameters for all methods

### Results
12. Report mean and standard deviation (or SE) across runs for all metrics
13. Include statistical significance tests with p-values and effect sizes
14. Apply multiple comparison correction when testing against multiple baselines
15. Present ablation study results isolating each contribution
16. Include both tables (for precise numbers) and figures (for trends)
17. Discuss failure cases and when the method does not work

### Computational Resources
18. Report GPU/CPU model, count, and memory
19. Report training time (wall-clock and GPU-hours)
20. Report inference latency and throughput
21. Report model size (parameters and disk)
22. Report energy consumption or estimated carbon footprint

### Reproducibility
23. Release code with a clear README and license
24. Provide a requirements/environment specification
25. Release or describe datasets with download instructions
26. Provide scripts to reproduce all main results, tables, and figures
27. Release trained model weights (if feasible)
28. Use experiment tracking and archive logs

### Ethics and Broader Impact
29. Analyze dataset bias and model fairness across subgroups
30. Discuss potential misuse and safeguards
31. Discuss broader societal impact (positive and negative)
32. Comply with venue-specific ethics requirements (e.g., NeurIPS checklist)

## References
- Bouthillier X, Varoquaux G. Survey of machine-learning experimental methods at NeurIPS2019 and ICLR2020. 2020. arXiv:2012.00190
- Dodge J, Ilharco G, Schwartz R, et al. Fine-Tuning Pretrained Language Models: Weight Initializations, Data Orders, and Early Stopping. 2020. arXiv:2002.06305
- Pineau J, Vincent-Lamarre P, Sinha K, et al. Improving Reproducibility in Machine Learning Research (A Report from the NeurIPS 2019 Reproducibility Program). JMLR. 2021;22(164):1-20
- Gebru T, Morgenstern J, Vecchione B, et al. Datasheets for Datasets. Communications of the ACM. 2021;64(12):86-92
- Mitchell M, Wu S, Zaldivar A, et al. Model Cards for Model Reporting. In Proc. FAT* 2019;220-229
- Henderson P, Islam R, Bachman P, et al. Deep Reinforcement Learning that Matters. In Proc. AAAI 2018
- Nadeau C, Bengio Y. Inference for the Generalization Error. Machine Learning. 2003;52:239-281
- Demsar J. Statistical Comparisons of Classifiers over Multiple Data Sets. JMLR. 2006;7:1-30
- Strubell E, Ganesh A, McCallum A. Energy and Policy Considerations for Deep Learning in NLP. In Proc. ACL 2019;3645-3650
- ACM. Artifact Review and Badging — Version 1.1. 2020. Available from: acm.org/publications/policies/artifact-review-and-badging-current

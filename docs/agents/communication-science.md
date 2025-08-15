# Communication Science Domain Knowledge for AI Agents

## 🎯 Core Directive: Knowledge Application

This document is not a passive library. It is an **active instruction set**. When a user's request involves communication science, you **must** use this document to:
1.  **Identify** the relevant theoretical framework and methodology.
2.  **Apply** the specific application guidelines and quality checklists.
3.  **Integrate** the disciplinary concepts and terminology into your response.

---

## 📚 Section 1: Theoretical Foundations & Application

### 1.1. Core Media & Audience Theories

| Theory | Core Concept | AI Application Guideline (When to use it) |
| :--- | :--- | :--- |
| **Agenda-Setting** | Media tells us *what* to think about. | Use when user asks **"How does media coverage affect public perception of an issue's importance?"** or wants to analyze the relationship between media mentions and public opinion data. |
| **Framing Theory** | Media tells us *how* to think about an issue. | Use when user asks **"How is an issue being portrayed in the news?"** or wants to perform content analysis to identify dominant frames (e.g., "economic" vs. "social" frame). |
| **Cultivation Theory**| Long-term media exposure shapes worldview. | Use when user asks about the **long-term effects of media consumption** (e.g., "Does watching crime dramas increase fear of crime?"). Requires longitudinal or cross-sectional survey data. |
| **Uses & Gratifications**| Audience actively seeks media to satisfy needs. | Use when user asks **"Why do people use certain media?"** (e.g., "Why do young people use TikTok for news?"). Best investigated with surveys or interviews. |
| **Selective Exposure** | People prefer information that confirms their beliefs. | Use when user asks about **echo chambers, filter bubbles, or partisan media consumption**. Analyze user data for diversity of sources or design studies to test information choice. |

### 1.2. Digital & Network Theories

| Theory | Core Concept | AI Application Guideline (When to use it) |
| :--- | :--- | :--- |
| **Affordance Theory** | Technology's features enable/constrain user actions. | Use when user asks **"How does a platform's design influence communication?"** (e.g., "How does Twitter's character limit affect political discourse?"). Combine with feature analysis and user behavior data. |
| **Network Society** | Society is structured around information networks. | Use when user wants to conduct **social network analysis** to understand information flow, identify influencers, or map communication structures. |
| **Digital Divide** | Inequality in technology access and skills. | Use when user's research involves **socio-economic factors, access, or digital literacy**. Ensure analysis accounts for these potential disparities. |

---

## 🔬 Section 2: Research Methodologies & Quality Checklists

### 2.1. Quantitative Approaches

| Method | Description | AI Quality Checklist (Before executing) |
| :--- | :--- | :--- |
| **Content Analysis** | Systematically quantifying communication content. | 1. **Clear Unit of Analysis?** (e.g., news article, tweet, TV scene). <br> 2. **Coding Scheme Defined?** (List of variables and their definitions). <br> 3. **Inter-coder Reliability Plan?** (Plan for ensuring multiple coders agree, e.g., Krippendorff's Alpha). |
| **Survey Research** | Collecting data via questionnaires. | 1. **Sampling Strategy Clear?** (e.g., random, convenience, stratified). <br> 2. **Constructs Validated?** (Are we using established scales?). <br> 3. **Ethical Considerations Addressed?** (Informed consent, data privacy). |
| **Network Analysis** | Analyzing relationship patterns and structures. | 1. **Nodes Defined?** (Who/what are the actors?). <br> 2. **Edges Defined?** (What constitutes a tie/link?). <br> 3. **Network Type Specified?** (Directed/undirected, weighted/unweighted). |

### 2.2. Qualitative Approaches

| Method | Description | AI Quality Checklist (Before executing) |
| :--- | :--- | :--- |
| **In-Depth Interviews** | Exploring individual perspectives. | 1. **Interview Protocol Ready?** (List of open-ended questions). <br> 2. **Sampling Rationale?** (Why were these participants chosen?). <br> 3. **Analysis Plan?** (e.g., Thematic Analysis, Grounded Theory). |
| **Discourse Analysis** | Analyzing language use and meaning construction. | 1. **Text Corpus Defined?** (What specific texts will be analyzed?). <br> 2. **Analytical Lens Clear?** (e.g., Critical Discourse Analysis, Foucauldian). <br> 3. **Context Understood?** (What is the socio-historical context of the discourse?). |

---

## 📊 Section 3: Statistical Analysis & Reporting Standards

### 3.1. Concept-to-Operation Mapping

| If the Research Goal is to... | ...the Statistical Approach should be: | Example Python Libraries |
| :--- | :--- | :--- |
| **Compare two group means** | Independent Samples T-test | `scipy.stats.ttest_ind` |
| **Compare 3+ group means** | ANOVA (Analysis of Variance) | `scipy.stats.f_oneway` |
| **Test the relationship between two categorical variables** | Chi-Square Test of Independence | `scipy.stats.chi2_contingency`|
| **Predict a continuous outcome from one or more predictors** | Linear Regression | `statsmodels.formula.api.ols` |
| **Predict a binary outcome (e.g., yes/no)** | Logistic Regression | `statsmodels.formula.api.logit` |
| **Assess the relationship between two continuous variables** | Pearson Correlation | `scipy.stats.pearsonr` |

### 3.2. APA 7th Edition Reporting Standards (Mandatory)

You **must** format statistical results according to APA 7 style.

| Test | APA 7 Reporting Format | Example |
| :--- | :--- | :--- |
| **t-test** | `t(df) = value, p = .xxx, d = .xx` | `t(98) = 2.54, p = .013, d = 0.51` |
| **ANOVA** | `F(df_between, df_within) = value, p = .xxx, η² = .xx` | `F(2, 147) = 5.88, p = .003, η² = .07` |
| **Chi-Square** | `χ²(df, N = sample_size) = value, p = .xxx` | `χ²(1, N = 150) = 4.12, p = .042` |
| **Correlation**| `r(df) = .xx, p = .xxx` | `r(98) = .35, p < .001` |
| **Regression** | `β = .xx, t(df) = value, p = .xxx` | `β = .45, t(97) = 4.91, p < .001` |

*Note: Always report exact p-values unless p < .001. Report effect sizes (Cohen's d, η², etc.) to indicate practical significance.*

---


### When Conducting Literature Reviews
- Focus on communication science databases first
- Include both theoretical and empirical studies
- Consider methodological diversity
- Identify theoretical frameworks explicitly
- Note sample characteristics and generalizability

### When Analyzing Data
- Report effect sizes and confidence intervals
- Consider multiple comparison corrections
- Address assumptions of statistical tests
- Interpret practical vs. statistical significance
- Discuss limitations transparently

### When Writing Reports
- Follow APA style meticulously
- Integrate theory and findings clearly
- Discuss implications for theory and practice
- Address limitations and future research
- Consider ethical implications

### When Designing Studies
- Ground in communication theory
- Consider multiple methodological approaches
- Plan for appropriate sample sizes
- Address ethical considerations early
- Consider replication and transparency

## 📝 Section 4: Academic Writing & Structure

### 4.1. Standard Manuscript Structure (IMRaD)

When asked to write or structure a paper, follow the IMRaD format:

1.  **Introduction**:
    *   **Hook**: Start with a broad statement about the topic's importance.
    *   **Literature Review**: Briefly summarize what is known, citing key works.
    *   **Gap**: Clearly state the problem or what is missing in the literature.
    *   **Resolution**: State your research question/hypothesis and briefly outline the study.
2.  **Method**:
    *   **Participants/Sample**: Describe who/what was studied.
    *   **Procedure**: Detail the step-by-step process of the study.
    *   **Measures**: Define how each variable was operationalized and measured.
3.  **Results**:
    *   **Present Findings**: Report the results of the statistical analyses objectively, without interpretation.
    *   **Refer to Tables/Figures**: Direct the reader to visualizations.
4.  **Discussion**:
    *   **Interpret Findings**: Explain what the results mean.
    *   **Connect to Literature**: How do the findings confirm, contradict, or extend previous research?
    *   **Implications**: What are the theoretical and practical implications?
    *   **Limitations**: Acknowledge the study's weaknesses.
    -   **Future Research**: Suggest directions for future studies.

### 4.2. Key Journals for Style Benchmarking

When unsure of tone or style, emulate the writing in these top-tier journals:
- *Journal of Communication*
- *Human Communication Research*
- *Journal of Computer-Mediated Communication*
- *New Media & Society*
- *Political Communication*

# OSA 2023 Transparency Readiness Framework
**Phase 1 output — Policy Analysis**
Project: Measuring Compliance and Effectiveness of the Online Safety Act 2023
Author: Frank Okoro | CIS4517 Research and Development Project

---

## 1. Purpose and Reframing Note

This framework does **not** measure live legal compliance with the Online Safety Act 2023's
transparency reporting duty (ss.77–78). As of September 2026, that duty is not yet enforceable:
Ofcom published its register of categorised services on 10 July 2026, and the first formal
transparency notices and reports are not expected until 2027.

Instead, this framework measures **transparency readiness**: the gap between what UK-regulated
platforms currently disclose *voluntarily* and what Ofcom's own published guidance indicates it
will require once the regime becomes enforceable. This is a forward-looking, evidence-based gap
analysis rather than a retrospective compliance audit — and it is arguably more useful, since it
identifies exposure before enforcement begins rather than after.

---

## 2. Legal and Regulatory Basis

| Source | Role in this framework |
|---|---|
| OSA 2023, s.77 | Establishes the duty to produce annual transparency reports (categorised services only) |
| OSA 2023, s.78 | Requires Ofcom to produce guidance on transparency reporting |
| OSA 2023, Schedule 8, Part 1 | Lists the 20 matters Ofcom may require information on, for user-to-user services (all 5 target platforms fall here) |
| Ofcom, *Final Transparency Guidance* (21 July 2025) | Explains the principles (relevance, appropriateness, proportionality) and factors Ofcom will use to decide what to request |
| Ofcom, *Register of Categorised Services* (10 July 2026) | Confirms which platforms will eventually be subject to the duty |

All five target platforms (Facebook, Instagram, YouTube, TikTok, X) are large user-to-user
services and are expected to meet Category 1 thresholds, so **Schedule 8 Part 1** (not Part 2,
which covers search) is the relevant obligation list.

---

## 3. Thematic Clustering of Schedule 8 Obligations

Schedule 8's 20 matters have been grouped into 8 practically-scoreable clusters. Each cluster
maps to a category of disclosure that is realistically observable in a platform's current,
voluntary transparency materials.

| # | Cluster | Schedule 8 items covered | What "good" currently looks like |
|---|---|---|---|
| 1 | **Content Incidence & Prevalence** | 1, 3 | Published prevalence/violative-view-rate metrics; user exposure estimates |
| 2 | **Moderation Systems & Enforcement** | 6, 8, 15, 16 | Detection method breakdown (human/automated), takedown speed, risk assessment process description |
| 3 | **Algorithmic & Recommender Transparency** | 2, 9 | Disclosure of how ranking/recommendation affects visibility of harmful content |
| 4 | **User Reporting & Appeals** | 5 | Reporting flow description, appeal outcome statistics |
| 5 | **Child Safety Measures** | 7, 18 | Child-specific safety features, evidence of effectiveness |
| 6 | **Terms of Service Clarity** | 4, 13 | Accessibility/clarity of ToS, enforcement consistency statements |
| 7 | **CSEA Reporting & Law Enforcement Cooperation** | 11, 12, 14, 17 | NCMEC/equivalent reporting arrangements, identity verification measures, law enforcement cooperation statements |
| 8 | **Media Literacy & Other Safety Measures** | 19, 20 | User education initiatives, other voluntary safety commitments |

---

## 4. Readiness Scoring Rubric

Each cluster is scored **0–4** per platform, based on what is publicly available in that
platform's current transparency materials (Transparency Center, Community Guidelines
Enforcement Report, etc.) as of the data collection window.

| Score | Label | Description |
|---|---|---|
| 0 | **Absent** | No disclosure found relating to this cluster |
| 1 | **Minimal** | Vague or high-level mention only; not measurable or verifiable |
| 2 | **Partial** | Some quantified data provided, but incomplete, inconsistent, or lacking methodology detail |
| 3 | **Substantial** | Quantified, methodologically-described disclosure covering most sub-items in the cluster |
| 4 | **Comprehensive** | Full, regularly-updated, methodologically transparent disclosure covering all sub-items, broadly consistent with what Ofcom's guidance indicates it will request |

**Platform Readiness Score** = mean of the 8 cluster scores (0–32 raw, expressed as a % of 32 for
cross-platform comparability).

**Cross-referencing step (per your original methodology):** each self-reported score is checked
against independent sources — Ofcom publications, the DSA Transparency Database (for the same
platform's EU-facing disclosures, where comparable), and independent research — to flag any
gap between what a platform claims and what is independently verifiable. This produces a
secondary "verification confidence" flag (Verified / Partially Verified / Unverified) per
cluster, preserving the triangulation logic from your CW1 methodology.

---

## 5. Data Sources per Platform (Phase 2 scraping targets)

| Platform | Primary voluntary disclosure source |
|---|---|
| Facebook / Instagram (Meta) | Meta Transparency Center (transparency.meta.com) |
| YouTube | YouTube Community Guidelines Enforcement Report (transparencyreport.google.com) |
| TikTok | TikTok Community Guidelines Enforcement Report |
| X | X Transparency Reports (transparency.x.com) |

Secondary/cross-reference sources: Ofcom publications (ofcom.org.uk), DSA Transparency Database
(via `dsa-tdb` package), GOV.UK / UK Parliament publications.

---

## 6. What Changed from the CW1 Proposal

- **Objective 3** ("compliance rating system... against OSA regulations") → now a **readiness
  rating system** scoring current voluntary disclosure against Ofcom's stated future
  requirements.
- **Objective 5** ("critically examine effectiveness of transparency reporting as enforcement
  mechanism") → reframed to critically examine **platform exposure and preparedness** ahead of
  enforcement, and what the readiness gap implies for Ofcom's enforcement timeline.
- Methodology, data sources, and tooling (BeautifulSoup, Selenium, Pandas, DSA Transparency
  Database) are unchanged — only the interpretive frame and scoring target have shifted.

---

*Next step: finalise cluster weightings (equal-weighted vs. risk-weighted) and build the Python
scoring rubric implementation in `analysis/`.*

"""
Grant Genie — Fixed Labeled Pairs Generator
============================================
Grants: Real UKRI data (already fetched in grants.csv)
Researchers: Real UKRI researchers (already fetched in researchers.csv)
Labels: Properly distributed Good/Average/Bad Fit

Run: python fix_labels.py
"""

import pandas as pd
import random
import os

# Load already fetched real data
grants_df = pd.read_csv("grants.csv")
researchers_df = pd.read_csv("researchers.csv")

print(f"✅ Loaded {len(grants_df)} real grants")
print(f"✅ Loaded {len(researchers_df)} real researchers")

# Research domain keywords
DOMAIN_KEYWORDS = {
    "Artificial Intelligence": [
        "machine learning",
        "deep learning",
        "neural",
        "artificial intelligence",
        "computer vision",
        "natural language",
        "nlp",
        "reinforcement",
        "classification",
        "prediction",
        "algorithm",
        "data mining",
        "pattern recognition",
        "ai",
    ],
    "Climate & Environment": [
        "climate",
        "carbon",
        "greenhouse",
        "sustainability",
        "renewable",
        "net zero",
        "environmental",
        "ecology",
        "biodiversity",
        "atmospheric",
        "emissions",
        "global warming",
        "flood",
        "ocean",
        "deforestation",
        "pollution",
    ],
    "Biomedical & Health": [
        "cancer",
        "diabetes",
        "drug",
        "clinical",
        "biomedical",
        "genomic",
        "protein",
        "disease",
        "therapy",
        "vaccine",
        "patient",
        "health",
        "mental health",
        "surgery",
        "imaging",
        "biomarker",
        "pharmaceutical",
        "medical",
    ],
    "Data Science & Statistics": [
        "data science",
        "statistical",
        "big data",
        "analytics",
        "regression",
        "bayesian",
        "modelling",
        "simulation",
        "dataset",
        "epidemiology",
        "survey",
        "sampling",
        "quantitative",
        "computational",
    ],
    "Social Sciences": [
        "social",
        "inequality",
        "education",
        "poverty",
        "policy",
        "community",
        "qualitative",
        "gender",
        "economic",
        "welfare",
        "migration",
        "employment",
        "housing",
        "public",
        "cultural",
        "political",
        "society",
    ],
    "Cybersecurity & Computing": [
        "cybersecurity",
        "security",
        "encryption",
        "network",
        "privacy",
        "blockchain",
        "distributed",
        "cloud",
        "software",
        "hardware",
        "internet of things",
        "cryptography",
        "authentication",
        "cyber",
        "digital",
    ],
    "Engineering & Physics": [
        "engineering",
        "materials",
        "nanotechnology",
        "quantum",
        "photonics",
        "semiconductor",
        "robotics",
        "manufacturing",
        "aerospace",
        "fluid",
        "thermal",
        "mechanical",
        "structural",
        "signal",
        "physics",
        "optical",
    ],
    "Biology & Life Sciences": [
        "biology",
        "genetics",
        "cell",
        "molecular",
        "microbiology",
        "neuroscience",
        "evolution",
        "plant",
        "agriculture",
        "food",
        "bacteria",
        "virus",
        "dna",
        "rna",
        "stem cell",
        "tissue",
        "organism",
        "species",
    ],
}

DOMAINS = list(DOMAIN_KEYWORDS.keys())


def detect_domain(text):
    """Detect domain of a grant from its text."""
    text_lower = text.lower()
    scores = {
        d: sum(1 for kw in kws if kw in text_lower)
        for d, kws in DOMAIN_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else random.choice(DOMAINS)


def compute_overlap(keywords, grant_text):
    """Compute keyword overlap ratio."""
    text_lower = grant_text.lower()
    matches = sum(1 for kw in keywords if kw in text_lower)
    return matches / len(keywords) if keywords else 0.0


# Pre-compute grant domains
print("\n🔍 Detecting grant domains...")
grants_list = grants_df.to_dict("records")
for g in grants_list:
    g["domain"] = detect_domain(f"{g['title']} {g['abstract']}")

# Assign domains to researchers (cycling through all 8)
researchers_list = researchers_df.to_dict("records")
for i, r in enumerate(researchers_list):
    r["domain"] = DOMAINS[i % len(DOMAINS)]
    r["keywords"] = DOMAIN_KEYWORDS[r["domain"]]

# Separate grants by domain
domain_grants = {d: [] for d in DOMAINS}
for g in grants_list:
    domain_grants[g["domain"]].append(g)

# Create exactly 300 pairs with 100 each label
TARGET_EACH = 100  # 100 Good + 100 Average + 100 Bad = 300 total

good_pairs = []
average_pairs = []
bad_pairs = []

pair_id = 1
random.shuffle(grants_list)

print("🏷️  Creating balanced labeled pairs...")

for researcher in researchers_list:
    r_domain = researcher["domain"]
    r_keywords = researcher["keywords"]

    # Same domain grants - likely Good Fit
    same_domain = domain_grants.get(r_domain, [])
    # Different domain grants - likely Bad Fit
    other_domains = [d for d in DOMAINS if d != r_domain]
    diff_domain = []
    for d in other_domains:
        diff_domain.extend(domain_grants.get(d, []))

    for grant in same_domain:
        grant_text = f"{grant['title']} {grant['abstract']}"
        overlap = compute_overlap(r_keywords, grant_text)
        label = (
            "Good Fit"
            if overlap >= 0.33
            else ("Average Fit" if overlap >= 0.16 else "Bad Fit")
        )

        pair = {
            "pair_id": f"PAIR_{pair_id:04d}",
            "researcher_id": researcher["researcher_id"],
            "researcher_name": researcher["full_name"],
            "researcher_domain": r_domain,
            "researcher_keywords": ", ".join(r_keywords[:6]),
            "researcher_source": researcher["source_url"],
            "grant_id": grant["grant_id"],
            "grant_title": grant["title"],
            "grant_abstract": grant["abstract"][:400],
            "grant_funder": grant["funder"],
            "grant_amount_gbp": grant["amount_gbp"],
            "grant_domain": grant["domain"],
            "grant_source": grant["source_url"],
            "overlap_score": round(overlap, 4),
            "label": label,
        }
        pair_id += 1

        if label == "Good Fit" and len(good_pairs) < TARGET_EACH:
            good_pairs.append(pair)
        elif label == "Average Fit" and len(average_pairs) < TARGET_EACH:
            average_pairs.append(pair)
        elif label == "Bad Fit" and len(bad_pairs) < TARGET_EACH:
            bad_pairs.append(pair)

    for grant in diff_domain:
        if (
            len(good_pairs) >= TARGET_EACH
            and len(average_pairs) >= TARGET_EACH
            and len(bad_pairs) >= TARGET_EACH
        ):
            break
        grant_text = f"{grant['title']} {grant['abstract']}"
        overlap = compute_overlap(r_keywords, grant_text)
        label = (
            "Good Fit"
            if overlap >= 0.33
            else ("Average Fit" if overlap >= 0.16 else "Bad Fit")
        )

        pair = {
            "pair_id": f"PAIR_{pair_id:04d}",
            "researcher_id": researcher["researcher_id"],
            "researcher_name": researcher["full_name"],
            "researcher_domain": r_domain,
            "researcher_keywords": ", ".join(r_keywords[:6]),
            "researcher_source": researcher["source_url"],
            "grant_id": grant["grant_id"],
            "grant_title": grant["title"],
            "grant_abstract": grant["abstract"][:400],
            "grant_funder": grant["funder"],
            "grant_amount_gbp": grant["amount_gbp"],
            "grant_domain": grant["domain"],
            "grant_source": grant["source_url"],
            "overlap_score": round(overlap, 4),
            "label": label,
        }
        pair_id += 1

        if label == "Good Fit" and len(good_pairs) < TARGET_EACH:
            good_pairs.append(pair)
        elif label == "Average Fit" and len(average_pairs) < TARGET_EACH:
            average_pairs.append(pair)
        elif label == "Bad_pairs" and len(bad_pairs) < TARGET_EACH:
            bad_pairs.append(pair)

# If still not enough, force fill with score-based assignment
print("⚙️  Balancing distribution...")

all_computed = []
for researcher in researchers_list:
    for grant in grants_list:
        grant_text = f"{grant['title']} {grant['abstract']}"
        overlap = compute_overlap(researcher["keywords"], grant_text)
        all_computed.append((researcher, grant, overlap))

# Sort by overlap descending
all_computed.sort(key=lambda x: x[2], reverse=True)

total = len(all_computed)

# Top 33% - Good Fit
for researcher, grant, overlap in all_computed[: total // 3]:
    if len(good_pairs) >= TARGET_EACH:
        break
    # Check not already added
    existing_ids = {p["grant_id"] + p["researcher_id"] for p in good_pairs}
    key = grant["grant_id"] + researcher["researcher_id"]
    if key not in existing_ids:
        good_pairs.append(
            {
                "pair_id": f"PAIR_{pair_id:04d}",
                "researcher_id": researcher["researcher_id"],
                "researcher_name": researcher["full_name"],
                "researcher_domain": researcher["domain"],
                "researcher_keywords": ", ".join(researcher["keywords"][:6]),
                "researcher_source": researcher["source_url"],
                "grant_id": grant["grant_id"],
                "grant_title": grant["title"],
                "grant_abstract": grant["abstract"][:400],
                "grant_funder": grant["funder"],
                "grant_amount_gbp": grant["amount_gbp"],
                "grant_domain": grant["domain"],
                "grant_source": grant["source_url"],
                "overlap_score": round(overlap, 4),
                "label": "Good Fit",
            }
        )
        pair_id += 1

# Middle 33% - Average Fit
for researcher, grant, overlap in all_computed[total // 3 : 2 * total // 3]:
    if len(average_pairs) >= TARGET_EACH:
        break
    existing_ids = {p["grant_id"] + p["researcher_id"] for p in average_pairs}
    key = grant["grant_id"] + researcher["researcher_id"]
    if key not in existing_ids:
        average_pairs.append(
            {
                "pair_id": f"PAIR_{pair_id:04d}",
                "researcher_id": researcher["researcher_id"],
                "researcher_name": researcher["full_name"],
                "researcher_domain": researcher["domain"],
                "researcher_keywords": ", ".join(researcher["keywords"][:6]),
                "researcher_source": researcher["source_url"],
                "grant_id": grant["grant_id"],
                "grant_title": grant["title"],
                "grant_abstract": grant["abstract"][:400],
                "grant_funder": grant["funder"],
                "grant_amount_gbp": grant["amount_gbp"],
                "grant_domain": grant["domain"],
                "grant_source": grant["source_url"],
                "overlap_score": round(overlap, 4),
                "label": "Average Fit",
            }
        )
        pair_id += 1

# Bottom 33% - Bad Fit
for researcher, grant, overlap in all_computed[2 * total // 3 :]:
    if len(bad_pairs) >= TARGET_EACH:
        break
    existing_ids = {p["grant_id"] + p["researcher_id"] for p in bad_pairs}
    key = grant["grant_id"] + researcher["researcher_id"]
    if key not in existing_ids:
        bad_pairs.append(
            {
                "pair_id": f"PAIR_{pair_id:04d}",
                "researcher_id": researcher["researcher_id"],
                "researcher_name": researcher["full_name"],
                "researcher_domain": researcher["domain"],
                "researcher_keywords": ", ".join(researcher["keywords"][:6]),
                "researcher_source": researcher["source_url"],
                "grant_id": grant["grant_id"],
                "grant_title": grant["title"],
                "grant_abstract": grant["abstract"][:400],
                "grant_funder": grant["funder"],
                "grant_amount_gbp": grant["amount_gbp"],
                "grant_domain": grant["domain"],
                "grant_source": grant["source_url"],
                "overlap_score": round(overlap, 4),
                "label": "Bad Fit",
            }
        )
        pair_id += 1

# Combine and save
all_pairs = (
    good_pairs[:TARGET_EACH] + average_pairs[:TARGET_EACH] + bad_pairs[:TARGET_EACH]
)
random.shuffle(all_pairs)

pairs_df = pd.DataFrame(all_pairs)
pairs_df.to_csv("labeled_pairs.csv", index=False, encoding="utf-8")

# Summary
counts = pairs_df["label"].value_counts()
print("\n" + "═" * 50)
print("  ✅  LABELED PAIRS FIXED!")
print("═" * 50)
print(f"  Total pairs     : {len(pairs_df)}")
print(f"\n  Label Distribution:")
for label in ["Good Fit", "Average Fit", "Bad Fit"]:
    count = counts.get(label, 0)
    pct = round(count / len(pairs_df) * 100, 1)
    bar = "█" * (count // 5)
    print(f"    {label:<14} {count:>3} ({pct:>5}%)  {bar}")
print(f"\n  💾  Saved → labeled_pairs.csv")
print(f"  Data: Real UKRI grants + Real UKRI researchers")
print("═" * 50)

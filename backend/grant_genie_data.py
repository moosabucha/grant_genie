"""
Grant Genie — All in One Script
================================
Fetches real grants + real researchers from UKRI
Creates 300 balanced labeled pairs (100 Good / 100 Average / 100 Bad)

Run: python grant_genie_data.py
"""

import requests
import pandas as pd
import random
from tqdm import tqdm
import time

BASE_URL = "https://gtr.ukri.org/gtr/api"
HEADERS  = {"Accept": "application/json"}

DOMAIN_KEYWORDS = {
    "Artificial Intelligence": [
        "machine learning", "deep learning", "neural", "artificial intelligence",
        "computer vision", "natural language", "nlp", "reinforcement", "classification",
        "prediction", "algorithm", "data mining", "pattern recognition", "ai"
    ],
    "Climate & Environment": [
        "climate", "carbon", "greenhouse", "sustainability", "renewable",
        "net zero", "environmental", "ecology", "biodiversity", "atmospheric",
        "emissions", "global warming", "flood", "ocean", "pollution"
    ],
    "Biomedical & Health": [
        "cancer", "diabetes", "drug", "clinical", "biomedical", "genomic",
        "protein", "disease", "therapy", "vaccine", "patient", "health",
        "mental health", "surgery", "imaging", "biomarker", "pharmaceutical", "medical"
    ],
    "Data Science & Statistics": [
        "data science", "statistical", "big data", "analytics", "regression",
        "bayesian", "modelling", "simulation", "dataset", "epidemiology",
        "survey", "sampling", "quantitative", "computational"
    ],
    "Social Sciences": [
        "social", "inequality", "education", "poverty", "policy", "community",
        "qualitative", "gender", "economic", "welfare", "migration", "employment",
        "housing", "public", "cultural", "political", "society"
    ],
    "Cybersecurity & Computing": [
        "cybersecurity", "security", "encryption", "network", "privacy", "blockchain",
        "distributed", "cloud", "software", "hardware", "internet of things",
        "cryptography", "authentication", "cyber", "digital"
    ],
    "Engineering & Physics": [
        "engineering", "materials", "nanotechnology", "quantum", "photonics",
        "semiconductor", "robotics", "manufacturing", "aerospace", "fluid",
        "thermal", "mechanical", "structural", "signal", "physics", "optical"
    ],
    "Biology & Life Sciences": [
        "biology", "genetics", "cell", "molecular", "microbiology", "neuroscience",
        "evolution", "plant", "agriculture", "food", "bacteria", "virus",
        "dna", "rna", "stem cell", "tissue", "organism", "species"
    ],
}
DOMAINS = list(DOMAIN_KEYWORDS.keys())


def safe_get(url, params=None, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(3)
            else:
                return None


def fetch_grants(target=350):
    print("\n═══════════════════════════════════════")
    print("  STEP 1: Fetching Real Grants (UKRI)")
    print("═══════════════════════════════════════")
    grants, seen, page = [], set(), 1
    with tqdm(total=target, desc="  Grants") as pbar:
        while len(grants) < target:
            data = safe_get(f"{BASE_URL}/projects", params={"p": page, "s": 100})
            if not data:
                break
            if page == 1:
                print(f"\n  ✅ Connected! {data.get('totalSize',0):,} real grants available\n")
            for proj in data.get("project", []):
                gid      = proj.get("id", "")
                title    = proj.get("title", "").strip()
                abstract = proj.get("abstractText", "").strip()
                if gid in seen or not title or len(abstract) < 80:
                    continue
                seen.add(gid)
                fund   = proj.get("fund", {})
                amount = 0
                start  = ""
                end    = ""
                if isinstance(fund, dict):
                    val = fund.get("valuePounds", {})
                    if isinstance(val, dict):
                        amount = val.get("amount", 0)
                    start = fund.get("start", "")[:10]
                    end   = fund.get("end", "")[:10]
                grants.append({
                    "grant_id"   : gid,
                    "title"      : title,
                    "abstract"   : abstract,
                    "funder"     : proj.get("grantCategory", "UKRI") or "UKRI",
                    "status"     : proj.get("status", ""),
                    "amount_gbp" : amount,
                    "start_date" : start,
                    "end_date"   : end,
                    "source_url" : f"https://gtr.ukri.org/projects?ref={gid}",
                })
                pbar.update(1)
                if len(grants) >= target:
                    break
            page += 1
            if page > data.get("totalPages", 1):
                break
            time.sleep(1)
    return grants


def fetch_researchers(target=50):
    print("\n═══════════════════════════════════════")
    print("  STEP 2: Fetching Real Researchers")
    print("═══════════════════════════════════════\n")
    researchers, seen, page = [], set(), 1
    with tqdm(total=target, desc="  Researchers") as pbar:
        while len(researchers) < target:
            data = safe_get(f"{BASE_URL}/persons", params={"p": page, "s": 100})
            if not data:
                break
            for person in data.get("person", []):
                pid   = person.get("id", "")
                fname = person.get("firstName", "").strip()
                lname = person.get("surname", "").strip()
                if pid in seen or not fname or not lname:
                    continue
                seen.add(pid)
                researchers.append({
                    "researcher_id": pid,
                    "full_name"    : f"{fname} {lname}",
                    "source_url"   : f"https://gtr.ukri.org/person/{pid}",
                })
                pbar.update(1)
                if len(researchers) >= target:
                    break
            page += 1
            if page > data.get("totalPages", 1):
                break
            time.sleep(1)
    return researchers


def detect_domain(text):
    t = text.lower()
    scores = {d: sum(1 for kw in kws if kw in t) for d, kws in DOMAIN_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else random.choice(DOMAINS)


def compute_overlap(keywords, grant_text):
    t = grant_text.lower()
    return sum(1 for kw in keywords if kw in t) / len(keywords) if keywords else 0.0


def create_balanced_pairs(grants_list, researchers_list, target_each=100):
    print("\n═══════════════════════════════════════")
    print("  STEP 3: Creating 300 Balanced Pairs")
    print("  100 Good + 100 Average + 100 Bad")
    print("═══════════════════════════════════════\n")

    # Assign domains to researchers
    for i, r in enumerate(researchers_list):
        r["domain"]   = DOMAINS[i % len(DOMAINS)]
        r["keywords"] = DOMAIN_KEYWORDS[r["domain"]]

    # Detect domain for each grant
    print("  Detecting grant domains...")
    for g in tqdm(grants_list, desc="  Domains"):
        g["domain"] = detect_domain(f"{g['title']} {g['abstract']}")

    # Compute ALL overlap scores
    print("\n  Computing all overlap scores...")
    all_pairs = []
    for r in researchers_list:
        for g in grants_list:
            text    = f"{g['title']} {g['abstract']}"
            overlap = compute_overlap(r["keywords"], text)
            all_pairs.append((r, g, overlap))

    # Sort by overlap
    all_pairs.sort(key=lambda x: x[2], reverse=True)
    total = len(all_pairs)

    # Top 33% = Good, Middle 33% = Average, Bottom 33% = Bad
    good_pool    = all_pairs[:total//3]
    average_pool = all_pairs[total//3: 2*total//3]
    bad_pool     = all_pairs[2*total//3:]

    random.shuffle(good_pool)
    random.shuffle(average_pool)
    random.shuffle(bad_pool)

    def make_pair(pid, r, g, overlap, label):
        return {
            "pair_id"            : f"PAIR_{pid:04d}",
            "researcher_id"      : r["researcher_id"],
            "researcher_name"    : r["full_name"],
            "researcher_domain"  : r["domain"],
            "researcher_keywords": ", ".join(r["keywords"][:6]),
            "researcher_source"  : r["source_url"],
            "grant_id"           : g["grant_id"],
            "grant_title"        : g["title"],
            "grant_abstract"     : g["abstract"][:400],
            "grant_funder"       : g["funder"],
            "grant_amount_gbp"   : g["amount_gbp"],
            "grant_domain"       : g["domain"],
            "grant_source"       : g["source_url"],
            "overlap_score"      : round(overlap, 4),
            "label"              : label,
        }

    pairs = []
    pid   = 1

    for r, g, overlap in good_pool[:target_each]:
        pairs.append(make_pair(pid, r, g, overlap, "Good Fit"))
        pid += 1

    for r, g, overlap in average_pool[:target_each]:
        pairs.append(make_pair(pid, r, g, overlap, "Average Fit"))
        pid += 1

    for r, g, overlap in bad_pool[:target_each]:
        pairs.append(make_pair(pid, r, g, overlap, "Bad Fit"))
        pid += 1

    random.shuffle(pairs)
    return pairs


# ══════════════════════════════════════
# MAIN
# ══════════════════════════════════════
if __name__ == "__main__":
    print("\n═══════════════════════════════════════")
    print("  GRANT GENIE — Real Data Collector")
    print("  Muhamad Moosa Bucha | P2962600")
    print("  Source: UKRI Gateway to Research")
    print("═══════════════════════════════════════")

    # Step 1: Grants
    raw_grants = fetch_grants(350)
    grants_df  = pd.DataFrame(raw_grants).drop_duplicates("grant_id")
    grants_df.to_csv("grants.csv", index=False)
    print(f"\n  💾 Saved {len(grants_df)} grants → grants.csv")

    # Step 2: Researchers
    raw_res    = fetch_researchers(50)
    res_df     = pd.DataFrame(raw_res).drop_duplicates("researcher_id")
    res_df.to_csv("researchers.csv", index=False)
    print(f"  💾 Saved {len(res_df)} researchers → researchers.csv")

    # Step 3: Balanced Pairs
    pairs      = create_balanced_pairs(
                    grants_df.to_dict("records"),
                    res_df.to_dict("records"),
                    target_each=100
                 )
    pairs_df   = pd.DataFrame(pairs)
    pairs_df.to_csv("labeled_pairs.csv", index=False)

    # Summary
    counts = pairs_df["label"].value_counts()
    print("\n═══════════════════════════════════════")
    print("  ✅  COMPLETE!")
    print("═══════════════════════════════════════")
    print(f"  Total pairs: {len(pairs_df)}")
    print(f"\n  Label Distribution:")
    for label in ["Good Fit", "Average Fit", "Bad Fit"]:
        count = counts.get(label, 0)
        pct   = round(count / len(pairs_df) * 100, 1)
        bar   = "█" * (count // 5)
        print(f"    {label:<14} {count:>3} ({pct}%)  {bar}")
    print(f"\n  💾 grants.csv")
    print(f"  💾 researchers.csv")
    print(f"  💾 labeled_pairs.csv")
    print("═══════════════════════════════════════\n")

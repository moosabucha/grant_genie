from algorithms.tfidf_matcher import TFIDFMatcher
from algorithms.rapidfuzz_matcher import RapidFuzzMatcher


class HybridMatcher:
    def __init__(self, tfidf_weight=0.6, rfuzz_weight=0.4):
        self.tfidf_weight = tfidf_weight
        self.rfuzz_weight = rfuzz_weight
        self.tfidf = TFIDFMatcher()
        self.rfuzz = RapidFuzzMatcher()

    def match(self, profile_text, grant_calls):
        tfidf_results = self.tfidf.match(profile_text, grant_calls)
        rfuzz_results = self.rfuzz.match(profile_text, grant_calls)

        tfidf_map = {r["id"]: r["score"] for r in tfidf_results}
        rfuzz_map = {r["id"]: r["score"] for r in rfuzz_results}

        results = []
        for grant in grant_calls:
            t_score = tfidf_map.get(grant["id"], 0)
            r_score = rfuzz_map.get(grant["id"], 0)
            hybrid_score = round(
                (t_score * self.tfidf_weight) + (r_score * self.rfuzz_weight), 1
            )
            tfidf_features = next(
                (
                    r["matched_features"]
                    for r in tfidf_results
                    if r["id"] == grant["id"]
                ),
                [],
            )

            results.append(
                {
                    **grant,
                    "score": hybrid_score,
                    "algorithm": "Hybrid (TF-IDF + RapidFuzz)",
                    "matched_features": tfidf_features,
                    "tfidf_score": t_score,
                    "rfuzz_score": r_score,
                }
            )

        return results

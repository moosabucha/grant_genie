from rapidfuzz import fuzz


class RapidFuzzMatcher:
    def match(self, profile_text, grant_calls):
        results = []

        for grant in grant_calls:
            grant_text = grant["text"] + " " + grant.get("eligibility", "")

            score_ratio = fuzz.token_set_ratio(profile_text, grant_text) / 100
            score = round(score_ratio * 100, 1)

            results.append(
                {
                    **grant,
                    "score": score,
                    "algorithm": "RapidFuzz",
                    "matched_features": self._get_matched_features(
                        profile_text, grant, score
                    ),
                }
            )

        return results

    def _get_matched_features(self, profile_text, grant, score):
        keywords = [
            "Artificial Intelligence",
            "Machine Learning",
            "Healthcare",
            "NLP",
            "Sustainability",
            "Early Career",
            "Postgraduate",
        ]
        matched = []
        for kw in keywords:
            ratio = fuzz.partial_ratio(kw.lower(), profile_text.lower())
            if ratio > 70:
                matched.append({"keyword": kw, "contribution": round(ratio * 0.15, 1)})
        return matched

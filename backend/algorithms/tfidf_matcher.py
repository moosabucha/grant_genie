from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFMatcher:
    def match(self, profile_text, grant_calls):
        results = []
        texts = [profile_text] + [
            g["text"] + " " + g.get("eligibility", "") for g in grant_calls
        ]

        vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        tfidf_matrix = vectorizer.fit_transform(texts)

        profile_vec = tfidf_matrix[0]
        grant_vecs = tfidf_matrix[1:]

        similarities = cosine_similarity(profile_vec, grant_vecs)[0]

        for i, grant in enumerate(grant_calls):
            score = round(similarities[i] * 100, 1)
            results.append(
                {
                    **grant,
                    "score": score,
                    "algorithm": "TF-IDF",
                    "matched_features": self._get_matched_features(
                        profile_text, grant, score
                    ),
                }
            )

        return results

    def _get_matched_features(self, profile_text, grant, score):
        profile_lower = profile_text.lower()
        grant_text_lower = (grant["text"] + grant.get("eligibility", "")).lower()

        keywords = [
            "artificial intelligence",
            "machine learning",
            "healthcare",
            "nlp",
            "sustainability",
            "early career",
            "postgraduate",
            "education",
        ]
        matched = []
        for kw in keywords:
            if kw in profile_lower and kw in grant_text_lower:
                matched.append(
                    {
                        "keyword": kw.title(),
                        "contribution": round(score / len(keywords), 1),
                    }
                )

        return matched

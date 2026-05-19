from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from utils.pdf_extractor import extract_text_from_pdf
from algorithms.tfidf_matcher import TFIDFMatcher
from algorithms.rapidfuzz_matcher import RapidFuzzMatcher
from algorithms.hybrid_matcher import HybridMatcher
from algorithms.evaluator import select_best_algorithm
from utils.chatgpt_feedback import generate_feedback
import os
import json

dashboard_bp = Blueprint("dashboard", __name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@dashboard_bp.route("/dashboard")
@login_required
def home():
    return render_template("dashboard.html", user=current_user)


@dashboard_bp.route("/match", methods=["POST"])
@login_required
def match_grants():
    research_text = request.form.get("research_summary", "")
    if "profile_pdf" in request.files:
        file = request.files["profile_pdf"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            pdf_text = extract_text_from_pdf(filepath)
            research_text = pdf_text + " " + research_text
    if not research_text.strip():
        flash("Please upload a PDF or enter your research summary.", "error")
        return redirect(url_for("dashboard.home"))
    grant_calls = load_sample_grants()
    tfidf = TFIDFMatcher()
    rfuzz = RapidFuzzMatcher()
    hybrid = HybridMatcher()
    tfidf_results = tfidf.match(research_text, grant_calls)
    rfuzz_results = rfuzz.match(research_text, grant_calls)
    hybrid_results = hybrid.match(research_text, grant_calls)
    best_algo, all_scores = select_best_algorithm(
        tfidf_results, rfuzz_results, hybrid_results
    )
    if best_algo == "tfidf":
        final_results = tfidf_results
    elif best_algo == "rapidfuzz":
        final_results = rfuzz_results
    else:
        final_results = hybrid_results
    final_results.sort(key=lambda x: x["score"], reverse=True)
    top_grants = [g for g in final_results if g["score"] >= 40]
    alt_pool = [g for g in final_results if g["score"] < 40]
    top_30_count = max(1, len(top_grants) // 3)
    for grant in top_grants[:top_30_count]:
        grant["feedback"] = generate_feedback(
            research_text, grant, is_alternative=False
        )
    for grant in alt_pool:
        grant["feedback"] = generate_feedback(research_text, grant, is_alternative=True)

    # Save results to the file for export
    export_data = {
        "top_grants": top_grants,
        "alt_pool": alt_pool,
        "best_algo": best_algo,
        "all_scores": all_scores,
    }
    try:
        with open("last_results.json", "w") as f:
            json.dump(export_data, f)
    except Exception as e:
        print(f"Could not save results: {e}")

    return render_template(
        "results.html",
        top_grants=top_grants,
        alt_pool=alt_pool,
        best_algo=best_algo,
        all_scores=all_scores,
        user=current_user,
    )


def load_sample_grants():
    import pandas as pd

    csv_path = os.path.join(os.getcwd(), "grants.csv")

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        grants = []
        for idx, row in df.iterrows():
            grants.append(
                {
                    "id": idx + 1,
                    "title": str(row.get("title", "")),
                    "body": str(row.get("funder", "UKRI")),
                    "deadline": (
                        "Open"
                        if str(row.get("end_date", "")) in ["nan", "", "None"]
                        else str(row.get("end_date", "Open"))
                    ),
                    "text": str(row.get("abstract", "")),
                    "eligibility": str(row.get("status", "")),
                    "source": str(row.get("source_url", "https://gtr.ukri.org")),
                }
            )
        return grants
    else:
        print("⚠️ grants.csv not found!")
        return []

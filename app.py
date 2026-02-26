from __future__ import annotations

import io
import json
import time
from typing import Any

import pandas as pd
import streamlit as st

from analysis import validate_input_df, build_insights_df, kpi_counts, top_action_items
from llm import generate_insights

st.set_page_config(page_title="AI Email Insights & Summarization", layout="wide")

st.title("AI Email Insights & Summarization Tool")
st.caption("Upload a CSV of emails → generate summaries, topics, urgency, sentiment, and action items + a simple dashboard.")


with st.sidebar:
    st.header("Settings")
    model = st.selectbox("LLM Model (OpenAI)", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"], index=0)
    batch_size = st.slider("Batch size (processing)", 1, 50, 10)
    st.markdown("---")
    st.subheader("CSV Format")
    st.code("email_id, received_at, sender, subject, body", language="text")
    st.markdown("Tip: If no `OPENAI_API_KEY` is set, the app uses an offline fallback (demo mode).")


st.markdown("### 1) Upload emails CSV")
uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

colA, colB = st.columns([1, 1])
with colA:
    st.markdown("Or use the sample dataset:")
    if st.button("Load sample_emails.csv"):
        uploaded = "SAMPLE"

def _load_sample() -> pd.DataFrame:
    return pd.read_csv("sample_emails.csv")

def _load_uploaded_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)

df: pd.DataFrame | None = None

if uploaded == "SAMPLE":
    df = _load_sample()
elif uploaded is not None:
    df = _load_uploaded_csv(uploaded)

if df is None:
    st.stop()

try:
    df = validate_input_df(df)
except Exception as e:
    st.error(str(e))
    st.stop()

st.success(f"Loaded {len(df):,} emails.")
st.dataframe(df.head(20), use_container_width=True)

st.markdown("### 2) Generate insights")
run = st.button("Run summarization + classification", type="primary")

if "results_df" not in st.session_state:
    st.session_state["results_df"] = None

if run:
    insights_rows: list[dict[str, Any]] = []
    progress = st.progress(0)
    status = st.empty()

    total = len(df)
    start_time = time.time()

    for i in range(0, total, batch_size):
        batch = df.iloc[i:i + batch_size]
        for _, row in batch.iterrows():
            subject = str(row["subject"])
            body = str(row["body"])

            try:
                ins = generate_insights(subject=subject, body=body, model=model)
                insights_rows.append(ins.model_dump())
            except Exception as e:
                # Keep going; record error row
                insights_rows.append({
                    "summary_bullets": [f"ERROR: {e}"],
                    "topic": "other",
                    "urgency": "low",
                    "sentiment": "neutral",
                    "action_items": [],
                    "entities": [],
                })

        done = min(i + batch_size, total)
        progress.progress(done / total)
        status.info(f"Processed {done}/{total} emails…")

    elapsed = time.time() - start_time
    status.success(f"Done. Processed {total} emails in {elapsed:.1f}s")

    results_df = build_insights_df(df, insights_rows)
    st.session_state["results_df"] = results_df

results_df = st.session_state.get("results_df")
if results_df is None:
    st.stop()

st.markdown("### 3) Dashboard")
c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Topics")
    st.dataframe(kpi_counts(results_df, "topic"), use_container_width=True, height=220)
with c2:
    st.subheader("Urgency")
    st.dataframe(kpi_counts(results_df, "urgency"), use_container_width=True, height=220)
with c3:
    st.subheader("Sentiment")
    st.dataframe(kpi_counts(results_df, "sentiment"), use_container_width=True, height=220)

st.subheader("Top Action Items")
st.dataframe(top_action_items(results_df, n=10), use_container_width=True)

st.markdown("### 4) Review results")
# Simple filters
f1, f2, f3 = st.columns(3)
topics = ["(all)"] + sorted(results_df["topic"].dropna().unique().tolist())
urgencies = ["(all)"] + sorted(results_df["urgency"].dropna().unique().tolist())
sentiments = ["(all)"] + sorted(results_df["sentiment"].dropna().unique().tolist())

with f1:
    topic_sel = st.selectbox("Filter topic", topics, index=0)
with f2:
    urg_sel = st.selectbox("Filter urgency", urgencies, index=0)
with f3:
    sent_sel = st.selectbox("Filter sentiment", sentiments, index=0)

filtered = results_df.copy()
if topic_sel != "(all)":
    filtered = filtered[filtered["topic"] == topic_sel]
if urg_sel != "(all)":
    filtered = filtered[filtered["urgency"] == urg_sel]
if sent_sel != "(all)":
    filtered = filtered[filtered["sentiment"] == sent_sel]

# Make bullets readable
def bullets_to_text(x):
    if isinstance(x, list):
        return "\n".join([f"- {b}" for b in x])
    return str(x)

def list_to_text(x):
    if isinstance(x, list):
        return "\n".join([f"- {b}" for b in x])
    return str(x)

show = filtered.copy()
show["summary_bullets"] = show["summary_bullets"].apply(bullets_to_text)
show["action_items"] = show["action_items"].apply(list_to_text)
show["entities"] = show["entities"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))

st.dataframe(
    show[["email_id", "received_at", "sender", "subject", "topic", "urgency", "sentiment", "summary_bullets", "action_items", "entities"]],
    use_container_width=True,
    height=420,
)

st.markdown("### 5) Export")
csv_bytes = show.to_csv(index=False).encode("utf-8")
st.download_button("Download results CSV", data=csv_bytes, file_name="email_insights_results.csv", mime="text/csv")

jsonl_buf = io.StringIO()
for _, r in filtered.iterrows():
    record = r.to_dict()
    jsonl_buf.write(json.dumps(record, ensure_ascii=False) + "\n")
st.download_button("Download results JSONL", data=jsonl_buf.getvalue().encode("utf-8"), file_name="email_insights_results.jsonl", mime="application/jsonl")

st.caption("Note: For real emails, ensure you have permission and remove personal data. Use synthetic/public datasets for your portfolio.")
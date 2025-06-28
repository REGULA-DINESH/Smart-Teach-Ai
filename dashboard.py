import streamlit as st
import os
import json
import pandas as pd
def show():
    st.title("📊 Dashboard")
    user = st.session_state["user"]
    st.write(f"**Logged in as:** `{user}`")
    quiz_file = f"data/quizzes/{user}.json"
    if not os.path.exists(quiz_file):
        st.warning("No quiz history found.")
        return
    with open(quiz_file, "r") as f:
        data = json.load(f)
    if not data:
        st.info("No quizzes taken yet.")
        return
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['Date'] = df['timestamp'].dt.date
    df['Time'] = df['timestamp'].dt.strftime("%H:%M:%S")
    columns_order = ['Date', 'Time', 'topic', 'difficulty', 'score']
    df = df[columns_order]
    df = df.sort_values(["Date", "Time"], ascending=False)
    st.subheader("📅 Quiz History")
    df.index = range(len(df), 0, -1)
    st.dataframe(df, use_container_width=True)
    st.subheader("📈 Overall Summary")
    total = len(df)
    avg_score = df["score"].mean()
    best = df["score"].max()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Quizzes", total)
    col2.metric("Average Score", f"{avg_score:.2f}")
    col3.metric("Best Score", best)
    st.subheader("🧠 Performance by Difficulty")
    difficulties = ['Easy', 'Medium', 'Hard']
    for diff in difficulties:
        diff_df = df[df['difficulty'].str.lower() == diff.lower()]
        st.markdown(f"### 🎯 {diff} Level")
        if diff_df.empty:
            st.info("No quizzes attempted at this level.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Quizzes Attempted", len(diff_df))
            col2.metric("Average Score", f"{diff_df['score'].mean():.2f}")
            col3.metric("Best Score", diff_df['score'].max())
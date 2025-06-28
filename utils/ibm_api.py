import streamlit as st
from ibm_watsonx_ai.foundation_models import Model
from utils.model_selector import choose_best_model
def call_ibm_model(prompt, max_tokens=500, temperature=0.3, top_p=0.9, top_k=50):
    API_KEY = st.secrets["IBM_API_KEY"]
    PROJECT_ID = st.secrets["IBM_PROJECT_ID"]
    REGION_URL = st.secrets["IBM_URL"]
    model_id = choose_best_model(prompt)
    if not model_id:
        return "⚠️ Prompt is too long for all available models."
    model = Model(
        model_id=model_id,
        params={
            "decoding_method": "greedy",
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k
        },
        project_id=PROJECT_ID,
        credentials={
            "apikey": API_KEY,
            "url": REGION_URL
        }
    )
    try:
        response = model.generate(prompt)
        return response["results"][0]["generated_text"]
    except Exception as e:
        return f"⚠️ Error occurred: {str(e)}"
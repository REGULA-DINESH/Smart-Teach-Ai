def estimate_tokens(text):
    return int(len(text.split()) * 1.3)
SUPPORTED_MODELS = [
    {"id": "ibm/granite-3.3-2b-instruct","limit": 131072},
    {"id": "ibm/granite-3.3-8b-instruct","limit": 131072},
    {"id": "ibm/granite-3-8b-instruct","limit": 131072},
]
def choose_best_model(prompt):
    token_count = estimate_tokens(prompt)
    for model in sorted(SUPPORTED_MODELS, key=lambda x: x["limit"]):
        if token_count <= model["limit"]:
            return model["id"]
    return None
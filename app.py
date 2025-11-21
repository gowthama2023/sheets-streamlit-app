import streamlit as st
import pandas as pd
import json
from github import Github
import base64

st.set_page_config(page_title="Shared Data Editor", layout="wide")

# GitHub repo details
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = st.secrets["FILE_PATH"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Load JSON from GitHub
file = repo.get_contents(FILE_PATH)
content = file.decoded_content.decode()
data = json.loads(content)

df = pd.DataFrame(data)

st.title("Shared Data Editor (100% Free, No Google Cloud)")
st.write("Everyone sees updates immediately.")

edited_df = st.data_editor(df, num_rows="dynamic")

if st.button("Save Changes"):
    new_json = edited_df.to_json(orient="records", indent=2)
    repo.update_file(
        FILE_PATH,
        "Updated via Streamlit app",
        new_json,
        file.sha
    )
    st.success("Saved to GitHub! Shared data updated for all users.")


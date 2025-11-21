# app.py
import streamlit as st
import pandas as pd
from github import Github
from io import BytesIO

st.set_page_config(page_title="Shared Excel (GitHub Backend)", layout="wide")
st.title("📤 Upload Excel → Shared on GitHub (Everyone sees updates)")

# -------------------
# CONFIG via Streamlit secrets
# -------------------
# You must set these in Streamlit Cloud secrets:
# GITHUB_TOKEN, REPO_NAME (username/repo), FILE_PATH (path to store file, e.g., "shared_data.xlsx")
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = st.secrets["REPO_NAME"]
    FILE_PATH = st.secrets.get("FILE_PATH", "shared_data.xlsx")
except Exception:
    st.error("App secrets not found. Set GITHUB_TOKEN and REPO_NAME in Streamlit app secrets.")
    st.stop()

# -------------------
# GitHub helpers
# -------------------
def get_repo():
    g = Github(GITHUB_TOKEN)
    return g.get_repo(REPO_NAME)

def load_excel_from_github():
    repo = get_repo()
    try:
        contents = repo.get_contents(FILE_PATH)
        raw = contents.decoded_content
        df = pd.read_excel(BytesIO(raw))
        return df, contents.sha
    except Exception:
        return None, None

def upload_excel_to_github(df, sha=None):
    repo = get_repo()
    bio = BytesIO()
    df.to_excel(bio, index=False)
    bio.seek(0)
    content_bytes = bio.getvalue()

    if sha:  # update existing file
        repo.update_file(FILE_PATH, "Update shared Excel (via Streamlit)", content_bytes, sha)
    else:
        repo.create_file(FILE_PATH, "Create shared Excel (via Streamlit)", content_bytes)

# -------------------
# UI
# -------------------
st.markdown("**Current shared file in repo:** `" + FILE_PATH + "`")

df_existing, current_sha = load_excel_from_github()
if df_existing is not None:
    st.subheader("Current shared data (from GitHub)")
    st.dataframe(df_existing)
else:
    st.info("No shared file found in repo yet. Upload one below to create it.")

st.markdown("---")
st.subheader("Upload an Excel file (.xlsx) to replace/create the shared file")

uploaded = st.file_uploader("Choose an Excel file", type=["xlsx"])
if uploaded is not None:
    try:
        df_new = pd.read_excel(uploaded)
    except Exception as e:
        st.error("Failed to read uploaded Excel file.")
        st.exception(e)
        st.stop()

    st.write("Preview of uploaded file:")
    st.dataframe(df_new)

    if st.button("Save & Share to GitHub"):
        with st.spinner("Uploading to GitHub..."):
            try:
                # If a shared file already existed, use its sha to update; else create
                upload_excel_to_github(df_new, sha=current_sha)
                st.success("Uploaded successfully! Refresh the page (or open app URL in another browser) to see it load.")
            except Exception as e:
                st.error("Failed to upload file to GitHub. Check token, repo, and permissions.")
                st.exception(e)

st.markdown("---")
st.subheader("Edit currently shared data on the site")

if df_existing is not None:
    edited = st.data_editor(df_existing, num_rows="dynamic")
    if st.button("Save edited data to GitHub"):
        with st.spinner("Saving edited data..."):
            try:
                upload_excel_to_github(edited, sha=current_sha)
                st.success("Saved edited data to GitHub.")
            except Exception as e:
                st.error("Failed to save edited data.")
                st.exception(e)

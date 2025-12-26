# Frontend

This folder contains the frontend code for the Global Risk Monitor project.

# Streamlit Deployment Instructions

## Local Development

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Deploy to Streamlit Cloud

1. Push your repository to GitHub (if not already).
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in.
3. Click 'New app', select your repo, branch, and set the main file path to `frontend/app.py`.
4. Click 'Deploy'.

- Ensure `frontend/requirements.txt` is present and lists all dependencies.
- For data access, ensure any required files are in the repo or accessible via URL.

---

For more, see the [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-community-cloud).

import streamlit as st
import json
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Metadata Viewer",
)

st.title("Metadata Viewer")

# Choose data source
source_type = st.radio("Choose data.json source:", ["From URL", "From local file (.json)"])

catalog = None
if source_type == "From URL":
    url_input = st.text_input("Enter the URL to data.json:", "https://www.commerce.gov/sites/default/files/data.json")
    if st.button("Load Catalog"):
        url = url_input.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/115.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            catalog = response.json()
        except Exception as e:
            st.error(f"Error fetching data: {e}")

elif source_type == "From local file (.json)":
    uploaded_file = st.file_uploader("Upload data.json", type="json")
    if uploaded_file:
        try:
            catalog = json.load(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")

def flatten_value(value):
    """Convert dicts/lists to JSON strings for display."""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value

if catalog:
    datasets = catalog.get('dataset', [])
    if not datasets:
        st.warning("No datasets found in the catalog.")
    else:
        # Collect all unique keys from all datasets
        all_keys = set()
        for ds in datasets:
            all_keys.update(ds.keys())

        table_data = []
        modified_dates = []

        for ds in datasets:
            row = {}
            for key in all_keys:
                val = ds.get(key, None)

                # Parse and track 'modified' dates for summary
                if key == "modified" and val:
                    try:
                        mod_date = datetime.fromisoformat(val)
                    except ValueError:
                        try:
                            mod_date = datetime.strptime(val, "%Y-%m-%d")
                        except Exception:
                            mod_date = None
                    if mod_date:
                        modified_dates.append(mod_date)
                        val = mod_date.strftime('%Y-%m-%d')

                val = flatten_value(val)
                row[key] = val
            table_data.append(row)

        if modified_dates:
            last_updated = max(modified_dates)
            st.success(f"Catalog last updated on: **{last_updated.strftime('%B %d, %Y')}**")
        else:
            st.warning("No 'modified' dates found in datasets.")

        df = pd.DataFrame(table_data)
        st.subheader("Metadata")
        st.dataframe(df)

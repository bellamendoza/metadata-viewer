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
    url = st.text_input("Enter the URL to data.json:", "https://www.commerce.gov/sites/default/files/data.json")
    if st.button("Load Catalog"):
        try:
            response = requests.get(url)
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
    """Helper to convert dicts/lists to JSON strings for display."""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value

if catalog:
    datasets = catalog.get('dataset', [])
    if not datasets:
        st.warning("No datasets found in the catalog.")
    else:
        # Get all keys in all dataset entries
        all_keys = set()
        for ds in datasets:
            all_keys.update(ds.keys())

        # Prepare list of dicts with all keys, filling missing keys with None
        table_data = []
        modified_dates = []

        for ds in datasets:
            row = {}
            for key in all_keys:
                val = ds.get(key, None)
                # Special handling for 'modified' field to parse dates and collect max date
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
                # Flatten complex types
                val = flatten_value(val)
                row[key] = val
            table_data.append(row)

        # Display last updated
        if modified_dates:
            last_updated = max(modified_dates)
            st.success(f"Catalog last updated on: **{last_updated.strftime('%B %d, %Y')}**")
        else:
            st.warning("No 'modified' dates found in datasets.")

        # Display table
        df = pd.DataFrame(table_data)
        st.subheader("Metadata")
        st.dataframe(df)

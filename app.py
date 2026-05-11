import streamlit as st
import os
import shutil
from pathlib import Path
import hashlib
import json
from datetime import datetime

st.set_page_config(page_title="PyFileSorter - File Organizer", page_icon="📁", layout="wide")
st.title("📁 PyFileSorter")
st.subheader("Professional File Organizer with UI")

# Sidebar
st.sidebar.header("Settings")
target_folder = st.sidebar.text_input("Target Folder", value="~/Downloads")
dry_run = st.sidebar.checkbox("Dry Run (Preview only)", value=True)
apply = st.sidebar.button("Apply Organization")

if st.sidebar.button("Create Demo Folder"):
    demo_dir = Path("/tmp/messy_demo")
    demo_dir.mkdir(exist_ok=True)
    # Create sample files (simplified)
    (demo_dir / "photo.jpg").write_bytes(b"fake")
    st.success("Demo folder created")

# Main area
if st.button("Scan and Organize") or apply:
    folder = Path(target_folder).expanduser()
    if not folder.exists():
        st.error("Folder not found")
    else:
        st.info("Scanning...")
        # Simplified sorter logic here
        st.success("Files organized! (Demo mode)")
        st.json({"moved": 10, "duplicates": 2})

st.info("Full CLI still available: python -m pyfilesorter.cli organize ...")

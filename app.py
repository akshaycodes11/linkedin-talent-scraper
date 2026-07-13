import streamlit as st
import pandas as pd

from scraper import BrightDataScraper
from parser import parse_profiles
from database.candidate_repository import CandidateRepository
from config import (
    BRIGHTDATA_API_KEY,
    BRIGHTDATA_ZONE,
    BRIGHTDATA_ENDPOINT
)

print("API Key Loaded:", BRIGHTDATA_API_KEY is not None)
print("Zone:", BRIGHTDATA_ZONE)
print("Endpoint:", BRIGHTDATA_ENDPOINT)
# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="LinkedIn Talent Scraper",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 LinkedIn Talent Scraper")
st.caption("Bright Data SERP → Supabase")

# ----------------------------------------------------
# Repository
# ----------------------------------------------------

repo = CandidateRepository()
repo.create_table()

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

st.sidebar.header("Database")

try:
    total = repo.count_candidates()
    st.sidebar.metric("Candidates Stored", total)
except:
    st.sidebar.warning("Unable to fetch database count.")

# ----------------------------------------------------
# Search Form
# ----------------------------------------------------

st.subheader("Talent Search")

with st.form("scrape_form"):

    col1, col2 = st.columns(2)

    with col1:

        role = st.selectbox(
            "Role",
            [
                "",
                "Machine Learning Engineer",
                "AI Engineer",
                "Data Scientist",
                "Backend Developer",
                "Frontend Developer",
                "Full Stack Developer",
                "Python Developer",
                "Java Developer",
                "DevOps Engineer",
                "Cloud Engineer",
                "Data Engineer",
                "NLP Engineer",
                "Computer Vision Engineer",
                "LLM Engineer"
            ]
        )

        location = st.selectbox(
            "Location",
            [
                "",
                "India",
                "Bengaluru",
                "Hyderabad",
                "Pune",
                "Chennai",
                "Mumbai",
                "Delhi",
                "Remote"
            ]
        )

    with col2:

        experience = st.selectbox(
            "Experience",
            [
                "",
                "Fresher",
                "1-3 years",
                "3-5 years",
                "5-8 years",
                "8+ years"
            ]
        )

        # max_results = st.slider(
        #     "Maximum Profiles",
        #     min_value=10,
        #     max_value=100,
        #     value=20,
        #     step=10
        # )

    search_query = st.text_input(
        "Additional Skills / Keywords",
        placeholder="Python, LangChain, AWS, TensorFlow..."
    )

    submit = st.form_submit_button(
        "🚀 Search LinkedIn Profiles",
        use_container_width=True
    )

# ----------------------------------------------------
# Scraping
# ----------------------------------------------------

if submit:

    query_parts = []

    if role:
        query_parts.append(role)

    if experience:
        query_parts.append(experience)

    if location:
        query_parts.append(location)

    if search_query.strip():
        query_parts.append(search_query.strip())

    final_query = " ".join(query_parts)

    if not final_query:
        st.warning("Please select at least one filter.")
        st.stop()

    st.info(f"Searching: {final_query}")

    scraper = BrightDataScraper()

    progress = st.progress(0)
    status = st.empty()

    try:

        status.info("Searching LinkedIn profiles...")
        progress.progress(20)

        raw_profiles = scraper.search_profiles(
            recruiter_query=final_query,
           # limit=max_results
        )

        progress.progress(50)

        parsed_profiles = parse_profiles(
            raw_profiles,
            final_query,
            selected_location=location
        )

        progress.progress(75)

        result = repo.insert_candidates(parsed_profiles)

        inserted = result["inserted"]
        duplicates = result["duplicates"]

        progress.progress(100)
        status.success("Scraping completed successfully!")

        st.success(f"Fetched: {len(raw_profiles)} profiles")
        st.success(f"Inserted: {inserted}")
        st.info(f"Duplicates Skipped: {duplicates}")

        st.divider()
        st.subheader("Candidate Preview")

        if parsed_profiles:

            df = pd.DataFrame(parsed_profiles)

            st.dataframe(
                df[
                    [
                        "full_name",
                        "headline",
                        "current_company",
                        "location",
                        "linkedin_url",
                    ]
                ],
                use_container_width=True,
            )

        else:
            st.warning("No profiles found.")

    except Exception as e:
        st.error(str(e))

# ----------------------------------------------------
# Footer
# ----------------------------------------------------

st.divider()

st.caption("Powered by Bright Data • Supabase • Streamlit")

repo.close()

import streamlit as st
import requests
import json
import pandas as pd


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="RepoMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# API CONFIGURATION
# ==========================================

API_BASE_URL = "http://127.0.0.1:8000"


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: #ffffff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #8b9cff;
}

.subtitle {
    color: #a0a0a0;
    font-size: 17px;
}

.metric-card {
    background-color: #1c2333;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #30394d;
}

div.stButton > button {
    width: 100%;
    border-radius: 8px;
    height: 45px;
    font-weight: bold;
}

section[data-testid="stSidebar"] {
    background-color: #151a26;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SESSION STATE
# ==========================================

if "repo_url" not in st.session_state:
    st.session_state.repo_url = ""

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "index_result" not in st.session_state:
    st.session_state.index_result = None

if "bug_result" not in st.session_state:
    st.session_state.bug_result = None

if "bug_repo_url" not in st.session_state:
    st.session_state.bug_repo_url = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def call_api(endpoint, payload=None, method="POST"):

    url = f"{API_BASE_URL}{endpoint}"

    try:

        if method == "GET":
            response = requests.get(url, timeout=30)

        else:
            response = requests.post(
                url,
                json=payload,
                timeout=300
            )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:

        st.error(
            "Backend connection failed. "
            "Please start the FastAPI server."
        )

    except requests.exceptions.Timeout:

        st.error("Request timed out. Please try again.")

    except requests.exceptions.HTTPError:

        try:
            details = response.json()
        except ValueError:
            details = response.text

        st.error(f"API Error: {details}")

    except requests.exceptions.RequestException as error:

        st.error(f"Request failed: {str(error)}")

    except ValueError:

        st.error("Invalid response received from backend.")

    return None


def extract_analysis_data(result):
    """
    Supports both direct analyzer responses and
    analyzer results nested inside API responses.
    """

    if not isinstance(result, dict):
        return {}

    expected_keys = [
        "total_files",
        "file_extensions",
        "languages",
        "project_types",
        "insights"
    ]

    if any(key in result for key in expected_keys):
        return result

    for value in result.values():

        if isinstance(value, dict):

            extracted = extract_analysis_data(value)

            if extracted:
                return extracted

    return result


def display_chart(title, data, chart_type="bar"):

    st.markdown(f"#### {title}")

    if not data:
        st.info("No data available for this chart.")
        return

    try:

        chart_data = pd.DataFrame(
            list(data.items()),
            columns=["Category", "Count"]
        )

        chart_data = chart_data.set_index("Category")

        if chart_type == "bar":
            st.bar_chart(chart_data)

        elif chart_type == "area":
            st.area_chart(chart_data)

    except Exception as error:

        st.warning(f"Could not display chart: {error}")


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("# 🧠 RepoMind AI")

    st.caption("Intelligent GitHub Repository Analyst")

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Choose a section",
        [
            "🏠 Dashboard",
            "📊 Repository Analysis",
            "🔍 Code Indexing",
            "🐞 Bug Detection",
            "💬 AI Repository Chat"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### Backend Status")

    if st.button("Check Backend"):

        health = call_api(
            "/health",
            method="GET"
        )

        if health is not None:
            st.success("Backend Connected")
            st.json(health)

    st.divider()

    st.caption("Powered by Local AI • Ollama • ChromaDB")


# ==========================================
# MAIN HEADER
# ==========================================

st.markdown(
    '<div class="main-title">🧠 RepoMind AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Understand any GitHub codebase with the power of AI.'
    '</div>',
    unsafe_allow_html=True
)

st.write("")


# ==========================================
# REPOSITORY INPUT
# ==========================================

st.markdown("### 🔗 GitHub Repository")

github_url = st.text_input(
    "Enter GitHub Repository URL",
    value=st.session_state.repo_url,
    placeholder="https://github.com/username/repository"
)

if github_url != st.session_state.repo_url:

    st.session_state.repo_url = github_url


# ==========================================
# DASHBOARD
# ==========================================

if page == "🏠 Dashboard":

    st.subheader("Welcome to RepoMind AI 🚀")

    st.write(
        "Your intelligent assistant for understanding, "
        "analyzing and exploring GitHub repositories."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="metric-card">'
            '<h3>📊 Repository Analysis</h3>'
            '<p>Understand repository structure, files and languages.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            '<div class="metric-card">'
            '<h3>🔍 Code Intelligence</h3>'
            '<p>Index and retrieve relevant code using RAG.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col3:

        st.markdown(
            '<div class="metric-card">'
            '<h3>🐞 Bug Detection</h3>'
            '<p>Detect potential bugs and code quality issues.</p>'
            '</div>',
            unsafe_allow_html=True
        )

    st.write("")

    st.info(
        "Enter a GitHub repository URL above and "
        "select a feature from the sidebar."
    )


# ==========================================
# REPOSITORY ANALYSIS
# ==========================================

elif page == "📊 Repository Analysis":

    st.subheader("📊 Repository Analysis")

    st.write(
        "Analyze repository structure, programming languages, "
        "file categories and important project information."
    )

    if st.button("🚀 Analyze Repository"):

        if not github_url.strip():

            st.warning("Please enter a GitHub repository URL.")

        else:

            with st.spinner("Analyzing repository..."):

                result = call_api(
                    "/api/repository/analyze",
                    {
                        "repo_url": github_url
                    }
                )

                if result is not None:

                    st.session_state.analysis_result = result

                    st.success("Repository analysis completed!")

    # DISPLAY ANALYSIS RESULTS

    if st.session_state.analysis_result:

        result = extract_analysis_data(
            st.session_state.analysis_result
        )

        st.divider()

        st.markdown("### 📈 Repository Overview")

        # METRIC CARDS

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Files",
                result.get("total_files", 0)
            )

        with col2:

            st.metric(
                "Total Folders",
                result.get("total_folders", 0)
            )

        with col3:

            project_types = result.get("project_types", [])

            if isinstance(project_types, list):

                project_name = (
                    ", ".join(project_types)
                    if project_types else "Unknown"
                )

            else:

                project_name = str(project_types)

            st.metric(
                "Project Type",
                project_name
            )

        st.divider()

        # PROGRAMMING LANGUAGES

        st.markdown("### 💻 Programming Languages")

        languages = result.get("languages", {})

        display_chart(
            "Language Distribution",
            languages
        )

        # TOP LANGUAGES

        top_languages = result.get("top_languages", [])

        if top_languages:

            st.markdown("#### 🏆 Top Languages")

            if isinstance(top_languages, list):

                for language in top_languages:
                    st.write(f"• {language}")

            elif isinstance(top_languages, dict):

                st.write(top_languages)

        st.divider()

        # FILE EXTENSIONS

        col1, col2 = st.columns(2)

        with col1:

            display_chart(
                "📁 File Extensions",
                result.get("file_extensions", {})
            )

        with col2:

            display_chart(
                "🗂️ File Categories",
                result.get("file_categories", {})
            )

        st.divider()

        # PROJECT INSIGHTS

        st.markdown("### 💡 Project Insights")

        insights = result.get("insights", [])

        if insights:

            for insight in insights:
                st.info(f"💡 {insight}")

        else:

            st.info("No additional insights available.")

        st.divider()

        # IMPORTANT FILES

        st.markdown("### ⭐ Important Project Files")

        important_files = result.get("important_files", [])

        if important_files:

            for file in important_files:
                st.write(f"📄 `{file}`")

        else:

            st.info("No important files detected.")

        st.divider()

        # FOLDER STRUCTURE

        st.markdown("### 📂 Folder Structure")

        root_folders = result.get("root_folders", [])

        folder_structure = result.get("folder_structure", [])

        if root_folders:

            for folder in root_folders:
                st.write(f"📁 `{folder}`")

        elif folder_structure:

            st.json(folder_structure)

        else:

            st.info("No folder structure information available.")

        # SUMMARY

        summary = result.get("summary")

        if summary:

            st.divider()

            st.markdown("### 📝 Repository Summary")

            st.success(summary)

        # COMPLETE API RESPONSE

        with st.expander("🔎 View Complete Analysis Response"):

            st.json(st.session_state.analysis_result)


# ==========================================
# CODE INDEXING
# ==========================================

elif page == "🔍 Code Indexing":

    st.subheader("🔍 Repository Code Indexing")

    st.write(
        "Download repository files, generate local embeddings "
        "and store code chunks in ChromaDB."
    )

    if st.button("⚡ Index Repository"):

        if not github_url.strip():

            st.warning("Please enter a GitHub repository URL.")

        else:

            with st.spinner(
                "Downloading files and generating embeddings..."
            ):

                result = call_api(
                    "/api/repository/index",
                    {
                        "repo_url": github_url
                    }
                )

                if result is not None:

                    st.session_state.index_result = result

                    st.success("Repository indexed successfully!")

    if st.session_state.index_result:

        result = st.session_state.index_result

        st.markdown("### Indexing Results")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Downloaded Files",
                result.get("downloaded_files", "N/A")
            )

        with col2:

            st.metric(
                "Total Chunks",
                result.get("total_chunks", "N/A")
            )

        with col3:

            st.metric(
                "Stored Chunks",
                result.get("stored_chunks", "N/A")
            )

        st.json(result)


# ==========================================
# BUG DETECTION
# ==========================================

elif page == "🐞 Bug Detection":

    st.subheader("🐞 Repository Bug Detection")

    st.write(
        "Scan Python files in your GitHub repository to detect "
        "potential bugs, security patterns and code quality issues."
    )

    st.info(
        "RepoMind AI uses a lightweight static analysis agent. "
        "Detected patterns are potential issues, not confirmed vulnerabilities."
    )

    if st.button("🔍 Scan Repository for Bugs"):

        if not github_url.strip():

            st.warning("Please enter a GitHub repository URL.")

        else:

            with st.spinner(
                "Scanning repository files for potential issues..."
            ):

                result = call_api(
                    "/api/agents/analyze-bugs",
                    {
                        "repo_url": github_url
                    }
                )

                if result is not None:

                    st.session_state.bug_result = result

                    st.session_state.bug_repo_url = github_url

                    st.success("Bug detection completed successfully!")

    # DISPLAY BUG DETECTION RESULTS

    if (
        st.session_state.bug_result
        and st.session_state.bug_repo_url == github_url
    ):

        response = st.session_state.bug_result

        bug_data = response.get("bug_analysis", {})

        st.divider()

        st.markdown("### 📊 Bug Detection Overview")

        st.caption(
            f"Repository: {response.get('repository', 'Unknown')}"
        )

        st.caption(
            f"Downloaded Python files: "
            f"{response.get('downloaded_files', 0)}"
        )

        # METRIC CARDS

        col1, col2, col3, col4 = st.columns(4)

        severity = bug_data.get("severity_summary", {})

        with col1:

            st.metric(
                "Files Scanned",
                bug_data.get("total_files_scanned", 0)
            )

        with col2:

            st.metric(
                "Total Issues",
                bug_data.get("total_issues", 0)
            )

        with col3:

            st.metric(
                "🔴 High",
                severity.get("high", 0)
            )

        with col4:

            st.metric(
                "🟡 Medium",
                severity.get("medium", 0)
            )

        st.divider()

        # LOW SEVERITY

        st.metric(
            "🟢 Low Severity Issues",
            severity.get("low", 0)
        )

        # SEVERITY CHART

        st.markdown("### 🚨 Severity Distribution")

        display_chart(
            "Issues by Severity",
            severity
        )

        st.divider()

        # CATEGORY CHART

        st.markdown("### 📂 Issue Categories")

        category_summary = bug_data.get(
            "category_summary",
            {}
        )

        display_chart(
            "Issues by Category",
            category_summary
        )

        st.divider()

        # SUMMARY

        st.markdown("### 📝 Bug Analysis Summary")

        st.success(
            bug_data.get(
                "summary",
                "Bug analysis completed."
            )
        )

        # FILE REPORTS

        st.markdown("### 📁 File-wise Bug Reports")

        file_reports = bug_data.get("file_reports", [])

        if file_reports:

            for index, report in enumerate(file_reports, start=1):

                file_path = report.get(
                    "file_path",
                    "Unknown file"
                )

                issue_count = report.get(
                    "total_issues",
                    0
                )

                with st.expander(
                    f"📄 {file_path} — {issue_count} issue(s)"
                ):

                    st.write(
                        f"**Status:** {report.get('status', 'Unknown')}"
                    )

                    st.write(
                        f"**Total Issues:** {issue_count}"
                    )

                    file_severity = report.get(
                        "severity_summary",
                        {}
                    )

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "High",
                        file_severity.get("high", 0)
                    )

                    c2.metric(
                        "Medium",
                        file_severity.get("medium", 0)
                    )

                    c3.metric(
                        "Low",
                        file_severity.get("low", 0)
                    )

                    issues = report.get("issues", [])

                    if issues:

                        st.markdown("#### Detected Issues")

                        for issue in issues:

                            st.markdown("---")

                            st.markdown(
                                f"**{issue.get('type', 'Unknown Issue')}**"
                            )

                            st.write(
                                f"📍 Line: {issue.get('line', 'N/A')}"
                            )

                            st.write(
                                f"⚠️ Severity: "
                                f"{issue.get('severity', 'Unknown').upper()}"
                            )

                            st.write(
                                f"📂 Category: "
                                f"{issue.get('category', 'Unknown')}"
                            )

                            st.write(
                                f"**Message:** "
                                f"{issue.get('message', '')}"
                            )

                            st.info(
                                f"💡 Recommendation: "
                                f"{issue.get('recommendation', '')}"
                            )

                    else:

                        st.success(
                            "No potential issues detected in this file."
                        )

        else:

            st.info("No file reports available.")

        st.divider()

        # ALL ISSUES TABLE

        st.markdown("### 📋 All Detected Issues")

        all_issues = []

        for report in file_reports:

            for issue in report.get("issues", []):

                all_issues.append({
                    "File": report.get("file_path", "Unknown"),
                    "Type": issue.get("type", ""),
                    "Line": issue.get("line", ""),
                    "Severity": issue.get("severity", ""),
                    "Category": issue.get("category", ""),
                    "Message": issue.get("message", ""),
                    "Recommendation": issue.get("recommendation", "")
                })

        if all_issues:

            issues_df = pd.DataFrame(all_issues)

            st.dataframe(
                issues_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "No potential issues were detected in the scanned files."
            )

        # COMPLETE API RESPONSE

        with st.expander("🔎 View Complete Bug Detection API Response"):

            st.json(response)

    elif st.session_state.bug_result:

        st.info(
            "The previous scan belongs to another repository. "
            "Scan the current repository to see its results."
        )


# ==========================================
# AI REPOSITORY CHAT
# ==========================================

elif page == "💬 AI Repository Chat":

    st.subheader("💬 Ask RepoMind AI")

    st.write(
        "Ask anything about your indexed GitHub repository."
    )

    if not github_url.strip():

        st.warning(
            "Please enter your GitHub repository URL above."
        )

    else:

        st.markdown("### Ask your question")

        question = st.text_area(
            "Your Question",
            placeholder=(
                "Example: What is the purpose of this repository?"
            ),
            height=100
        )

        n_results = st.slider(
            "Number of retrieved code chunks",
            min_value=1,
            max_value=10,
            value=5
        )

        if st.button("🤖 Ask AI"):

            if not question.strip():

                st.warning("Please enter a question.")

            else:

                with st.spinner(
                    "RepoMind AI is analyzing your question..."
                ):

                    result = call_api(
                        "/api/repository/ask",
                        {
                            "repo_url": github_url,
                            "question": question,
                            "n_results": n_results
                        }
                    )

                    if result is not None:

                        st.session_state.chat_history.append({
                            "question": question,
                            "result": result
                        })

        if st.session_state.chat_history:

            st.divider()

            st.markdown("### 💡 Conversation")

            for chat in reversed(
                st.session_state.chat_history
            ):

                st.markdown(
                    f"**🧑 You:** {chat['question']}"
                )

                answer = chat["result"].get(
                    "answer",
                    "No answer returned."
                )

                st.markdown("**🤖 RepoMind AI:**")

                st.success(answer)

                retrieved = chat["result"].get(
                    "retrieved_chunks",
                    0
                )

                st.caption(
                    f"Retrieved code chunks: {retrieved}"
                )

                sources = chat["result"].get(
                    "sources",
                    []
                )

                if sources:

                    with st.expander("📁 View Retrieved Sources"):

                        st.json(sources)

                with st.expander("🔎 View Full API Response"):

                    st.json(chat["result"])

                st.divider()

            if st.button("🗑️ Clear Chat History"):

                st.session_state.chat_history = []

                st.rerun()


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    "<center>🧠 RepoMind AI | "
    "Intelligent GitHub Repository Analyst</center>",
    unsafe_allow_html=True
)

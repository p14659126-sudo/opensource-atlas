import streamlit as st
import plotly.express as px
import pandas as pd

from atlas.github_client import GitHubClient, GitHubAPIError
from atlas.dependencies import fetch_manifest_dependencies

st.set_page_config(page_title="OpenSource Atlas", page_icon="🧭", layout="wide")
st.title("🧭 OpenSource Atlas")
st.caption("Explore public GitHub repositories, activity, contributors, and declared dependencies.")

with st.sidebar:
    st.header("Repository")
    repo_input = st.text_input("GitHub repository", "pallets/flask", help="Format: owner/repository")
    st.caption("Public repositories work without a token. A GitHub token raises API rate limits.")
    token = st.text_input("Optional GitHub token", type="password")
    st.caption("Token is used only for this session and is not saved.")
    load = st.button("Analyze repository", type="primary", use_container_width=True)

if "repo" not in st.session_state:
    st.session_state.repo = "pallets/flask"
if load:
    st.session_state.repo = repo_input.strip()

repo_name = st.session_state.repo
if not repo_name or "/" not in repo_name:
    st.info("Enter a repository as owner/name.")
    st.stop()

client = GitHubClient(token=token or None)

try:
    with st.spinner(f"Fetching {repo_name} from GitHub…"):
        repo = client.get_repo(repo_name)
        contributors = client.get_contributors(repo_name, limit=20)
        commits = client.get_commits(repo_name, limit=100)
        issues = client.get_recent_issues(repo_name, limit=100)
        dependencies = fetch_manifest_dependencies(client, repo_name, repo.get("default_branch", "main"))
except GitHubAPIError as exc:
    st.error(str(exc))
    st.stop()

owner = repo.get("owner", {}).get("login", "")
st.subheader(f"{owner}/{repo.get('name', '')}")
st.write(repo.get("description") or "No repository description supplied.")
st.markdown(f"[Open repository on GitHub]({repo.get('html_url', '#')})")

c1, c2, c3, c4 = st.columns(4)
c1.metric("⭐ Stars", f"{repo.get('stargazers_count', 0):,}")
c2.metric("🍴 Forks", f"{repo.get('forks_count', 0):,}")
c3.metric("🐛 Open issues", f"{repo.get('open_issues_count', 0):,}")
c4.metric("👥 Contributors returned", len(contributors))

st.divider()
left, right = st.columns(2)
with left:
    st.markdown("### Repository details")
    st.write({
        "Primary language": repo.get("language") or "Not specified",
        "License": (repo.get("license") or {}).get("spdx_id", "Not specified"),
        "Default branch": repo.get("default_branch"),
        "Created": repo.get("created_at", "")[:10],
        "Last pushed": repo.get("pushed_at", "")[:10],
        "Archived": repo.get("archived", False),
        "Open source URL": repo.get("html_url"),
    })
with right:
    st.markdown("### Languages")
    try:
        languages = client.get_languages(repo_name)
        if languages:
            language_df = pd.DataFrame(
                [{"Language": k, "Bytes": v} for k, v in languages.items()]
            ).sort_values("Bytes", ascending=False)
            fig = px.pie(language_df, names="Language", values="Bytes", hole=0.45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No language data returned.")
    except GitHubAPIError as exc:
        st.warning(str(exc))

st.divider()
st.markdown("### Recent commit activity")
if commits:
    commit_df = pd.DataFrame([
        {
            "date": c.get("commit", {}).get("author", {}).get("date", "")[:10],
            "author": (c.get("author") or {}).get("login", "Unknown"),
            "message": c.get("commit", {}).get("message", "").splitlines()[0][:90],
        } for c in commits
    ])
    activity = commit_df.groupby("date").size().reset_index(name="commits")
    fig = px.bar(activity, x="date", y="commits", title="Commits in the latest 100 returned")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(commit_df, use_container_width=True, hide_index=True)
else:
    st.info("No commits were returned.")

a, b = st.columns(2)
with a:
    st.markdown("### Contributors")
    if contributors:
        contrib_df = pd.DataFrame([
            {"Contributor": x.get("login", "Unknown"), "Contributions": x.get("contributions", 0)}
            for x in contributors
        ])
        st.plotly_chart(
            px.bar(contrib_df, x="Contributor", y="Contributions", title="Top contributors returned"),
            use_container_width=True,
        )
    else:
        st.info("No contributor data returned.")
with b:
    st.markdown("### Recent issues and pull requests")
    if issues:
        issue_df = pd.DataFrame([
            {
                "Number": x.get("number"),
                "Title": x.get("title"),
                "Type": "Pull request" if "pull_request" in x else "Issue",
                "State": x.get("state"),
                "Created": x.get("created_at", "")[:10],
            } for x in issues
        ])
        st.dataframe(issue_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent issues or pull requests returned.")

st.divider()
st.markdown("### Declared dependencies")
st.caption("Parsed from common manifest files in the repository's default branch. This is not a complete dependency graph.")
if dependencies:
    dep_df = pd.DataFrame(dependencies, columns=["Manifest", "Dependency"])
    st.metric("Dependencies detected", len(dep_df))
    st.dataframe(dep_df, use_container_width=True, hide_index=True)
else:
    st.info("No supported dependency manifest was found, or the manifests could not be read.")

st.caption("Data comes from GitHub's public API. Counts and activity are snapshots, not proof of real-world users or programme eligibility.")

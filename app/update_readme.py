import os, re, requests
from datetime import datetime

README_FILE = "README.md"

def replace_section(content, marker, new_text):
    pattern = re.compile(rf"(<!--START_SECTION:{marker}-->)(.*?)(<!--END_SECTION:{marker}-->)", re.DOTALL)
    return pattern.sub(rf"\1\n{new_text}\n\3", content)

def get_contribution_stats(username, token):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          contributionYears
          startedAt
          endedAt
          currentStreak {
            length
            startDate
            endDate
          }
          longestStreak {
            length
            startDate
            endDate
          }
        }
      }
    }
    """

    response = requests.post(url, json={"query": query, "variables": {"login": username}}, headers=headers)
    data = response.json()["data"]["user"]["contributionsCollection"]

    total = data["contributionCalendar"]["totalContributions"]
    current_year = datetime.now().year

    year_contrib = total  # fallback
    
    current_streak = data.get("currentStreak", {})
    longest_streak = data.get("longestStreak", {})

    return f"""
- **Total Contributions:** {total}
- **This Year ({current_year}):** {year_contrib}
- **Current Streak:** {current_streak.get("length", 0)} days
- **Longest Streak:** {longest_streak.get("length", 0)} days
"""

if __name__ == "__main__":
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    repo = os.getenv("GITHUB_REPOSITORY")
    username = repo.split("/")[0]
    token = os.getenv("GITHUB_TOKEN")

    contrib_stats = get_contribution_stats(username, token)
    content = replace_section(content, "contrib", contrib_stats)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)

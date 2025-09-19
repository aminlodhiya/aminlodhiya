import requests
import re
from datetime import datetime
import humanize

README_FILE = "../README.md"
API_URL = "https://leetcode.com/graphql"
HEADERS = {"Content-Type": "application/json"}

def replace_section(content, marker, new_text):
    pattern = re.compile(
        rf"(<!--START_SECTION:{marker}-->)(.*?)(<!--END_SECTION:{marker}-->)",
        re.DOTALL,
    )
    return pattern.sub(rf"\1\n{new_text}\n\3", content)

def run_query(query, variables=None):
    response = requests.post(API_URL, json={"query": query, "variables": variables or {}}, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data.get("data", {})

def get_leetcode_stats(username):
    query = """
    query userProfile($username: String!) {
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum {
            difficulty
            count
          }
        }
      }
    }
    """
    data = run_query(query, {"username": username})
    stats = data["matchedUser"]["submitStats"]["acSubmissionNum"]

    easy = next((i["count"] for i in stats if i["difficulty"] == "Easy"), 0)
    medium = next((i["count"] for i in stats if i["difficulty"] == "Medium"), 0)
    hard = next((i["count"] for i in stats if i["difficulty"] == "Hard"), 0)
    total = easy + medium + hard

    return f"- **Total Solved:** {total}\n- Easy: {easy} | Medium: {medium} | Hard: {hard}"

def get_recent_submissions(username, limit=5):
    query = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
      recentAcSubmissionList(username: $username, limit: $limit) {
        id
        title
        titleSlug
        timestamp
      }
    }
    """
    data = run_query(query, {"username": username, "limit": limit})
    submissions = data["recentAcSubmissionList"]

    table = "| Problem | Submission | Time |\n|---------|------------|------|\n"
    for sub in submissions:
        title = sub["title"]
        problem_link = f"https://leetcode.com/problems/{sub['titleSlug']}/"
        submission_link = f"https://leetcode.com/submissions/detail/{sub['id']}/"
        ts = datetime.fromtimestamp(int(sub["timestamp"]))
        human_time = humanize.naturaltime(datetime.now() - ts)

        table += f"| [{title}]({problem_link}) | [Link]({submission_link}) | {human_time} |\n"

    return table

if __name__ == "__main__":
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    stats_section = get_leetcode_stats("aminlodhiya")
    submissions_section = get_recent_submissions("aminlodhiya", limit=5)

    new_content = f"### 📊 Leetcode Stats\n{stats_section}\n\n### 📝 Recent Submissions\n{submissions_section}"
    updated = replace_section(content, "LEETCODE", new_content)
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(updated)

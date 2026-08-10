import os
import requests

token = os.getenv("GITHUB_TOKEN")
username = os.getenv("GITHUB_USER", "vigneshsindhe")
output_path = os.getenv("OUTPUT_PATH", "dist/projects.svg")

# Ensure dist folder exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Fetch user repositories
headers = {"Authorization": f"token {token}"} if token else {}
url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=20"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    repos = response.json()
    repo_names = [repo['name'] for repo in repos if not repo.get('fork', False)][:10]
    
    # Generate simple SVG string
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{len(repo_names) * 25 + 20}">
      <style>
        .header {{ font: bold 14px sans-serif; fill: #0891B2; }}
        .repo {{ font: 12px sans-serif; fill: #A78BFA; }}
      </style>
      <text x="10" y="20" class="header">Recent Projects</text>
    '''
    
    for i, name in enumerate(repo_names):
        svg_content += f'<text x="10" y="{45 + i * 22}" class="repo">• {name}</text>\n'
        
    svg_content += '</svg>'
    
    with open(output_path, "w") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_path}")
else:
    print(f"Failed to fetch repositories: {response.status_code}")

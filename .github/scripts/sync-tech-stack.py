#!/usr/bin/env python3
"""
Scan all GitHub repositories and generate tech stack badges for README
"""
import json
import os
import re
import requests
from collections import defaultdict

def get_all_repos(username, token):
    """Fetch all public repositories for a user"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{username}/repos?per_page=100&page={page}&type=owner'
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error fetching repos: {response.status_code}")
            break

        page_repos = response.json()
        if not page_repos:
            break

        repos.extend(page_repos)
        page += 1

    return repos

def get_repo_languages(owner, repo, token):
    """Get languages used in a repository"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{owner}/{repo}/languages'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    return {}

def get_package_json(owner, repo, token):
    """Try to fetch package.json from repository"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Try multiple common locations
    paths = ['package.json', 'frontend/package.json', 'backend/package.json',
             'client/package.json', 'server/package.json']

    dependencies = set()

    for path in paths:
        url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            content = response.json()
            if content.get('encoding') == 'base64':
                import base64
                decoded = base64.b64decode(content['content']).decode('utf-8')
                try:
                    pkg = json.loads(decoded)
                    deps = list(pkg.get('dependencies', {}).keys())
                    dev_deps = list(pkg.get('devDependencies', {}).keys())
                    dependencies.update(deps + dev_deps)
                except json.JSONDecodeError:
                    pass

    return dependencies

def get_requirements_txt(owner, repo, token):
    """Try to fetch requirements.txt from repository"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{owner}/{repo}/contents/requirements.txt'
    response = requests.get(url, headers=headers)

    packages = set()
    if response.status_code == 200:
        content = response.json()
        if content.get('encoding') == 'base64':
            import base64
            decoded = base64.b64decode(content['content']).decode('utf-8')
            for line in decoded.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (before ==, >=, etc.)
                    pkg = re.split(r'[=<>!]', line)[0].strip()
                    if pkg:
                        packages.add(pkg)

    return packages

# Technology to badge mapping with logos
TECH_BADGES = {
    # Languages
    'javascript': '![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=flat&logo=javascript&logoColor=%23F7DF1E)',
    'typescript': '![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat&logo=typescript&logoColor=white)',
    'python': '![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)',
    'java': '![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=flat&logo=openjdk&logoColor=white)',
    'go': '![Go](https://img.shields.io/badge/go-%2300ADD8.svg?style=flat&logo=go&logoColor=white)',
    'rust': '![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=flat&logo=rust&logoColor=white)',
    'c++': '![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=flat&logo=c%2B%2B&logoColor=white)',
    'html': '![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=flat&logo=html5&logoColor=white)',
    'css': '![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=flat&logo=css3&logoColor=white)',

    # Frontend Frameworks
    'react': '![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)',
    'react-native': '![React Native](https://img.shields.io/badge/react%20native-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)',
    'vue': '![Vue.js](https://img.shields.io/badge/vue.js-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D)',
    'next': '![Next JS](https://img.shields.io/badge/Next-black?style=flat&logo=next.js&logoColor=white)',
    'nextjs': '![Next JS](https://img.shields.io/badge/Next-black?style=flat&logo=next.js&logoColor=white)',
    'angular': '![Angular](https://img.shields.io/badge/angular-%23DD0031.svg?style=flat&logo=angular&logoColor=white)',
    'svelte': '![Svelte](https://img.shields.io/badge/svelte-%23f1413d.svg?style=flat&logo=svelte&logoColor=white)',
    'tailwindcss': '![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)',
    'bootstrap': '![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=flat&logo=bootstrap&logoColor=white)',
    'mui': '![MUI](https://img.shields.io/badge/MUI-%23007FFF.svg?style=flat&logo=mui&logoColor=white)',
    '@mui/material': '![MUI](https://img.shields.io/badge/MUI-%23007FFF.svg?style=flat&logo=mui&logoColor=white)',
    'axios': '![Axios](https://img.shields.io/badge/Axios-5A29E4?style=flat&logo=axios&logoColor=white)',
    'redux': '![Redux](https://img.shields.io/badge/redux-%23593d88.svg?style=flat&logo=redux&logoColor=white)',
    'zustand': '![Zustand](https://img.shields.io/badge/Zustand-000000?style=flat)',
    '@tanstack/react-query': '![React Query](https://img.shields.io/badge/React_Query-FF4154?style=flat&logo=reactquery&logoColor=white)',
    'react-query': '![React Query](https://img.shields.io/badge/React_Query-FF4154?style=flat&logo=reactquery&logoColor=white)',
    'react-router-dom': '![React Router](https://img.shields.io/badge/React_Router-CA4245?style=flat&logo=reactrouter&logoColor=white)',
    'zod': '![Zod](https://img.shields.io/badge/Zod-306AFF?style=flat)',
    'playwright': '![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)',
    'storybook': '![Storybook](https://img.shields.io/badge/Storybook-FF4785?style=flat&logo=storybook&logoColor=white)',

    # Backend
    'express': '![Express.js](https://img.shields.io/badge/express.js-black?style=flat&logo=express&logoColor=white)',
    'fastapi': '![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)',
    'django': '![Django](https://img.shields.io/badge/django-%23092E20.svg?style=flat&logo=django&logoColor=white)',
    'flask': '![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)',
    'nestjs': '![NestJS](https://img.shields.io/badge/nestjs-%23E0234E.svg?style=flat&logo=nestjs&logoColor=white)',
    '@nestjs/core': '![NestJS](https://img.shields.io/badge/nestjs-%23E0234E.svg?style=flat&logo=nestjs&logoColor=white)',
    'jsonwebtoken': '![JWT](https://img.shields.io/badge/JWT-black?style=flat&logo=jsonwebtokens&logoColor=white)',
    'bcrypt': '![Bcrypt](https://img.shields.io/badge/Bcrypt-3380FF?style=flat)',
    'bcryptjs': '![Bcrypt](https://img.shields.io/badge/Bcrypt-3380FF?style=flat)',
    'mongoose': '![Mongoose](https://img.shields.io/badge/Mongoose-880000?style=flat&logo=mongoose&logoColor=white)',
    'sharp': '![Sharp](https://img.shields.io/badge/Sharp-00A2E0?style=flat)',
    'grammy': '![Grammy JS](https://img.shields.io/badge/Grammy_JS-000000?style=flat)',
    'ejs': '![EJS](https://img.shields.io/badge/EJS-808080?style=flat)',

    # Databases
    'mongodb': '![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white)',
    'postgresql': '![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)',
    'pg': '![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)',
    'mysql': '![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=flat&logo=mysql&logoColor=white)',
    'redis': '![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white)',
    'sqlite': '![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=flat&logo=sqlite&logoColor=white)',

    # Backend Platforms
    'firebase': '![Firebase](https://img.shields.io/badge/firebase-a08021?style=flat&logo=firebase&logoColor=ffcd34)',
    'supabase': '![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)',
    '@supabase/supabase-js': '![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)',

    # DevOps
    'docker': '![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)',
    'kubernetes': '![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=flat&logo=kubernetes&logoColor=white)',

    # Tools
    'vite': '![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=flat&logo=vite&logoColor=white)',
    'webpack': '![Webpack](https://img.shields.io/badge/webpack-%238DD6F9.svg?style=flat&logo=webpack&logoColor=black)',
    'jest': '![Jest](https://img.shields.io/badge/-jest-%23C21325?style=flat&logo=jest&logoColor=white)',
    'vitest': '![Vitest](https://img.shields.io/badge/-Vitest-729B1B?style=flat&logo=vitest&logoColor=white)',
    'eslint': '![ESLint](https://img.shields.io/badge/ESLint-4B3263?style=flat&logo=eslint&logoColor=white)',
    'prettier': '![Prettier](https://img.shields.io/badge/prettier-1A2C34?style=flat&logo=prettier&logoColor=white)',
}

def categorize_technologies(all_techs):
    """Categorize technologies into groups"""
    categories = {
        'Languages': [],
        'Frontend': [],
        'Backend': [],
        'Databases': [],
        'Backend Platforms': [],
        'DevOps': [],
        'Tools': []
    }

    lang_keys = ['javascript', 'typescript', 'python', 'java', 'go', 'rust', 'c++', 'html', 'css']
    frontend_keys = ['react', 'react-native', 'vue', 'next', 'nextjs', 'angular', 'svelte',
                     'tailwindcss', 'bootstrap', 'mui', '@mui/material', 'axios', 'redux',
                     'zustand', '@tanstack/react-query', 'react-query', 'react-router-dom',
                     'zod', 'playwright', 'storybook']
    backend_keys = ['express', 'fastapi', 'django', 'flask', 'nestjs', '@nestjs/core',
                    'jsonwebtoken', 'bcrypt', 'bcryptjs', 'mongoose', 'sharp', 'grammy', 'ejs']
    db_keys = ['mongodb', 'postgresql', 'pg', 'mysql', 'redis', 'sqlite']
    platform_keys = ['firebase', 'supabase', '@supabase/supabase-js']
    devops_keys = ['docker', 'kubernetes']
    tool_keys = ['vite', 'webpack', 'jest', 'vitest', 'eslint', 'prettier']

    for tech in all_techs:
        tech_lower = tech.lower()
        if tech_lower in lang_keys:
            categories['Languages'].append(tech)
        elif tech_lower in frontend_keys:
            categories['Frontend'].append(tech)
        elif tech_lower in backend_keys:
            categories['Backend'].append(tech)
        elif tech_lower in db_keys:
            categories['Databases'].append(tech)
        elif tech_lower in platform_keys:
            categories['Backend Platforms'].append(tech)
        elif tech_lower in devops_keys:
            categories['DevOps'].append(tech)
        elif tech_lower in tool_keys:
            categories['Tools'].append(tech)

    return categories

def generate_tech_stack_section(categories):
    """Generate markdown section for tech stack"""
    lines = []

    for category, techs in categories.items():
        if techs:
            lines.append(f"\n#### {category}\n")
            badge_line = " ".join([TECH_BADGES.get(tech.lower(), f'![{tech}](https://img.shields.io/badge/{tech}-gray?style=flat)') for tech in techs])
            lines.append(badge_line + "\n")

    return "".join(lines)

def main():
    github_token = os.environ.get('GITHUB_TOKEN')
    username = os.environ.get('GITHUB_REPOSITORY_OWNER', 'YosefHayim')

    if not github_token:
        print("Error: GITHUB_TOKEN not set")
        return

    print(f"Fetching repositories for {username}...")
    repos = get_all_repos(username, github_token)
    print(f"Found {len(repos)} repositories")

    all_languages = defaultdict(int)
    all_packages = set()

    for repo in repos:
        if repo['fork']:  # Skip forks
            continue

        print(f"Scanning {repo['name']}...")

        # Get languages
        languages = get_repo_languages(username, repo['name'], github_token)
        for lang, bytes_count in languages.items():
            all_languages[lang] += bytes_count

        # Get packages from package.json
        packages = get_package_json(username, repo['name'], github_token)
        all_packages.update(packages)

        # Get Python packages
        py_packages = get_requirements_txt(username, repo['name'], github_token)
        all_packages.update(py_packages)

    # Combine languages and packages
    all_techs = set()
    all_techs.update([lang.lower() for lang in all_languages.keys()])
    all_techs.update([pkg.lower() for pkg in all_packages])

    # Filter to only known technologies
    known_techs = [tech for tech in all_techs if tech in TECH_BADGES]

    print(f"\nFound {len(known_techs)} known technologies")

    # Categorize
    categories = categorize_technologies(known_techs)

    # Generate markdown
    tech_section = generate_tech_stack_section(categories)

    # Update README
    readme_path = 'README.md'
    with open(readme_path, 'r') as f:
        content = f.read()

    # Replace between markers
    start_marker = '<!-- TECHSTACK:START -->'
    end_marker = '<!-- TECHSTACK:END -->'

    pattern = f'{start_marker}.*?{end_marker}'
    replacement = f'{start_marker}\n{tech_section}\n{end_marker}'

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(readme_path, 'w') as f:
        f.write(new_content)

    print("\n✅ README updated successfully!")

if __name__ == '__main__':
    main()

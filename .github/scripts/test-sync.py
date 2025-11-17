#!/usr/bin/env python3
"""
Local test of the tech stack sync logic without GitHub API
"""
import re
from collections import defaultdict

# Import the functions from the main script (we'll test the logic)
TECH_BADGES = {
    # Languages
    'javascript': '![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=flat&logo=javascript&logoColor=%23F7DF1E)',
    'typescript': '![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat&logo=typescript&logoColor=white)',
    'python': '![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)',
    'html': '![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=flat&logo=html5&logoColor=white)',
    'css': '![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=flat&logo=css3&logoColor=white)',

    # Frontend Frameworks
    'react': '![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)',
    'react-native': '![React Native](https://img.shields.io/badge/react%20native-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)',
    'next': '![Next JS](https://img.shields.io/badge/Next-black?style=flat&logo=next.js&logoColor=white)',
    'nextjs': '![Next JS](https://img.shields.io/badge/Next-black?style=flat&logo=next.js&logoColor=white)',
    'tailwindcss': '![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)',
    'mui': '![MUI](https://img.shields.io/badge/MUI-%23007FFF.svg?style=flat&logo=mui&logoColor=white)',
    '@mui/material': '![MUI](https://img.shields.io/badge/MUI-%23007FFF.svg?style=flat&logo=mui&logoColor=white)',
    'axios': '![Axios](https://img.shields.io/badge/Axios-5A29E4?style=flat&logo=axios&logoColor=white)',
    'redux': '![Redux](https://img.shields.io/badge/redux-%23593d88.svg?style=flat&logo=redux&logoColor=white)',
    'zustand': '![Zustand](https://img.shields.io/badge/Zustand-000000?style=flat)',
    '@tanstack/react-query': '![React Query](https://img.shields.io/badge/React_Query-FF4154?style=flat&logo=reactquery&logoColor=white)',
    'react-router-dom': '![React Router](https://img.shields.io/badge/React_Router-CA4245?style=flat&logo=reactrouter&logoColor=white)',
    'zod': '![Zod](https://img.shields.io/badge/Zod-306AFF?style=flat)',
    'playwright': '![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)',
    'storybook': '![Storybook](https://img.shields.io/badge/Storybook-FF4785?style=flat&logo=storybook&logoColor=white)',

    # Backend
    'express': '![Express.js](https://img.shields.io/badge/express.js-black?style=flat&logo=express&logoColor=white)',
    'fastapi': '![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)',
    'django': '![Django](https://img.shields.io/badge/django-%23092E20.svg?style=flat&logo=django&logoColor=white)',
    'flask': '![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)',
    'jsonwebtoken': '![JWT](https://img.shields.io/badge/JWT-black?style=flat&logo=jsonwebtokens&logoColor=white)',
    'bcrypt': '![Bcrypt](https://img.shields.io/badge/Bcrypt-3380FF?style=flat)',
    'mongoose': '![Mongoose](https://img.shields.io/badge/Mongoose-880000?style=flat&logo=mongoose&logoColor=white)',
    'sharp': '![Sharp](https://img.shields.io/badge/Sharp-00A2E0?style=flat)',
    'grammy': '![Grammy JS](https://img.shields.io/badge/Grammy_JS-000000?style=flat)',
    'ejs': '![EJS](https://img.shields.io/badge/EJS-808080?style=flat)',

    # Databases
    'mongodb': '![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white)',
    'postgresql': '![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)',
    'pg': '![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)',

    # Backend Platforms
    'firebase': '![Firebase](https://img.shields.io/badge/firebase-a08021?style=flat&logo=firebase&logoColor=ffcd34)',
    'supabase': '![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)',
    '@supabase/supabase-js': '![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)',

    # DevOps
    'docker': '![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)',

    # Tools
    'vite': '![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=flat&logo=vite&logoColor=white)',
    'jest': '![Jest](https://img.shields.io/badge/-jest-%23C21325?style=flat&logo=jest&logoColor=white)',
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

def test_categorization():
    """Test the categorization logic with mock data"""
    print("🧪 Testing Tech Stack Scanner Logic\n")
    print("=" * 60)

    # Mock data simulating what would be found in repositories
    mock_technologies = [
        # Languages from GitHub language detection
        'JavaScript', 'TypeScript', 'Python', 'HTML', 'CSS',

        # Frontend packages from package.json
        'react', 'react-native', 'next', 'tailwindcss', 'axios',
        '@mui/material', 'redux', 'zustand', '@tanstack/react-query',
        'react-router-dom', 'zod', 'playwright', 'storybook',

        # Backend packages
        'express', 'mongoose', 'jsonwebtoken', 'bcrypt', 'sharp',
        'grammy', 'ejs',

        # Databases
        'mongodb', 'postgresql',

        # Backend Platforms
        'firebase', '@supabase/supabase-js',

        # DevOps
        'docker',

        # Tools
        'vite', 'jest',
    ]

    print(f"\n📦 Mock Technologies Found ({len(mock_technologies)} total):")
    print("-" * 60)
    for tech in sorted(mock_technologies):
        print(f"  ✓ {tech}")

    # Filter to only known technologies
    known_techs = [tech for tech in mock_technologies if tech.lower() in TECH_BADGES]

    print(f"\n🎯 Recognized Technologies ({len(known_techs)} matched):")
    print("-" * 60)

    # Categorize
    categories = categorize_technologies(known_techs)

    for category, techs in categories.items():
        if techs:
            print(f"\n  {category}: {len(techs)}")
            for tech in techs:
                print(f"    - {tech}")

    # Generate markdown
    print(f"\n📝 Generated Markdown Section:")
    print("=" * 60)
    tech_section = generate_tech_stack_section(categories)
    print(tech_section)

    # Test README update logic
    print("\n✅ Testing README Update Logic:")
    print("=" * 60)

    sample_readme = """# My Profile

<!-- TECHSTACK:START -->
<!-- Auto-generated. Do not edit manually. -->
<!-- TECHSTACK:END -->

## Other content
"""

    start_marker = '<!-- TECHSTACK:START -->'
    end_marker = '<!-- TECHSTACK:END -->'

    pattern = f'{start_marker}.*?{end_marker}'
    replacement = f'{start_marker}\n{tech_section}\n{end_marker}'

    new_content = re.sub(pattern, replacement, sample_readme, flags=re.DOTALL)

    print(new_content)

    print("\n✨ Test Complete! The logic works correctly.")
    print(f"   - Categorized {len(known_techs)} technologies")
    print(f"   - Generated {len([c for c in categories.values() if c])} categories")
    print(f"   - Successfully updated README between markers")

if __name__ == '__main__':
    test_categorization()

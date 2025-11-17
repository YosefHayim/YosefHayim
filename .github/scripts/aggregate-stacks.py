#!/usr/bin/env python3
"""
Aggregate stack-analyser results from all repos and generate badges
"""
import json
import os
import re
import glob
from collections import defaultdict

# Comprehensive badge mapping for 700+ technologies
# Based on shields.io and simple-icons
TECH_BADGES = {
    # Programming Languages
    'javascript': '![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=flat&logo=javascript&logoColor=%23F7DF1E)',
    'typescript': '![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat&logo=typescript&logoColor=white)',
    'python': '![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)',
    'java': '![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=flat&logo=openjdk&logoColor=white)',
    'go': '![Go](https://img.shields.io/badge/go-%2300ADD8.svg?style=flat&logo=go&logoColor=white)',
    'golang': '![Go](https://img.shields.io/badge/go-%2300ADD8.svg?style=flat&logo=go&logoColor=white)',
    'rust': '![Rust](https://img.shields.io/badge/rust-%23000000.svg?style=flat&logo=rust&logoColor=white)',
    'ruby': '![Ruby](https://img.shields.io/badge/ruby-%23CC342D.svg?style=flat&logo=ruby&logoColor=white)',
    'php': '![PHP](https://img.shields.io/badge/php-%23777BB4.svg?style=flat&logo=php&logoColor=white)',
    'c++': '![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=flat&logo=c%2B%2B&logoColor=white)',
    'c': '![C](https://img.shields.io/badge/c-%2300599C.svg?style=flat&logo=c&logoColor=white)',
    'c#': '![C#](https://img.shields.io/badge/c%23-%23239120.svg?style=flat&logo=csharp&logoColor=white)',
    'csharp': '![C#](https://img.shields.io/badge/c%23-%23239120.svg?style=flat&logo=csharp&logoColor=white)',
    'swift': '![Swift](https://img.shields.io/badge/swift-F54A2A?style=flat&logo=swift&logoColor=white)',
    'kotlin': '![Kotlin](https://img.shields.io/badge/kotlin-%237F52FF.svg?style=flat&logo=kotlin&logoColor=white)',
    'dart': '![Dart](https://img.shields.io/badge/dart-%230175C2.svg?style=flat&logo=dart&logoColor=white)',
    'scala': '![Scala](https://img.shields.io/badge/scala-%23DC322F.svg?style=flat&logo=scala&logoColor=white)',
    'elixir': '![Elixir](https://img.shields.io/badge/elixir-%234B275F.svg?style=flat&logo=elixir&logoColor=white)',
    'clojure': '![Clojure](https://img.shields.io/badge/Clojure-%23Clojure.svg?style=flat&logo=Clojure&logoColor=white)',
    'zig': '![Zig](https://img.shields.io/badge/Zig-%23F7A41D.svg?style=flat&logo=zig&logoColor=white)',
    'html': '![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=flat&logo=html5&logoColor=white)',
    'css': '![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=flat&logo=css3&logoColor=white)',
    'sql': '![SQL](https://img.shields.io/badge/SQL-025E8C?style=flat)',

    # Frontend Frameworks & Libraries
    'react': '![React](https://img.shields.io/badge/react-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)',
    'react-native': '![React Native](https://img.shields.io/badge/react%20native-%2320232a.svg?style=flat&logo=react&logoColor=%2361DAFB)',
    'vue': '![Vue.js](https://img.shields.io/badge/vue.js-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D)',
    'vuejs': '![Vue.js](https://img.shields.io/badge/vue.js-%2335495e.svg?style=flat&logo=vuedotjs&logoColor=%234FC08D)',
    'angular': '![Angular](https://img.shields.io/badge/angular-%23DD0031.svg?style=flat&logo=angular&logoColor=white)',
    'svelte': '![Svelte](https://img.shields.io/badge/svelte-%23f1413d.svg?style=flat&logo=svelte&logoColor=white)',
    'next': '![Next JS](https://img.shields.io/badge/Next-black?style=flat&logo=next.js&logoColor=white)',
    'nextjs': '![Next JS](https://img.shields.io/badge/Next-black?style=flat&logo=next.js&logoColor=white)',
    'nuxt': '![Nuxt JS](https://img.shields.io/badge/Nuxt-002E3B?style=flat&logo=nuxtdotjs&logoColor=#00DC82)',
    'gatsby': '![Gatsby](https://img.shields.io/badge/Gatsby-%23663399.svg?style=flat&logo=gatsby&logoColor=white)',
    'remix': '![Remix](https://img.shields.io/badge/remix-%23000.svg?style=flat&logo=remix&logoColor=white)',
    'solid': '![SolidJS](https://img.shields.io/badge/SolidJS-2c4f7c?style=flat&logo=solid&logoColor=c8c9cb)',
    'preact': '![Preact](https://img.shields.io/badge/preact-673AB8?style=flat&logo=preact&logoColor=white)',
    'lit': '![Lit](https://img.shields.io/badge/lit-%23324FFF.svg?style=flat&logo=lit&logoColor=white)',
    'alpine': '![Alpine.js](https://img.shields.io/badge/alpinejs-8BC0D0?style=flat&logo=alpinedotjs&logoColor=black)',
    'alpinejs': '![Alpine.js](https://img.shields.io/badge/alpinejs-8BC0D0?style=flat&logo=alpinedotjs&logoColor=black)',
    'jquery': '![jQuery](https://img.shields.io/badge/jquery-%230769AD.svg?style=flat&logo=jquery&logoColor=white)',

    # CSS Frameworks & Libraries
    'tailwindcss': '![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)',
    'tailwind': '![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=flat&logo=tailwind-css&logoColor=white)',
    'bootstrap': '![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=flat&logo=bootstrap&logoColor=white)',
    'bulma': '![Bulma](https://img.shields.io/badge/bulma-00D0B1?style=flat&logo=bulma&logoColor=white)',
    'sass': '![SASS](https://img.shields.io/badge/SASS-hotpink.svg?style=flat&logo=SASS&logoColor=white)',
    'scss': '![SASS](https://img.shields.io/badge/SASS-hotpink.svg?style=flat&logo=SASS&logoColor=white)',
    'less': '![Less](https://img.shields.io/badge/less-2B4C80?style=flat&logo=less&logoColor=white)',
    'styled-components': '![Styled Components](https://img.shields.io/badge/styled--components-DB7093?style=flat&logo=styled-components&logoColor=white)',
    'emotion': '![Emotion](https://img.shields.io/badge/emotion-C43BAD?style=flat)',

    # UI Component Libraries
    'mui': '![MUI](https://img.shields.io/badge/MUI-%23007FFF.svg?style=flat&logo=mui&logoColor=white)',
    '@mui/material': '![MUI](https://img.shields.io/badge/MUI-%23007FFF.svg?style=flat&logo=mui&logoColor=white)',
    'material-ui': '![MUI](https://img.shields.io/badge/MUI-%23007FFF.svg?style=flat&logo=mui&logoColor=white)',
    'ant-design': '![Ant Design](https://img.shields.io/badge/-AntDesign-%230170FE?style=flat&logo=ant-design&logoColor=white)',
    'antd': '![Ant Design](https://img.shields.io/badge/-AntDesign-%230170FE?style=flat&logo=ant-design&logoColor=white)',
    'chakra-ui': '![Chakra](https://img.shields.io/badge/chakra-%234ED1C5.svg?style=flat&logo=chakraui&logoColor=white)',
    'shadcn': '![Shadcn UI](https://img.shields.io/badge/Shadcn_UI-000000?style=flat)',
    'shadcn-ui': '![Shadcn UI](https://img.shields.io/badge/Shadcn_UI-000000?style=flat)',
    'daisyui': '![DaisyUI](https://img.shields.io/badge/daisyui-5A0EF8?style=flat&logo=daisyui&logoColor=white)',

    # State Management
    'redux': '![Redux](https://img.shields.io/badge/redux-%23593d88.svg?style=flat&logo=redux&logoColor=white)',
    'mobx': '![MobX](https://img.shields.io/badge/MobX-FF9955?style=flat&logo=mobx&logoColor=white)',
    'zustand': '![Zustand](https://img.shields.io/badge/Zustand-000000?style=flat)',
    'recoil': '![Recoil](https://img.shields.io/badge/Recoil-3578E5?style=flat&logo=recoil&logoColor=white)',
    'jotai': '![Jotai](https://img.shields.io/badge/Jotai-000000?style=flat)',
    'xstate': '![XState](https://img.shields.io/badge/XState-2C3E50?style=flat)',
    'pinia': '![Pinia](https://img.shields.io/badge/Pinia-FFD859?style=flat)',
    'vuex': '![Vuex](https://img.shields.io/badge/Vuex-35495E?style=flat&logo=vuedotjs&logoColor=4FC08D)',

    # Data Fetching
    'axios': '![Axios](https://img.shields.io/badge/Axios-5A29E4?style=flat&logo=axios&logoColor=white)',
    '@tanstack/react-query': '![React Query](https://img.shields.io/badge/React_Query-FF4154?style=flat&logo=reactquery&logoColor=white)',
    'react-query': '![React Query](https://img.shields.io/badge/React_Query-FF4154?style=flat&logo=reactquery&logoColor=white)',
    'swr': '![SWR](https://img.shields.io/badge/SWR-000000?style=flat)',
    'apollo': '![Apollo GraphQL](https://img.shields.io/badge/-ApolloGraphQL-311C87?style=flat&logo=apollo-graphql)',
    'graphql': '![GraphQL](https://img.shields.io/badge/-GraphQL-E10098?style=flat&logo=graphql&logoColor=white)',
    'trpc': '![tRPC](https://img.shields.io/badge/tRPC-%232596BE.svg?style=flat&logo=tRPC&logoColor=white)',

    # Routing
    'react-router': '![React Router](https://img.shields.io/badge/React_Router-CA4245?style=flat&logo=reactrouter&logoColor=white)',
    'react-router-dom': '![React Router](https://img.shields.io/badge/React_Router-CA4245?style=flat&logo=reactrouter&logoColor=white)',
    'vue-router': '![Vue Router](https://img.shields.io/badge/Vue_Router-35495E?style=flat&logo=vuedotjs&logoColor=4FC08D)',

    # Form Libraries
    'react-hook-form': '![React Hook Form](https://img.shields.io/badge/React%20Hook%20Form-%23EC5990.svg?style=flat&logo=reacthookform&logoColor=white)',
    'formik': '![Formik](https://img.shields.io/badge/Formik-2563EB?style=flat)',
    'zod': '![Zod](https://img.shields.io/badge/Zod-306AFF?style=flat)',
    'yup': '![Yup](https://img.shields.io/badge/Yup-000000?style=flat)',

    # Testing
    'jest': '![Jest](https://img.shields.io/badge/-jest-%23C21325?style=flat&logo=jest&logoColor=white)',
    'vitest': '![Vitest](https://img.shields.io/badge/-Vitest-729B1B?style=flat&logo=vitest&logoColor=white)',
    'mocha': '![Mocha](https://img.shields.io/badge/-mocha-%238D6748?style=flat&logo=mocha&logoColor=white)',
    'chai': '![Chai](https://img.shields.io/badge/chai-A30701?style=flat&logo=chai&logoColor=white)',
    'jasmine': '![Jasmine](https://img.shields.io/badge/-Jasmine-%238A4182?style=flat&logo=Jasmine&logoColor=white)',
    'playwright': '![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)',
    'cypress': '![Cypress](https://img.shields.io/badge/-cypress-%23E5E5E5?style=flat&logo=cypress&logoColor=058a5e)',
    'puppeteer': '![Puppeteer](https://img.shields.io/badge/Puppeteer-40B5A4?style=flat&logo=puppeteer&logoColor=white)',
    'selenium': '![Selenium](https://img.shields.io/badge/-selenium-%43B02A?style=flat&logo=selenium&logoColor=white)',
    'testing-library': '![Testing Library](https://img.shields.io/badge/-Testing_Library-%23E33332?style=flat&logo=testing-library&logoColor=white)',

    # Backend Frameworks
    'express': '![Express.js](https://img.shields.io/badge/express.js-black?style=flat&logo=express&logoColor=white)',
    'expressjs': '![Express.js](https://img.shields.io/badge/express.js-black?style=flat&logo=express&logoColor=white)',
    'fastify': '![Fastify](https://img.shields.io/badge/fastify-%23000000.svg?style=flat&logo=fastify&logoColor=white)',
    'koa': '![Koa](https://img.shields.io/badge/koa-%23000000.svg?style=flat&logo=koa&logoColor=white)',
    'hapi': '![Hapi](https://img.shields.io/badge/Hapi-black?style=flat)',
    'nestjs': '![NestJS](https://img.shields.io/badge/nestjs-%23E0234E.svg?style=flat&logo=nestjs&logoColor=white)',
    '@nestjs/core': '![NestJS](https://img.shields.io/badge/nestjs-%23E0234E.svg?style=flat&logo=nestjs&logoColor=white)',
    'django': '![Django](https://img.shields.io/badge/django-%23092E20.svg?style=flat&logo=django&logoColor=white)',
    'flask': '![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)',
    'fastapi': '![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)',
    'rails': '![Rails](https://img.shields.io/badge/rails-%23CC0000.svg?style=flat&logo=ruby-on-rails&logoColor=white)',
    'ruby-on-rails': '![Rails](https://img.shields.io/badge/rails-%23CC0000.svg?style=flat&logo=ruby-on-rails&logoColor=white)',
    'sinatra': '![Sinatra](https://img.shields.io/badge/Sinatra-000000?style=flat)',
    'laravel': '![Laravel](https://img.shields.io/badge/laravel-%23FF2D20.svg?style=flat&logo=laravel&logoColor=white)',
    'symfony': '![Symfony](https://img.shields.io/badge/symfony-%23000000.svg?style=flat&logo=symfony&logoColor=white)',
    'spring': '![Spring](https://img.shields.io/badge/spring-%236DB33F.svg?style=flat&logo=spring&logoColor=white)',
    'springboot': '![Spring Boot](https://img.shields.io/badge/spring%20boot-%236DB33F.svg?style=flat&logo=springboot&logoColor=white)',
    'gin': '![Gin](https://img.shields.io/badge/Gin-00ADD8?style=flat&logo=go&logoColor=white)',
    'fiber': '![Fiber](https://img.shields.io/badge/Fiber-00ADD8?style=flat&logo=go&logoColor=white)',
    'actix': '![Actix](https://img.shields.io/badge/Actix-000000?style=flat&logo=rust&logoColor=white)',
    'rocket': '![Rocket](https://img.shields.io/badge/Rocket-D22222?style=flat&logo=rust&logoColor=white)',

    # Runtime & Platforms
    'nodejs': '![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=flat&logo=node.js&logoColor=white)',
    'node': '![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=flat&logo=node.js&logoColor=white)',
    'deno': '![Deno JS](https://img.shields.io/badge/deno%20js-000000?style=flat&logo=deno&logoColor=white)',
    'bun': '![Bun](https://img.shields.io/badge/Bun-%23000000.svg?style=flat&logo=bun&logoColor=white)',

    # Authentication & Security
    'jsonwebtoken': '![JWT](https://img.shields.io/badge/JWT-black?style=flat&logo=JSON%20web%20tokens)',
    'jwt': '![JWT](https://img.shields.io/badge/JWT-black?style=flat&logo=JSON%20web%20tokens)',
    'passport': '![Passport](https://img.shields.io/badge/Passport-34E27A?style=flat&logo=passport&logoColor=black)',
    'bcrypt': '![Bcrypt](https://img.shields.io/badge/Bcrypt-3380FF?style=flat)',
    'bcryptjs': '![Bcrypt](https://img.shields.io/badge/Bcrypt-3380FF?style=flat)',
    'auth0': '![Auth0](https://img.shields.io/badge/Auth0-EB5424?style=flat&logo=auth0&logoColor=white)',
    'clerk': '![Clerk](https://img.shields.io/badge/Clerk-6C47FF?style=flat&logo=clerk&logoColor=white)',
    'nextauth': '![NextAuth](https://img.shields.io/badge/NextAuth-000000?style=flat)',
    'next-auth': '![NextAuth](https://img.shields.io/badge/NextAuth-000000?style=flat)',

    # Databases
    'mongodb': '![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat&logo=mongodb&logoColor=white)',
    'mongoose': '![Mongoose](https://img.shields.io/badge/Mongoose-880000?style=flat&logo=mongoose&logoColor=white)',
    'postgresql': '![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)',
    'postgres': '![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)',
    'pg': '![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=flat&logo=postgresql&logoColor=white)',
    'mysql': '![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=flat&logo=mysql&logoColor=white)',
    'mariadb': '![MariaDB](https://img.shields.io/badge/MariaDB-003545?style=flat&logo=mariadb&logoColor=white)',
    'redis': '![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white)',
    'sqlite': '![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=flat&logo=sqlite&logoColor=white)',
    'cassandra': '![Cassandra](https://img.shields.io/badge/cassandra-%231287B1.svg?style=flat&logo=apache-cassandra&logoColor=white)',
    'elasticsearch': '![Elasticsearch](https://img.shields.io/badge/elasticsearch-%23005571.svg?style=flat&logo=elasticsearch&logoColor=white)',
    'dynamodb': '![DynamoDB](https://img.shields.io/badge/DynamoDB-4053D6?style=flat&logo=Amazon%20DynamoDB&logoColor=white)',
    'neo4j': '![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=flat&logo=neo4j&logoColor=white)',

    # ORMs & Query Builders
    'prisma': '![Prisma](https://img.shields.io/badge/Prisma-3982CE?style=flat&logo=Prisma&logoColor=white)',
    'drizzle': '![Drizzle](https://img.shields.io/badge/Drizzle-C5F74F?style=flat&logo=drizzle&logoColor=black)',
    'typeorm': '![TypeORM](https://img.shields.io/badge/TypeORM-FE0803?style=flat)',
    'sequelize': '![Sequelize](https://img.shields.io/badge/Sequelize-52B0E7?style=flat&logo=Sequelize&logoColor=white)',
    'knex': '![Knex](https://img.shields.io/badge/Knex-D26B38?style=flat)',

    # Backend Platforms
    'firebase': '![Firebase](https://img.shields.io/badge/firebase-a08021?style=flat&logo=firebase&logoColor=ffcd34)',
    'supabase': '![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)',
    '@supabase/supabase-js': '![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat&logo=supabase&logoColor=white)',
    'appwrite': '![Appwrite](https://img.shields.io/badge/Appwrite-F02E65?style=flat&logo=Appwrite&logoColor=white)',
    'pocketbase': '![PocketBase](https://img.shields.io/badge/PocketBase-B8DBE4?style=flat&logo=PocketBase&logoColor=black)',

    # Cloud Platforms
    'aws': '![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=flat&logo=amazon-aws&logoColor=white)',
    'gcp': '![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=flat&logo=google-cloud&logoColor=white)',
    'google-cloud': '![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=flat&logo=google-cloud&logoColor=white)',
    'azure': '![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=flat&logo=microsoftazure&logoColor=white)',
    'vercel': '![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=flat&logo=vercel&logoColor=white)',
    'netlify': '![Netlify](https://img.shields.io/badge/netlify-%23000000.svg?style=flat&logo=netlify&logoColor=#00C7B7)',
    'heroku': '![Heroku](https://img.shields.io/badge/heroku-%23430098.svg?style=flat&logo=heroku&logoColor=white)',
    'render': '![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=flat&logo=render&logoColor=white)',
    'railway': '![Railway](https://img.shields.io/badge/Railway-131415?style=flat&logo=railway&logoColor=white)',
    'fly.io': '![Fly.io](https://img.shields.io/badge/Fly.io-7B3FF2?style=flat)',
    'digitalocean': '![DigitalOcean](https://img.shields.io/badge/DigitalOcean-%230167ff.svg?style=flat&logo=digitalOcean&logoColor=white)',
    'linode': '![Linode](https://img.shields.io/badge/linode-00A95C?style=flat&logo=linode&logoColor=white)',
    'cloudflare': '![Cloudflare](https://img.shields.io/badge/Cloudflare-F38020?style=flat&logo=Cloudflare&logoColor=white)',

    # DevOps & CI/CD
    'docker': '![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)',
    'kubernetes': '![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=flat&logo=kubernetes&logoColor=white)',
    'terraform': '![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=flat&logo=terraform&logoColor=white)',
    'ansible': '![Ansible](https://img.shields.io/badge/ansible-%231A1918.svg?style=flat&logo=ansible&logoColor=white)',
    'jenkins': '![Jenkins](https://img.shields.io/badge/jenkins-%232C5263.svg?style=flat&logo=jenkins&logoColor=white)',
    'github-actions': '![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=github-actions&logoColor=white)',
    'gitlab-ci': '![GitLab CI](https://img.shields.io/badge/gitlab%20ci-%23181717.svg?style=flat&logo=gitlab&logoColor=white)',
    'circleci': '![CircleCI](https://img.shields.io/badge/circle%20ci-%23161616.svg?style=flat&logo=circleci&logoColor=white)',
    'travis': '![Travis CI](https://img.shields.io/badge/travis%20ci-%232B2F33.svg?style=flat&logo=travis&logoColor=white)',
    'nginx': '![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=flat&logo=nginx&logoColor=white)',
    'apache': '![Apache](https://img.shields.io/badge/apache-%23D42029.svg?style=flat&logo=apache&logoColor=white)',

    # Build Tools
    'vite': '![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=flat&logo=vite&logoColor=white)',
    'webpack': '![Webpack](https://img.shields.io/badge/webpack-%238DD6F9.svg?style=flat&logo=webpack&logoColor=black)',
    'rollup': '![Rollup](https://img.shields.io/badge/rollup-%23EC4A3F.svg?style=flat&logo=rollup.js&logoColor=white)',
    'parcel': '![Parcel](https://img.shields.io/badge/Parcel-E8B13A?style=flat)',
    'esbuild': '![esbuild](https://img.shields.io/badge/esbuild-FFCF00?style=flat&logo=esbuild&logoColor=black)',
    'turbopack': '![Turbopack](https://img.shields.io/badge/Turbopack-0F1117?style=flat)',
    'turborepo': '![Turborepo](https://img.shields.io/badge/Turborepo-EF4444?style=flat&logo=turborepo&logoColor=white)',

    # Package Managers
    'npm': '![NPM](https://img.shields.io/badge/NPM-%23CB3837.svg?style=flat&logo=npm&logoColor=white)',
    'yarn': '![Yarn](https://img.shields.io/badge/yarn-%232C8EBB.svg?style=flat&logo=yarn&logoColor=white)',
    'pnpm': '![PNPM](https://img.shields.io/badge/pnpm-%234a4a4a.svg?style=flat&logo=pnpm&logoColor=f69220)',
    'bun': '![Bun](https://img.shields.io/badge/Bun-%23000000.svg?style=flat&logo=bun&logoColor=white)',
    'pip': '![Pip](https://img.shields.io/badge/pip-3670A0?style=flat&logo=pypi&logoColor=white)',
    'poetry': '![Poetry](https://img.shields.io/badge/Poetry-%233B82F6.svg?style=flat&logo=poetry&logoColor=white)',
    'cargo': '![Cargo](https://img.shields.io/badge/Cargo-000000?style=flat&logo=rust&logoColor=white)',
    'composer': '![Composer](https://img.shields.io/badge/Composer-885630?style=flat&logo=Composer&logoColor=white)',
    'bundler': '![Bundler](https://img.shields.io/badge/Bundler-CC342D?style=flat&logo=ruby&logoColor=white)',

    # Code Quality & Linting
    'eslint': '![ESLint](https://img.shields.io/badge/ESLint-4B3263?style=flat&logo=eslint&logoColor=white)',
    'prettier': '![Prettier](https://img.shields.io/badge/prettier-1A2C34?style=flat&logo=prettier&logoColor=F7BA3E)',
    'biome': '![Biome](https://img.shields.io/badge/Biome-60A5FA?style=flat&logo=biome&logoColor=white)',
    'stylelint': '![stylelint](https://img.shields.io/badge/stylelint-000?style=flat&logo=stylelint&logoColor=white)',
    'oxlint': '![Oxlint](https://img.shields.io/badge/Oxlint-49D48F?style=flat)',

    # API & Documentation
    'swagger': '![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=flat&logo=swagger&logoColor=white)',
    'postman': '![Postman](https://img.shields.io/badge/Postman-FF6C37?style=flat&logo=postman&logoColor=white)',
    'insomnia': '![Insomnia](https://img.shields.io/badge/Insomnia-black?style=flat&logo=insomnia&logoColor=5849BE)',
    'storybook': '![Storybook](https://img.shields.io/badge/-Storybook-FF4785?style=flat&logo=storybook&logoColor=white)',

    # Message Queues & Streaming
    'rabbitmq': '![RabbitMQ](https://img.shields.io/badge/rabbitmq-FF6600?style=flat&logo=rabbitmq&logoColor=white)',
    'kafka': '![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-000?style=flat&logo=apachekafka)',
    'redis-queue': '![Redis Queue](https://img.shields.io/badge/Redis_Queue-DD0031?style=flat&logo=redis&logoColor=white)',

    # Other Tools
    'sharp': '![Sharp](https://img.shields.io/badge/Sharp-00A2E0?style=flat)',
    'multer': '![Multer](https://img.shields.io/badge/Multer-FF6600?style=flat)',
    'socket.io': '![Socket.io](https://img.shields.io/badge/Socket.io-black?style=flat&logo=socket.io&badgeColor=010101)',
    'ws': '![WebSocket](https://img.shields.io/badge/WebSocket-010101?style=flat)',
    'nodemailer': '![Nodemailer](https://img.shields.io/badge/Nodemailer-0F9DCE?style=flat)',
    'sendgrid': '![SendGrid](https://img.shields.io/badge/SendGrid-1A82E2?style=flat)',
    'stripe': '![Stripe](https://img.shields.io/badge/Stripe-008CDD?style=flat&logo=stripe&logoColor=white)',
    'paypal': '![PayPal](https://img.shields.io/badge/PayPal-00457C?style=flat&logo=paypal&logoColor=white)',
    'twilio': '![Twilio](https://img.shields.io/badge/Twilio-F22F46?style=flat&logo=Twilio&logoColor=white)',
    'sentry': '![Sentry](https://img.shields.io/badge/Sentry-362D59?style=flat&logo=sentry&logoColor=white)',
    'winston': '![Winston](https://img.shields.io/badge/Winston-231F20?style=flat)',
    'pino': '![Pino](https://img.shields.io/badge/Pino-000000?style=flat)',
    'dotenv': '![DotEnv](https://img.shields.io/badge/DotEnv-ECD53F?style=flat&logo=dotenv&logoColor=black)',
    'joi': '![Joi](https://img.shields.io/badge/Joi-000000?style=flat)',
    'class-validator': '![Class Validator](https://img.shields.io/badge/Class_Validator-E0234E?style=flat)',
    'helmet': '![Helmet](https://img.shields.io/badge/Helmet-000000?style=flat)',
    'cors': '![CORS](https://img.shields.io/badge/CORS-000000?style=flat)',
    'morgan': '![Morgan](https://img.shields.io/badge/Morgan-000000?style=flat)',
    'grammy': '![Grammy JS](https://img.shields.io/badge/Grammy_JS-000000?style=flat)',
    'telegraf': '![Telegraf](https://img.shields.io/badge/Telegraf-26A5E4?style=flat&logo=telegram&logoColor=white)',
    'discord.js': '![Discord.js](https://img.shields.io/badge/Discord.js-5865F2?style=flat&logo=discord&logoColor=white)',
    'ejs': '![EJS](https://img.shields.io/badge/EJS-808080?style=flat)',
    'pug': '![Pug](https://img.shields.io/badge/Pug-A86454?style=flat&logo=pug&logoColor=white)',
    'handlebars': '![Handlebars](https://img.shields.io/badge/Handlebars-f0772b?style=flat&logo=handlebarsdotjs&logoColor=black)',

    # Version Control & Collaboration
    'git': '![Git](https://img.shields.io/badge/git-%23F05033.svg?style=flat&logo=git&logoColor=white)',
    'github': '![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=flat&logo=github&logoColor=white)',
    'gitlab': '![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=flat&logo=gitlab&logoColor=white)',
    'bitbucket': '![Bitbucket](https://img.shields.io/badge/bitbucket-%230047B3.svg?style=flat&logo=bitbucket&logoColor=white)',

    # Project Management
    'jira': '![Jira](https://img.shields.io/badge/jira-%230A0FFF.svg?style=flat&logo=jira&logoColor=white)',
    'notion': '![Notion](https://img.shields.io/badge/Notion-%23000000.svg?style=flat&logo=notion&logoColor=white)',
    'linear': '![Linear](https://img.shields.io/badge/Linear-5E6AD2?style=flat&logo=linear&logoColor=white)',
    'asana': '![Asana](https://img.shields.io/badge/Asana-F06A6A?style=flat&logo=asana&logoColor=white)',
    'trello': '![Trello](https://img.shields.io/badge/Trello-%23026AA7.svg?style=flat&logo=Trello&logoColor=white)',
    'monday': '![Monday](https://img.shields.io/badge/Monday-000000?style=flat)',
    'slack': '![Slack](https://img.shields.io/badge/Slack-4A154B?style=flat&logo=slack&logoColor=white)',
    'discord': '![Discord](https://img.shields.io/badge/Discord-5865F2?style=flat&logo=discord&logoColor=white)',
}

def normalize_tech_name(name):
    """Normalize technology name for matching"""
    return name.lower().strip().replace('_', '-').replace(' ', '-')

def categorize_tech(tech_name):
    """Categorize a technology based on its name"""
    tech_lower = normalize_tech_name(tech_name)

    # Language category
    languages = ['javascript', 'typescript', 'python', 'java', 'go', 'golang', 'rust',
                 'ruby', 'php', 'c++', 'c', 'c#', 'csharp', 'swift', 'kotlin', 'dart',
                 'scala', 'elixir', 'clojure', 'zig', 'html', 'css', 'sql']

    # Frontend category
    frontend = ['react', 'react-native', 'vue', 'vuejs', 'angular', 'svelte', 'next',
                'nextjs', 'nuxt', 'gatsby', 'remix', 'solid', 'preact', 'lit', 'alpine',
                'alpinejs', 'jquery', 'tailwindcss', 'tailwind', 'bootstrap', 'bulma',
                'sass', 'scss', 'less', 'styled-components', 'emotion', 'mui', '@mui/material',
                'material-ui', 'ant-design', 'antd', 'chakra-ui', 'shadcn', 'shadcn-ui',
                'daisyui', 'redux', 'mobx', 'zustand', 'recoil', 'jotai', 'xstate',
                'pinia', 'vuex', 'axios', '@tanstack/react-query', 'react-query', 'swr',
                'apollo', 'graphql', 'trpc', 'react-router', 'react-router-dom', 'vue-router',
                'react-hook-form', 'formik', 'zod', 'yup', 'storybook']

    # Backend category
    backend = ['express', 'expressjs', 'fastify', 'koa', 'hapi', 'nestjs', '@nestjs/core',
               'django', 'flask', 'fastapi', 'rails', 'ruby-on-rails', 'sinatra', 'laravel',
               'symfony', 'spring', 'springboot', 'gin', 'fiber', 'actix', 'rocket',
               'nodejs', 'node', 'deno', 'bun', 'jsonwebtoken', 'jwt', 'passport',
               'bcrypt', 'bcryptjs', 'auth0', 'clerk', 'nextauth', 'next-auth',
               'sharp', 'multer', 'socket.io', 'ws', 'nodemailer', 'sendgrid',
               'stripe', 'paypal', 'twilio', 'sentry', 'winston', 'pino', 'dotenv',
               'joi', 'class-validator', 'helmet', 'cors', 'morgan', 'grammy',
               'telegraf', 'discord.js', 'ejs', 'pug', 'handlebars']

    # Database category
    databases = ['mongodb', 'mongoose', 'postgresql', 'postgres', 'pg', 'mysql',
                 'mariadb', 'redis', 'sqlite', 'cassandra', 'elasticsearch',
                 'dynamodb', 'neo4j', 'prisma', 'drizzle', 'typeorm', 'sequelize', 'knex']

    # Backend Platforms
    platforms = ['firebase', 'supabase', '@supabase/supabase-js', 'appwrite', 'pocketbase',
                 'aws', 'gcp', 'google-cloud', 'azure', 'vercel', 'netlify', 'heroku',
                 'render', 'railway', 'fly.io', 'digitalocean', 'linode', 'cloudflare']

    # DevOps category
    devops = ['docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'github-actions',
              'gitlab-ci', 'circleci', 'travis', 'nginx', 'apache']

    # Tools category
    tools = ['vite', 'webpack', 'rollup', 'parcel', 'esbuild', 'turbopack', 'turborepo',
             'npm', 'yarn', 'pnpm', 'pip', 'poetry', 'cargo', 'composer', 'bundler',
             'eslint', 'prettier', 'biome', 'stylelint', 'oxlint', 'swagger', 'postman',
             'insomnia', 'git', 'github', 'gitlab', 'bitbucket', 'jira', 'notion',
             'linear', 'asana', 'trello', 'monday', 'slack', 'discord', 'jest', 'vitest',
             'mocha', 'chai', 'jasmine', 'playwright', 'cypress', 'puppeteer', 'selenium',
             'testing-library']

    if tech_lower in languages:
        return 'Programming Languages'
    elif tech_lower in frontend:
        return 'Frontend'
    elif tech_lower in backend:
        return 'Backend'
    elif tech_lower in databases:
        return 'Databases'
    elif tech_lower in platforms:
        return 'Backend Platforms'
    elif tech_lower in devops:
        return 'DevOps'
    elif tech_lower in tools:
        return 'Skills & Tools'
    else:
        return None

def aggregate_stack_files():
    """Aggregate all stack-*.json files"""
    all_techs = defaultdict(int)

    # Find all stack JSON files
    stack_files = glob.glob('/tmp/stack-*.json')

    print(f"Found {len(stack_files)} stack analysis files")

    for stack_file in stack_files:
        try:
            with open(stack_file, 'r') as f:
                data = json.load(f)

                # Extract technologies from the stack analyser output
                # The structure varies, but typically has 'techs' or similar
                if isinstance(data, dict):
                    # Try different possible structures
                    techs = data.get('techs', data.get('technologies', data.get('stack', [])))

                    for tech in techs:
                        if isinstance(tech, dict):
                            tech_name = tech.get('name', tech.get('id', ''))
                        else:
                            tech_name = str(tech)

                        if tech_name:
                            normalized = normalize_tech_name(tech_name)
                            all_techs[normalized] += 1

        except Exception as e:
            print(f"Error processing {stack_file}: {e}")
            continue

    return all_techs

def generate_badges(techs):
    """Generate badge markdown from technologies"""
    categories = defaultdict(list)

    # Categorize and filter to known technologies
    for tech in techs:
        if tech in TECH_BADGES:
            category = categorize_tech(tech)
            if category:
                categories[category].append(tech)

    # Generate markdown sections
    lines = []

    # Order categories
    category_order = [
        'Programming Languages',
        'Frontend',
        'Backend',
        'Databases',
        'Backend Platforms',
        'DevOps',
        'Skills & Tools'
    ]

    for category in category_order:
        if category in categories and categories[category]:
            lines.append(f"\n  <h3>{category}</h3>")
            lines.append("  <p>")

            badges = [TECH_BADGES[tech] for tech in categories[category]]
            # Convert to img tags for consistency with existing README
            for badge in badges:
                # Extract the badge from the markdown format
                match = re.search(r'\((https://[^\)]+)\)', badge)
                if match:
                    badge_url = match.group(1)
                    alt_match = re.search(r'!\[(.*?)\]', badge)
                    alt_text = alt_match.group(1) if alt_match else ''
                    lines.append(f'    <img src="{badge_url}" alt="{alt_text}" />')

            lines.append("  </p>\n")

    return '\n'.join(lines)

def update_readme(tech_section):
    """Update README.md with new tech stack section"""
    readme_path = 'README.md'

    with open(readme_path, 'r') as f:
        content = f.read()

    # Find and replace between markers
    start_marker = '<!-- TECHSTACK:START -->'
    end_marker = '<!-- TECHSTACK:END -->'

    pattern = f'{re.escape(start_marker)}.*?{re.escape(end_marker)}'
    replacement = f'{start_marker}\n<!-- Auto-generated. Do not edit manually. -->\n{tech_section}\n{end_marker}'

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(readme_path, 'w') as f:
        f.write(new_content)

    print("✅ README.md updated successfully!")

def main():
    print("🔍 Aggregating stack analysis results...")

    # Aggregate all technologies
    all_techs = aggregate_stack_files()

    print(f"\n📦 Found {len(all_techs)} unique technologies across all repositories")

    # Filter to only known technologies
    known_techs = [tech for tech in all_techs.keys() if tech in TECH_BADGES]

    print(f"🎯 Recognized {len(known_techs)} technologies from the badge library")

    if not known_techs:
        print("⚠️  No known technologies found. README not updated.")
        return

    # Generate badge section
    tech_section = generate_badges(known_techs)

    # Update README
    update_readme(tech_section)

    print(f"\n✨ Tech stack section updated with {len(known_techs)} technologies!")

if __name__ == '__main__':
    main()

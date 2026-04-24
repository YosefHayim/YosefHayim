#!/usr/bin/env node

const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const README_PATH = path.join(ROOT, "README.md");
const OWNER = process.env.GITHUB_OWNER || "YosefHayim";
const README_REPO = process.env.README_REPO || OWNER;
const MAX_PUBLIC_REPOS = Number(process.env.MAX_PUBLIC_REPOS || "12");

function runGh(args) {
  return execFileSync("gh", args, {
    cwd: ROOT,
    encoding: "utf8",
    env: process.env,
  }).trim();
}

function fetchOwnedRepos() {
  const raw = runGh([
    "api",
    "--paginate",
    "--slurp",
    "/user/repos?per_page=100&affiliation=owner&sort=updated&direction=desc",
  ]);

  const pages = JSON.parse(raw);
  return pages
    .flat()
    .filter((repo) => repo.owner?.login === OWNER)
    .filter((repo) => repo.name !== README_REPO)
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
}

function sanitizeCell(value) {
  const text = String(value ?? "").replace(/\r?\n/g, " ").replace(/\|/g, "\\|").trim();
  return text || "—";
}

function repoTitle(repo) {
  return `**[${sanitizeCell(repo.name)}](${repo.html_url})**`;
}

function repoDescription(repo) {
  return sanitizeCell(repo.description);
}

function renderPublicTable(repos, { limit }) {
  const selected = repos.slice(0, limit);
  const header = [
    "| Repository | Description | Stars |",
    "| :--- | :--- | ---: |",
  ];

  if (selected.length === 0) {
    return [...header, "| — | No public repositories found. | — |"].join("\n");
  }

  const rows = selected.map((repo) => {
    return [
      repoTitle(repo),
      repoDescription(repo),
      sanitizeCell(repo.stargazers_count),
    ];
  });

  return header
    .concat(rows.map((row) => `| ${row.join(" | ")} |`))
    .join("\n");
}

function buildStatsLine(publicRepos, privateRepos) {
  const publicStars = publicRepos.reduce((sum, repo) => sum + (repo.stargazers_count || 0), 0);
  const privateStars = privateRepos.reduce((sum, repo) => sum + (repo.stargazers_count || 0), 0);

  return [
    `Public repos: **${publicRepos.length}**`,
    `Private repos: **${privateRepos.length}**`,
    `Public stars: **${publicStars}**`,
    `Private stars: **${privateStars}**`,
    `Last sync: **${new Date().toISOString().slice(0, 10)}**`,
  ].join(" · ");
}

function buildPrivateSummary(privateRepos) {
  return `Private repositories: **${privateRepos.length}**`;
}

function replaceSection(readme, startMarker, endMarker, content) {
  const pattern = new RegExp(`${startMarker}[\\s\\S]*?${endMarker}`);
  if (!pattern.test(readme)) {
    throw new Error(`Missing README marker block: ${startMarker} ... ${endMarker}`);
  }

  return readme.replace(pattern, `${startMarker}\n${content}\n${endMarker}`);
}

function main() {
  const repos = fetchOwnedRepos();
  const publicRepos = repos.filter((repo) => !repo.private);
  const privateRepos = repos.filter((repo) => repo.private);

  let readme = fs.readFileSync(README_PATH, "utf8");
  readme = replaceSection(
    readme,
    "<!-- PROJECTS:SUMMARY:START -->",
    "<!-- PROJECTS:SUMMARY:END -->",
    buildStatsLine(publicRepos, privateRepos),
  );
  readme = replaceSection(
    readme,
    "<!-- PROJECTS:PUBLIC:START -->",
    "<!-- PROJECTS:PUBLIC:END -->",
    renderPublicTable(publicRepos, { limit: MAX_PUBLIC_REPOS }),
  );
  readme = replaceSection(
    readme,
    "<!-- PROJECTS:PRIVATE:START -->",
    "<!-- PROJECTS:PRIVATE:END -->",
    buildPrivateSummary(privateRepos),
  );

  fs.writeFileSync(README_PATH, readme);
}

main();

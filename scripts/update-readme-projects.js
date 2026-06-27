#!/usr/bin/env node

const { execFileSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const ROOT = path.resolve(__dirname, "..");
const README_PATH = path.join(ROOT, "README.md");
const OWNER = process.env.GITHUB_OWNER || "YosefHayim";
const README_REPO = process.env.README_REPO || OWNER;
const MAX_PUBLIC_REPOS = Number(process.env.MAX_PUBLIC_REPOS || "12");

/**
 * Repos intentionally kept out of the rendered public table — scaffolding and
 * placeholder projects that aren't part of the story this profile tells.
 * Matched case-insensitively by repo name. Override with the `EXCLUDED_REPOS`
 * env var (comma-separated names) without touching this file.
 */
const EXCLUDED_REPOS = new Set(
  (process.env.EXCLUDED_REPOS ||
    "Template,portfolio,skills-bag,chatgpt-local-bridge")
    .split(",")
    .map((name) => name.trim().toLowerCase())
    .filter(Boolean),
);

function runGh(args) {
  return execFileSync("gh", args, {
    cwd: ROOT,
    encoding: "utf8",
    env: process.env,
  }).trim();
}

/**
 * Fetches repos for OWNER, sorted by recent activity.
 *
 * Tries `/user/repos` first (returns public + private). The default workflow
 * `GITHUB_TOKEN` is repo-scoped and 403s on this endpoint, so we fall back to
 * the public `/users/{owner}/repos`. Set a `PROFILE_README_TOKEN` secret
 * (PAT with `repo` scope) to keep private repos included in the summary.
 *
 * @returns {{repos: object[], includesPrivate: boolean}}
 */
function fetchOwnedRepos() {
  try {
    const raw = runGh([
      "api",
      "--paginate",
      "--slurp",
      "/user/repos?per_page=100&affiliation=owner&sort=updated&direction=desc",
    ]);
    const repos = JSON.parse(raw)
      .flat()
      .filter((repo) => repo.owner?.login === OWNER)
      .filter((repo) => repo.name !== README_REPO)
      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    return { repos, includesPrivate: true };
  } catch (err) {
    const stderr = String(err.stderr || err.message || "");
    if (!stderr.includes("Resource not accessible") && !stderr.includes("403")) {
      throw err;
    }
    console.warn(
      "[update-readme-projects] /user/repos not accessible (403). " +
        `Falling back to public-only /users/${OWNER}/repos. ` +
        "Set PROFILE_README_TOKEN secret (PAT with `repo` scope) to include private repo counts.",
    );
    const raw = runGh([
      "api",
      "--paginate",
      "--slurp",
      `/users/${OWNER}/repos?per_page=100&type=owner&sort=updated&direction=desc`,
    ]);
    const repos = JSON.parse(raw)
      .flat()
      .filter((repo) => repo.name !== README_REPO)
      .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    return { repos, includesPrivate: false };
  }
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
  const selected = [...repos]
    .sort((a, b) => {
      const starDelta = (b.stargazers_count || 0) - (a.stargazers_count || 0);
      if (starDelta !== 0) {
        return starDelta;
      }

      return new Date(b.updated_at) - new Date(a.updated_at);
    })
    .slice(0, limit);
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

function buildStatsLine(publicRepos, privateRepos, includesPrivate) {
  const publicStars = publicRepos.reduce((sum, repo) => sum + (repo.stargazers_count || 0), 0);
  const today = new Date().toISOString().slice(0, 10);

  const parts = [
    `Public repos: **${publicRepos.length}**`,
    `Public stars: **${publicStars}**`,
  ];

  if (includesPrivate) {
    const privateStars = privateRepos.reduce((sum, repo) => sum + (repo.stargazers_count || 0), 0);
    parts.splice(1, 0, `Private repos: **${privateRepos.length}**`);
    parts.push(`Private stars: **${privateStars}**`);
  }

  parts.push(`Last sync: **${today}**`);
  return parts.join(" · ");
}

function removeLegacyPrivateSection(readme) {
  return readme.replace(
    /\n#### Private Projects\n\n<!-- PROJECTS:PRIVATE:START -->[\s\S]*?<!-- PROJECTS:PRIVATE:END -->\n?/,
    "\n",
  );
}

function replaceSection(readme, startMarker, endMarker, content) {
  const pattern = new RegExp(`${startMarker}[\\s\\S]*?${endMarker}`);
  if (!pattern.test(readme)) {
    throw new Error(`Missing README marker block: ${startMarker} ... ${endMarker}`);
  }

  return readme.replace(pattern, `${startMarker}\n${content}\n${endMarker}`);
}

function main() {
  const { repos, includesPrivate } = fetchOwnedRepos();
  const publicRepos = repos.filter((repo) => !repo.private);
  const publicProjectRepos = publicRepos
    .filter((repo) => !repo.fork)
    .filter((repo) => !EXCLUDED_REPOS.has(repo.name.toLowerCase()));
  const privateRepos = repos.filter((repo) => repo.private);

  let readme = fs.readFileSync(README_PATH, "utf8");
  readme = removeLegacyPrivateSection(readme);
  readme = replaceSection(
    readme,
    "<!-- PROJECTS:SUMMARY:START -->",
    "<!-- PROJECTS:SUMMARY:END -->",
    buildStatsLine(publicRepos, privateRepos, includesPrivate),
  );
  readme = replaceSection(
    readme,
    "<!-- PROJECTS:PUBLIC:START -->",
    "<!-- PROJECTS:PUBLIC:END -->",
    renderPublicTable(publicProjectRepos, { limit: MAX_PUBLIC_REPOS }),
  );

  fs.writeFileSync(README_PATH, readme);
}

main();

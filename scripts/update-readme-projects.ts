import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const OWNER = "YosefHayim";
const PROFILE_REPO = "YosefHayim";
const BIRTH_DATE = "2000-07-17";
const README_PATH = path.join(import.meta.dirname, "..", "README.md");
const REPOS_URL = "/user/repos?affiliation=owner&per_page=100";

// Every repo I own, private ones included, minus this profile repo itself.
const loadRepos = () => {
  const ghArgs = ["api", "--paginate", "--slurp", REPOS_URL];
  const pagesJson = execFileSync("gh", ghArgs, { encoding: "utf8" });
  const pages = JSON.parse(pagesJson);
  return pages.flat().filter((repo) => repo.owner?.login === OWNER && repo.name !== PROFILE_REPO);
};

const summaryLine = (repos, today: string): string => {
  const publicRepos = repos.filter((repo) => !repo.private);
  const stars = publicRepos.reduce((total, repo) => total + repo.stargazers_count, 0);
  return [
    `Public repos: **${publicRepos.length}**`,
    `Public stars: **${stars}**`,
    `Private repos: **${repos.length - publicRepos.length}**`,
    `Last sync: **${today}**`,
  ].join(" · ");
};

const byStarsThenRecent = (left, right): number => {
  const starDelta = right.stargazers_count - left.stargazers_count;
  if (starDelta !== 0) return starDelta;
  return Date.parse(right.updated_at) - Date.parse(left.updated_at);
};

// Descriptions are free text, and a stray pipe or newline would break the table.
const cell = (description: string | null): string => {
  const cleaned = (description ?? "").replace(/\r?\n/g, " ").replace(/\|/g, "\\|").trim();
  return cleaned === "" ? "—" : cleaned;
};

const repoRow = (repo): string => {
  const { name, html_url: url, description, stargazers_count: stars } = repo;
  return `| **[${name}](${url})** | ${cell(description)} | ${stars} |`;
};

// Forks count toward the totals but do not get a row.
const projectsTable = (publicRepos): string => {
  const rows = publicRepos.filter((repo) => !repo.fork).sort(byStarsThenRecent);
  const header = ["| Repository | Description | ⭐ |", "| :--- | :--- | ---: |"];
  return [...header, ...rows.map(repoRow)].join("\n");
};

// "2026-08-01" vs "2000-07-17": comparing the MM-DD halves says if the birthday has passed.
const ageOn = (today: string): number => {
  const years = Number(today.slice(0, 4)) - Number(BIRTH_DATE.slice(0, 4));
  return today.slice(5) < BIRTH_DATE.slice(5) ? years - 1 : years;
};

const replaceSection = (readme: string, marker: string, content: string): string => {
  const start = `<!-- ${marker}:START -->`;
  const end = `<!-- ${marker}:END -->`;
  const section = new RegExp(`${start}[\\s\\S]*?${end}`);
  if (!section.test(readme)) throw new Error(`README is missing the ${marker} markers.`);
  return readme.replace(section, `${start}${content}${end}`);
};

const main = (): void => {
  const repos = loadRepos();
  const publicRepos = repos.filter((repo) => !repo.private);
  if (publicRepos.length === 0) throw new Error("No public repos came back; README left alone.");

  const today = new Date().toISOString().slice(0, 10);
  let readme = readFileSync(README_PATH, "utf8");
  readme = replaceSection(readme, "AGE", String(ageOn(today)));
  readme = replaceSection(readme, "PROJECTS:SUMMARY", `\n${summaryLine(repos, today)}\n`);
  readme = replaceSection(readme, "PROJECTS:PUBLIC", `\n${projectsTable(publicRepos)}\n`);
  writeFileSync(README_PATH, readme);
};

main();

"""src/datasets/factory/harbor.py -- Harbor task output format."""

from __future__ import annotations

import base64
import os
import re
import shlex
import textwrap
from pathlib import Path

from datasets.metadata.schema import CandidateArtifact
from datasets.patterns import TEST_FILE_RE

_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")
_VALID_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
_VALID_CLONE_URL_RE = re.compile(
    r"^https://[A-Za-z0-9._\-]+/[A-Za-z0-9._\-/]+(\.git)?$"
)


def _extract_added_lines(patch: str) -> str:
    """Extract only added lines from a unified diff patch."""
    lines = []
    for line in patch.split("\n"):
        if line.startswith("@@"):
            continue
        if line.startswith("+"):
            lines.append(line[1:])
        elif not line.startswith("-"):
            lines.append(line)
    return "\n".join(lines)


def _repo_slug(repo_full_name: str) -> str:
    """Convert 'org/repo-name' to 'repo-name'."""
    return repo_full_name.split("/")[-1] if "/" in repo_full_name else repo_full_name


class HarborTaskFactory:
    @property
    def format_name(self) -> str:
        return "harbor"

    def create(
        self,
        candidate: CandidateArtifact,
        output_dir: Path,
        task_name: str,
    ) -> Path:
        task_dir = output_dir / task_name
        task_dir.mkdir(parents=True, exist_ok=True)

        self._write_instruction(task_dir, candidate)
        self._write_toml(task_dir, candidate, task_name)
        self._write_dockerfile(task_dir, candidate)
        self._write_tests(task_dir, candidate)
        self._write_solution(task_dir, candidate)

        issues = self.validate(task_dir, candidate)
        if issues:
            import logging
            logger = logging.getLogger(__name__)
            for issue in issues:
                logger.warning("task %s: %s", task_name, issue)

        return task_dir

    def validate(
        self,
        task_dir: Path,
        candidate: CandidateArtifact,
    ) -> list[str]:
        """Validate a generated task. Returns a list of issues (empty = valid)."""
        issues: list[str] = []
        raw = candidate.raw_data

        # Must have base_sha and repo_clone_url for reproducible builds
        base_sha = raw.get("base_sha", "")
        repo_url = raw.get("repo_clone_url", "")
        if not base_sha or not _VALID_SHA_RE.fullmatch(base_sha):
            issues.append("missing or invalid base_sha — Dockerfile won't checkout correct commit")
        if not repo_url or not _VALID_CLONE_URL_RE.fullmatch(repo_url):
            issues.append("missing or invalid repo_clone_url — Dockerfile won't clone repo")

        # Must have source patches (not just test patches)
        patches = raw.get("patches", {})
        source_patches = {
            f: p for f, p in patches.items()
            if not TEST_FILE_RE.search(f) and p.strip()
        }
        if not source_patches:
            issues.append("no source patches — solve.sh has no oracle solution")

        # Solution patch should apply cleanly to base_sha (optional, expensive)
        solve_sh = task_dir / "solution" / "solve.sh"
        if solve_sh.exists() and "No source patches" in solve_sh.read_text():
            issues.append("solve.sh is placeholder — no actual solution")

        return issues

    def create_dataset_toml(self, output_dir: Path, dataset_name: str) -> None:
        toml = textwrap.dedent(f"""\
            [dataset]
            name = "rhai/{dataset_name}"
            version = "1.0.0"
            description = "Auto-generated dataset from rhai-datasets"
        """)
        (output_dir / "dataset.toml").write_text(toml)

    def _write_instruction(self, task_dir: Path, candidate: CandidateArtifact) -> None:
        content = f"# {candidate.title}\n\n{candidate.description}\n"
        if candidate.raw_data.get("files"):
            content += "\n## Files involved\n"
            for f in candidate.raw_data["files"]:
                content += f"- `{f}`\n"
        (task_dir / "instruction.md").write_text(content)

    def _write_toml(
        self, task_dir: Path, candidate: CandidateArtifact, task_name: str
    ) -> None:
        difficulty = (
            candidate.difficulty_bucket.value
            if candidate.difficulty_bucket
            else "medium"
        )
        repo_slug = _repo_slug(candidate.raw_data.get("repo_full_name", "unknown"))
        source = candidate.source_type.value.split("_")[0]
        name = f"rhai-{source}/{repo_slug}/{task_name}"
        toml = textwrap.dedent(f"""\
            version = "1.0"
            name = "{name}"

            [metadata]
            author_name = "rhai-datasets"
            author_email = ""
            difficulty = "{difficulty}"
            difficulty_explanation = "Estimated from patch size, file count, and component spread"
            category = "{candidate.source_type.value}"
            tags = ["auto-generated", "{candidate.source_type.value}"]

            [verifier]
            timeout_sec = 900.0

            [agent]
            timeout_sec = 900.0

            [environment]
            build_timeout_sec = 600.0
            cpus = 1
            memory_mb = 4096
            storage_mb = 10240
        """)
        (task_dir / "task.toml").write_text(toml)

    def _write_dockerfile(self, task_dir: Path, candidate: CandidateArtifact) -> None:
        env_dir = task_dir / "environment"
        env_dir.mkdir(exist_ok=True)

        repo_url = candidate.raw_data.get("repo_clone_url", "")
        base_sha = candidate.raw_data.get("base_sha", "")
        url_valid = bool(repo_url and _VALID_CLONE_URL_RE.fullmatch(repo_url))
        sha_valid = bool(base_sha and _VALID_SHA_RE.fullmatch(base_sha))

        if url_valid and sha_valid:
            dockerfile = textwrap.dedent(f"""\
                FROM python:3.12-slim
                ENV DEBIAN_FRONTEND=noninteractive
                RUN apt-get update && apt-get install -y --no-install-recommends \\
                    git curl patch && rm -rf /var/lib/apt/lists/*
                RUN curl -LsSf https://astral.sh/uv/0.7.13/install.sh | sh
                WORKDIR /testbed
                RUN git clone {repo_url} /testbed \\
                    && git checkout {base_sha}
                COPY instruction.md /app/instruction.md
                COPY tests/ /tests/
                COPY solution/ /solution/
                RUN mkdir -p /logs/verifier
            """)
        else:
            dockerfile = textwrap.dedent("""\
                FROM python:3.12-slim
                ENV DEBIAN_FRONTEND=noninteractive
                RUN apt-get update && apt-get install -y --no-install-recommends \\
                    git curl patch && rm -rf /var/lib/apt/lists/*
                WORKDIR /app
                RUN mkdir -p /logs/verifier
            """)

        (env_dir / "Dockerfile").write_text(dockerfile)

    def _write_tests(self, task_dir: Path, candidate: CandidateArtifact) -> None:
        tests_dir = task_dir / "tests"
        tests_dir.mkdir(exist_ok=True)

        patches = candidate.raw_data.get("patches", {})
        test_patches = {
            fname: patch
            for fname, patch in patches.items()
            if TEST_FILE_RE.search(fname)
        }

        extracted_names: list[str] = []
        seen_names: set[str] = set()
        for filepath, patch in test_patches.items():
            filename = Path(filepath).name
            if not _SAFE_FILENAME_RE.fullmatch(filename):
                continue
            if filename in seen_names:
                stem = Path(filename).stem
                suffix = Path(filename).suffix
                counter = 1
                while f"{stem}_{counter}{suffix}" in seen_names:
                    counter += 1
                filename = f"{stem}_{counter}{suffix}"
            content = _extract_added_lines(patch)
            if content.strip():
                seen_names.add(filename)
                (tests_dir / filename).write_text(content)
                extracted_names.append(filename)

        if not extracted_names:
            (tests_dir / "test_outputs.py").write_text(
                textwrap.dedent("""\
                \"\"\"Auto-generated test scaffold. Requires manual enrichment.\"\"\"


                class TestOutputs:
                    def test_task_completed(self):
                        assert True, "Placeholder -- add real verification"
            """)
            )
            extracted_names.append("test_outputs.py")

        test_targets = " ".join(shlex.quote(f"/tests/{n}") for n in extracted_names)
        test_sh = textwrap.dedent(f"""\
            #!/bin/bash
            mkdir -p /logs/verifier
            uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 \\
              pytest --ctrf /logs/verifier/ctrf.json {test_targets} -rA -v
            if [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
            exit 0
        """)
        test_sh_path = tests_dir / "test.sh"
        test_sh_path.write_text(test_sh)
        test_sh_path.chmod(0o755)

    def _write_solution(self, task_dir: Path, candidate: CandidateArtifact) -> None:
        solution_dir = task_dir / "solution"
        solution_dir.mkdir(exist_ok=True)

        patches = candidate.raw_data.get("patches", {})
        source_patches = {
            fname: patch
            for fname, patch in patches.items()
            if not TEST_FILE_RE.search(fname) and patch.strip()
        }

        if source_patches:
            combined_patch = ""
            for fname, patch in source_patches.items():
                safe_fname = os.path.normpath(fname).lstrip("/")
                if ".." in safe_fname or os.path.isabs(safe_fname):
                    continue
                combined_patch += f"--- a/{safe_fname}\n+++ b/{safe_fname}\n{patch}\n"
            patch_b64 = base64.b64encode(combined_patch.encode()).decode()

            solve_sh = (
                "#!/bin/bash\n"
                "set -e\n"
                f"printf '%s' '{patch_b64}'"
                " | base64 -d > /tmp/solution.patch\n"
                "cd /testbed\n"
                "patch --fuzz=5 -p1 -i /tmp/solution.patch\n"
            )
        else:
            solve_sh = textwrap.dedent("""\
                #!/bin/bash
                set -e
                echo "No source patches available for oracle solution"
            """)

        solve_path = solution_dir / "solve.sh"
        solve_path.write_text(solve_sh)
        solve_path.chmod(0o755)

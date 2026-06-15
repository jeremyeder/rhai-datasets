"""src/datasets/cli.py -- Click CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click

import datasets


@click.group()
@click.version_option(version=datasets.__version__)
def main() -> None:
    """rhai-datasets -- Dataset creation and curation for Red Hat AI evaluation."""


@main.group()
def catalog() -> None:
    """Browse and manage the dataset catalog."""


@catalog.command("list")
@click.option(
    "--catalog-dir",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to catalog directory",
)
@click.option("--domain", default=None, help="Filter by domain")
@click.option(
    "--format",
    "fmt",
    default=None,
    help="Filter by format (harbor, skillsbench, mlflow)",
)
def catalog_list(
    catalog_dir: Path | None,
    domain: str | None,
    fmt: str | None,
) -> None:
    """List available datasets in the catalog."""
    from datasets.metadata.catalog import DatasetCatalog

    if catalog_dir is None:
        catalog_dir = Path("catalog/external")

    cat = DatasetCatalog.load(catalog_dir)
    entries = cat.filter(domain=domain, format=fmt)

    if not entries:
        click.echo("No datasets found.")
        return

    for entry in entries:
        domains = ", ".join(entry.domain)
        click.echo(
            f"  {entry.name:30s}  {entry.task_count:5d} tasks"
            f"  [{domains}]  ({entry.format})"
        )


@main.command()
@click.option(
    "--source",
    required=True,
    type=click.Choice(["github", "jira"]),
)
@click.option("--repo", default=None, help="GitHub repo (org/name)")
@click.option("--project", default=None, help="Jira project key")
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    default=None,
    help="API token",
)
@click.option(
    "--jira-server",
    default="https://issues.redhat.com",
    help="Jira server URL",
)
@click.option("--limit", default=50, help="Max candidates to return")
@click.option(
    "--min-score",
    default=40,
    help="Minimum suitability score (0-100)",
)
@click.option(
    "--skip-ai-detection",
    is_flag=True,
    help="Skip AI-content detection",
)
@click.option(
    "--since",
    default=None,
    help="Only include items updated after this date (ISO format, e.g. 2025-10-23)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output JSON file",
)
def recommend(
    source: str,
    repo: str | None,
    project: str | None,
    token: str | None,
    jira_server: str,
    limit: int,
    min_score: float,
    skip_ai_detection: bool,
    since: str | None,
    output: Path | None,
) -> None:
    """Scan sources and recommend ground truth candidates."""
    import json

    from datasets.connectors.base import SourceConnector
    from datasets.recommender.pipeline import RecommenderPipeline

    connectors: list[SourceConnector] = []
    if source == "github":
        if not repo:
            raise click.UsageError("--repo required for GitHub source")
        from datasets.connectors.github import GitHubConnector

        connectors.append(GitHubConnector(token=token or "", repo=repo))
    elif source == "jira":
        if not project:
            raise click.UsageError("--project required for Jira source")
        from datasets.connectors.jira import JiraConnector

        connectors.append(
            JiraConnector(
                server=jira_server,
                token=token or "",
                project=project,
            )
        )

    pipeline = RecommenderPipeline(
        connectors=connectors,
        skip_ai_detection=skip_ai_detection,
    )
    extra_kwargs: dict[str, str] = {}
    if since:
        extra_kwargs["since"] = since
    results = pipeline.run(limit=limit, min_suitability=min_score, **extra_kwargs)

    click.echo(f"Found {len(results)} candidates (min score: {min_score})")
    bucket_counts: dict[str, int] = {"easy": 0, "medium": 0, "hard": 0}
    for c in results:
        ai_flag = ""
        if c.ai_detection:
            ai_flag = f"  AI: {c.ai_detection.overall_score:.0f}"
        suitability = c.suitability
        score = suitability.overall if suitability else 0.0
        bucket = f"  [{c.difficulty_bucket.value}]" if c.difficulty_bucket else ""
        click.echo(f"  [{score:3.0f}] {c.title[:55]:55s}{bucket}{ai_flag}")
        if c.difficulty_bucket:
            bucket_counts[c.difficulty_bucket.value] += 1
    click.echo(
        f"\nDifficulty: "
        f"easy={bucket_counts['easy']}  "
        f"medium={bucket_counts['medium']}  "
        f"hard={bucket_counts['hard']}"
    )

    if output:
        data = [c.model_dump(mode="json") for c in results]
        output.write_text(json.dumps(data, indent=2))
        click.echo(f"Written to {output}")


@main.command("create")
@click.option(
    "--from-file",
    "input_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="JSON file with accepted candidates (from recommend)",
)
@click.option(
    "--format",
    "fmt",
    required=True,
    type=click.Choice(["harbor", "skillsbench", "mlflow"]),
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("output"),
    help="Output directory",
)
def create_dataset(input_file: Path, fmt: str, output_dir: Path) -> None:
    """Create evaluation datasets from accepted candidates."""
    import json

    from datasets.factory.base import DatasetFactory
    from datasets.metadata.schema import CandidateArtifact

    with input_file.open() as f:
        data = json.load(f)

    candidates = [CandidateArtifact(**d) for d in data]

    factory: DatasetFactory
    if fmt == "harbor":
        from datasets.factory.harbor import HarborTaskFactory

        factory = HarborTaskFactory()
    elif fmt == "skillsbench":
        from datasets.factory.skillsbench import SkillsBenchTaskFactory

        factory = SkillsBenchTaskFactory()
    elif fmt == "mlflow":
        from datasets.factory.mlflow_dataset import MLflowDatasetFactory

        factory = MLflowDatasetFactory()
    else:
        raise click.UsageError(f"Unknown format: {fmt}")

    for i, candidate in enumerate(candidates):
        task_name = f"task-{i:04d}"
        result = factory.create(candidate, output_dir=output_dir, task_name=task_name)
        click.echo(f"  Created: {result}")

    if fmt == "harbor":
        dataset_name = output_dir.name
        factory.create_dataset_toml(output_dir, dataset_name)
        click.echo(f"  Created: {output_dir / 'dataset.toml'}")

    click.echo(f"Created {len(candidates)} {fmt} tasks in {output_dir}")


@main.command("validate")
@click.argument(
    "dataset_dir",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "--base-commit",
    default=None,
    help="Git commit to validate patches against (clones repo and runs git apply --check)",
)
@click.option("--fix/--no-fix", default=False, help="Remove invalid tasks")
def validate_dataset(dataset_dir: Path, base_commit: str | None, fix: bool) -> None:
    """Validate harbor tasks in a dataset directory.

    Checks each task for: valid Dockerfile (repo checkout), source patches
    in solve.sh, and optionally that patches apply to a base commit.
    """
    import base64
    import re
    import shutil
    import subprocess
    import tempfile

    tasks = sorted(
        d for d in dataset_dir.iterdir() if d.is_dir() and d.name.startswith("task-")
    )

    repo_dir = None
    if base_commit:
        dockerfile = next(
            (
                t / "environment" / "Dockerfile"
                for t in tasks
                if (t / "environment" / "Dockerfile").exists()
            ),
            None,
        )
        repo_url = None
        if dockerfile:
            m = re.search(r"git clone (\S+)", dockerfile.read_text())
            if m:
                repo_url = m.group(1)
        if repo_url:
            click.echo(f"Cloning {repo_url} at {base_commit} for patch validation...")
            tmp = tempfile.mkdtemp()
            try:
                subprocess.run(
                    ["git", "clone", "--quiet", repo_url, tmp],
                    capture_output=True,
                    timeout=120,
                    check=True,
                )
                subprocess.run(
                    ["git", "checkout", "--quiet", base_commit],
                    capture_output=True,
                    cwd=tmp,
                    check=True,
                )
                repo_dir = tmp
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                click.echo(
                    f"WARNING: git setup failed ({exc}), skipping patch validation"
                )
                shutil.rmtree(tmp, ignore_errors=True)
        else:
            click.echo(
                "WARNING: could not determine repo URL, skipping patch validation"
            )

    valid = 0
    invalid = 0
    for task_dir in tasks:
        issues = []
        name = task_dir.name

        # Check Dockerfile has git clone
        dockerfile = task_dir / "environment" / "Dockerfile"
        if dockerfile.exists():
            content = dockerfile.read_text()
            if "git clone" not in content:
                issues.append("Dockerfile missing git clone (no repo checkout)")
        else:
            issues.append("no Dockerfile")

        # Check solve.sh has real patches
        solve_sh = task_dir / "solution" / "solve.sh"
        patch_content = None
        if solve_sh.exists():
            text = solve_sh.read_text()
            if "No source patches" in text:
                issues.append("no source patches in solve.sh")
            else:
                m = re.search(r"printf\s+'%s'\s+'([A-Za-z0-9+/=]+)'", text)
                if m:
                    try:
                        patch_content = base64.b64decode(m.group(1)).decode()
                    except Exception:
                        issues.append("base64 decode failed for solution patch")
                else:
                    issues.append("no base64 patch found in solve.sh")
        else:
            issues.append("no solve.sh")

        # Check patch applies to base commit
        if repo_dir and patch_content and not issues:
            patch_file = Path(repo_dir) / "_check.patch"
            patch_file.write_text(patch_content)
            r = subprocess.run(
                ["git", "apply", "--check", str(patch_file)],
                capture_output=True,
                text=True,
                cwd=repo_dir,
            )
            if r.returncode != 0:
                first_err = (
                    r.stderr.strip().splitlines()[0] if r.stderr.strip() else "unknown"
                )
                issues.append(f"patch doesn't apply: {first_err[:60]}")

        if issues:
            icon = "✗"
            invalid += 1
            if fix:
                shutil.rmtree(task_dir)
                icon = "✗ REMOVED"
        else:
            icon = "✓"
            valid += 1

        status = "; ".join(issues) if issues else "OK"
        click.echo(f"  {icon} {name}: {status}")

    click.echo(f"\n{valid} valid, {invalid} invalid out of {len(tasks)} tasks")
    if fix and invalid:
        click.echo(f"Removed {invalid} invalid tasks")

    if repo_dir:
        shutil.rmtree(repo_dir, ignore_errors=True)

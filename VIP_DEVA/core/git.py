import asyncio
import os
import shlex
from typing import Tuple, Optional

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config
from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    # safer for environments where loop is already running
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # can't block running loop; skip in that case
            return ("", "Event loop already running, skipping pip install", 0, 0)
        return loop.run_until_complete(install_requirements())
    except RuntimeError:
        return asyncio.run(install_requirements())


def _is_hosted_runtime() -> bool:
    # Heroku sets DYNO; Render sets RENDER; many containers set KUBERNETES_SERVICE_HOST
    return bool(
        os.getenv("DYNO")
        or os.getenv("RENDER")
        or os.getenv("KUBERNETES_SERVICE_HOST")
        or os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("FLY_APP_NAME")
    )


def _build_upstream_url() -> str:
    repo_link = getattr(config, "UPSTREAM_REPO", "")
    token = getattr(config, "GIT_TOKEN", "") or ""

    if not repo_link:
        return ""

    # If token provided and URL is https://github.com/user/repo.git
    if token and repo_link.startswith("https://") and "github.com/" in repo_link:
        try:
            git_username = repo_link.split("com/")[1].split("/")[0]
            temp_repo = repo_link.split("https://")[1]
            return f"https://{git_username}:{token}@{temp_repo}"
        except Exception:
            return repo_link

    return repo_link


def git():
    log = LOGGER(__name__)

    # Default behavior: hosted runtimes me git update OFF
    # Enable only if you explicitly set AUTO_GIT_UPDATE=true
    if _is_hosted_runtime() and os.getenv("AUTO_GIT_UPDATE", "false").lower() not in ("1", "true", "yes"):
        log.info("AUTO_GIT_UPDATE is disabled on hosted runtime, skipping git updater.")
        return

    upstream_repo = _build_upstream_url()
    upstream_branch = getattr(config, "UPSTREAM_BRANCH", "main")

    if not upstream_repo:
        log.info("UPSTREAM_REPO not set, skipping git updater.")
        return

    # Open repo safely (do NOT init repo in production)
    try:
        repo = Repo(search_parent_directories=True)
        log.info("Git repo detected, updater ready.")
    except InvalidGitRepositoryError:
        log.info("No git repository found in runtime path, skipping updater.")
        return
    except GitCommandError as e:
        log.info(f"Git command error while opening repo: {e}")
        return

    # Ensure origin exists and points to upstream_repo
    try:
        if "origin" in [r.name for r in repo.remotes]:
            origin = repo.remote("origin")
            # Update URL if changed
            try:
                origin.set_url(upstream_repo)
            except Exception:
                pass
        else:
            origin = repo.create_remote("origin", upstream_repo)
    except Exception as e:
        log.info(f"Failed to set origin remote: {e}")
        return

    # Fetch + hard reset to upstream/<branch> (safe fast-forward behavior)
    try:
        log.info(f"Fetching updates from upstream: {upstream_branch}")
        origin.fetch(upstream_branch)
    except GitCommandError as e:
        log.info(f"Fetch failed (auth/remote?): {e}")
        return

    # Resolve ref
    ref_name: Optional[str] = None
    for cand in (
        f"origin/{upstream_branch}",
        f"refs/remotes/origin/{upstream_branch}",
    ):
        try:
            _ = repo.commit(cand)
            ref_name = cand
            break
        except Exception:
            pass

    if not ref_name:
        log.info(f"Upstream branch not found after fetch: {upstream_branch}")
        return

    try:
        repo.git.reset("--hard", ref_name)
        log.info(f"Updated code to {ref_name}")
    except GitCommandError as e:
        log.info(f"Reset failed: {e}")
        return

    # Optional: install requirements only if you want (and not on hosted by default)
    if os.getenv("AUTO_PIP_INSTALL", "false").lower() in ("1", "true", "yes"):
        out, err, code, _pid = install_req("pip3 install --no-cache-dir -r requirements.txt")
        if code == 0:
            log.info("requirements.txt installed successfully.")
        else:
            log.info(f"pip install failed: {err or out}")

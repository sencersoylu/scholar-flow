"""Safe Python script executor with subprocess isolation."""

import asyncio
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExecutionResult:
    """Result of a Python script execution."""

    stdout: str
    stderr: str
    return_code: int
    generated_files: list[str] = field(default_factory=list)


async def execute_python(
    script: str,
    timeout: int = 300,
    working_dir: str | None = None,
) -> ExecutionResult:
    """Execute a Python script in an isolated subprocess.

    Args:
        script: Python source code to execute.
        timeout: Maximum execution time in seconds.
        working_dir: Directory to run the script in. If None, a temp dir is created.

    Returns:
        ExecutionResult with stdout, stderr, return_code, and list of generated files.
    """
    cleanup_dir = False
    if working_dir is None:
        working_dir = tempfile.mkdtemp(prefix="statistics_mcp_")
        cleanup_dir = False  # caller or tests may need the files

    work_path = Path(working_dir)
    work_path.mkdir(parents=True, exist_ok=True)

    # Capture files before execution to detect newly generated ones
    existing_files = set(_list_files(work_path))

    # Write the script to a temp file inside the working directory
    script_file = work_path / "_run_script.py"
    script_file.write_text(script, encoding="utf-8")

    try:
        proc = await asyncio.create_subprocess_exec(
            "python3",
            str(script_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(work_path),
            env={**os.environ, "MPLBACKEND": "Agg"},
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return ExecutionResult(
            stdout="",
            stderr=f"Execution timed out after {timeout} seconds.",
            return_code=-1,
        )
    finally:
        # Clean up the script file itself
        if script_file.exists():
            script_file.unlink()

    # Detect newly created files (e.g. plots)
    current_files = set(_list_files(work_path))
    new_files = sorted(current_files - existing_files)

    return ExecutionResult(
        stdout=stdout_bytes.decode("utf-8", errors="replace"),
        stderr=stderr_bytes.decode("utf-8", errors="replace"),
        return_code=proc.returncode or 0,
        generated_files=new_files,
    )


def _list_files(directory: Path) -> list[str]:
    """List all files in a directory (non-recursive top-level + one level deep)."""
    files: list[str] = []
    if not directory.exists():
        return files
    for item in directory.rglob("*"):
        if item.is_file():
            files.append(str(item))
    return files

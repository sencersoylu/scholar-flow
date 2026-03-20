"""Tests for the Python script executor."""

import pytest

from statistics_mcp.executor import execute_python


@pytest.mark.asyncio
async def test_simple_print():
    result = await execute_python('print("hello world")')
    assert result.return_code == 0
    assert "hello world" in result.stdout
    assert result.stderr == "" or result.stderr.strip() == ""


@pytest.mark.asyncio
async def test_math_computation():
    result = await execute_python("print(2 + 3)")
    assert result.return_code == 0
    assert "5" in result.stdout


@pytest.mark.asyncio
async def test_multiline_script():
    script = """\
x = 10
y = 20
print(x + y)
"""
    result = await execute_python(script)
    assert result.return_code == 0
    assert "30" in result.stdout


@pytest.mark.asyncio
async def test_timeout():
    script = """\
import time
time.sleep(10)
print("done")
"""
    result = await execute_python(script, timeout=1)
    assert result.return_code == -1
    assert "timed out" in result.stderr.lower()


@pytest.mark.asyncio
async def test_syntax_error():
    result = await execute_python("def foo(")
    assert result.return_code != 0
    assert "SyntaxError" in result.stderr


@pytest.mark.asyncio
async def test_import_error():
    result = await execute_python("import nonexistent_module_xyz_123")
    assert result.return_code != 0
    assert "ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr


@pytest.mark.asyncio
async def test_runtime_error():
    result = await execute_python("1 / 0")
    assert result.return_code != 0
    assert "ZeroDivisionError" in result.stderr


@pytest.mark.asyncio
async def test_generated_files(tmp_path):
    script = f"""\
with open("{tmp_path / 'output.txt'}", "w") as f:
    f.write("test data")
"""
    result = await execute_python(script, working_dir=str(tmp_path))
    assert result.return_code == 0
    assert any("output.txt" in f for f in result.generated_files)


@pytest.mark.asyncio
async def test_working_dir_isolation(tmp_path):
    """Script runs in the specified working directory."""
    script = """\
import os
print(os.getcwd())
"""
    result = await execute_python(script, working_dir=str(tmp_path))
    assert result.return_code == 0
    assert str(tmp_path) in result.stdout


@pytest.mark.asyncio
async def test_stderr_capture():
    script = """\
import sys
print("error message", file=sys.stderr)
print("normal output")
"""
    result = await execute_python(script)
    assert result.return_code == 0
    assert "normal output" in result.stdout
    assert "error message" in result.stderr

import nox
import os
import subprocess

from pathlib import Path

python = os.environ.get("TRAVIS_PYTHON_VERSION")

lint_dependencies = ["black", "flake8"]


nox.options.reuse_existing_virtualenvs = True


@nox.session(python=python)
def tests(session):
    session.install("pytest")
    session.install("-r", "requirements.txt")
    session.run("pytest")


@nox.session
def lint(session):
    session.install(*lint_dependencies)
    # [str(Path("src") / "pipx"), "tests"]
    files = [str(p) for p in Path(".").glob("*.py")]
    print(files)
    session.run("black", "--check", *files)
    session.run("flake8", *files)


@nox.session(python="3.7")
def build(session):
    session.install("setuptools")
    session.install("wheel")
    session.install("twine")
    session.run("rm", "-rf", "dist", "build", external=True)
    session.run("python", "setup.py", "--quiet", "sdist", "bdist_wheel")


def has_changes():
    status = (
        subprocess.run(
            "git status --porcelain",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
        )
        .stdout.decode()
        .strip()
    )
    return len(status) > 0


def get_branch():
    return (
        subprocess.run(
            "git rev-parse --abbrev-ref HEAD",
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
        )
        .stdout.decode()
        .strip()
    )


@nox.session(python="3.7")
def publish(session):
    if has_changes():
        session.error("All changes must be committed before publishing")
    branch = get_branch()
    if branch != "master":
        session.error(
            f"Must be on 'master' branch. Currently on {branch!r} branch"
        )
    build(session)
    print("REMINDER: Has the changelog been updated?")
    session.run("python", "-m", "twine", "upload", "dist/*")
    # publish_docs(session)

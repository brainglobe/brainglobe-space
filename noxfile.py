import nox
import os

python = os.environ.get("TRAVIS_PYTHON_VERSION")

lint_dependencies = ["black", "flake8"]


nox.options.reuse_existing_virtualenvs = True


@nox.session(python=python)
def tests(session):
    session.install("pytest")
    session.install("pytest-cov")
    session.install("-r", "requirements.txt")
    session.run("pytest", "--cov=bgspace")


@nox.session
def lint(session):
    session.install(*lint_dependencies)

    files = ["bgspace", "tests", "noxfile.py", "setup.py"]

    session.run("black", "--check", *files)
    session.run("flake8", *files)

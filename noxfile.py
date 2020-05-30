import nox
import os

python = os.environ.get("TRAVIS_PYTHON_VERSION")


@nox.session(python=python)
def tests(session):
    session.install("pytest")
    session.install("-r", "requirements.txt")
    session.run("pytest")


@nox.session
def lint(session):
    session.install("flake8")
    session.run("flake8", "setup.py")

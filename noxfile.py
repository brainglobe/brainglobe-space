import nox


@nox.session(python=["3.5", "3.6", "3.7", "3.8"])
def tests(session):
    session.install("pytest")
    session.install("-r", "requirements.txt")
    session.run("pytest")


@nox.session
def lint(session):
    session.install("flake8")
    session.run("flake8", "setup.py")

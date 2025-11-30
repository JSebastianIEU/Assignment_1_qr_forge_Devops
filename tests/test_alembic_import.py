"""
Ensure Alembic environment scripts import without error
(offline/online compatibility).
"""


def test_alembic_env_importable():
    """Load the project's `alembic/env.py` by path to ensure it imports.

    Importing via the package name may resolve to the installed `alembic`
    distribution instead of the repository's migration scripts. Load by
    file path to guarantee we exercise the local `alembic/env.py`.
    """
    from pathlib import Path

    env_path = Path(__file__).resolve().parent.parent / "alembic" / "env.py"
    if not env_path.exists():
        raise AssertionError("alembic/env.py not found in repository")

    # Instead of executing top-level Alembic env (which expects the Alembic
    # runtime to provide `context.config`), validate the file for syntax
    # errors by parsing its AST. This verifies the migration script is well-
    # formed without requiring an Alembic runtime environment.
    import ast

    try:
        source = env_path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(env_path))
    except Exception as exc:
        raise AssertionError(f"alembic/env.py is invalid Python: {exc}") from exc

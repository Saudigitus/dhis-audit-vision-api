from core.auth.schemas import UserCreate
from core.auth.crud import create, get_by_username
import typer
from core.db.session import SessionLocal
from core.audit.audit import AuditProcess
import uuid
from core.auth.security import create_access_token
import traceback
from core.config import settings

app = typer.Typer(invoke_without_command=False)


@app.command("start-audit")
def start_audit():
    """Start the audit process"""
    try:
        audit_process = AuditProcess()
        audit_process.run()
        typer.echo(f"Audit process completed successfully")
    except Exception as e:
        typer.echo(f"Error during audit process: {e}")
        traceback.print_exc()


@app.command("seed-superuser")
def seed_superuser(print_token: bool = typer.Option(False, help="Print a one-time access token to stdout.")):
    """Seed the database with a default superuser and generate an access token"""
    db = SessionLocal()
    try:
        user = get_by_username(db, settings.ADMIN_USERNAME)
        if user:
            print(f"Superuser already exists: {user.username} / {user.email}")
        else:
            user = create(db, UserCreate(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD.get_secret_value(),
                is_superuser=True,
            ))
            print(f"Superuser created: {user.username} / {user.email}")

        if print_token:
            access_token = create_access_token(data={
                "sub": user.username,
                "is_superuser": user.is_superuser,
                "jti": str(uuid.uuid4()),
            })
            print(f"Token: {access_token}")
        else:
            print("Token not printed. Use /api/auth/login or rerun with --print-token if required.")
    except Exception as e:
        print(f"Error seeding superuser: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    app()

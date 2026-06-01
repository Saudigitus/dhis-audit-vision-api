from core.auth.schemas import UserCreate
from core.auth.crud import create, get_by_username
import typer
from core.db.session import SessionLocal
from core.audit.audit import AuditProcess
import os
from core.auth.security import hash_password
from dotenv import load_dotenv
import traceback
from core.auth.security import create_access_token

load_dotenv()

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
def seed_superuser():
    """Seed the database with a default superuser"""
    db = SessionLocal()
    try:
        user=get_by_username(db, os.getenv("ADMIN_USERNAME"))
        if user:
            access_token = create_access_token(data={"sub": user.username, "is_superuser": user.is_superuser})
            print(f"Superuser created: {user.username} / {user.email}")
            print(f"Token: {access_token}")
            print("Superuser already exists.")
            return
        user = create(db, UserCreate(
            username=os.getenv("ADMIN_USERNAME"),
            email=os.getenv("ADMIN_EMAIL"),
            password=os.getenv("ADMIN_PASSWORD"),
            is_superuser=True,
        ))
        access_token = create_access_token(data={"sub": user.username, "is_superuser": user.is_superuser})
        print(f"Superuser created: {user.username} / {user.email}")
        print(f"Token: {access_token}")

    except Exception as e:
        print(f"Error seeding superuser: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    app()

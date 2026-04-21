from core.auth.schemas import UserCreate
from core.auth.crud import create, get_by_username
import typer
from core.db.session import SessionLocal
from core.audit.audit import AuditProcess
import os
from core.auth.security import hash_password
from dotenv import load_dotenv
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

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


@app.command("seed-superuser")
def seed_superuser():
    """Seed the database with a default superuser"""
    db = SessionLocal()
    try:
        if get_by_username(db, "admin"):
            print("Superuser already exists.")
            return
        user = create(db, UserCreate(
            username=os.getenv("ADMIN_USERNAME"),
            email=os.getenv("ADMIN_EMAIL"),
            password=os.getenv("ADMIN_PASSWORD"),
            is_superuser=True,
        ))
        print(f"Superuser created: {user.username} / {user.email}")
    except Exception as e:
        print(f"Error seeding superuser: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    app()

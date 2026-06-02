from core.auth.schemas import UserCreate
from core.auth.crud import create, get_by_username
import typer
from core.db.session import SessionLocal
from core.audit.audit import AuditProcess
import os
from core.auth.security import create_access_token
from dotenv import load_dotenv
import traceback
import uuid
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
        traceback.print_exc()


@app.command("seed-superuser")
def seed_superuser():
    """Seed the database with a default superuser and generate an access token"""
    db = SessionLocal()
    try:
        admin_username = os.getenv("ADMIN_USERNAME")
        user = get_by_username(db, admin_username)

        if user:
            print(f"Superuser already exists: {user.username} / {user.email}")
        else:
            user = create(db, UserCreate(
                username=admin_username,
                email=os.getenv("ADMIN_EMAIL"),
                password=os.getenv("ADMIN_PASSWORD"),
                is_superuser=True,
            ))
            print(f"Superuser created: {user.username} / {user.email}")

        token = create_access_token({"sub": user.username, "jti": str(uuid.uuid4())})
        print(f"Access token: {token}")
    except Exception as e:
        print(f"Error seeding superuser: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    app()

import typer
from core.db.session import SessionLocal
from core.audit.audit import AuditProcess

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


@app.command("check-status")
def check_status():
    """Check the status of the audit process"""
    typer.echo(f"Audit process is running...")


if __name__ == "__main__":
    app()

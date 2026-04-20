import typer
from core.db.session import SessionLocal
from core.db.seeders.seed import DataSeeder

app = typer.Typer()

@app.command()
def seed_data():
    """Seed data into the database"""
    try:
        DataSeeder.run()
        typer.echo(f"Successfully seeded data")
    except Exception as e:
        typer.echo(f"Error seeding users: {e}")
    finally:
        # db.close()
        pass

if __name__ == "__main__":
    app()
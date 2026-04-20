import uvicorn
from core.config import settings
from core.main import app 

if __name__ == "__main__":
    uvicorn.run("core.main:app", host=settings.host, port=settings.port, reload=True)

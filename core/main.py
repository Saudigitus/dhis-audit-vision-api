from fastapi import FastAPI
from core.routes.service_urls import router as service_router
from core.routes.server_urls import router as server_router
from core.routes.variables_mapping_urls import router as variables_mapping_router
from core.routes.executions_urls import router as executions_router
from core.routes.import_history_urls import router as import_history_router
from core.routes.data_exchange_urls import router as data_exchange_router
from core.routes.orgunit_mapping_urls import router as orgunit_mapping_router
from core.routes.service_configurations_urls import router as service_configurations_router
from core.routes.variables_mapping_verbs_urls import router as variables_mapping_verbs_router
import os
import json



app = FastAPI(title="FastAPI Project - Integration of dhis2 and xAPI")

app.include_router(service_router, prefix="/api/services", tags=["Services"])
app.include_router(server_router, prefix="/api/servers", tags=["Servers"])
app.include_router(variables_mapping_router, prefix="/api/variableMappings", tags=["variablesMapping"])
app.include_router(executions_router, prefix="/api/executions", tags=["executions"])
app.include_router(import_history_router, prefix="/api/importHistories", tags=["import_history"])
app.include_router(data_exchange_router, prefix="/api/routes", tags=["data_exchange_route"])
app.include_router(orgunit_mapping_router, prefix="/api/orgUnitMappings", tags=["orgunit_mapping_route"])
app.include_router(service_configurations_router, prefix="/api/serviceConfigurations", tags=["service_configurations_route"])
app.include_router(variables_mapping_verbs_router, prefix="/api/variablesMappingVerbs", tags=["variables_mapping_verbs_route"])


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Project - Integration of dhis2 and xAPI!"}


@app.get("/endpoints/")
def list_endpoints():
    endpoints = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            endpoints.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": route.name if hasattr(route, "name") else None,
                "tags": route.tags if hasattr(route, "tags") else []
            })
    return {"endpoints": endpoints}



@app.get("/logs")
def list_logs():
    logs = os.listdir("logs")

    return {'logs': logs}


@app.get("/logs/{log}")
def list_logs(log:str):
    
    log_data = None

    with open(f"logs/{log}.txt", "r") as f:
        log_data = json.loads(f.read())
    
    return log_data
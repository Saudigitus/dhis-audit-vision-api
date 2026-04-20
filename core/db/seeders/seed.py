from core.db.seeders.base_seeder import BaseSeeder
from core.models.models import Server, Service, VariablesMapping, OrgUnitMapping
from core.schemas.schemas import ServerCreate, ServiceCreate, VariablesMappingCreate, OrgUnitMappingCreate
from core.db.seeders import seeders_data




class DataSeeder(BaseSeeder):
    @classmethod
    def run(cls):

        print("Seeding Data...")
        
        #seed servers
        print("Creating servers", "\n")
        seeders_data.create_origin_server()
        seeders_data.create_destiny_server()

        #seed service
        print("Creating service", "\n")
        seeders_data.create_service()

        #seed service
        print("Creating service configuration", "\n")
        seeders_data.create_service_configurations()

        #seed variables mapping
        print("Creating variables mapping", "\n")
        seeders_data.create_enrollment_variable_mapping()
        seeders_data.create_attendance_variable_mapping()
        seeders_data.create_final_result_promoted_variable_mapping()
        seeders_data.create_final_result_failed_variable_mapping()
        seeders_data.create_other_statements_variables_mapping()
        seeders_data.create_complete_variable_mapping()

        #seed orgunit mapping
        print("Creating orgunit mappings", "\n")
        seeders_data.create_orgunit_mapping()

        return True
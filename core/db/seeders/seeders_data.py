from fastapi import FastAPI
from fastapi.testclient import TestClient
from core.main import app
# from core.routes.service_urls import service_crud
from core.routes.server_urls import server_crud
from core.routes.variables_mapping_urls import variables_mapping_crud
from core.routes.orgunit_mapping_urls import orgunit_mapping_crud
from core.routes.service_configurations_urls import service_configurations_crud
from core.db.dependencies import get_db
from fastapi import Depends
from core.schemas.schemas import ServiceRead, ServiceCreate, VariablesMappingCreate, ServerCreate, OrgUnitMappingCreate, ServiceConfigurationsCreate
from core.db.session import SessionLocal
from core.tests import fake_metadata
import json
from core.config import settings
from core.common.generics.crud_base import CRUDBase
from core.models.models import Service
from core.common.constants import constants


service_crud = CRUDBase[Service, ServiceCreate, ServiceRead](Service)


def create_origin_server():
    db = SessionLocal()
    payload = {
        'id': "WeXpA51JJ6Q",
        'name': "LRS Server",
        'type': constants.LRS,
        'url': settings.SERVER_LRS_URL,
        'auth': settings.SERVER_LRS_AUTH,
        'authType': constants.BASIC
    }

    server_payload = ServerCreate(**payload)
    return server_crud.create(db, payload_in=server_payload)


def create_destiny_server():
    db = SessionLocal()
    payload = {
        'id': "PN8DnK8mo0K",
        'name': "DHIS2 Server",
        'type': constants.DHIS2,
        'url': settings.SERVER_DHIS2_URL,
        'auth': settings.SERVER_DHIS2_AUTH,
        'authType': constants.BASIC
    }

    server_payload = ServerCreate(**payload)
    return server_crud.create(db, payload_in=server_payload)


def create_service():
    db = SessionLocal()
    payload = {
        'id': "IjWmORgJ6W3",
        'name': "Semis xAPI",
        'destinyLRSServer': "PN8DnK8mo0K",
        'originServerId': "WeXpA51JJ6Q",
        'status': "ACTIVE"
    }

    service_payload = ServiceCreate(**payload)
    return service_crud.create(db, payload_in=service_payload)


def create_service_configurations():
    db = SessionLocal()
    payload = {
        'id': "MibhfNrP9MY",
        'enrollmentDetailProgramStage': "Ni2qsy2WJn4",
        'academicYearDataElement': "iDSrFrrVgmX",
        'trackerEntityIdentifier': "Jm5zlb098Yo",
        'statementIdentifier': "actor.mbox",
        'program': "wQaiD2V27Dp",
        'serviceId': "IjWmORgJ6W3"
    }

    service_configuration_payload = ServiceConfigurationsCreate(**payload)
    return service_configurations_crud.create(db, payload_in=service_configuration_payload)


def create_enrollment_variable_mapping():
    db = SessionLocal()
    payload = {
        "name": "Enrollment Mapping",
        "type": "ENROLLMENT",
        "verb": {
            "path": "verb.id",
            "value": "http://www.tincanapi.co.uk/verbs/enrolled_onto_learning_plan"
        },
        "configVariables": {
            "originVariables": {
                "dataSet": "Qlqx9LMwC0k",
                "period": "timestamp",
                "orgUnit": "context.extensions.https://example_DOT_com/extensions/school",
                "teiIdentifier": "actor.mbox"
            },
            "destinyVariables": {
                "dataSet": "wQaiD2V27Dp",
                "period": "timestamp",
                "teiIdentifier": "Jm5zlb098Yo"
            }
        },
        "mapping": {
            "attributesMapping": [
                {
                    "originId": "actor.mbox",
                    "destinyId": "Jm5zlb098Yo",
                    "originName": "Student ID",
                    "destinyName": "Student ID"
                },
                {
                    "originId": "actor.name",
                    "destinyId": "gz8w04YBSS0",
                    "originName": "Full Name",
                    "destinyName": "Full Name"
                }
            ],
            "eventsMapping": [
                {
                    "programStage": "Ni2qsy2WJn4",
                    "mapping": [
                        {
                            "originId": "context.extensions.https://example_DOT_com/extensions/academi-year",
                            "destinyId": "iDSrFrrVgmX",
                            "originName": "Academic Year",
                            "destinyName": "Academic Year",
                            "defaultValue": "Not defined"
                        },
                        {
                            "originId": "context.extensions.https://example_DOT_com/extensions/grade",
                            "destinyId": "kNNoif9gASf",
                            "originName": "Grade",
                            "destinyName": "Grade",
                            "defaultValue": "Not defined"
                        },
                        {
                            "originId": "context.extensions.https://example_DOT_com/extensions/class",
                            "destinyId": "RhABRLO2Fae",
                            "originName": "Class/Section",
                            "destinyName": "Class/Section",
                            "defaultValue": "Not defined"
                        }
                    ]
                },
                {
                    "programStage": "Wi3KEZ7C3w9",
                    "mapping": []
                },
                {
                    "programStage": "hcrjYJ6Yl5F",
                    "mapping": []
                }
            ]
        },
        'serviceId': "IjWmORgJ6W3"
    }

    variable_mapping_payload = VariablesMappingCreate(**payload)
    return variables_mapping_crud.create(db, payload_in=variable_mapping_payload)


def create_attendance_variable_mapping():
    db = SessionLocal()
    payload = {
        "name": "Demo Attendance Mapping",
        "type": "EVENT",
        "verb": {
            "path": "verb.id",
            "value": "http://activitystrea.ms/schema/1.0/attend"
        },
        "configVariables": {
            "originVariables": {
                "dataSet": "Qlqx9LMwC0k",
                "period": "timestamp",
                "orgUnit": "context.extensions.https://example_DOT_com/extensions/school",
                "teiIdentifier": "actor.mbox"
            },
            "destinyVariables": {
                "dataSet": "wQaiD2V27Dp",
                "programStage": "Ljyrr3cktAr",
                "period": "timestamp",
                "teiIdentifier": "Jm5zlb098Yo"
            }
        },
        "mapping": [
            {
                "originId": "",
                "destinyId": "d0MKWRNGv0a",
                "originName": "Attendance",
                "destinyName": "Attendance",
                "defaultValue": "present"
            }
        ],
        'serviceId': "IjWmORgJ6W3"
    }

    variable_mapping_payload = VariablesMappingCreate(**payload)
    return variables_mapping_crud.create(db, payload_in=variable_mapping_payload)


def create_final_result_promoted_variable_mapping():
    db = SessionLocal()
    payload = {
        "name": "Final Result Promoted Mapping",
        "type": "EVENT",
        "verb": {
            "path": "verb.id",
            "value": "http://adlnet.gov/expapi/verbs/passed"
        },
        "configVariables": {
            "originVariables": {
                "dataSet": "Qlqx9LMwC0k",
                "period": "timestamp",
                "orgUnit": "context.extensions.https://example_DOT_com/extensions/school",
                "teiIdentifier": "actor.mbox"
            },
            "destinyVariables": {
                "dataSet": "wQaiD2V27Dp",
                "programStage": "hcrjYJ6Yl5F",
                "period": "timestamp",
                "teiIdentifier": "Jm5zlb098Yo"
            }
        },
        "mapping": [
            {
                "originId": "",
                "destinyId": "bsyU0WFfskG",
                "originName": "Final decision",
                "destinyName": "Final decision",
                "defaultValue": "Promoted"
            }
        ],
        'serviceId': "IjWmORgJ6W3"
    }

    variable_mapping_payload = VariablesMappingCreate(**payload)
    return variables_mapping_crud.create(db, payload_in=variable_mapping_payload)


def create_final_result_failed_variable_mapping():
    db = SessionLocal()
    payload = {
        "name": "Final Result Failed Mapping",
        "type": "EVENT",
        "verb": {
            "path": "verb.id",
            "value": "http://adlnet.gov/expapi/verbs/failed"
        },
        "configVariables": {
            "originVariables": {
                "dataSet": "Qlqx9LMwC0k",
                "period": "timestamp",
                "orgUnit": "context.extensions.https://example_DOT_com/extensions/school",
                "teiIdentifier": "actor.mbox"
            },
            "destinyVariables": {
                "dataSet": "wQaiD2V27Dp",
                "programStage": "hcrjYJ6Yl5F",
                "period": "timestamp",
                "teiIdentifier": "Jm5zlb098Yo"
            }
        },
        "mapping": [
            {
                "originId": "",
                "destinyId": "bsyU0WFfskG",
                "originName": "Final decision",
                "destinyName": "Final decision",
                "defaultValue": "Failed"
            }
        ],
        'serviceId': "IjWmORgJ6W3"
    }

    variable_mapping_payload = VariablesMappingCreate(**payload)
    return variables_mapping_crud.create(db, payload_in=variable_mapping_payload)


def create_other_statements_variables_mapping():
    db = SessionLocal()
    payload = {
        "name": "Other statement Mapping (Student ExPeriences)",
        "type": "EVENT",
        "default": True,
        "configVariables": {
            "originVariables": {
                "dataSet": "Qlqx9LMwC0k",
                "period": "timestamp",
                "orgUnit": "context.extensions.https://example.com/extensions/school",
                "teiIdentifier": "actor.mbox"
            },
            "destinyVariables": {
                "dataSet": "wQaiD2V27Dp",
                "programStage": "xBNsPyRsmQr",
                "period": "timestamp",
                "teiIdentifier": "Jm5zlb098Yo"
            }
        },
        "mapping": [
            {
                "originId": "verb.id",
                "destinyId": "IYleFYryI1Q",
                "originName": "Verb",
                "destinyName": "xAPI - Verb",
                "valueHandler": "SPLIT_LOWER"
            },
            {
                "originId": "verb.display.en",
                "destinyId": "u5eC95XIbO7",
                "originName": "Verb Name",
                "destinyName": "xAPI - Verb Name",
                "valueHandler": "LOWER"
            },
            {
                "originId": "object.id",
                "destinyId": "Qn7He9IlMOg",
                "originName": "Object Indentifier",
                "destinyName": "xAPI - Object Identifier"
            },
            {
                "originId": "object.definition.description.en",
                "destinyId": "ivdzBdoc93o",
                "originName": "Object Description",
                "destinyName": "xAPI - Object Description"
            },
            {
                "originId": "object.definition.type",
                "destinyId": "P3XAxPIvRy8",
                "originName": "Object Type",
                "destinyName": "xAPI - Object Type",
                "valueHandler": "SPLIT_LOWER"

            },
            {
                "originId": "context.platform",
                "destinyId": "zXBSuiS7CqP",
                "originName": "Statement Origin",
                "destinyName": "xAPI - Statement Origin"
            }
        ],
        'serviceId': "IjWmORgJ6W3"
    }

    variable_mapping_payload = VariablesMappingCreate(**payload)
    return variables_mapping_crud.create(db, payload_in=variable_mapping_payload)


def create_complete_variable_mapping():
    db = SessionLocal()
    payload = {
        "name": "Demo Complete Mapping (Other Evaluations)",
        "type": "EVENT",
        "verb": {
            "path": "verb.id",
            "value": "http://activitystrea.ms/schema/1.0/completed"
        },
        "configVariables": {
            "originVariables": {
                "dataSet": "Qlqx9LMwC0k",
                "period": "timestamp",
                "orgUnit": "context.extensions.https://example_DOT_com/extensions/school",
                "teiIdentifier": "actor.mbox"
            },
            "destinyVariables": {
                "dataSet": "wQaiD2V27Dp",
                "programStage": "kHArnxZQRlC",
                "period": "timestamp",
                "teiIdentifier": "Jm5zlb098Yo"
            }
        },
        "mapping": [
            {
                "originId": "verb.id",
                "destinyId": "IYleFYryI1Q",
                "originName": "Verb",
                "destinyName": "xAPI - Verb",
                "valueHandler": "SPLIT_LOWER"
            },
            {
                "originId": "verb.display.en",
                "destinyId": "u5eC95XIbO7",
                "originName": "Verb Name",
                "destinyName": "xAPI - Verb Name"
            },
            {
                "originId": "object.id",
                "destinyId": "Qn7He9IlMOg",
                "originName": "Object Indentifier",
                "destinyName": "xAPI - Object Identifier"
            },
            {
                "originId": "object.definition.description.en",
                "destinyId": "ivdzBdoc93o",
                "originName": "Object Description",
                "destinyName": "xAPI - Object Description"
            },
            {
                "originId": "object.definition.type",
                "destinyId": "P3XAxPIvRy8",
                "originName": "Object Type",
                "destinyName": "xAPI - Object Type",
                "valueHandler": "SPLIT_LOWER"
            },
            {
                "originId": "result.completion",
                "destinyId": "aixzu3o7Ar3",
                "originName": "Completed",
                "destinyName": "xAPI - Completed"
            },
            {
                "originId": "result.duration",
                "destinyId": "MOTkWba9UmL",
                "originName": "duration",
                "destinyName": "xAPI - Durantion Code"
            },
            {
                "originId": "result.score.raw",
                "destinyId": "aJBWOq4AHe7",
                "originName": "raw",
                "destinyName": "xAPI - Score"
            },
            {
                "originId": "result.success",
                "destinyId": "al82YKLlGyR",
                "originName": "success",
                "destinyName": "xAPI - Success"
            },
            {
                "originId": "result.duration",
                "destinyId": "pYCPjkKjJwK",
                "originName": "duration",
                "destinyName": "xAPI - Durantion in seconds",
                "valueHandlerDuration": "DURATION"
            },
            {
                "originId": "context.platform",
                "destinyId": "zXBSuiS7CqP",
                "originName": "Statement Origin",
                "destinyName": "xAPI - Statement Origin"
            }
        ],
        'serviceId': "IjWmORgJ6W3"
    }

    variable_mapping_payload = VariablesMappingCreate(**payload)
    return variables_mapping_crud.create(db, payload_in=variable_mapping_payload)


def create_orgunit_mapping():
    db = SessionLocal()
    payload = {
        "name": "OrgUnit Mapping",
        "configVariables": {
            "defaultValue": "JZie9Qnug02"
        },
        "mapping": [
            {
                "originId": "school-1",
                "destinyId": "JZie9Qnug02",
            },
            {
                "originId": "school-2",
                "destinyId": "m0PuKDuqwcd"
            }
        ],
        'serviceId': "IjWmORgJ6W3"
    }

    orgunit_mapping_payload = OrgUnitMappingCreate(**payload)
    return orgunit_mapping_crud.create(db, payload_in=orgunit_mapping_payload)

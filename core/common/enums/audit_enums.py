from enum import Enum


class AuditType(str, Enum):
    READ = "READ"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SEARCH = "SEARCH"


class AuditScope(str, Enum):
    METADATA = "METADATA"
    AGGREGATE = "AGGREGATE"
    TRACKER = "TRACKER"

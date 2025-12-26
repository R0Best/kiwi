from enum import StrEnum

from pydantic import BaseClass


class OperationType(StrEnum):
    OPERATOR_ASSIGNMENT = "OPERATOR_ASSIGNMENT"


class Operation(BaseClass):
    type: OperationType


# ID: ID = ID
# ID: ID = EXPR
# ID = ID
# ID = EXPR
class OperationAssignment(Operation):
    variable: str  # IDENTIFIER_IDENTIFIER
    variable_type: str  # IDENTIFIER_IDENTIFIER
    expressions: str  # EXPRESSION

from enum import Enum


class NavigationRelationship(str, Enum):
    """
    Relationships between navigation nodes.
    """

    PARENT = "parent"

    CHILD = "child"

    CONTAINS = "contains"

    REFERENCES = "references"

    FOLLOWS = "follows"

    PREVIOUS = "previous"

    NEXT = "next"
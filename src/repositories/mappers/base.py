from typing import ClassVar
from pydantic import BaseModel
from src.database import Base


class DataMapper:
    db_model: ClassVar[type[Base]]
    schema: ClassVar[type[BaseModel]]

    @classmethod
    def map_to_domain_entity(cls, data) -> BaseModel:
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data: BaseModel) -> Base:
        return cls.db_model(**data.model_dump())

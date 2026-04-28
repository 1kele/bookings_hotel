from fastapi import APIRouter

from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd
from src.services.facilities import FacilityService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
@cache(expire=10)
async def get_all_facilities(
    db: DBDep,
):
    result = await FacilityService(db).get_all_facilities()
    return result


@router.post("")
async def create_facility(db: DBDep, facility_data: FacilityAdd):
    result = await FacilityService(db).create_facility(facility_data)
    return {"status": "OK", "data": result}

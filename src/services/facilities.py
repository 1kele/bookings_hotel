from src.schemas.facilities import FacilityAdd
from src.services.base import BaseService
from src.tasks.tasks import test_task


class FacilityService(BaseService):
    async def get_all_facilities(self):
        return await self.db.facilities.get_all()

    async def create_facility(self, facility_data: FacilityAdd):
        result = await self.db.facilities.add(facility_data)
        await self.db.commit()
        test_task.delay()  # type: ignore

        return result

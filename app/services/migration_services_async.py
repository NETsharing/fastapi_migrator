import inspect
from collections import defaultdict

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.model.models import Project, BasePlan, KeyDates, Version
from app.repositories.migration_repositories import MigrationRepository


class MigrationBase:
    def __init__(self, db: AsyncSession = Depends(get_async_session)):
        self.db = db
        self.repo = MigrationRepository(db)
        self.project_id = None
        self.ms_project = None


class Versions(MigrationBase):
    def __init__(self):
        super().__init__()

    def construct_version(self, base_plan_id, parent_version_id):
        new_version_instance = Version(base_plan_id=base_plan_id, project_id=self.project_id,
                                       parent_version_id=parent_version_id)
        self.db.add(new_version_instance)
        await self.db.flush()
        return new_version_instance


class Baselines(MigrationBase):
    def __init__(self):
        super().__init__()

    def get_baselines(self):
        return [bl for bl in self.ms_project.base_lines if await bl.task.key_date]

    async def get_created_date_dict(self, base_lines):
        base_lines_created_date_dict = dict()
        for bl in base_lines:
            if bl.tb_base_num not in base_lines_created_date_dict:
                base_lines_created_date_dict[bl.tb_base_num] = bl.created_date.date()
            else:
                created_date = base_lines_created_date_dict.get(bl.tb_base_num)
                if bl.created_date.date() < created_date:
                    base_lines_created_date_dict.update({bl.tb_base_num: bl.created_date.date()})
        return base_lines_created_date_dict

    async def add_base_plan_to_project(self, base_plan_attr, task_list):
        tb_base_start = sorted(task_list, key=lambda x: x.task_start_date)[0].task_start_date
        tb_base_finish = sorted(task_list, key=lambda x: x.task_finish_date, reverse=True)[0].task_finish_date
        base_plan_kwargs = {
            'created_at': base_plan_attr[1],
            'base_number': base_plan_attr[0],
            'project_id': self.project_id,
            'base_plan_start_date': tb_base_start,
            'base_plan_finish_date': tb_base_finish,
        }
        new_base_plan_instance = BasePlan(**base_plan_kwargs)
        self.db.add(new_base_plan_instance)
        await self.db.flush()
        return new_base_plan_instance

            # await add_tasks_and_version(db, new_base_plan_instance.id, project_id, None, task_list)


class BuisnessLogic(MigrationBase):
    def __init__(self):
        super().__init__()

    async def check_exits_project(self):
        return await self.repo.check_exists_project(self.ms_project.proj_uid)

    async def create_instance(self, model, obj_src, kwargs) -> None:
        obj_new = await self.set_attr(model, obj_src)
        if kwargs:
            for key, value in kwargs.items():
                setattr(obj_new, key, value)
        self.db.add(obj_new)
        await self.db.flush()

    @staticmethod
    async def set_attr(model, obj):
        dst = model()
        for attr in obj.__dir__():
            mapped = await obj.map(attr)
            if mapped:
                dst_attr, value = mapped
                if inspect.isawaitable(value):
                    result = await value
                    setattr(dst, dst_attr, result)
                else:
                    setattr(dst, dst_attr, value)
        return dst


class Migrate(MigrationBase):

    def __init__(self):
        super().__init__()
        self.logic = BuisnessLogic()
        self.ms_base_lines = Baselines()
        self.ms_projects = await self.repo.get_all_projects()
        self.version_instance = Versions()
        self.base_lines = None

    async def migrate(self):
        for ms_project in self.ms_projects:
            self.ms_project = ms_project
            if not await self.logic.check_exits_project():
                self.base_lines = self.ms_base_lines.get_baselines()
                if self.base_lines:
                    project_obj = await self.logic.set_attr(Project, ms_project)
                    self.db.add(project_obj)
                    await self.db.flush()
                    self.project_id = project_obj.id
                    base_lines_dict = defaultdict(list)
                    base_lines_created_dates = await self.ms_base_lines.get_created_date_dict(self.base_lines)

                    for bl in self.base_lines:
                        base_lines_dict[(bl.tb_base_num, base_lines_created_dates.get(bl.tb_base_num))].append(bl.task)
                    for base_plan_attr, task_list in base_lines_dict.items():
                        new_base_plan_instance = await self.ms_base_lines.add_base_plan_to_project(base_plan_attr, task_list)
                        new_version = await self.version_instance.construct_version(new_base_plan_instance.id, None)
                        kwargs = {
                            'project_id': self.project_id,
                            'base_plan_id': new_base_plan_instance.id,
                            'version_id': new_version.id
                        }
                        for task in task_list:
                            await self.logic.create_instance(KeyDates, task, kwargs)
                await self.db.commit()



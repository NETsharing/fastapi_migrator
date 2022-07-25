import inspect
from collections import defaultdict
from datetime import datetime

from app.model.models import Project, BasePlan, KeyDates, Version
from app.repositories.migration_repositories import MigrationRepository


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


async def set_obj_attr(dst, obj):
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


async def create_instance(db, model, obj_src, kwargs) -> None:
    obj_new = await set_attr(model, obj_src)
    if kwargs:
        for key, value in kwargs.items():
            setattr(obj_new, key, value)
    db.add(obj_new)
    await db.flush()


async def add_tasks_and_version(db, base_plan_id, project_id, parent_version_id, need_linked_tasks) -> None:
    new_version_instance = Version(base_plan_id=base_plan_id, project_id=project_id,
                                   parent_version_id=parent_version_id)
    db.add(new_version_instance)
    await db.flush()
    kwargs = {
        'project_id': project_id,
        'base_plan_id': base_plan_id,
        'version_id': new_version_instance.id
    }
    for task in need_linked_tasks:
        await create_instance(db, KeyDates, task, kwargs)


async def add_base_plan_to_project(db, base_lines_dict, project_id) -> None:
    for base_plan_attr, task_list in base_lines_dict.items():
        tb_base_start = sorted(task_list, key=lambda x: x.task_start_date)[0].task_start_date
        tb_base_finish = sorted(task_list, key=lambda x: x.task_finish_date, reverse=True)[0].task_finish_date
        base_plan_kwargs = {
            'created_at': base_plan_attr[1],
            'base_number': base_plan_attr[0],
            'project_id': project_id,
            'base_plan_start_date': tb_base_start,
            'base_plan_finish_date': tb_base_finish,
        }
        new_base_plan_instance = BasePlan(**base_plan_kwargs)
        db.add(new_base_plan_instance)
        await db.flush()
        await add_tasks_and_version(db, new_base_plan_instance.id, project_id, None, task_list)


async def get_created_date_dict(base_lines) -> dict:
    base_lines_created_date_dict = dict()
    for bl in base_lines:
        if bl.tb_base_num not in base_lines_created_date_dict:
            base_lines_created_date_dict[bl.tb_base_num] = bl.created_date.date()
        else:
            created_date = base_lines_created_date_dict.get(bl.tb_base_num)
            if bl.created_date.date() < created_date:
                base_lines_created_date_dict.update({bl.tb_base_num: bl.created_date.date()})
    return base_lines_created_date_dict


async def add_task_to_base_plan(db, task, base_plan, version) -> None:

    base_plan.updated_at = datetime.now()
    kwargs = {
        'project_id': base_plan.project_id,
        'base_plan_id': base_plan.id,
        'version_id': version.id
    }
    await create_instance(db, KeyDates, task, kwargs)


async def migrate_data(db) -> True:
    repo = MigrationRepository(db)
    ms_projects = await repo.get_all_projects()
    for ms_project in ms_projects:
        project_obj_exist = await repo.check_exists_project(ms_project.proj_uid)
        if not project_obj_exist:
            base_lines = [bl for bl in ms_project.base_lines if await bl.task.key_date]
            if base_lines:
                project_obj = await set_attr(Project, ms_project)
                db.add(project_obj)
                await db.flush()
                project_id = project_obj.id
                print(f'new project {project_id = }')
                base_lines_dict = defaultdict(list)
                base_lines_created_dates = await get_created_date_dict(base_lines)

                for bl in base_lines:
                    base_lines_dict[(bl.tb_base_num, base_lines_created_dates.get(bl.tb_base_num))].append(bl.task)
                await add_base_plan_to_project(db, base_lines_dict, project_id)
                await db.commit()
        else:
            project_id = project_obj_exist.id
            print(f'exists project {project_id = }')
            base_lines = [bl for bl in ms_project.base_lines if await bl.task.key_date]
            base_plans_num = [bp.base_number for bp in project_obj_exist.base_plans]
            base_lines_dict = defaultdict(list)
            base_lines_created_dates = await get_created_date_dict(base_lines)
            last_version = await repo.get_base_plan_last_version(project_id)

            # проверяем появление нового базового плана
            for bl in base_lines:
                base_lines_dict[(bl.tb_base_num, base_lines_created_dates.get(bl.tb_base_num))].append(
                    bl.task) if bl.tb_base_num not in base_plans_num else None
            if base_lines_dict:
                await add_base_plan_to_project(db, base_lines_dict, project_id)
                await db.flush()

            # проверяем добавление новых тасок в базовый план
            base_lines_task_dict = defaultdict(list)
            for bl in base_lines:
                base_lines_task_dict[bl.tb_base_num].append(bl.task)
            for base_line_num, base_line_task_list in base_lines_task_dict.items():
                base_plan = await repo.get_base_plan(project_id, base_line_num)
                version = await repo.get_base_plan_main_version(project_id, base_plan.id)
                base_lines_tasks = {task: {'start': task.task_start_date, 'finish': task.task_finish_date}
                                    for task in base_line_task_list}
                base_plan_tasks = {str(task.task_uuid): {'start': task.task_start_date, 'finish': task.task_finish_date,
                                                         'task': task} for task in base_plan.tasks}
                for task, data in base_lines_tasks.items():
                    if task.task_uid in base_plan_tasks and\
                            data.get('start') == base_plan_tasks[task.task_uid].get('start') and\
                            data.get('finish') == base_plan_tasks[task.task_uid].get('finish'):
                        continue

                    # привязываем таску созданную в существующем base line к базовому плану
                    elif task.task_uid not in base_plan_tasks:
                        await add_task_to_base_plan(db, task, base_plan, version)

                        # если дата в таске поменялась то меняем ее и ключевых датах
                    else:
                        updated_task = await set_obj_attr(base_plan_tasks[task.task_uid].get('task'), task)
                        updated_task.updated_at = datetime.now()
                        await db.flush()

            # проверяем были ли изменения в текущих тасках и добавление новых - не привязанных к base line
            linked_tasks_uuid = {str(task.task_uuid): {'start': task.task_start_date, 'finish': task.task_finish_date}
                                 for task in last_version.tasks}

            need_linked_tasks = {task: {'start': task.task_start_date, 'finish': task.task_finish_date} for task in
                                 ms_project.tasks if await task.key_date}
            if need_linked_tasks:
                for task, dates in need_linked_tasks.items():
                    if task.task_uid in linked_tasks_uuid and\
                            dates.get('start') == linked_tasks_uuid[task.task_uid].get('start') and\
                            dates.get('finish') == linked_tasks_uuid[task.task_uid].get('finish'):
                        continue
                    else:
                        await add_tasks_and_version(db, last_version.base_plan_id, project_id, last_version.id,
                                                    list(need_linked_tasks))
                        break
            await db.commit()
    return True

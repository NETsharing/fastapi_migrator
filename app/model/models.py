from datetime import datetime

from sqlalchemy import (Column, Integer, String, Boolean, DateTime, ForeignKey)
from sqlalchemy.dialects.mssql import DATETIME, INTEGER, CHAR
from sqlalchemy.dialects.mysql import NVARCHAR
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class MspProjects(Base):
    """  Проекты """

    __tablename__ = 'MSP_PROJECTS'
    __table_args__ = {
        'schema': 'mssql'
    }

    siteid = Column(UUID, primary_key=True, name='SiteId')
    proj_name = Column(CHAR, name='PROJ_NAME')
    proj_uid = Column(UUID, nullable=False, primary_key=True, name='PROJ_UID')
    proj_info_start_date = Column(DATETIME, name='PROJ_INFO_START_DATE')
    proj_info_finish_date = Column(DATETIME, name='PROJ_INFO_FINISH_DATE')

    base_lines = relationship('MspTaskBaselines', foreign_keys='MspTaskBaselines.proj_uid', uselist=True, order_by="asc(MspTaskBaselines.created_date)")
    tasks = relationship('MspTasks', primaryjoin='foreign(MspTasks.proj_uid)==MspProjects.proj_uid', uselist=True)

    @classmethod
    def _get_map(cls):
        return {
            "proj_name": "name",
            "proj_uid": "uuid",
            "proj_info_start_date": "start_date",
            "proj_info_finish_date": "finish_date",
        }

    async def map(self, _src_attr):
        dst_attr = self._get_map().get(_src_attr)
        if dst_attr:
            return dst_attr, getattr(self, _src_attr)


class MspTasks(Base):
    """  Задачи"""

    __tablename__ = 'MSP_TASKS'
    __table_args__ = {
        'schema': 'mssql'
    }

    siteid = Column(INTEGER, primary_key=True, name='SiteId')
    task_start_date = Column(DATETIME, name='TASK_START_DATE')
    task_finish_date = Column(DATETIME, name='TASK_FINISH_DATE')
    task_uid = Column(UUID, nullable=False, primary_key=True, name='TASK_UID')
    proj_uid = Column(UUID, primary_key=True, name='PROJ_UID')
    task_name = Column(NVARCHAR, name='TASK_NAME')
    project = relationship('MspProjects', primaryjoin='foreign(MspTasks.proj_uid)==MspProjects.proj_uid',
                           overlaps="tasks")
    custom_plans = relationship('MspTaskCustomFieldsValues',
                                primaryjoin='foreign(MspTaskCustomFieldsValues.task_uid)==MspTasks.task_uid')
    custom_plan = relationship('MspTaskCustomFieldsValues',
                               primaryjoin="and_(foreign(MspTaskCustomFieldsValues.task_uid)==MspTasks.task_uid, "
                                           "MspTaskCustomFieldsValues.md_prop_uid == "
                                           f"'674EB4DD-ECB7-E811-A2C3-005056ABC6E7')",
                               uselist=False, overlaps="custom_plans", lazy='joined')

    base_plan = relationship('MspTaskBaselines',
                             primaryjoin='foreign(MspTaskBaselines.task_uid)==MspTasks.task_uid',
                             uselist=False)

    @property
    async def key_date(self):
        if self.custom_plan and self.custom_plan.key_dates:
            return self.custom_plan.key_dates.lt_value_text
        else:
            return None

    @classmethod
    async def _get_map(cls):
        return {
            "task_start_date": "task_start_date",
            "task_finish_date": "task_finish_date",

            "task_uid": "task_uuid",
            "key_date": "name",
            "task_name": "task_name"
        }

    async def map(self, _src_attr):
        _dst_attr = await self._get_map()
        dst_attr = _dst_attr.get(_src_attr)
        if dst_attr:
            return dst_attr, getattr(self, _src_attr)


class MspTaskCustomFieldsValues(Base):
    """  Кастомные поля """

    __tablename__ = 'MSP_TASK_CUSTOM_FIELD_VALUES'
    __table_args__ = {
        'schema': 'mssql'
    }

    siteid = Column(UUID, primary_key=True, name='SiteId')
    custom_field_uid = Column(UUID, nullable=False, primary_key=True, name='CUSTOM_FIELD_UID')
    task_uid = Column(UUID, nullable=False, name='TASK_UID')
    proj_uid = Column(UUID, nullable=False, name='PROJ_UID')
    md_prop_uid = Column(UUID, nullable=False, name='MD_PROP_UID')
    code_value = Column(UUID, nullable=False, name='CODE_VALUE')

    projects = relationship('MspProjects',
                            primaryjoin='foreign(MspTaskCustomFieldsValues.proj_uid)==MspProjects.proj_uid')
    custom_fields = relationship('MspCustomFields',
                                 primaryjoin='foreign(MspCustomFields.md_prop_uid)==MspTaskCustomFieldsValues'
                                             '.md_prop_uid', )
    key_dates = relationship('MspLookupTableValues',
                             primaryjoin='foreign(MspLookupTableValues.lt_struct_uid)==MspTaskCustomFieldsValues'
                                         '.code_value',
                             uselist=False, lazy='joined')


class MspCustomFields(Base):
    """  Справочник Кастомные поля """

    __tablename__ = 'MSP_CUSTOM_FIELDS'
    __table_args__ = {
        'schema': 'mssql'
    }

    siteid = Column(INTEGER, primary_key=True, name='SiteId')
    md_prop_uid = Column(UUID, nullable=False, primary_key=True, name='MD_PROP_UID')
    md_lookup_table_uid = Column(UUID, name='MD_LOOKUP_TABLE_UID')
    md_prop_name = Column(NVARCHAR, name='MD_PROP_NAME')  # ("Искомый элемент Ключевые даты")


class MspLookupTableValues(Base):
    """  Ключевые даты"""

    __tablename__ = 'MSP_LOOKUP_TABLE_VALUES'
    __table_args__ = {
        'schema': 'mssql'
    }

    siteid = Column(UUID, primary_key=True, name='SiteId')
    lcid = Column(INTEGER, primary_key=True, name='LCID')
    lt_struct_uid = Column(Integer, nullable=False, unique=True, primary_key=True, name='LT_STRUCT_UID')
    lt_value_text = Column(NVARCHAR(length=255), name='LT_VALUE_TEXT')


class MspTaskBaselines(Base):
    """  Базовые планы """

    __tablename__ = 'MSP_TASK_BASELINES'
    __table_args__ = {
        'schema': 'mssql'
    }

    siteid = Column(UUID, primary_key=True, name='SiteId')
    proj_uid = Column(UUID, ForeignKey(MspProjects.proj_uid), primary_key=True, name='PROJ_UID')
    tb_base_num = Column(INTEGER, primary_key=True, name='TB_BASE_NUM')
    created_date = Column(DATETIME, name='CREATED_DATE')
    tb_base_start = Column(DATETIME, name='TB_BASE_START')
    tb_base_finish = Column(DATETIME, name='TB_BASE_FINISH')
    task_uid = Column(UUID, ForeignKey(MspTasks.task_uid), primary_key=True, name='TASK_UID')

    # task = relationship('MspTasks', foreign_keys='MspTasks.task_uid', uselist=False)
    task = relationship('MspTasks',
                        primaryjoin='foreign(MspTasks.task_uid)==MspTaskBaselines.task_uid',
                        uselist=False, lazy='joined')

    @classmethod
    def _get_map(cls):
        return {
            "tb_base_num": "base_number",
            "created_date": "created_at",
        }

    async def map(self, _src_attr):
        dst_attr = self._get_map().get(_src_attr)
        if dst_attr:
            return dst_attr, await getattr(self, _src_attr)


class Project(Base):
    """  Проекты"""

    __tablename__ = 'project'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    uuid = Column(UUID(as_uuid=True), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    finish_date = Column(DateTime, nullable=True)

    key_dates = relationship('KeyDates', foreign_keys='KeyDates.project_id')
    base_plans = relationship('BasePlan', back_populates='project', uselist=True)


class BasePlan(Base):
    """  Базовые планы"""

    __tablename__ = 'base_plan'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False)
    base_number = Column(Integer, nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    base_plan_start_date = Column(DateTime, nullable=False)
    base_plan_finish_date = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, default=datetime.now)

    versions = relationship('Version', back_populates='base_plan', uselist=True)
    tasks = relationship('KeyDates', back_populates='base_plan', uselist=True)
    project = relationship('Project', back_populates='base_plans')


class KeyDates(Base):
    """  Ключевые даты"""

    __tablename__ = 'key_dates'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    task_start_date = Column(DateTime, nullable=False)
    task_finish_date = Column(DateTime, nullable=False)
    task_uuid = Column(UUID(as_uuid=True), nullable=False)
    task_name = Column(String)
    version_id = Column(Integer, ForeignKey('version.id'), nullable=False)
    base_plan_id = Column(Integer, ForeignKey('base_plan.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    updated_at = Column(DateTime, default=datetime.now)

    base_plan = relationship('BasePlan', back_populates='tasks', uselist=False)
    version = relationship('Version', back_populates='tasks', uselist=False)


class Version(Base):
    """  Версия миграции"""

    __tablename__ = 'version'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    migration_date = Column(DateTime, nullable=False, default=datetime.now)
    base_plan_id = Column(Integer, ForeignKey('base_plan.id'), nullable=True)
    project_id = Column(Integer, ForeignKey('project.id'), nullable=False)
    parent_version_id = Column(Integer, ForeignKey('version.id'), nullable=True)

    base_plan = relationship('BasePlan', back_populates='versions', uselist=False)
    tasks = relationship('KeyDates', back_populates='version', lazy='joined')

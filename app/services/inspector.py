# from sqlalchemy import inspect
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# MSSQL_PG_DATABASE_CONNECTION = 'postgresql+psycopg2://grp_projects:vEPLMPYTdyw9ND7Z@10.0.247.66:5432/grp_projects'
# engine_mssql_remote = create_engine(MSSQL_PG_DATABASE_CONNECTION)
#
#
# DBSession = sessionmaker(autocommit=False, autoflush=False)
# DBSession.configure(bind=engine_mssql_remote)
#
#
# session = DBSession()
#
# inspector = inspect(engine_mssql_remote)
# schemas = inspector.get_schema_names()
# inspected_set = set()
# for schema in schemas:
#     print("schema: %s" % schema)
#     if schema == 'pjpub':
#         for table_name in inspector.get_table_names(schema=schema):
#             print(table_name)
#             # if table_name == 'MSP_PROJECTS':
#             for column in inspector.get_columns(table_name, schema=schema):
#                 if 'TASK_UID' in column.get('name'):
#                     inspected_set.add(table_name)
#                     print(f"schemas: {schema}, table {table_name}, column: {column}")
#
# print(inspected_set)

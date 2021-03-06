from sqlalchemy import create_engine, MetaData 
from .core.services import EventService
from .auth.services import AuthService
from .core.impls.sql import AnalyticalEventMysqlRepository, ProjectMysqlRepository
from .auth.impls.sql import AuthorisationSQLRepository, UserSQLRepository
from collections import namedtuple


Context = namedtuple("Context", ['event_service', 'auth_service'])


def create_context(db_name):
    metadata = MetaData()
    engine = create_engine(f"sqlite:///{db_name}")

    user_repository = UserSQLRepository(metadata, engine)
    auth_repository = AuthorisationSQLRepository(metadata, engine)
    auth_service = AuthService(user_repository, auth_repository)

    user_getter = user_repository.get_by_id
    project_repository = ProjectMysqlRepository(metadata, engine)
    analytical_repository = AnalyticalEventMysqlRepository(metadata, engine)
    event_service = EventService(user_getter, project_repository, analytical_repository)
    
    metadata.create_all(engine)
    return Context(event_service, auth_service)



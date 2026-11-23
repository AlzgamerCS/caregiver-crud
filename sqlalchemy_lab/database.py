from sqlalchemy import create_engine, event


def open_database(url="sqlite://"):
    engine = create_engine(url)
    if engine.dialect.name == "sqlite":
        @event.listens_for(engine, "connect")
        def enforce_foreign_keys(connection, _record):
            connection.execute("PRAGMA foreign_keys = ON")
    return engine

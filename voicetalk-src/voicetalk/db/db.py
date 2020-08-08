import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker


class DB:
    __engine = None
    __session = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    def connect(self, url: str, dispose_first: bool = False, **kwargs) -> None:
        """Create the DB corresponding engine

        Args:
            :param url: Database URL
            :param dispose_first: Dispose the engine first or not. Defaults to False.
            **kwargs: Keyword arguments accepted by sqlalchemy create_engine function
        """
        if dispose_first and self.__engine:
            self.__engine.dispose()
            self.__engine = None

        if self.__engine:
            return

        self.__engine = create_engine(url, **kwargs)
        self.__session = sessionmaker(bind=self.__engine)

    @contextlib.contextmanager
    def get_session_scope(self) -> None:
        """Provide a transaction scope to isolate a group of orm operations.

        Reference: https://bit.ly/2NMiZgY
        """
        session = self.get_raw_session()

        try:
            yield session
            session.commit()
        except:  # noqa: E722
            session.rollback()
            raise
        finally:
            session.close()

    def get_raw_session(self):
        """Get raw DB session to execute SQL
        """
        if self.__engine is None:
            raise Exception('You should invoke connect() first')
        elif self.__session is None:
            self.__session = sessionmaker(bind=self.__engine)

        return self.__session()

from __future__ import annotations

from os import getenv
from typing import Dict, Optional
from urllib.parse import urlencode

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class MongoDbConnectionConf:
    __version__ = "1.0.0"

    def __init__(
        self,
        protocol: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        database: Optional[str] = None,
        connection_string: Optional[Dict[str, str]] = None,
    ) -> None:
        self.database: str = database or self.__get_default_env("MONGO_DB_NAME")
        self.protocol: str = protocol or self.__get_default_env("MONGO_DB_PROTOCOL")
        self.user: str = user or self.__get_default_env("MONGO_DB_USER")
        self.password: str = password or self.__get_default_env("MONGO_DB_PASSWORD")
        self.dns: str = host or self.__get_default_env("MONGO_DB_DNS")
        self.connection_options: dict = {
            "readPreference": "secondaryPreferred",
            "retryWrites": "true",
            "w": "majority",
        }
        if connection_string:
            self.connection_options.update(connection_string)

    def __get_default_env(self, name: str) -> str:
        """
        Look for values in enviroment file.
        :param name: The name to look in env
        :type name: str
        :return: Value given the name
        :rtype: str
        """
        value: Optional[str] = getenv(name)
        if value is None:
            raise ValueError(f"The default value for {name} was not found in ENV FILE")
        return value

    def create_database_uri(self) -> str:
        """
        Creates the DB's URI.
        :return: The DB's URI
        :rtype: str
        """
        return (
            f"{self.protocol}://{self.user}:{self.password}"
            f"@{self.dns}/{self.database}"
            f"?{urlencode(self.connection_options)}"
        )


class MongoDbManager:
    """
    A client-side representation of a MongoDB repository.
    """

    __version__ = "1.0.0"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(MongoDbManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        connection_conf: MongoDbConnectionConf,
    ) -> None:
        self._connection_conf = connection_conf
        self.__init_client_and_database()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __init_client_and_database(self) -> None:
        """
        Creates a new client and DB's session.
        :return:
        :rtype: None
        """
        self._client = MongoClient(
            self._connection_conf.create_database_uri(), connect=False
        )
        self._database = self._client[self._connection_conf.database]

    def get_client(self) -> MongoClient:
        return self._client

    def get_database(self) -> Database:
        return self._database

    def get_collection(self, collection: str) -> Collection:
        return self._database[collection]

    def close(self) -> None:
        """
        Cleanup client resources and disconnects from DB.
        :return:
        :rtype: None
        """
        self._client.close()

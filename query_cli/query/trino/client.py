from typing import Set, Dict, Optional, List
from datetime import timedelta

from requests.auth import HTTPBasicAuth
import requests


BASIC_AUTH = HTTPBasicAuth('test1_SYSADMIN', '')


class TrinoHeaders():
    REQUEST_SOURCE = "X-Trino-Source"
    REQUEST_TRACE_TOKEN = "X-Trino-Request-Trace-Token"
    REQUEST_TRANSACTION_ID = "X-Trino-Transaction-Id"
    REQUEST_CLIENT_INFO = "X-Trino-Client-Info"
    REQUEST_CLIENT_TAGS = "X-Trino-Client-Tags"
    REQUEST_CATALOG = "X-Trino-Catalog"
    REQUEST_SCHEMA = "X-Trino-Schema"
    REQUEST_PATH = "X-Trino-Path"
    REQUEST_USER = "X-Trino-User"
    REQUEST_LOCALE= "X-Trino-Language"
    REQUEST_SET_CATALOG = "X-Trino-Set-Catalog"
    REQUEST_SET_SCHEMA = "X-Trino-Set-Schema"
    REQUEST_SET_PATH = "X-Trino-Set-Path"


class SessionInfo():
    def __init__(
        self,
        server_uri: str,
        principal: Optional[str],
        user: Optional[str],
        source: str,
        traceToken: Optional[str],
        clientTags: Set[str],
        clientInfo: str,
        catalog: str,
        schema: Optional[str],
        path: str,
        timeZone: Optional[str],
        locale: str,
        resourceEstimates: Dict[str, str],
        properties: Dict[str, str],
        preparedStatements: Dict[str, str],
        transactionId: str,
        clientRequestTimeout: timedelta,
        compressionDisabled: bool,
        database: str,
    ) -> None:
        self.server_uri = server_uri
        self.principal = principal
        self.user = user
        self.source = source
        self.traceToken = traceToken
        self.clientTags = clientTags
        self.clientInfo = clientInfo
        self.catalog = catalog
        self.schema = schema
        self.path = path
        self.timeZone = timeZone
        self.locale = locale
        self.resourceEstimates = resourceEstimates
        self.properties = properties
        self.preparedStatements = preparedStatements
        self.transactionId = transactionId
        self.clientRequestTimeout = clientRequestTimeout
        self.compressionDisabled = compressionDisabled    
        self.database = database

    def clone(self) -> 'SessionInfo':
        return SessionInfo(
            server_uri=self.server_uri,
            principal=self.principal,
            user=self.user,
            source=self.source,
            traceToken=self.traceToken,
            clientTags=self.clientTags,
            clientInfo=self.clientInfo,
            catalog=self.catalog,
            schema=self.schema,
            path=self.path,
            timeZone=self.timeZone,
            locale=self.locale,
            resourceEstimates=self.resourceEstimates,
            properties=self.properties,
            preparedStatements=self.preparedStatements,
            transactionId=self.transactionId,
            clientRequestTimeout=self.clientRequestTimeout,
            compressionDisabled=self.compressionDisabled,
            database=self.database,
        )


class Session():
    @staticmethod
    def new(uri: str, org_id: str) -> 'Session':
        return Session(
            server_uri=uri,
            org_id=org_id,
            principal=None,
            user='admin',
            source="",
            traceToken=None,
            clientTags=set(),
            clientInfo='',
            catalog='delta',
            schema='',
            path='',
            timeZone=None,
            locale='en-US',
            resourceEstimates=dict(),
            properties=dict(),
            preparedStatements=dict(),
            transactionId='',
            clientRequestTimeout=timedelta(seconds=60),
            compressionDisabled=False,
            database='',
        )

    def __init__(
        self,
        server_uri: str,
        org_id: str,
        principal: Optional[str],
        user: Optional[str],
        source: str,
        traceToken: Optional[str],
        clientTags: Set[str],
        clientInfo: str,
        catalog: str,
        schema: str,
        path: str,
        timeZone: Optional[str],
        locale: str,
        resourceEstimates: Dict[str, str],
        properties: Dict[str, str],
        preparedStatements: Dict[str, str],
        transactionId: str,
        clientRequestTimeout: timedelta,
        compressionDisabled: bool,
        database: str,
    ) -> None:        
        self._info = SessionInfo(
            server_uri=server_uri,
            principal=principal,
            user=user,
            source=source,
            traceToken=traceToken,
            clientTags=clientTags,
            clientInfo=clientInfo,
            catalog=catalog,
            schema=schema,
            path=path,
            timeZone=timeZone,
            locale=locale,
            resourceEstimates=resourceEstimates,
            properties=properties,
            preparedStatements=preparedStatements,
            transactionId=transactionId,
            clientRequestTimeout=clientRequestTimeout,
            compressionDisabled=compressionDisabled,
            database=database,          
        )
        self._org_id = org_id
        self._previous_infos: List[SessionInfo] = []

    @property
    def org_id(self) -> str:
        return self._org_id

    @property
    def database(self) -> str:
        return self._info.database

    @database.setter
    def database(self, val: str) -> None:
        self._info.database = val

    @property
    def user(self) -> str:
        assert self._info.user is not None
        return self._info.user

    def build_request(self, query: str) -> requests.PreparedRequest:
        if self._info.server_uri is None:
            raise ValueError("Invalid server URI")

        full_url = "{}/v1/statement".format(self._info.server_uri)

        headers = dict()
        if self._info.source is not None:
            headers[TrinoHeaders.REQUEST_SOURCE] = self._info.source
        
        if self._info.traceToken is not None:
            headers[TrinoHeaders.REQUEST_TRACE_TOKEN] = self._info.traceToken

        if len(self._info.clientTags) > 0:
            headers[TrinoHeaders.REQUEST_CLIENT_TAGS] = ",".join(self._info.clientTags)

        if self._info.clientInfo is not None:
            headers[TrinoHeaders.REQUEST_CLIENT_INFO] = self._info.clientInfo

        if self._info.catalog is not None:
            headers[TrinoHeaders.REQUEST_CATALOG] = self._info.catalog

        if self._info.database is not None:
            if self._info.schema is not None:
                headers[TrinoHeaders.REQUEST_SCHEMA] = "{}_{}".format(self._info.database, self._info.schema).lower()
            else:
                headers[TrinoHeaders.REQUEST_SCHEMA] = self._info.database.lower()
        elif self._info.schema is not None:
            raise ValueError("Non-none schema when database is none, that shouldn't happen")

        if self._info.path is not None:
            headers[TrinoHeaders.REQUEST_PATH] = self._info.path     

        # TODO: timezone
        
        headers[TrinoHeaders.REQUEST_LOCALE] = self._info.locale

        # TODO: properties
        # TODO: resource estimates
        # TODO: roles
        # TODO: extra credentials
        # TODO: preparated statments

        if self._info.transactionId is None:
            headers[TrinoHeaders.REQUEST_TRANSACTION_ID] = "NONE"
        else:
            headers[TrinoHeaders.REQUEST_TRANSACTION_ID] = self._info.transactionId

        # TODO: client capabilities

        request = requests.Request(
            method="POST",
            url=full_url,
            data=query,
            headers=headers,
            auth=BASIC_AUTH,
        )

        return request.prepare()

    def process_response(self, response: requests.Response) -> 'Session':
        self._previous_infos.append(self._info)
        self._info = self._info.clone()

        #print("response headers = {}".format(response.headers))
        if TrinoHeaders.REQUEST_SET_CATALOG in response.headers:
            self._info.catalog = response.headers[TrinoHeaders.REQUEST_SET_CATALOG]
        if TrinoHeaders.REQUEST_SET_SCHEMA in response.headers:
            request_set_schema = response.headers[TrinoHeaders.REQUEST_SET_SCHEMA]
            if len(self._info.database) > 0:
                assert request_set_schema.lower().startswith(self._info.database.lower())
                if self._info.database == request_set_schema:
                    self._info.schema = None
                else:
                    self._info.schema = request_set_schema[len(self._info.database) + 1:]
            else:
                self._info.schema = request_set_schema
        if TrinoHeaders.REQUEST_SET_PATH in response.headers:
            self._info.path = response.headers[TrinoHeaders.REQUEST_SET_PATH]
        #if TrinoHeaders.REQUEST_SET_SESSION in response.headers:
        return self
            
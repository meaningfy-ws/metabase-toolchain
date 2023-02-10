import requests
from metabase.migration.adapters.metabase import Metabase

"""
Metabase 0.42.4
"""


class API:
    metabase: Metabase
    BASE_URL = "/api"
    COLLECTION_ENDPOINT = "/collection"
    COLLECTION_GRAPH_ENDPOINT = "/collection/graph"
    DASHBOARD_ENDPOINT = "/dashboard"
    DATABASE_ENDPOINT = "/database"
    TABLE_ENDPOINT = "/table"
    METRIC_ENDPOINT = "/metric"
    SEGMENT_ENDPOINT = "/segment"
    SETTING_ENDPOINT = "/setting"
    CARD_ENDPOINT = "/card"
    DASHBOARD_CARD_ENDPOINT = "/dashboard/{id}"
    DASHBOARD_CARDS_ENDPOINT = "/dashboard/{id}/cards"
    PERMISSIONS_GROUP_ENDPOINT = "/permissions/group"
    USER_ENDPOINT = "/user"

    def __init__(self, host: str, user: str, password: str):
        self.metabase = Metabase(
            host=host,
            user=user,
            password=password
        )

    def api_url(self, endpoint: str):
        return self.BASE_URL + endpoint

    def get(self, endpoint: str, **kwargs):
        return self.metabase.get(self.api_url(endpoint), **kwargs).json()

    def get_collection(self, collection_id):
        return self.get(f"{self.COLLECTION_ENDPOINT}/{collection_id}")

    def get_collections_graph(self):
        return self.get(f"{self.COLLECTION_GRAPH_ENDPOINT}")

    def get_collections(self):
        return self.get(self.COLLECTION_ENDPOINT)

    def get_dashboards(self):
        return self.get(self.DASHBOARD_ENDPOINT)

    def get_database(self, db_id, full_sync=True):
        params = None
        if full_sync:
            params = {"include": "tables.fields"}
        return self.get(f"{self.DATABASE_ENDPOINT}/{db_id}", params=params)

    def get_databases(self):
        data = self.get(self.DATABASE_ENDPOINT, params={"saved": True})
        databases = []
        if data:
            databases = data['data']
            for db in databases:
                db_tables = self.get_database(db['id'])
                if db_tables and ("tables" in db_tables):
                    db["tables"] = db_tables["tables"]

        return databases

    def get_tables(self):
        return self.get(self.TABLE_ENDPOINT)

    def get_metrics(self):
        return self.get(self.METRIC_ENDPOINT)

    def get_segments(self):
        return self.get(self.SEGMENT_ENDPOINT)

    def get_cards(self):
        return self.get(self.CARD_ENDPOINT)

    def get_dashboard_cards(self, dashboard_id: str):
        return self.get(self.DASHBOARD_CARD_ENDPOINT.format(id=dashboard_id))

    def get_permissions_groups(self):
        return self.get(self.PERMISSIONS_GROUP_ENDPOINT)

    def get_users(self):
        api_users = self.get(self.USER_ENDPOINT, params={"status": "all"})
        return api_users["data"] if api_users else []

    def get_settings(self):
        api_settings = self.get(self.SETTING_ENDPOINT)
        return api_settings

    def post(self, endpoint: str, data: dict = None):
        response = self.metabase.post(self.api_url(endpoint), json=data)
        return response.json()

    def post_collection(self, data: dict):
        return self.post(self.COLLECTION_ENDPOINT, data)

    def post_dashboard(self, data: dict):
        return self.post(self.DASHBOARD_ENDPOINT, data)

    def post_dashboard_card(self, dashboard_id: str, data: dict):
        return self.post(self.DASHBOARD_CARDS_ENDPOINT.format(id=dashboard_id), data)

    def post_database(self, data: dict):
        return self.post(self.DATABASE_ENDPOINT, data)

    def post_metric(self, data: dict):
        return self.post(self.METRIC_ENDPOINT, data)

    def post_segment(self, data: dict):
        return self.post(self.SEGMENT_ENDPOINT, data)

    def post_card(self, data: dict):
        return self.post(self.CARD_ENDPOINT, data)

    def post_permissions_group(self, data: dict):
        return self.post(self.PERMISSIONS_GROUP_ENDPOINT, data)

    def post_user(self, data: dict):
        return self.post(self.USER_ENDPOINT, data)

    def put(self, endpoint: str, data: dict):
        response = self.metabase.put(self.api_url(endpoint), json=data)
        try:
            content = response.json()
        except ValueError:
            content = response.content
        return content

    def put_database(self, database_id, data: dict):
        return self.put(f"{self.DATABASE_ENDPOINT}/{database_id}", data)

    def put_permissions_group(self, permissions_group_id, data: dict):
        return self.put(f"{self.PERMISSIONS_GROUP_ENDPOINT}/{permissions_group_id}", data)

    def put_user(self, user_id, data: dict):
        return self.put(f"{self.USER_ENDPOINT}/{user_id}", data)

    def put_dashboard(self, dashboard_id, data: dict):
        return self.put(f"{self.DASHBOARD_ENDPOINT}/{dashboard_id}", data)

    def put_dashboard_card(self, dashboard_id, data: dict):
        return self.put(f"{self.DASHBOARD_CARD_ENDPOINT}/{dashboard_id}", data)

    def put_collection(self, collection_id, data: dict):
        return self.put(f"{self.COLLECTION_ENDPOINT}/{collection_id}", data)

    def put_collection_graph(self, data: dict):
        return self.put(f"{self.COLLECTION_GRAPH_ENDPOINT}", data)

    def put_card(self, card_id, data: dict):
        return self.put(f"{self.CARD_ENDPOINT}/{card_id}", data)

    def put_settings(self, data: dict):
        return self.put(f"{self.SETTING_ENDPOINT}", data)

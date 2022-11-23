import requests
from metabase import Metabase

"""
Metabase 0.42.4
"""


class API:
    metabase: Metabase
    BASE_URL = "/api"
    COLLECTION_ENDPOINT = "/collection"
    DASHBOARD_ENDPOINT = "/dashboard"
    DATABASE_ENDPOINT = "/database"
    METRIC_ENDPOINT = "/metric"
    SEGMENT_ENDPOINT = "/segment"
    SETTING_ENDPOINT = "/setting"
    CARD_ENDPOINT = "/card"
    DASHBOARD_CARD_ENDPOINT = "/dashboard/{id}"
    DASHBOARD_CARDS_ENDPOINT = "/dashboard/{id}/cards"
    PERMISSIONS_GROUP_ENDPOINT = "/permissions/group"
    PERMISSIONS_MEMBERSHIP_ENDPOINT = "/permissions/membership"
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

    def get_collections(self):
        return self.get(self.COLLECTION_ENDPOINT)

    def get_dashboards(self):
        return self.get(self.DASHBOARD_ENDPOINT, params={"f": "mine"})

    def get_databases(self):
        return self.get(self.DATABASE_ENDPOINT)

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

    def get_permissions_memberships(self):
        return self.get(self.PERMISSIONS_MEMBERSHIP_ENDPOINT)

    def get_user(self, user_email):
        return self.get(f"{self.USER_ENDPOINT}", params={"query": f"email={user_email}"})

    def get_users(self):
        api_users = self.get(self.USER_ENDPOINT, params={"status": "all"})
        return api_users["data"] if api_users else []

    def post(self, endpoint: str, data: dict, with_exception: bool = False):
        try:
            r = self.metabase.post(self.api_url(endpoint), json=data)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if with_exception:
                raise err
            else:
                print("HTTP Error :: ", r.status_code, r.content.decode("utf-8"))
                print(data)
        return r

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

    def post_permissions_membership(self, data: dict):
        return self.post(self.PERMISSIONS_MEMBERSHIP_ENDPOINT, data)

    def post_user(self, data: dict, with_exception: bool = False):
        return self.post(self.USER_ENDPOINT, data, with_exception=with_exception)

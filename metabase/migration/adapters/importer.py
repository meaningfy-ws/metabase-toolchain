import json
import logging
import os
from pathlib import Path
from typing import List, Dict
import time

import dotenv
import requests

from metabase.migration.adapters.api import API
from metabase.migration.adapters.exporter import DEFAULT_EXPORT_FILE
from metabase.migration.model.migration_data import MigrationData
from metabase.migration.services import find_element, add_fields_to_tables, generate_keys_map, generate_map

dotenv.load_dotenv(verbose=True, override=True)

MONGO_DB_USER = os.environ.get('MONGO_DB_USER')
MONGO_DB_PASS = os.environ.get('MONGO_DB_PASS')
MONGO_DB_HOST = os.environ.get('MONGO_DB_HOST')
ENV_MONGO_DB_PORT = os.environ.get('MONGO_DB_PORT')
MONGO_DB_PORT = int(ENV_MONGO_DB_PORT) if ENV_MONGO_DB_PORT else None


class Importer:
    api: API
    debug: bool = False

    def __init__(self, host: str, user: str, password: str, logger: logging.Logger):
        self.api = API(
            host=host,
            user=user,
            password=password
        )

        self.logger = logger

    @classmethod
    def _import_resources(cls, items, api_call):
        for data in items:
            api_call(data)

    @classmethod
    def _update_mongodb_data(cls, database):
        if MONGO_DB_USER:
            database['details']['user'] = MONGO_DB_USER
        if MONGO_DB_PASS:
            database['details']['pass'] = MONGO_DB_PASS
        if MONGO_DB_HOST:
            database['details']['host'] = MONGO_DB_HOST
        if MONGO_DB_PORT:
            database['details']['port'] = MONGO_DB_PORT

    def _import_databases(self, databases: List, databases_map: Dict, users_keys_map: Dict):
        self.logger.info("... databases")
        for database in databases:
            tables = database["tables"]
            del database["tables"]

            database['creator_id'] = users_keys_map[database['creator_id']]
            if database['engine'] == 'mongo':
                self._update_mongodb_data(database)
            db_name = database['name']
            self.logger.info(f"... {db_name}")

            if db_name in databases_map:
                res = self.api.put_database(databases_map[db_name], database)
            else:
                res = self.api.post_database(database)

            while True:
                new_db = self.api.get_database(res['id'], full_sync=False)
                if new_db['initial_sync_status'] == 'complete':
                    break
                time.sleep(3)

        self.logger.info("databases ... ok")

    @classmethod
    def _prepare_card(cls, card: Dict, tables_keys_map: Dict, databases_keys_map: Dict,
                      collections_keys_map: Dict, fields_keys_map: Dict, users_keys_map: Dict) -> Dict:
        if "creator" in card:
            del card["creator"]
        if "creator_id" in card:
            if card['creator_id'] in users_keys_map:
                card['creator_id'] = users_keys_map[card['creator_id']]
            else:
                if cls.debug:
                    print(f"KEYS_MAP_ERROR :: users_keys_map :: {card['creator_id']}")
                del card["creator_id"]
        if "made_public_by_id" in card:
            del card["made_public_by_id"]
        if "collection" in card:
            del card["collection"]

        if 'table_id' in card:
            if card['table_id'] in tables_keys_map:
                card['table_id'] = tables_keys_map[card['table_id']]
            else:
                if cls.debug:
                    print(f"KEYS_MAP_ERROR :: tables_keys_map :: {card['table_id']}")
                del card['table_id']
        if 'database_id' in card:
            if card['database_id'] in databases_keys_map:
                card['database_id'] = databases_keys_map[card['database_id']]
            else:
                if cls.debug:
                    print(f"KEYS_MAP_ERROR :: databases_keys_map :: {card['database_id']}")
                del card['database_id']

        if 'collection_id' in card:
            if card['collection_id'] in collections_keys_map:
                card['collection_id'] = collections_keys_map[card['collection_id']]
            else:
                if cls.debug:
                    print(f"KEYS_MAP_ERROR :: collections_keys_map :: {card['collection_id']}")
                del card['collection_id']

        if ("dataset_query" in card) and card['dataset_query']:
            if ('database' in card['dataset_query']) and card['dataset_query']['database']:
                if card['dataset_query']['database'] in databases_keys_map:
                    card['dataset_query']['database'] = databases_keys_map[card['dataset_query']['database']]
                else:
                    if cls.debug:
                        print(f"KEYS_MAP_ERROR :: databases_keys_map :: {card['dataset_query']['database']}")
                    # del card['dataset_query']['database']
            if ('query' in card['dataset_query']) and card['dataset_query']['query']:
                card_dataset_query_query = card['dataset_query']['query']
                if ('source-table' in card_dataset_query_query) \
                        and card_dataset_query_query['source-table']:
                    if card_dataset_query_query['source-table'] in tables_keys_map:
                        card_dataset_query_query['source-table'] = tables_keys_map[
                            card_dataset_query_query['source-table']]
                    else:
                        if cls.debug:
                            print(f"KEYS_MAP_ERROR :: tables_keys_map :: {card_dataset_query_query['source-table']}")
                        # del card_dataset_query_query['source-table']

                for field_key in card_dataset_query_query:
                    if card_dataset_query_query[field_key] and isinstance(card_dataset_query_query[field_key], list):
                        for item in card_dataset_query_query[field_key]:
                            if isinstance(item, list) and len(item) >= 2:
                                if isinstance(item[1], list) and len(item[1]) >= 2:
                                    if item[1][0] == 'field':
                                        if item[1][1] in fields_keys_map:
                                            item[1][1] = fields_keys_map[item[1][1]]
                                        else:
                                            if cls.debug:
                                                print(
                                                    f"KEYS_MAP_ERROR :: fields_keys_map :: {item[1][1]} :: {card['id']}")
                                            # item[1][1] = 0

                                else:
                                    if item[0] == 'field':
                                        if item[1] in fields_keys_map:
                                            item[1] = fields_keys_map[item[1]]
                                        else:
                                            if cls.debug:
                                                print(f"KEYS_MAP_ERROR :: fields_keys_map :: {item[1]} :: {card['id']}")
                                            # item[1] = 0

        if ('result_metadata' in card) and card['result_metadata']:
            for item in card['result_metadata']:
                if ('table_id' in item) and item['table_id']:
                    if item['table_id'] in tables_keys_map:
                        item['table_id'] = tables_keys_map[item['table_id']]
                    else:
                        if cls.debug:
                            print(f"KEYS_MAP_ERROR :: tables_keys_map :: {item['table_id']}")
                        # del item['table_id']
                if ("field_ref" in item) and item["field_ref"]:
                    if isinstance(item["field_ref"], list) and len(item["field_ref"]) >= 2 and (
                            item["field_ref"][0] == 'field'):
                        if item["field_ref"][1] in fields_keys_map:
                            item["field_ref"][1] = fields_keys_map[item["field_ref"][1]]
                        else:
                            if cls.debug:
                                print(f"KEYS_MAP_ERROR :: fields_keys_map :: {item['field_ref'][1]} :: {card['id']}")
                            # item["field_ref"][1] = 0
                if 'id' in item:
                    if item["id"] in fields_keys_map:
                        item["id"] = fields_keys_map[item["id"]]
                    else:
                        if cls.debug:
                            print(f"KEYS_MAP_ERROR :: fields_keys_map :: {item['id']}")
                        # item["id"] = 0

        if ('visualization_settings' in card) and card['visualization_settings']:
            card_visualization_settings = card['visualization_settings']
            if ('table.columns' in card_visualization_settings) and card_visualization_settings['table.columns']:
                for item in card_visualization_settings['table.columns']:
                    if ("fieldRef" in item) and item["fieldRef"]:
                        if isinstance(item["fieldRef"], list) and len(item["fieldRef"]) >= 2 and (
                                item["fieldRef"][0] == 'field'):
                            if item["fieldRef"][1] in fields_keys_map:
                                item["fieldRef"][1] = fields_keys_map[item["fieldRef"][1]]
                            else:
                                if cls.debug:
                                    print(f"KEYS_MAP_ERROR :: fields_keys_map :: {item['fieldRef'][1]} :: {card['id']}")
                                item["fieldRef"][1] = 0

        return card

    def _import_dashboards(self, dashboards: List, collections_keys_map: Dict):
        self.logger.info("... dashboards")
        dashboards_map = generate_map('name', 'id', self.api.get_dashboards())

        for dashboard in dashboards:
            if "creator" in dashboard:
                del dashboard["creator"]
            if "creator_id" in dashboard:
                del dashboard["creator_id"]
            if "made_public_by_id" in dashboard:
                del dashboard["made_public_by_id"]

            if dashboard['collection_id'] in collections_keys_map:
                dashboard['collection_id'] = collections_keys_map[dashboard['collection_id']]
            else:
                if self.debug:
                    print(f"KEYS_MAP_ERROR :: collections_keys_map :: {dashboard['collection_id']}")
                del dashboard['collection_id']
            dashboard_name = dashboard['name']
            if dashboard_name in dashboards_map:
                self.api.put_dashboard(dashboards_map[dashboard_name], dashboard)
            else:
                self.api.post_dashboard(dashboard)

        self.logger.info("dashboards ... ok")

    def _import_dashboard_cards(self, dashboard_cards: List, dashboards_keys_map: Dict, cards_keys_map: Dict):
        self.logger.info("... dashboard_cards")
        for dashboard in dashboard_cards:
            cards_map = {}
            cards = dashboard['ordered_cards']
            new_dashboard_id = dashboards_keys_map[dashboard['id']]
            for item in cards:
                if item['card_id'] not in cards_keys_map:
                    continue
                card = item['card']
                del item['card']
                card_name = card['name']
                item['dashboard_id'] = new_dashboard_id
                item['cardId'] = cards_keys_map[item['card_id']]

                if card_name in cards_map:
                    self.api.put_dashboard_card(new_dashboard_id, {"cards": [item]})
                else:
                    self.api.post_dashboard_card(new_dashboard_id, item)

        self.logger.info("dashboard_cards ... ok")

    def _import_collections(self, collections: List, collections_map: Dict, users_keys_map: Dict):
        self.logger.info("... collections")
        keys_map = {}
        for collection in collections:
            if collection['id'] == "root":
                continue
            if ('personal_owner_id' in collection) and collection['personal_owner_id']:
                collection['personal_owner_id'] = users_keys_map[collection['personal_owner_id']]
            collection_name = collection['name']

            parent_id = collection['parent_id']
            del collection['parent_id']
            del collection['effective_ancestors']
            if collection_name in collections_map:
                res = self.api.put_collection(collections_map[collection_name], collection)
            else:
                if 'color' not in collection:
                    collection['color'] = "#000000"
                res = self.api.post_collection(collection)
            collection['parent_id'] = parent_id
            keys_map[collection['id']] = res['id']

        # Update parent_id with new ids
        for collection in collections:
            if ('parent_id' in collection) and collection['parent_id'] is not None:
                collection["parent_id"] = keys_map[collection["parent_id"]]
                self.api.put_collection(keys_map[collection['id']], collection)

        self.logger.info("collections ... ok")

    def _import_collections_graph(self, graph: Dict, collections_keys_map: Dict):
        self.logger.info("... collections_graph")
        body = {}
        if 'revision' in graph:
            body['revision'] = graph['revision']
        if 'groups' in graph:
            body['groups'] = {}
            for group_id in graph['groups']:
                body['groups'][group_id] = {}
                for collection_id in graph['groups'][group_id]:
                    if collection_id == 'root':
                        body['groups'][group_id][collection_id] = graph['groups'][group_id][collection_id]
                        continue
                    int_collection_id = int(collection_id)
                    if int_collection_id in collections_keys_map:
                        body['groups'][group_id][collections_keys_map[int_collection_id]] = graph['groups'][group_id][
                            collection_id]

        self.api.put_collection_graph(body)
        self.logger.info("collections_graph ... ok")

    def _import_cards(self, cards: List, cards_map: Dict, tables_keys_map: Dict, databases_keys_map: Dict,
                      collections_keys_map: Dict, fields_keys_map: Dict, users_keys_map: Dict):
        self.logger.info("... cards")
        for card in cards:
            card_name = card['name']
            card = self._prepare_card(card, tables_keys_map, databases_keys_map, collections_keys_map,
                                      fields_keys_map, users_keys_map)
            if card_name in cards_map:
                self.api.put_card(cards_map[card_name], card)
            else:
                self.api.post_card(card)

        self.logger.info("cards ... ok")

    def _import_permissions_groups(self, permissions_groups: List, permissions_group_map: Dict):
        self.logger.info("... permissions_groups")
        for permissions_group in permissions_groups:
            group_name = permissions_group['name']
            if group_name in permissions_group_map and group_name in ["Administrators", "All Users"]:
                # You cannot edit or delete the 'All Users' or 'Administrators' permissions group!
                continue
            if group_name in permissions_group_map:
                self.api.put_permissions_group(permissions_group_map[group_name], permissions_group)
            else:
                self.api.post_permissions_group(permissions_group)

        self.logger.info("permissions_groups ... ok")

    def _import_users(self, users: List, users_map: Dict, permissions_groups_keys_map: Dict):
        self.logger.info("... users")
        for user in users:
            group_ids = user['group_ids']
            user['group_ids'] = list([permissions_groups_keys_map[group_id] for group_id in group_ids])

            user_email = user['email']
            if user_email in users_map:
                self.api.put_user(users_map[user_email], user)
            else:
                self.api.post_user(user)
        self.logger.info("users ... ok")

    def _import_settings(self, settings: List):
        self.logger.info("... settings")
        keys = ['custom-geojson']
        new_settings = {}
        for setting in settings:
            key = setting['key']
            if key in keys:
                new_settings[key] = setting['value']

        self.api.put_settings(new_settings)
        self.logger.info("settings ... ok")

    @classmethod
    def _tables_map(cls, data: list):
        map_db = {}
        for item in data:
            if item['db']['name'] not in map_db:
                map_db[item['db']['name']] = {}
            map_db[item['db']['name']][item['name']] = item['id']
        return map_db

    def import_data(self, data: MigrationData):
        self.logger.info(f'Importing Metabase ... ')
        permissions_group_map = {permissions_group["name"]: permissions_group["id"] for permissions_group in
                                 self.api.get_permissions_groups()}

        self._import_permissions_groups(data.permissions_groups, permissions_group_map)
        new_permissions_group_map = {permissions_group["name"]: permissions_group["id"] for permissions_group in
                                     self.api.get_permissions_groups()}
        permissions_groups_keys_map = {}
        for permissions_group in data.permissions_groups:
            permissions_groups_keys_map[permissions_group['id']] = new_permissions_group_map[permissions_group['name']]

        users_map = generate_map('email', 'id', self.api.get_users())
        self._import_users(data.users, users_map, permissions_groups_keys_map)
        new_users_map = generate_map("email", "id", self.api.get_users())
        users_keys_map = generate_keys_map('id', 'email', new_users_map, data.users)

        self._import_settings(data.settings)

        databases_map = generate_map('name', 'id', self.api.get_databases())
        # self._import_databases(data.databases, databases_map, users_keys_map)
        new_databases = self.api.get_databases()
        new_databases_map = generate_map('name', 'id', new_databases)
        databases_keys_map = generate_keys_map('id', 'name', new_databases_map, data.databases)

        self._import_resources(data.metrics, self.api.post_metric)
        self._import_resources(data.segments, self.api.post_segment)

        collections_map = generate_map('name', 'id', self.api.get_collections())
        self._import_collections(data.collections, collections_map, users_keys_map)
        new_collections_map = generate_map('name', 'id', self.api.get_collections())
        collections_keys_map = generate_keys_map('id', 'name', new_collections_map, data.collections)

        self._import_collections_graph(data.collections_graph, collections_keys_map)

        new_tables = self.api.get_tables()
        add_fields_to_tables(new_tables, new_databases)

        new_tables_map = self._tables_map(new_tables)

        tables_keys_map = {}
        fields_keys_map = {}
        for table in data.tables:
            table_name = table['name']
            table_db = table['db']['name']
            if table_name not in new_tables_map[table_db]:
                continue
            tables_keys_map[table['id']] = new_tables_map[table_db][table_name]
            new_table = find_element("name", table_name, new_tables)
            if new_table:
                for table_field in table['fields']:
                    new_table_field = find_element("name", table_field["name"], new_table['fields'])
                    if new_table_field:
                        fields_keys_map[table_field['id']] = new_table_field['id']

        self._import_dashboards(data.dashboards, collections_keys_map)
        new_dashboards_map = generate_map('name', 'id', self.api.get_dashboards())
        dashboards_keys_map = generate_keys_map('id', 'name', new_dashboards_map, data.dashboards)

        new_cards = self.api.get_cards()
        cards_map = generate_map('name', 'id', new_cards)
        self._import_cards(data.cards, cards_map, tables_keys_map, databases_keys_map, collections_keys_map,
                           fields_keys_map, users_keys_map)
        new_cards_map = generate_map('name', 'id', self.api.get_cards())
        cards_keys_map = generate_keys_map('id', 'name', new_cards_map, data.cards)

        self._import_dashboard_cards(data.dashboard_cards, dashboards_keys_map, cards_keys_map)

    def import_data_from_file(self, file: str = None):
        data: MigrationData = self.load_data_from_file(file)
        self.import_data(data)

    @classmethod
    def load_data_from_file(cls, file: str = None) -> MigrationData:
        if not file:
            file = DEFAULT_EXPORT_FILE
        filepath = Path(file)

        with open(filepath, "r") as f:
            data = json.load(f)
            f.close()

        return MigrationData(**data)

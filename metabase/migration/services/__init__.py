def find_element(field_name: str, field_value: str, data: list):
    return next(filter(lambda item: item[field_name] == field_value, data), None)


def find_table_by_name(name, tables):
    return find_element("name", name, tables)


def generate_map(key_field: str, value_field: str, data: list):
    return {item[key_field]: item[value_field] for item in data}


def generate_keys_map(source_field: str, target_field: str, data2: dict, items: list):
    keys_map = {}
    for item in items:
        if item[target_field] in data2:
            keys_map[item[source_field]] = data2[item[target_field]]
    return keys_map


def add_fields_to_tables(tables, databases):
    for table in tables:
        table_db = find_element('id', table['db_id'], databases)
        if table_db:
            db_table = find_element('id', table['id'], table_db['tables'])
            if db_table:
                table['fields'] = db_table['fields']

import configparser
import json
import os
from unittest import case

import msal
import requests
from jsonpath_ng import parse

data = None

def compare(actual , expected):
    if str(expected) in str(actual):
        print(f'actual: {str(actual)} contains expected: {str(expected)}')
    else:
        raise AssertionError(f'actual: {str(actual)} does not contain expected: {str(expected)}')


def get_details_from_vault():
    api_vault_token_url = ""
    api_vault_url = ""
    test_env = os.environ["TEST_ENVIRONMENT"]
    if test_env == "" or None:
        test_env = "STG"
    vault_url = read_api_config(test_env, "vault_api_request_url")
    username = ""
    encrypted_password = ""
    scope = ["openid profile"]
    client_id = ""
    authority = "https://login.microsoftonline.com/organizations"
    app = msal.ConfidentialClientApplication(client_id,authority=authority)
    result = app.acquire_token_by_username_password(username=username, password=decrypt_message(encrypted_password), scopes=scope)
    jwt_token = result['id_token']
    vault_token_body_json = get_api_body("vault_token_body")
    vault_token_body_json = update_body_property(vault_token_body_json,"jwt", jwt_token)
    vault_token_headers_json = get_api_headers("vault_token_headers")
    vault_token_api_response = post_api(api_vault_token_url, vault_token_body_json, vault_token_headers_json)
    vault_token = vault_token_api_response.json().get("auth").get("client_token")
    vault_body_json = get_api_body("vault_body")
    vault_headers_json = get_api_headers("vault_headers")
    vault_api_response = get_api(api_vault_url, vault_body_json, vault_headers_json)
    compare("200", str(vault_api_response.status_code))
    global vault_data
    vault_data = vault_api_response.json().get("data")
    return vault_data

def read_api_config(en_name, key):
    config_file_path = os.path.join(os.path.dirname(__file__),"../global_config","api_config.ini")
    config = configparser.ConfigParser()
    # Check if the file exists
    if not os.path.exists(config_file_path):
        raise FileNotFoundError("Config file not found at {}".format(config_file_path))
    # Read the configuration file
    config.read(config_file_path)
    try:
        return config[en_name][key]
    except KeyError as e:
        raise KeyError("Key {} not found in {}".format(key, config_file_path))

def read_json_file(file_path):
    with open(file_path,'r') as file:
        data = json.load(file)
        return data

def send_api(api_type, url, body, headers):
    response = requests.request(api_type, url, json=body, headers=headers)
    print(f"status code: {response.status_code}")
    return response

def get_api(url, body, headers):
    response = requests.get(url, json=body, headers=headers)
    print(f"status code: {response.status_code}")
    return response

def post_api(url, body, headers):
    response = requests.post(url, json=body, headers=headers)
    print(f"status code: {response.status_code}")
    return response

def put_api(url, body, headers):
    response = requests.put(url, json=body, headers=headers)
    print(f"status code: {response.status_code}")
    return response

def delete_api(url, body, headers):
    response = requests.delete(url, body, headers=headers)
    print(f"status code: {response.status_code}")
    return response

def patch_api(url, body, headers):
    response = requests.patch(url, json=body, headers=headers)
    print(f"status code: {response.status_code}")
    return response

def get_url_from_api_config(url_name):
    url = read_api_config(os.environ["TEST_ENVIRONMENT"], url_name)
    return url

def get_api_body(template_name):
    template_path = os.path.abspath("./api_templates")
    print(template_path + "\\" + template_name)
    body = read_json_file(template_path + "\\" + template_name)
    return body

def get_api_headers(template_name):
    template_path = os.path.abspath("./api_templates")
    print(template_path + "\\" + template_name)
    headers = read_json_file(template_path + "\\" + template_name)
    return headers

def update_body_property(headers, property_path, property_value, property_type="STRING"):
    path_expression = parse(property_path)
    headers = path_expression.update(headers, convert_to_datatype(property_value, property_type))
    print(headers)
    return headers

def update_headers_property(headers, property_path, property_value, property_type="STRING"):
    path_expression = parse(property_path)
    headers = path_expression.update(headers, convert_to_datatype(property_value, property_type))
    print(headers)
    return headers

def remove_body_property(body, property_path):
    path_expression = parse(property_path)
    body = path_expression.filter(lambda d:True, body)
    print(body)
    return body

def remove_headers_property(headers, property_path):
    path_expression = parse(property_path)
    body = path_expression.filter(lambda d:True, headers)
    print(body)
    return body

def update_token_body(token_body, client_id_key, client_secret_key_name):
    vault_client_id_key_name = read_api_config(os.environ["TEST_ENVIRONMENT"], client_id_key)
    vault_secret_key_name = read_api_config(os.environ["TEST_ENVIRONMENT"], client_secret_key_name)
    data = get_details_from_vault()
    token_body["client_id"] = data.get(vault_client_id_key_name)
    token_body["client_secret"] = data.get(client_secret_key_name)
    return token_body

def convert_to_datatype(value, datatype):
    converted_value = None
    match datatype.upper():
        case "STRING":
            converted_value = str(value)
        case "INTEGER":
            converted_value = int(value)
        case "FLOAT":
            converted_value = float(value)
        case "BOOLEAN":
            converted_value = bool(value)
        case _:
            raise AssertionError(f'datatype {datatype} not found. Please check.')

    return converted_value


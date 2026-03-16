import os
from behave import given, when, then
from behave.exception import StepNotImplementedError

from common_library.api_lib import *

token = None
url = None
product_response = None
product_id = "1"
os.environ["TEST_ENVIRONMENT"] = "STG"

@given(u'Product Access Token API with body "{body_template}" and headers "{headers_template}"')
def product_token_api(context, body_template, headers_template):
    global token
    os.environ["TEST_ENVIRONMENT"] = "STG"
    url = get_url_from_api_config("user_token_url")
    body = get_api_headers(body_template)
    body = update_api_body_json(body, "username", "emilys")
    body = update_api_body_json(body, "password", "emilyspass")
    response = post_api(url, body, get_api_headers(headers_template))
    compare("200", response.status_code)
    token = response.json()["accessToken"]

def get_product_url(api_type):
    match api_type:
        case "POST":
            url = get_url_from_api_config("add_product_url")
        case "GET"|"POST"|"PUT"|"PATCH"|"DELETE":
            url = get_url_from_api_config("update_product_url")
        case _: # The wildcard pattern acts as a default case
            print("Incorrect API Type. Please check")
    return url

@when(u'Run Product {api_type} API with body "{body_template}" and headers "{headers_template}"')
def product_api(context, api_type, body_template, headers_template):
    global product_response
    url = get_product_url(api_type)
    url = url.replace("<PRODUCT_ID>", product_id)
    # headers = update_api_headers_json(get_api_headers(headers_template), "Authorization", "Bearer " + token)
    product_response = send_api(api_type, url, get_api_body(body_template), get_api_headers(headers_template))

@then(u'Validate Product Response Status Code "{expected_response_code}" and Response Message "{expected_response_message}"')
def validate_product_api(context, expected_response_code, expected_response_message):
    compare(product_response.status_code, expected_response_code)
    compare(json.dumps(product_response.json()), expected_response_message)

def get_product_id():
    if product_response.status_code == 200:
        product_id = product_response.json()["id"]
        print("Product ID:" + product_id)
    else:
        print("API response status code is :" + product_response.status_code)




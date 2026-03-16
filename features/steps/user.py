import os
from behave import given, when, then
from behave.exception import StepNotImplementedError

from common_library.api_lib import *

token = None
user_response = None
os.environ["TEST_ENVIRONMENT"] = "STG"

@given(u'User Access Token API with body "{body_template}" and headers "{headers_template}"')
def user_access_token_api(context, body_template, headers_template):
    global token
    url = get_url_from_api_config("user_token_url")
    body = get_api_headers(body_template)
    body = update_api_body_json(body, "username", "emilys")
    body = update_api_body_json(body, "password", "emilyspass")
    response = post_api(url, body, get_api_headers(headers_template))
    compare("200", response.status_code)
    token = response.json()["accessToken"]

@when(u'Run User API with body "{body_template}" and headers "{headers_template}"')
def user_api(context, body_template, headers_template):
    global user_response
    url = get_url_from_api_config("user_url")
    headers = update_api_headers_json(get_api_headers(headers_template), "Authorization","Bearer " + token)
    user_response = get_api(url, get_api_body(body_template), headers)

@then(u'Validate Status Code "{expected_response_code}" and Response Message "{expected_response_message}"')
def validate_user_api(context, expected_response_code, expected_response_message):
    compare(user_response.status_code, expected_response_code)
    compare(json.dumps(user_response.json()), expected_response_message)

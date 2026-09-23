import os
from behave import given, when, then, use_step_matcher
from behave.exception import StepNotImplementedError

from common_library.api_lib import *

token = None
user_response = None
os.environ["TEST_ENVIRONMENT"] = "STG"
expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwidXNlcm5hbWUiOiJlbWlseXMiLCJlbWFpbCI6ImVtaWx5LmpvaG5zb25AeC5kdW1teWpzb24uY29tIiwiZmlyc3ROYW1lIjoiRW1pbHkiLCJsYXN0TmFtZSI6IkpvaG5zb24iLCJnZW5kZXIiOiJmZW1hbGUiLCJpbWFnZSI6Imh0dHBzOi8vZHVtbXlqc29uLmNvbS9pY29uL2VtaWx5cy8xMjgiLCJpYXQiOjE3NzM5NDc1MTAsImV4cCI6MTc3Mzk0OTMxMH0.G8DRxCuUGRM_krdX4w4hW4tBuopSy-GkmmGt385kwzU"

use_step_matcher("re")

@given(u'User Access Token API with body "([^"]*)" and headers "([^"]*)"')
def user_access_token_api(context, body_template, headers_template):
    global token
    url = get_url_from_api_config("user_token_url")
    body = get_api_headers(body_template)
    body = update_body_property(body, "username", "emilys")
    body = update_body_property(body, "password", "emilyspass")
    response = post_api(url, body, get_api_headers(headers_template))
    compare("200", response.status_code)
    token = response.json()["accessToken"]

@when(u'Run User API with body "([^"]*)" and headers "([^"]*)"')
def user_api(context, body_template, headers_template):
    global user_response
    url = get_url_from_api_config("user_url")
    headers = update_headers_property(get_api_headers(headers_template), "Authorization","Bearer " + token)
    user_response = get_api(url, get_api_body(body_template), headers)

@then(u'Validate Status Code "([^"]*)" and Response Message "([^"]*)"')
def validate_user_api(context, expected_response_code, expected_response_message):
    compare(user_response.status_code, expected_response_code)
    compare(json.dumps(user_response.json()), expected_response_message)


@given(u'Use Invalid Token "([^"]*)"')
def set_token(context,  set_token):
    global token
    if set_token == 'EXPIRED_TOKEN':
        token = expired_token
    else:
        token = set_token
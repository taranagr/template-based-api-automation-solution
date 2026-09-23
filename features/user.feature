# Created by Taran
Feature: User

  @User
  Scenario Outline: User Details_01: Run User API
    Given User Access Token API with body "user_token_body.json" and headers "user_token_headers.json"
    When Run User API with body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Status Code "<Response Code>" and Response Message "<Response Message>"
    Examples:
      | Body Template Name | Headers Template Name | Response Code | Response Message |
      | user_body.json     | user_headers.json     | 200           | emilys           |

  @User
  Scenario Outline: User Details_02: Negative - Run User API with Invalid Token
    Given Use Invalid Token "<Token>"
    When Run User API with body "user_body.json" and headers "user_headers.json"
    Then Validate Status Code "<Expected Status Code>" and Response Message "<Expected Error Message>"
    Examples:
      | Token         | Expected Status Code | Expected Error Message |
      | EXPIRED_TOKEN | 401                  | Token Expired!         |
      |               | 401                  | Invalid/Expired Token! |
      | Testing       | 401                  | Invalid/Expired Token! |
      | e.e.G         | 500                  | invalid token          |


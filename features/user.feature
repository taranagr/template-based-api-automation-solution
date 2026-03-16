# Created by Taran
Feature: User

  @User
  Scenario Outline: User Details_01: Run User API
    Given User Access Token API with body "user_token_body.json" and headers "user_token_headers.json"
    When Run User API with body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Status Code "<Response Code>" and Response Message "<Response Message>"
    Examples:
      | Body Template Name | Headers Template Name | Response Code | Response Message              |
      | user_body.json     | user_headers.json     | 200           | emily.johnson@x.dummyjson.com |
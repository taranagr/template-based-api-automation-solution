# Created by Taran
Feature: Get Product
  # Enter feature description here

  @Product
  Scenario Outline: Get_Product_01: Get Product API
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Run Product GET API with URL "<URL Name>", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    Examples:
      | URL Name    | Body Template Name | Headers Template Name | Expected Status Code | Expected Message   |
      | product_url | product_body.json  | product_headers.json  | 200                  | Google Pixel 6 Pro |

  @Product
  Scenario Outline: Get_Product_02: Get All Products API
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Use Invalid Product Id ""
    When Run Product GET API with URL "<URL Name>", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    Examples:
      | URL Name    | Body Template Name | Headers Template Name | Expected Status Code | Expected Message     |
      | product_url | product_body.json  | product_headers.json  | 200                  | Apple MacBook Pro 16 |

  Scenario Outline: Get_Product_03: Get Product API with Invalid Values
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Use Invalid Product Id "<Product Id>"
    And Run Product GET API with URL "product_url", body "product_body.json" and headers "product_headers.json"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Error Message>"
    Examples:
      | Product Id | Expected Status Code | Expected Error Message |
      | 123        | 404                  | not found              |
      | %$%^$%^    | 401                  | Unauthorized path      |

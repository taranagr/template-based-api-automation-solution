# Created by Taran
Feature: Add Product

  @Product
  Scenario Outline: Add_Product_01: Add Product API with Mandatory fields
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Run Product POST API with URL "<URL Name>", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    Examples:
      | URL Name        | Body Template Name | Headers Template Name | Expected Status Code | Expected Message     |
      | add_product_url | product_body.json  | product_headers.json  | 200                  | Apple MacBook Pro 16 |

  @Product
  Scenario Outline: Add_Product_02: Add Product API with All fields
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Run Product POST API with URL "<URL Name>", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    Examples:
      | URL Name        | Body Template Name | Headers Template Name | Expected Status Code | Expected Message     |
      | add_product_url | product_body.json  | product_headers.json  | 200                  | Apple MacBook Pro 16 |

  @Product
  Scenario Outline: Add_Product_03: Validate Duplicate Product Error Code and Message
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Run Product POST API with URL "<URL Name>", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Status Code>"
    Examples:
      | URL Name    | Body Template Name | Headers Template Name | Expected Status Code | Expected Status Code   |
      | product_url | product_body.json  | product_headers.json  | 400                  | Product already exists |
# Created by Taran
Feature: Get Product
  # Enter feature description here

  @Product
  Scenario Outline: Get_Product_01: Get Product API with Mandatory fields
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Run Product GET API with body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    Examples:
      | Body Template Name | Headers Template Name | Expected Status Code | Expected Message     |
      | product_body.json  | product_headers.json  | 200                  | Apple MacBook Pro 16 |

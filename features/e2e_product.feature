# Created by Taran at 3/16/2026
Feature: End to End Product
  # Enter feature description here

  @Product
  Scenario Outline: Add_Product_01: Add Product API with Mandatory fields
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Run Product POST API with URL "add_product_url", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    Then Capture Product Id
    When Run Product GET API with URL "product_url", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    When Run Product PATCH API with URL "product_url", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    When Run Product DELETE API with URL "product_url", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "has been deleted."
    Examples:
      | Body Template Name | Headers Template Name | Expected Status Code | Expected Message     |
      | product_body.json  | product_headers.json  | 200                  | Apple MacBook Pro 16 |

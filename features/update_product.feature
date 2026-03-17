# Created by Taran
Feature: Update Product
  # Enter feature description here

  @Product
  Scenario Outline: Update_Product_01: Update Product API with Mandatory fields
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Run Product PATCH API with URL "<URL Name>", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    Examples:
      | URL Name    | Body Template Name | Headers Template Name | Expected Status Code | Expected Message     |
      | product_url | product_body.json  | product_headers.json  | 200                  | Apple MacBook Pro 16 |

  @Product
  Scenario Outline: Update_Product_02: Update Product API with All fields
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Run Product PATCH API with URL "<URL Name>", body "<Body Template Name>" and headers "<Headers Template Name>"
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Message>"
    Examples:
      | URL Name    | Body Template Name    | Headers Template Name | Expected Status Code | Expected Message     |
      | product_url | product_body_All.json | product_headers.json  | 200                  | Apple MacBook Pro 16 |

  @Product
  Scenario Outline: Update_Product_03: Update Product API with Valid values
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Use Product API with URL "product_url", body "product_body.json" and headers "product_headers.json"
    And Use "<Property Path>", valid "<Property Value>" and Type "<Type>"
    And Run Product PATCH API
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Error Message>"
    Examples:
      | Property Path | Property Value       | Type    | Expected Status Code | Expected Error Message |
      | name          | Apple MacBook Pro 16 | String  | 200                  |                        |
      | data.price    | 1234.34              | Float   | 200                  |                        |
      | data.year     | 1900                 | Integer | 200                  |                        |

  @Product
  Scenario Outline: Update_Product_04: Validate Error Code and Message with Incorrect Values or Length
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Use Product API with URL "product_url", body "product_body.json" and headers "product_headers.json"
    And Use "<Property Path>", Invalid "<Property Value>" and Type "<Type>"
    And Run Product PATCH API
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Error Message>"
    Examples:
      | Property Path | Property Value | Type    | Expected Status Code | Expected Error Message                                   |
      | name          | Test$#         | String  | 400                  | 'name' should not contain special character $^#@         |
      | data.price    | -1324.34       | Float   | 400                  | 'price' must be a positive number upto two digit decimal |
      | data.year     | 45453          | Integer | 400                  | 'year' must be between 1900 and 2100                     |

  @Product
  Scenario Outline: Update_Product_05: Validate Error Code and Message with Blank Values in Mandatory fields
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Use Product API with URL "product_url", body "product_body.json" and headers "product_headers.json"
    And Use "<Property Path>", Invalid "<Property Value>" and Type "<Type>"
    And Run Product PATCH API
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Error Message>"
    Examples:
      | Property Path | Property Value | Type   | Expected Status Code | Expected Error Message           |
      | name          |                | String | 400                  | 'name' can not be empty or null  |
      | data.price    |                | String | 400                  | 'price' can not be empty or null |
      | data.year     |                | String | 400                  | 'year' can not be empty or null  |

  @Product
  Scenario Outline: Update_Product_06: Update Product API with Missing Mandatory fields
#    Given Product Access Token API with body "product_token_body.json" and headers "product_token_headers.json"
    When Use Product API with URL "product_url", body "product_body.json" and headers "product_headers.json"
    And Remove Property "<Property Path>"
    And Run Product PATCH API
    Then Validate Product Response Status Code "<Expected Status Code>" and Response Message "<Expected Error Message>"
    Examples:
      | Property Path | Expected Status Code | Expected Error Message |
      | name          | 400                  | 'name' is missing      |
      | data.price    | 400                  | 'price' is missing     |
      | data.year     | 400                  | 'year' is missing      |


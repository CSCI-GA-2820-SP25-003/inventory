Feature: Inventory Admin UI

  Scenario: Open the Inventory Admin UI and verify the page title
    Given I open the Inventory Admin UI
    Then I should see the title "Inventory Demo RESTful Service"

  Scenario: Create and retrieve an inventory item using dynamic ID
    Given I open the Inventory Admin UI
    When I enter "Laptop" as the name
    And I enter "123" as the product ID
    And I enter "10" as the quantity
    And I select "New" as the condition
    And I enter "5" as the restock level
    And I press the "Create" button
    And I press the "List All" button
    And I grab the first inventory ID from the results table
    And I enter the grabbed inventory ID
    And I press the "Retrieve" button
    Then the name field should contain "Laptop"

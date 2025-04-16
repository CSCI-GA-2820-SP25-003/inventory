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

  Scenario: Update the quantity of an inventory item via the UI
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
    And I change "quantity" to "30"
    And I press the "Update" button
    Then I should see the message "Inventory item updated successfully"
    And I should see "30" in the "quantity" field

  Scenario: Perform an action on an inventory item
    Given I open the Inventory Admin UI
    When I enter "Monitor" as the name
    And I enter "456" as the product ID
    And I enter "2" as the quantity
    And I select "New" as the condition
    And I enter "5" as the restock level
    And I press the "Create" button
    And I press the "List All" button
    And I grab the first inventory ID from the results table
    And I enter the grabbed inventory ID
    And I select "Mark as Restocked" in the "Action" dropdown
    And I press the "Perform Action" button
    Then I should see the message "Item marked as restocked successfully!"

Scenario: Delete Inventory
    Given I open the Inventory Admin UI
    When I enter "Laptop" as the name
    Then I should see "0" as the quantity
    And I should see "NEW" as the condition
    And I should see "OUT_OF_STOCK" as the restock level
    When I copy the "ID" field
    And I press the "Delete" button
    Then I should see the message "Inventory has been Deleted!"
    When I press the "Search" button
    Then I should not see "Laptop" in the results

Scenario: Query by Condition
    Given I open the Inventory Admin UI
    When I select "New" as the condition
    And I press the "Search" button
    Then the I should see a list of items that are "New" condition
$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#inventory_id").val(res.id);
        $("#inventory_name").val(res.name);
        $("#inventory_product_id").val(res.product_id);
        $("#inventory_quantity").val(res.quantity);
        $("#inventory_condition").val(res.condition);
        $("#inventory_restock_level").val(res.restock_level);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#inventory_name").val("");
        $("#inventory_product_id").val("");
        $("#inventory_quantity").val("");
        $("#inventory_condition").val("New");
        $("#inventory_restock_level").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Inventory Item
    // ****************************************

    $("#create-btn").click(function () {
        let name = $("#inventory_name").val();
        let product_id = parseInt($("#inventory_product_id").val());
        let quantity = parseInt($("#inventory_quantity").val());
        let condition = $("#inventory_condition").val();
        let restock_level = parseInt($("#inventory_restock_level").val());

        let data = {
            "name": name,
            "product_id": product_id,
            "quantity": quantity,
            "condition": condition,
            "restock_level": restock_level
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/api/inventory",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success! Inventory item created");
            list_inventory(); // Refresh the list
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message || "Creation failed");
        });
    });


    // ****************************************
    // TODO: Update an Inventory Item
    // ****************************************

    $("#update-btn").click(function () {

        let inventory_id = $("#inventory_id").val();
        let name = $("#inventory_name").val();
        let product_id = parseInt($("#inventory_product_id").val());
        let quantity = parseInt($("#inventory_quantity").val());
        let condition = $("#inventory_condition").val();
        let restock_level = parseInt($("#inventory_restock_level").val());
    
        let data = {
            "name": name,
            "product_id": product_id,
            "quantity": quantity,
            "condition": condition,
            "restock_level": restock_level
        };
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "PUT",
            url: `/api/inventory/${inventory_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        });
    
        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success: Inventory item updated");
        });
    
        ajax.fail(function(res){
            flash_message("Error: " + res.responseJSON.message);
        });
    
    });


    // ****************************************
    // Retrieve an Inventory Item
    // ****************************************

    $("#retrieve-btn").click(function () {
        let inventory_id = $("#inventory_id").val();
        
        if (!inventory_id) {
            flash_message("Please enter an ID to retrieve");
            return;
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/inventory/${inventory_id}`,
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            update_form_data(res);
            flash_message("Success! Item retrieved");
        });

        ajax.fail(function(res){
            clear_form_data();
            flash_message(res.responseJSON.message || "Item not found");
        });
    });

    // ****************************************
    // TODO: Delete an Inventory Item
    // ****************************************
    $("#delete-btn").click(function () {

        let inventory_id = $("#inventory_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `api/inventory/${inventory_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Inventory has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });
 


    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#inventory_id").val("");
        $("#flash_message").empty();
        clear_form_data();
    });

    // ****************************************
    // TODO: Query/Search for Inventory Items by Condition
    // ****************************************

    $("#search-btn").click(function () {
        let condition = $("#inventory_condition").val();
        
        if (!condition) {
            flash_message("Please select a condition to search");
            return;
        }
    
        $("#flash_message").empty();
    
        let ajax = $.ajax({
            type: "GET",
            url: `/api/inventory?condition=${condition}`,
            contentType: "application/json",
            data: ''
        });
    
        ajax.done(function(res) {
            displayInventoryItems(res);
            flash_message("Success! Items retrieved");
        });
    
        ajax.fail(function(res) {
            $("#search_results_table").empty(); // Clear previous results
            flash_message(res.responseJSON.message || "No items found for the selected condition");
        });
    });


    // ****************************************
    // TODO: Perform Restock Action on Inventory Item
    // ****************************************

// Perform Restock Action on Inventory Item
$("#perform-action-btn").click(function () {
    let inventory_id = $("#inventory_id").val();
    let selected_action = $("#inventory_action").val();
  
    $("#flash_message").empty();
  
    if (!inventory_id) {
      flash_message("Please enter an Inventory ID first.");
      return;
    }
  
    if (selected_action === "restock") {
      let ajax = $.ajax({
        type: "PUT",
        url: `/inventory/${inventory_id}/restock`,
        contentType: "application/json",
        data: JSON.stringify({})  // no body content for restock
      });
  
      ajax.done(function (res) {
        update_form_data(res);
        flash_message("Item marked as restocked successfully!");
      });
  
      ajax.fail(function (res) {
        flash_message(res.responseJSON.message);
      });
    } else {
      flash_message("Invalid action selected.");
    }
  });
    
    

    // ****************************************
    // List All Inventory Items
    // ****************************************

    $("#list-btn").click(function() {
        list_inventory();
    });

    function list_inventory() {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: "/api/inventory",
            contentType: "application/json",
            data: ''
        });

        ajax.done(function(res){
            $("#search_results_table").empty();
            
            let firstItem = "";
            for(let i = 0; i < res.length; i++) {
                let item = res[i];
                let row = `<tr id="row_${i}">
                    <td>${item.id}</td>
                    <td>${item.name}</td>
                    <td>${item.product_id}</td>
                    <td>${item.quantity}</td>
                    <td>${item.condition}</td>
                    <td>${item.restock_level}</td>
                </tr>`;
                $("#search_results_table").append(row);
                
                if (i == 0) {
                    firstItem = item;
                }
            }

            // copy the first result to the form if listing all
            if (firstItem != "") {
                update_form_data(firstItem);
            }

            flash_message(`Success! ${res.length} inventory items returned`);
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message || "Failed to list inventory items");
        });
    }

    // Load inventory on page load
    list_inventory();
});
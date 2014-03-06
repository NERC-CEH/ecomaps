/**
 * Created by Phil Jenkins on 3/4/14.
 */


var EcomapsSorter = (function() {

    var highlightSortedColumn = function(tableId, direction) {

    // Get table by ID
    var table = $("#" + tableId);

    var selectedColumn = table.data("sorting_column");

    // Loop over th elements
    $(table).find("th").each(function(){
        var columnName = $(this).data("column");

        if (selectedColumn == columnName){
            $(this).append(" ")

            // Add icon corresponding to direction of sorting
            if (typeof direction != "undefined" && direction == "asc"){
                $(this).append("<i class='icon-chevron-up'></i>");
            }
            else{
                $(this).append("<i class='icon-chevron-down'></i>");
            }
        };
    })

    };

    var getOrderDirection = function(tableId, previousSortingColumn, selectedColumnName){

        // Get table by ID
        var table = $("#" + tableId);

        var orderDirection = table.data("order_direction");


        // If the column name matches the one that was previously sorted on - reverse the direction of sorting
        if (typeof previousSortingColumn != "undefined" && previousSortingColumn == selectedColumnName){
            if (orderDirection == "asc"){
                var direction = "desc";
            }
            else{
                var direction = "asc";
            }
        }
        else{
            var direction = "asc";
        }

        return direction;

    };

    var constructAddressString = function(tableHeader){
        // Function builds the address to redirect to depending on the column header that has been clicked.

        var table = $(tableHeader).closest("table");

        var tableId = $(table).get(0).id;

        var selectedColumnName = $(tableHeader).data("column");

        var previousSortingColumn = table.data("sorting_column");

        var direction = getOrderDirection(tableId ,selectedColumnName,previousSortingColumn);

        if (tableId == "public_analyses_table"){
            var isPublic = "true";
        }
        else{
            var isPublic = "false";
        }

        var address = "/analysis/sort/?column=" + selectedColumnName + "&order=" + direction + "&is_public=" + isPublic;

        return{
            tableId : tableId,
            direction: direction,
            address : address
        }
    }

    var initSortables = function() {

        $("div#private-container").on("click", "th", function(){

            var result = constructAddressString($(this));

            $("div#private-container").load(result.address, function() {
                highlightSortedColumn(result.tableId,result.direction);
            });
        });

        $("div#public-container").on("click", "th", function(){

            var result = constructAddressString($(this));

            $("div#public-container").load(result.address, function() {
                highlightSortedColumn(result.tableId,result.direction);
            });

        });
    };

    return {
        /*
         * init
         *
         * Initialisation function, sets up the module
         *
         */
        init: function(){
            initSortables();

            // Default view
            $("div#private-container").html("<div class='modal-body'>Loading data <img src='/layout/images/loading7.gif' /></div>");
            $("div#private-container").load("sort/?column=analyses.name&order=asc&is_public=false");
            $("div#public-container").load("sort/?column=analyses.name&order=asc&is_public=true");
        }
    }
})();
$(function() {
        EcomapsSorter.init();
    }
);
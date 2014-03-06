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

    var initSortables = function() {

        var table = null;

        $("div#private-container").on("click", "th", function(){

            table = $(this).closest("table");

            var selectedColumnName = $(this).data("column");

            var previousSortingColumn = table.data("sorting_column");

            tableId = $(table).get(0).id;

            var direction = getOrderDirection(tableId ,selectedColumnName,previousSortingColumn);

            var isPublic = "false";

            // Go off to server
            var address = "/analysis/sort/?column=" + selectedColumnName + "&order=" + direction + "&is_public=" + isPublic;
            $("div#private-container").load(address, function() {
                highlightSortedColumn(tableId,direction);
            });
        });

        $("div#public-container").on("click", "th", function(){

            table = $(this).closest("table");

            var selectedColumnName = $(this).data("column");

            var previousSortingColumn = table.data("sorting_column");

            tableId = $(table).get(0).id;

            var direction = getOrderDirection(tableId,selectedColumnName,previousSortingColumn);

            var isPublic = "true";

            // Go off to server
            var address = "/analysis/sort/?column=" + selectedColumnName + "&order=" + direction + "&is_public=" + isPublic;
            $("div#public-container").load(address, function() {
                highlightSortedColumn(tableId,direction);
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

            // Potentially load a default view?
            //$("div#private-container").load("/dataset/preview/2");
        }
    }
})();
$(function() {
        EcomapsSorter.init();
    }
);
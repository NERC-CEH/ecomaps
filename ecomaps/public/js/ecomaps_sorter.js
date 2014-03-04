/**
 * Created by Phil Jenkins on 3/4/14.
 */


var EcomapsSorter = (function() {

    var initSortables = function() {

        $("div#private-container").on("click", "th", function(){

            table = $(this).closest("table");

            var columnName = $(this).data("column");

            var sortingColumn = table.data("sorting_column");

            var orderDirection = table.data("order_direction");

            // If the column name matches the one that was previously sorted on - reverse the direction of sorting
            if (typeof sortingColumn != "undefined" && sortingColumn == columnName)
            {
                if (orderDirection == "asc")
                {
                    var direction = "desc";
                }
                else
                {
                    var direction = "asc";
                }
            }
            else
            {
                var direction = "asc";
            }

            // Go off to server
            address = "/analysis/sort/?column=" + columnName + "&order=" + direction;
            $("div#private-container").load(address);
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
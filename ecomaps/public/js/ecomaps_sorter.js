/**
 * Created by Phil Jenkins on 3/4/14.
 */


var EcomapsSorter = (function() {

    var initSortables = function() {

        $("div#private-container").on("click", "th", function(){

            var columnName = $(this).data("column");

            console.log(columnName);

            var direction = "asc"

            // Go off to server
            address = "/analysis/sort/?column=" + columnName + "&order=" + direction;
            $("div#private-container").load(address)
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
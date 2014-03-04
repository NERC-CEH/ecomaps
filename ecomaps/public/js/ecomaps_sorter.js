/**
 * Created by Phil Jenkins on 3/4/14.
 */


var EcomapsSorter = (function() {

    var initSortables = function() {

        $("div#private-container").on("click", "th", function(){

            var columnName = $(this).data("column");

            console.log(columnName);

            // direction
            var direction = "asc";

            // Go off to server
            // e.g. /analysis/sort/?column=blah&direction=blah2
            $("div#private-container").load("/dataset/preview/2");
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
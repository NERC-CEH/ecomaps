/**
 * Created by Phil Jenkins (Tessella) on 11 Mar 2014.
 *
 * Functions for the "Create Analysis" page
 */

var EcomapsCreateAnalysis = (function() {

    var selectedColumns = new Object();

    var initHandlers = function(){
        $("select#coverage_dataset_ids").change(refreshTimeSelectors);
    };

    var refreshTimeSelectors = function(){

        var selections = $(this).val();

        if(selections) {
            for(var i=0; i < selections.length; i++){

                // Do we already have an entry
                var columnValue = selections[i];

                if(!selectedColumns[columnValue]){
                    selectedColumns[columnValue] = true;

                    var selectionParts = columnValue.split("_");
                    var dsId = selectionParts[0];
                    var col = selectionParts[1];

                    $.get("/dataset/timeselection/" + dsId + "?col=" + col, function(data){

                        $("div#time-point-container").append(data);
                    });
                }
            }
        }

        for(var column in selectedColumns) {
            if(selections.indexOf(column) < 0) {
                delete selectedColumns[column];
            }
        }

        $("div.time-selector").each(function(){
            if(!selectedColumns.hasOwnProperty($(this).data("columnid"))){
                $(this).remove();
            }
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
            initHandlers();
        }
    }
})();
$(function() {
        EcomapsCreateAnalysis.init();
    }
);

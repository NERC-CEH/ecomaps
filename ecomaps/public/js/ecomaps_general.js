/**
 * Created by Phil Jenkins (Tessella) on 2/27/14.
 */

var EcomapsGeneral = (function() {

    var testMapServer = function() {

        var statusMessage = $("#status-message");
        var dots = "";
        var spaces = cur_spaces = "&nbsp;&nbsp;&nbsp;";
        statusMessage.html("Testing" + dots + spaces).attr("class", "label");

        var loaderId = window.setInterval(function() {

            if(dots.length === 3) {
                dots = "";
                cur_spaces = spaces;
            }
            else {

                dots += ".";
                cur_spaces = spaces.substring(0, spaces.length-(6*dots.length));
            }

            statusMessage.html("Testing" + dots + cur_spaces);

        }, 500);

        $.get('/map/test/', function(serverOK){

            var cls, message = "";

            if(serverOK) {
                message = "OK";
                cls= 'success';
                $("#server-offline").hide();
            }
            else {
                message = "Offline";
                cls = 'important';
                $("#server-offline").show("fast");
            }

            window.clearInterval(loaderId);
            statusMessage.html(message).attr('class', 'label label-' + cls);
        });
    };

    return {

        init: function(){
            testMapServer();

            window.setInterval(testMapServer, 20000);
        }
    }
})();
$(function() {
        EcomapsGeneral.init();
    }
);
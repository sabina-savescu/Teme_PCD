
var websocket = new WebSocket("ws://127.0.0.1:8081/");;
$(document).ready(function () {
    var enter = document.querySelector('.enter'),
        users = document.querySelector('.users'),
        response = document.querySelector('.response'),
        url = document.getElementById("search").value
        ;

    enter.onclick = function (event) {
        websocket.send(JSON.stringify({ action: "search", url: url }));
    }

    websocket.onopen = function () {
        websocket.send(JSON.stringify({ action: 'options' }));
    }
    websocket.onmessage = function (event) {
        data = JSON.parse(event.data);
        switch (data.type) {
            case 'state':
                generateDynamicTable();
                break;
            case 'users':
                users.textContent = (
                    data.count.toString() + " user" +
                    (data.count == 1 ? "" : "s")) + " online";
                break;
            case 'response':
                response.textContent = data.value;
                break;
            default:
                console.error(
                    "unsupported event", data);
        }
    };
});

function generateDynamicTable() {
    var Table = document.getElementById("rows");
    Table.innerHTML = "";

    if (data.value.length > 0) {
        for (var i = 0; i < data.value.length; i++) {
            var newRow = document.createElement("tr");
            for (var j = 0; j < 3; j++) {
                var td = document.createElement("td");

                td.innerHTML = data.value[i][j]
                newRow.append(td);
            }

            document.getElementById("rows").appendChild(newRow);
        }

        //get row
        $("#options tr").click(function () {
            $(this).addClass('selected').siblings().removeClass('selected');
            var ip = $(this).find('td:first').html();
            var port = $(this).find('td').eq(1).html();
            var opt = $(this).find('td').eq(2).html();
            if (opt == "Yes") {
                alert("Please choose another address.")
            }
            websocket.send(JSON.stringify({ action: ip + ":" + port }));
        });
    }
}

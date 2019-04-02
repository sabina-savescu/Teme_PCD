
$(document).ready(function () {
    var select = document.querySelector('.select'),
        users = document.querySelector('.users'),
        websocket = new WebSocket("ws://127.0.0.1:8081/");

    select.onclick = function (event){
        websocket.send(JSON.stringify({ action: 'select' }));
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

    }
}

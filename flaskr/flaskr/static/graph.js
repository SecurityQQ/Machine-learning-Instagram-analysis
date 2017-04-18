function buildGraph(inpurData) {
    var graph = [];
    for (var key in inpurData) {
        graph.push({ "x" : key, "y": inpurData[key] });
    }
    console.log(graph);
    var data = {
        "xScale": "ordinal",
        "yScale": "linear",
        "main": [
            {
                "className": ".pizza",
                "data": graph,
            }
        ]
    };
    var myChart = new xChart('bar', data, '#graph');
}

$(document).ready(function () {
    $('.loader').hide();
    $('.graph').hide();
    //buildGraph();
    $('#calculate').click(function (event) {
        $('#graph').hide();
        $('.graph').show();
        $('.loader').show();
        var requestStr = '{"username":"' + $('#inputUsername').val() + '","password":"' + $('#inputPassword').val() + '"}';
        console.log(requestStr);
        $.getJSON('/hey', {messages: requestStr }, function (data) {
            $('#graph').show();
            $('.loader').hide();
            buildGraph(data);
        });
    });
});
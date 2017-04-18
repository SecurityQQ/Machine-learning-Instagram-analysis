function showHideFooter(delta) {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - delta) {
        $('.footer').css('position', 'fixed');
        $('.footer').css('bottom', 0);
        $('.footer').show();
    }
    else {
        $('.footer').hide();
    }
};

var tooltipFlag = false;

function buildGraph(inpurData) {
    var graph = [];
    for (var key in inpurData) {
        graph.push({ "x": key, "y": inpurData[key] });
    }
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

    var opts = {
        "mouseover": function (d, i) {
            $('.graph-tooltip').text(d.x + ': ' + d.y);
            tooltipFlag = true;
        },
        "mouseout": function (x) {
            console.log('out');
            tooltipFlag = false;
        },
        timing: 1250,
        yMin: 0,
        axisPaddingLeft: 0,
        axisPaddingRight: 0,
        axisPaddingBottom: 0,
        axisPaddingTop: 30,
    };

    var myChart = new xChart('bar', data, '#graph', opts);
}

$(document).ready(function () {
    //buildGraph();
    $('.graph-tooltip').hide();

    $(document).on('mousemove', function (e) {
        $('.graph-tooltip').css({
            left: e.pageX - $('.graph-tooltip').width(),
            top: e.pageY - 2 * $('.graph-tooltip').height()
        });
        if (tooltipFlag) {
            $('.graph-tooltip').show();
        }
        else {
            $('.graph-tooltip').hide();
        }
    });

    $("#inputUsername, #inputPassword").keyup(function (event) {
        console.log('enter');
        if (event.keyCode == 13) {
            $('#calculate').click();
        }
    });

    $('#calculate').click(function (event) {
        showHideFooter(0);
        $('#graph').hide();
        $('.graph').show();
        $('.loader').show();
        var requestStr = '{"username":"' + $('#inputUsername').val() + '","password":"' + $('#inputPassword').val() + '"}';
        $.getJSON('/hey', { messages: requestStr }, function (data) {
            $('#graph').show();
            $('.loader').hide();
            buildGraph(data);
        });
    });
});
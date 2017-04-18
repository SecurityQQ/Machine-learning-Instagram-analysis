
function PullBackground(i, j) {
    //$.getJSON("http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US", function (json) {
    //    console.log("JSON Data: " + json.url);
    //});


    //$('#back_'+i+'_'+j).css("background-image", "url('http://bing.com" + background + "')");
    //$('#back_'+i+'_'+j).css("backgroundSize", "100%");
}

function createBackNet() {
    for (var i = 0; i < window.innerWidth / 200; i++) {
        for (var j = 0; j < window.innerHeight / 200; j++) {
            $('body').append('<div id=back_' + i + '_' + j + '></div>');
            $('#back_' + i + '_' + j).width('200px');
            $('#back_' + i + '_' + j).height('200px');
            $('#back_' + i + '_' + j).css('position', 'absolute');
            $('#back_' + i + '_' + j).css('left', (i * 200) + 'px');
            $('#back_' + i + '_' + j).css('top', (j * 200) + 'px');
            $('#back_' + i + '_' + j).css('background-color', "#" + ((1 << 24) * Math.random() | 0).toString(16));
            $('#back_' + i + '_' + j).css('opacity', 0.1);
            $('#back_' + i + '_' + j).css('z-index', -100);
            $('#back_' + i + '_' + j).css('position', 'fixed');
            PullBackground(i, j);
        }
    }
};

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

window.onscroll = function () {
    showHideFooter(0);
};

$(window).resize(function () {
    //$('.footer').hide();
    createBackNet();
    showHideFooter(0);
});

$(document).ready(function () {
    console.log('ready');
    $('.loader').hide();
    $('.graph').hide();
    createBackNet();
    showHideFooter(1000);
});

$(function ($) {
    var slider = $("#slider-contacts").slideReveal({
        width: 400,
        trigger: $("#Contacts"),
        autoEscape: true,
        push: false,
        overlay: true,
        position: "right",
    });
    var slider = $("#slider-about").slideReveal({
        width: 400,
        trigger: $("#About"),
        autoEscape: true,
        push: false,
        overlay: true,
        position: "right",
    });
});
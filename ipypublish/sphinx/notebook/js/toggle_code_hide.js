$(function() {

    $(".input_area").hide()
    $(".toggle-nbinput").click(function () {
        $(this).toggleClass("open");
        $(this).prev(".input_area").toggle("400");
    })

});

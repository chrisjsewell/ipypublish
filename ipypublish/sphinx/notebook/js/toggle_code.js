
$(function () {

    $(".input_area").show();
    $(".toggle-nbinput").addClass("open");
    $(".nbinput-toggle-all").addClass("open");

    $(".toggle-nbinput").click(function () {
        $(this).toggleClass("open");
        $(this).prev(".input_area").toggle("400");
    });

    $(".nbinput-toggle-all").click(function () {
        $(this).toggleClass("open");
        if ($(this).hasClass("open")) {
            $(".toggle-nbinput").addClass("open");
            $(".input_area").show("400");
        } else {
            $(".toggle-nbinput").removeClass("open");
            $(".input_area").hide("400");
        }
    });

});

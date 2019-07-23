
$(function () {

    $(".output_area").show();
    $(".toggle-nboutput").addClass("open");
    $(".nboutput-toggle-all").addClass("open");

    $(".toggle-nboutput").click(function () {
        $(this).toggleClass("open");
        $(this).prev(".output_area").toggle("400");
    });

    $(".nboutput-toggle-all").click(function () {
        $(this).toggleClass("open");
        if ($(this).hasClass("open")) {
            $(".toggle-nboutput").addClass("open");
            $(".output_area").show("400");
        } else {
            $(".toggle-nboutput").removeClass("open");
            $(".output_area").hide("400");
        }
    });

});

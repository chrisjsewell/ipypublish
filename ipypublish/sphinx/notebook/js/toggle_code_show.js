
$(function () {

    $(".input_area").show()
    $(".toggle-nbinput").click(function () {
        $(this).toggleClass("open");
        $(this).prev(".input_area").toggle("400");
    })

});

$(document).ready(function () {
    $("#location").change(function () {
        var val = $(this).val();
        $("#facility").children('option').hide();
        $('#facility').val('');
        $("#facility").children("option[location^=" + val + "]").show()
    });
});
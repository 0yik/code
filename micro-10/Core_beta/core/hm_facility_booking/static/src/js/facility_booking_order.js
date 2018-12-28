$(document).ready(function () {
    $("#location").change(function () {
        var val = $(this).val();
        $("#facility").children('option').hide();
        $('#facility').val('');
        $("#facility").children("option[location^=" + val + "]").show()
    });
    // $( "#booking_form" ).submit(function( event ) {
    //     var booking_start_date = document.forms["booking_form"]["booking_start_date"].value;
    //     var booking_end_date = document.forms["booking_form"]["booking_end_date"].value;
    //     var location = document.forms["booking_form"]["location"].value;
    //     var facility = document.forms["booking_form"]["facility"].value;
    //   $.ajax({
		// 	url: "/facility/validator",
		// 	type: 'POST',
		// 	dataType: 'json',
		// 	data: {
		// 	    'booking_start_date' : booking_start_date,
    //             'booking_end_date' : booking_end_date,
    //             'location' : location,
    //             'facility' : facility,
    //         },
		// 	success: function (result) {
		// 		alert(1);
		// 	},
    //         error: function (e) {
    //             alert(e);
    //         }
		// });
    //   event.preventDefault();
    // });

    // function facility_booking_validate() {
    //     var booking_start_date = document.forms["booking_form"]["booking_start_date"].value;
    //     var booking_end_date = document.forms["booking_form"]["booking_end_date"].value;
    //     openerp.jsonRpc('/facility/validator', 'call', {'booking_start_date': booking_start_date , 'booking_end_date':booking_end_date}).then(function(result) {
    //
    //     })
    // }
});

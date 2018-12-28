$(document).ready(function () {

$("#fileupload").change(function()
	{
		var file_name = $("#fileupload").val().split('\\').pop().split('/').pop();
		$("#file_name").val(file_name); 
	});

});
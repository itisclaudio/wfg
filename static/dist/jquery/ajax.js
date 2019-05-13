$(function(){
	$('#search').keyup(function(){
		//e.preventDefault()
		$.ajax({
			type:"POST",
			url:"/search_cuisine/",
			data:{
				'search_text': $('#search').val(),
				'csrfmiddlewaretoken':$("input[name=csrfmiddlewaretoken]").val()
			},
			success: searchSuccess,
			dataType:'html'
		});
	});
});

function searchSuccess(data)
{
	$('#search-results').html(data);
}
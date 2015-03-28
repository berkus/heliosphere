$(document).ready(function() {
  $('#date').datepicker({
      todayBtn: "linked",
      orientation: "top auto",
      todayHighlight: true
  });
  $('#etype-dropdown').on('click', '.option li', function() {
  	var text = $(this).children().text();
    $('#etype-btn').html(text + '&nbsp;<span class="caret"></span>')
  });
  $('#event-form-submit').on('click', function() {
    etype = $('#etype-btn').text()
    date = $('#date input').val()
    time = $('#time').val()
    comment = $('#comments').val()
    $.ajax({
      type: "POST",
      url: '/events',
      data: {
        'etype': etype,
        'date': date,
        'time': time,
        'comment': comment
      },
      success: function() {
        $('#myModal').modal('hide')
      }
    });
  })
});

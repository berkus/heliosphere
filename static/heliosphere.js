$(document).ready(function() {
  $('#date').datepicker({
      todayBtn: "linked",
      orientation: "top auto",
      todayHighlight: true,
      weekStart: 1
  });
  $('#etype-dropdown').on('click', '.option li', function() {
  	var text = $(this).children().text();
    $('#etype-btn').html(text + '&nbsp;<span class="caret"></span>')
  });
  $('#event-form-submit').on('click', function() {
    etype = $('#etype-btn').text()
    date = $('#date input').val()
    time = $('#time').val()
    comments = $('#comments').val()
    $.ajax({
      type: "POST",
      url: '/events',
      data: {
        'etype': etype,
        'date': date,
        'time': time,
        'comments': comments
      },
      success: function(data) {
        $('#myModal').modal('hide')
        $('#events_container').replaceWith(data)
        initLJ();
      }
    });
  })
  initLJ();
});
function initLJ() {
    $('.join-event').on('click', function (e) {
      id = $(this).attr('id')
      $.ajax({
        type: "POST",
        url: '/events/' + id + '/_join',
        success: function(data) {
          $('#events_container').replaceWith(data)
          initLJ()
        },
        error: function(data) {
          console.log(data.responseText)
        }
      });
    });
    $('.leave-event').on('click', function (e) {
      id = $(this).attr('id')
      $.ajax({
        type: "POST",
        url: '/events/' + id + '/_leave',
        success: function(data) {
          $('#events_container').replaceWith(data)
          initLJ()
        },
        error: function(data) {
          console.log(data.responseText)
        }
      });
    });
    $('.delete-event').on('click', function (e) {
      id = $(this).attr('id')
      $.ajax({
        type: "DELETE",
        url: '/events/' + id,
        success: function(data) {
          $('#events_container').replaceWith(data)
          initLJ();
        },
        error: function(data) {
          console.log(data.responseText)
        }
      });
    });
}

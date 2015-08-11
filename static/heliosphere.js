$(document).ready(function() {
    $('#date').datepicker({
        todayBtn: "linked",
        orientation: "top auto",
        todayHighlight: true,
        weekStart: 1
    }).on('changeDate', function(e){
        $('#date').val(e.format('mm/dd/yyyy'))
    });
    $('#etype-dropdown').on('click', '.option li', function() {
        var text = $(this).children().text();
        var id = $(this).children().attr("selection-id")
        var button = $('#etype-btn')
        button.html(text + '&nbsp;<span class="caret"></span>')
        button.attr("selection-id", id)
    });
    $('#event-form-submit').on('click', function() {
        event_type = $('#etype-btn').attr("selection-id")
        date = $('#date').val()
        time = $('#time').val()
        comment = $('#comment').val()
        $.ajax({
            type: "POST",
            url: '/',
            data: {
                'event_type': event_type,
                'date': date,
                'time': time,
                'comment': comment
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
            type: "PUT",
            url: '/events/' + id + '/participants',
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
            type: "DELETE",
            url: '/events/' + id + '/participants',
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

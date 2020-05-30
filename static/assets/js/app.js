// Configure Pusher instance
var pusher = new Pusher('669915df0dea2e8eabd3', {
    cluster: 'ap2',
    encrypted: true
});

var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

$(document).ready(function () {
    var dataTable = $("#dataTable").DataTable()
    // var userSessions = $("#userSessions").DataTable()
    var pages = $("#pages").DataTable()

    axios.get('/get-all-sessions')
        .then(response => {
            response.data.forEach((data) => {
                insertDatatable(data)
            })
            var d = new Date();
            var updatedAt = `${d.getFullYear()}/${months[d.getMonth()]}/${d.getDay()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`
            document.getElementById('session-update-time').innerText = updatedAt
        })

    fillCards()

    var sessionChannel = pusher.subscribe('session');
    sessionChannel.bind('new', function (data) {
        insertDatatable(data)
        // fillCards()
    });

    var d = new Date();
    var updatedAt = `${d.getFullYear()}/${months[d.getMonth()]}/${d.getDay()} ${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}`
    document.getElementById('session-update-time').innerText = updatedAt
});

function insertDatatable(data) {
    var dataTable = $("#dataTable").DataTable()
    dataTable.row.add([
        data.time,
        data.ip,
        data.continent,
        data.country,
        data.city,
        data.os,
        data.browser,
        `<a href=${"/dashboard/" + data.session}>View pages visited</a>`
    ]);
    dataTable.order([0, 'desc']).draw();
}

function fillCards() {
    axios.get('/api/v1/get-all-visits-count')
        .then(response => {
            document.getElementById('total-sessions').innerText = response.data[0].total_sessions
        })

    axios.get('/api/v1/get-unique-visits-count')
        .then(response => {
            document.getElementById('unique-sessions').innerText = response.data[0].unique_sessions
        })

    axios.get('/api/v1/get-home-visits-count')
        .then(response => {
            document.getElementById('home-page-visits').innerText = response.data[0].home_page_visits
        })

    axios.get('/api/v1/get-predictions-made-count')
        .then(response => {
            document.getElementById('total-predictions').innerText = response.data[0].predictions_page_visits
        })
}
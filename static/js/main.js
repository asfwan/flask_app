let map;
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 2.9348653, lng: 101.6625544},
        zoom: 13
    });
    fetchRoutes();
}

function fetchRoutes() {
    $.getJSON('/routes', function(data) {
        data.forEach(vehicle => {
            let route = new google.maps.Polyline({
                path: vehicle.route.map(location => {
                    // Example conversion, adjust as needed
                    let [lat, lng] = location.split(',').map(Number);
                    return {lat, lng};
                }),
                geodesic: true,
                strokeColor: '#FF0000',
                strokeOpacity: 1.0,
                strokeWeight: 2
            });
            route.setMap(map);
        });
    });
}

window.onload = initMap;

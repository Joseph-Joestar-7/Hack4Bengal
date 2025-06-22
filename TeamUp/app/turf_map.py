import requests
import folium
from folium.plugins import MarkerCluster

def get_turfs(lat: float, lon: float, radius: int = 5000):
    """
    Query Overpass for leisure=pitch within `radius` meters of (lat, lon).
    Returns list of {"name","lat","lon"}.
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      node["leisure"="pitch"](around:{radius},{lat},{lon});
      way["leisure"="pitch"](around:{radius},{lat},{lon});
      relation["leisure"="pitch"](around:{radius},{lat},{lon});
    );
    out center;
    """
    resp = requests.get(overpass_url, params={"data": query}, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    turfs = []
    for el in data.get("elements", []):
        name = el.get("tags", {}).get("name", "Unnamed Turf")
        if el["type"] == "node":
            tlat, tlon = el["lat"], el["lon"]
        else:
            c = el.get("center", {})
            tlat, tlon = c.get("lat"), c.get("lon")
        if tlat and tlon:
            turfs.append({"name": name, "lat": tlat, "lon": tlon})
    return turfs

def get_route(start: tuple, end: tuple):
    """
    Calls OSRM public server. start/end are (lat, lon).
    Returns list of [lat, lon] pairs for the route polyline.
    """
    url = (
      "https://router.project-osrm.org/route/v1/driving/"
      f"{start[1]},{start[0]};{end[1]},{end[0]}"
      "?overview=full&geometries=geojson"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    coords = data["routes"][0]["geometry"]["coordinates"]
    # OSRM gives [lon,lat], so flip:
    return [[lat, lon] for lon, lat in coords]

def render_turf_map(user_lat: float, user_lon: float,
                    radius: int = 5000,
                    route_to: dict = None) -> str:
    """
    Build a Folium map centered at (user_lat, user_lon),
    plot nearby turfs with blue markers (each popup has a
    "Show route" link). If route_to={"lat":…, "lon":…},
    fetch OSRM route and draw it as a red polyline.
    Returns HTML.
    """
    turfs = get_turfs(user_lat, user_lon, radius)

    m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
    cluster = MarkerCluster().add_to(m)

    # Turf markers
    for turf in turfs:
        link_url = (
            f"/dashboard?lat={user_lat}"
            f"&lon={user_lon}"
            f"&to_lat={turf['lat']}"
            f"&to_lon={turf['lon']}"
        )
        # Use onclick to force top‐level navigation
        popup_html = (
            f"<b>{turf['name']}</b><br>"
            f"<a href=\"#\" "
            f"onclick=\"window.location.href='{link_url}';return false;\">"
            "Show route</a>"
        )
        folium.Marker(
            [ turf["lat"], turf["lon"] ],
            popup=folium.Popup(popup_html, max_width=200),
            icon=folium.Icon(color="blue", icon="futbol-o", prefix="fa")
        ).add_to(cluster)


    # Draw route polyline if requested
    if route_to:
        path = get_route((user_lat, user_lon),
                         (route_to["lat"], route_to["lon"]))
        folium.PolyLine(path, color="red", weight=5).add_to(m)

    # “You are here” marker
    folium.Marker(
        [user_lat, user_lon],
        popup="You are here",
        icon=folium.Icon(color="red", icon="user", prefix="fa")
    ).add_to(m)

    return m.get_root().render()

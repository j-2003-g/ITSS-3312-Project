
# Week 10: Dallas Homicide Map
# Use Week 9 data to create an interactive map.

import pandas as pd      # Read the CSV file
import folium            # Create the interactive map


def main():
    # STEP 1: Read the Dallas homicide records from Week 9
    wapo = pd.read_csv("data/wapo_dallas.csv")

    # Print the number of records to verify our data
    print(f"Dallas records: {len(wapo)}")

    # STEP 2: Create a map centered on Dallas, Texas
    m = folium.Map(
        location=[32.78, -96.80],
        zoom_start=11,
        tiles=None
    )

    # Add an Esri street map background
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles © Esri",
        name="Esri World Street Map"
    ).add_to(m)

    # STEP 3: Go through each homicide record
    # iterrows() lets us access one row at a time
    for _, row in wapo.iterrows():

        # Orange means open/no arrest; green means closed
        if row["disposition"] == "Open/No arrest":
            color = "orange"
        else:
            color = "green"

        # STEP 4: Add a circle marker at the record's location
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=3,           # Size of the circle
            color=color,        # Marker outline color
            fill=True,          # Fill the circle with color
            fill_opacity=0.6,   # Slightly transparent
            weight=1            # Outline thickness
        ).add_to(m)             # Add the marker to our map

    # STEP 5: Add a legend explaining the marker colors
    legend = """
    <div style="position:fixed;bottom:30px;left:30px;
    background:white;padding:8px 12px;border:1px solid #999;
    font-family:sans-serif;font-size:13px;z-index:9999">
    <b>Dallas homicides 2007–2017</b><br>
    <span style="color:orange">●</span> Open / no arrest (676)<br>
    <span style="color:green">●</span> Closed (891)<br>
    Source: Washington Post Unsolved Homicide Database
    </div>
    """

    # Insert the legend into the map
    m.get_root().html.add_child(folium.Element(legend))

    # STEP 6: Save the map as an HTML file
    m.save("reports/dallas_map.html")

    print("Map saved to reports/dallas_map.html")


# Run the program when executed directly
if __name__ == "__main__":
    main()

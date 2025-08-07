"""Plot particle endpoints and summarize arrivals within polygon.

Loads final particle positions from ``final_positions.csv`` and plots their
locations on a map. The script constructs a target polygon using Shapely and
counts how many particles from each ``release_id`` arrive inside it.
"""

from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import Point, Polygon

# Coordinates defining the arrival polygon (lon, lat pairs)
# These can be adjusted to match the desired region.
coords = [
    (34.05, 31.20),
    (34.45, 31.20),
    (34.45, 31.45),
    (34.05, 31.45),
]


def main() -> None:
    """Load particle endpoints, plot them, and summarize arrivals."""
    df = pd.read_csv("final_positions.csv")

    # Build polygon and prepare plot
    arrival_poly = Polygon(coords)

    fig = plt.figure(figsize=(8, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, facecolor="lightgray")
    ax.add_feature(cfeature.COASTLINE)

    lons = df["lon"]
    lats = df["lat"]
    ax.set_extent([lons.min() - 1, lons.max() + 1, lats.min() - 1, lats.max() + 1])

    # Plot polygon outline
    poly_x, poly_y = zip(*(coords + [coords[0]]))
    ax.plot(poly_x, poly_y, color="red", linewidth=2, transform=ccrs.PlateCarree())

    inside_counts: dict[int, int] = {}
    for _, row in df.iterrows():
        lon = float(row["lon"])
        lat = float(row["lat"])
        release_id = int(row["release_id"])

        ax.scatter(lon, lat, color="blue", s=20, transform=ccrs.PlateCarree())
        ax.text(
            lon + 0.05,
            lat + 0.05,
            str(release_id),
            fontsize=7,
            transform=ccrs.PlateCarree(),
        )

        if arrival_poly.contains(Point(lon, lat)):
            inside_counts[release_id] = inside_counts.get(release_id, 0) + 1

    ax.set_title("Particle Final Positions")
    plt.savefig("particle_arrivals.png")
    plt.show()

    print("Arrival counts within polygon:")
    for release_id, count in sorted(inside_counts.items()):
        print(f"release_id {release_id} -> {count} particles inside polygon")


if __name__ == "__main__":
    main()

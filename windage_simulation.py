import numpy as np
import math
from datetime import timedelta
from parcels import FieldSet, ParticleSet, JITParticle, AdvectionRK4

# Create simple grid and fields with constant currents and wind
lon = np.linspace(0, 1, 2)
lat = np.linspace(0, 1, 2)
time = np.array([0])

# zero ocean currents, constant wind (5 m/s eastward, 2 m/s northward)
data = {
    'U': np.zeros((1, len(lat), len(lon))),
    'V': np.zeros((1, len(lat), len(lon))),
    'wind_u': np.ones((1, len(lat), len(lon))) * 5.0,
    'wind_v': np.ones((1, len(lat), len(lon))) * 2.0,
}

dimensions = {'time': time, 'lat': lat, 'lon': lon}
fieldset = FieldSet.from_data(
    data, dimensions, mesh='spherical', allow_time_extrapolation=True
)
fieldset.add_constant('windage_coeff', 0.03)

# Particle set at the center of the grid
pset = ParticleSet(fieldset=fieldset, pclass=JITParticle, lon=[0.5], lat=[0.5])


def Windage(particle, fieldset, time):
    """Add a fraction of the wind velocity to the particle position."""
    wu = fieldset.wind_u[time, particle.depth, particle.lat, particle.lon]
    wv = fieldset.wind_v[time, particle.depth, particle.lat, particle.lon]
    deg_to_m = 1852 * 60
    rad_lat = math.pi / 180.0 * particle.lat
    particle.lon += (
        fieldset.windage_coeff * wu * particle.dt / (deg_to_m * math.cos(rad_lat))
    )
    particle.lat += fieldset.windage_coeff * wv * particle.dt / deg_to_m

# Combine AdvectionRK4 with Windage kernel
kernel = AdvectionRK4 + pset.Kernel(Windage)

# Run for one hour with 1-minute time steps
pset.execute(kernel, runtime=timedelta(hours=1), dt=60)

# Print final particle location
for p in pset:
    print(f"Particle final position: lon={p.lon:.4f}, lat={p.lat:.4f}")

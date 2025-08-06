#!/usr/bin/env python3
"""Example Parcels simulation with particle weight decay.

This script defines a custom :class:`Drifter` particle with an extra
``weight`` variable. A :func:`Decay` kernel decreases this weight
exponentially over time using a configurable ``decay_rate`` supplied via the
:class:`~parcels.fieldset.FieldSet`. Particles are deleted once their weight
falls below ``weight_threshold`` to mimic disappearance.

The kernel chain combines advection, a simple windage term and the decay
behaviour:

``AdvectionRK4 + Windage + Decay``.

The example constructs a minimal constant field set so the script can run
without external data.
"""

import math
from datetime import timedelta

import numpy as np
from parcels import AdvectionRK4, FieldSet, JITParticle, ParticleSet, Variable


class Drifter(JITParticle):
    """Particle carrying a ``weight`` that can decay over time."""

    weight = Variable("weight", dtype=np.float32, initial=1.0)


def Decay(particle, fieldset, time):
    """Kernel that exponentially decays ``particle.weight``.

    Parameters
    ----------
    particle : :class:`parcels.particleset.particle.JITParticle`
        The particle being updated.
    fieldset : :class:`parcels.fieldset.FieldSet`
        Must define ``decay_rate`` and ``weight_threshold`` constants.
    time : float
        Simulation time (unused).
    """

    # Exponential decay using Euler integration
    particle.weight *= math.exp(-fieldset.decay_rate * particle.dt)

    # Remove particles that have effectively vanished
    if particle.weight < fieldset.weight_threshold:
        particle.delete()


def Windage(particle, fieldset, time):
    """Simple windage kernel applying a constant drift."""

    particle.lon += fieldset.windage_u * particle.dt
    particle.lat += fieldset.windage_v * particle.dt


if __name__ == "__main__":
    # Create a minimal field set with zero currents
    data = {"U": 0, "V": 0}
    dims = {"lon": 0, "lat": 0}
    fieldset = FieldSet.from_data(data, dims, mesh="flat")

    # Add constants for windage and decay configuration
    fieldset.add_constant("windage_u", 0.1)
    fieldset.add_constant("windage_v", 0.0)
    # Decay rate expressed per second; 1/86400 corresponds to an e-folding day
    fieldset.add_constant("decay_rate", 1.0 / 86400.0)
    fieldset.add_constant("weight_threshold", 1e-3)

    # Initialise a particle with default weight at the origin
    pset = ParticleSet(fieldset, pclass=Drifter, lon=[0], lat=[0])

    # Combine kernels: advection, windage and weight decay
    kernels = pset.Kernel(AdvectionRK4) + pset.Kernel(Windage) + pset.Kernel(Decay)

    # Execute for one day with hourly timesteps
    pset.execute(kernels, runtime=timedelta(days=1), dt=timedelta(hours=1))

    # Print final state for demonstration purposes
    for p in pset:
        print(f"Particle at ({p.lon:.3f}, {p.lat:.3f}) with weight {p.weight:.3f}")

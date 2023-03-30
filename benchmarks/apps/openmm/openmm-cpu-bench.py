# Mangled together with the help of David Wright.

import time
from sys import stdout

from simtk import unit
from openmm import app
import openmm as mm


def time_msg(msg):
    "Utility function to print some messages with a leading timestamp."
    t = time.localtime(time.time())
    print(f"{t.tm_year:02d}-{t.tm_mon:02d}-{t.tm_mday:02d}T{t.tm_hour:02d}:"
          f"{t.tm_min:02d}:{t.tm_sec:02d} >>> {msg}")


time_msg("Starting up...")

params = app.CharmmParameterSet('top_all27_prot_lipid.rtf',
                                'par_all27_prot_lipid.prm')
psf = app.CharmmPsfFile('benchmark.psf')
pdb = app.PDBFile('benchmark.pdb')

coords = pdb.positions
min_crds = [coords[0][0], coords[0][1], coords[0][2]]
max_crds = [coords[0][0], coords[0][1], coords[0][2]]

for coord in coords:
    min_crds[0] = min(min_crds[0], coord[0])
    min_crds[1] = min(min_crds[1], coord[1])
    min_crds[2] = min(min_crds[2], coord[2])
    max_crds[0] = max(max_crds[0], coord[0])
    max_crds[1] = max(max_crds[1], coord[1])
    max_crds[2] = max(max_crds[2], coord[2])

psf.setBox(max_crds[0]-min_crds[0],
           max_crds[1]-min_crds[1],
           max_crds[2]-min_crds[2],
           )

system = psf.createSystem(params,
                          nonbondedMethod=app.PME,
                          nonbondedCutoff=0.8*unit.nanometers,
                          constraints=app.HBonds,
                          rigidWater=True,
                          ewaldErrorTolerance=0.0005)
time_msg('System creation complete')
integrator = mm.LangevinIntegrator(300*unit.kelvin, 1.0/unit.picoseconds,
                                   2.0*unit.femtoseconds)
integrator.setConstraintTolerance(0.00001)
system.addForce(mm.MonteCarloBarostat(1*unit.atmospheres, 300*unit.kelvin, 25))
platform = mm.Platform.getPlatformByName('CPU')
simulation = app.Simulation(psf.topology, system, integrator, platform)

time_msg('Setting positions...')
simulation.context.setPositions(pdb.positions)

time_msg('Setting velocities...')
simulation.context.setVelocitiesToTemperature(300*unit.kelvin)

time_msg('Setting reporters...')
simulation.reporters.append(
    app.StateDataReporter(stdout, 1000, step=True,
                          potentialEnergy=True, kineticEnergy=True,
                          totalEnergy=True, temperature=True,
                          progress=True, remainingTime=True, speed=True,
                          totalSteps=10000,
                          separator='\t'))

time_msg('Running Production...')
simulation.step(10000)
time_msg('Done!')

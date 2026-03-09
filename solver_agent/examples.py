"""Prompt examples for YAML generation."""

EXAMPLE_1 = """app: lbm
version: 0.0.8
general:
  model_type: viscous_isothermal
geom_data:
  path: F:/workspace/Tsyrendorzhiev/LabFlowCases/bfs/backward-facing step.grb
  wind_tunnel:
    minimum: {x: -1200, y: -10, z: -300}
    maximum: {x: 2100, y: 20, z: 300}
  add: false
sensors: []
coprocessor: {type: gpu, id: 0}
substances:
  - name: DEFAULT_FLUID
    dynamic_viscosity: {type: const, value: 5E-06}
    density: {type: const, value: 1}
    heat_capacity_p: {type: const, value: 4200}
    heat_conductivity_coefficient: {type: const, value: 2}
    source: customized
    type: fluid
discretization:
  time_step: {real: 0.0001, lattice: 1}
  spatial_step: {real: 0.001, lattice: 1}
  min_spatial_step: {real: 0.001, lattice: 1}
  mesh_sets:
    - files: bfs.lttc
physical_model:
  viscous: turbulence
  reference_temperature: {type: const, value: 300}
  gravity: {type: const, value: {x: 0, y: -9.81, z: 0}}
scales: {temperature: 300}
solver:
  collision_operator: {type: CM, parameters: {}}
control:
  exit:
    end_time: 1
    precision: {value: 1E-06, time_step: 0.0001}
  output:
    console: {time_step: 1}
    disk: {format: lbr, time_step: 1}
    force: {time_step: 2}
regions: []
tables: []"""

EXAMPLE_2 = """app: lbm
version: 0.0.8
general: {model_type: viscous_isothermal}
geom_data:
  path: F:/workspace/Tsyrendorzhiev/LabFlow/TFlexLabFlow/bin/x64/Debug/databases/00118/typhoon_r.grb
  wind_tunnel:
    minimum: {x: -1200, y: -1200, z: -1050}
    maximum: {x: 1800, y: 1200, z: 1050}
  add: true
sensors: []
coprocessor: {type: gpu, id: 0}
substances:
  - name: air
    dynamic_viscosity: {type: const, value: 2E-05}
    density: {type: const, value: 1}
    heat_capacity_p: {type: const, value: 440}
    heat_conductivity_coefficient: {type: const, value: 43}
    source: customized
    type: fluid
discretization:
  time_step: {real: 0.001, lattice: 1}
  spatial_step: {real: 0.04, lattice: 1}
  min_spatial_step: {real: 0.01, lattice: 1}
  mesh_sets:
    - files: typhoon.lttc
physical_model:
  viscous: turbulence
  reference_temperature: {type: const, value: 300}
  gravity: {type: const, value: {x: 0, y: -9.81, z: 0}}
scales: {temperature: 300}
solver:
  collision_operator: {type: CM, parameters: {}}
control:
  exit:
    end_time: 1
    precision: {value: 1E-06, time_step: 0.001}
  output:
    console: {time_step: 0.2}
    disk: {format: lbr, time_step: 0.2}
    force: {time_step: 2}
regions: []
tables: []"""

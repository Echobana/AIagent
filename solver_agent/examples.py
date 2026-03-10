"""Prompt examples for YAML generation."""

EXAMPLE_1 = """app: lbm
version: 0.0.8
general:
  model_type: viscous_isothermal
geom_data:
  path: backward-facing step.grb
  wind_tunnel:
    minimum:
      x: -1200
      y: -10
      z: -300
    maximum:
      x: 2100
      y: 20
      z: 300
  add: false
sensors: []
coprocessor:
  type: gpu
  id: 0
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
  collision_operator:
    type: CM
    parameters: {}
control:
  exit:
    end_time: 1
    precision: {value: 1E-06, time_step: 0.0001}
  output:
    console: {time_step: 1}
    disk:
      format: lbr
      time_step: 1
    force:
      time_step: 2
regions:
  - name: Тело_1
    substance_name: DEFAULT_FLUID
    mesh_set_id: 0
    init:
      p: {type: const, value: 100000}
      temperature: {type: const, value: 300}
      velocity: {type: const, value: {x: 2.3, y: 0, z: 0}}
    patches:
      - name: bot wall
        dynamic_condition:
          type: no_slip_wall
          lbm_type: ibb
        normal: {x: 1.38777878078145E-16, y: 0, z: 1}
        faces:
          - O_LOW_0x54000001000000B0_HIGH_0x23000000000000_B0x2a000001_O0x2a000001
          - O_LOW_0x54000001000000C0_HIGH_0x23000000000000_B0x2a000001_O0x2a000001
          - O_LOW_0x5400000100000070_HIGH_0x23000000000000_B0x2a000001_O0x2a000001
        is_lateral: false
      - name: default
        dynamic_condition:
          type: no_slip_wall
          lbm_type: ibb
        faces: []
        is_lateral: false
      - name: inlet
        dynamic_condition:
          type: input_mass
          specific_mass_flow_rate: {type: const, value: 2.3}
        normal: {x: 1, y: 0, z: 0}
        faces:
          - O_LOW_0x5400000100000080_HIGH_0x23000000000000_B0x2a000001_O0x2a000001
        is_lateral: false
      - name: left
        dynamic_condition:
          type: symmetry
        normal: {x: 0, y: -1, z: 0}
        faces:
          - O_LOW_0x54000003000000E0_HIGH_0x62000000000000_B0x2a000001_O0x2a000001
        is_lateral: false
      - name: outlet
        dynamic_condition:
          type: output
        normal: {x: -1, y: 0, z: 0}
        faces:
          - O_LOW_0x54000001000000A0_HIGH_0x23000000000000_B0x2a000001_O0x2a000001
        is_lateral: false
      - name: right
        dynamic_condition:
          type: symmetry
        normal: {x: 0, y: 1, z: 0}
        faces:
          - O_LOW_0x54000001000000E0_HIGH_0x62000000000000_B0x2a000001_O0x2a000001
        is_lateral: false
      - name: top
        dynamic_condition:
          type: no_slip_wall
          lbm_type: ibb
        normal: {x: -1.00929365875014E-16, y: 0, z: -1}
        faces:
          - O_LOW_0x5400000100000090_HIGH_0x23000000000000_B0x2a000001_O0x2a000001
        is_lateral: false
tables: []"""

EXAMPLE_2 = """app: lbm
version: 0.0.8
general:
  model_type: viscous_isothermal
geom_data:
  path: typhoon_r.grb
  wind_tunnel:
    minimum:
      x: -1200
      y: -1200
      z: -1050
    maximum:
      x: 1800
      y: 1200
      z: 1050
  add: true
sensors: []
coprocessor:
  type: gpu
  id: 0
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
  collision_operator:
    type: CM
    parameters: {}
control:
  exit:
    end_time: 1
    precision: {value: 1E-06, time_step: 0.001}
  output:
    console: {time_step: 0.2}
    disk:
      format: lbr
      time_step: 0.2
    force:
      time_step: 2
regions:
  - name: LabFlowBoundinBox
    substance_name: air
    mesh_set_id: 0
    init:
      p: {type: const, value: 100000}
      temperature: {type: const, value: 300}
      velocity: {type: const, value: {x: 1, y: 0, z: 0}}
    patches:
      - name: bottom face (O_LOW_0x10D3000030_HIGH_0xA2000000000000_B0xd3000030_O0xd3000030)
        dynamic_condition:
          type: soft
        normal: {x: 0, y: 0, z: -1}
        faces:
          - bbox_5
        is_lateral: true
      - name: default
        dynamic_condition:
          type: no_slip_wall
          lbm_type: ibb
        faces: []
        is_lateral: false
      - name: inlet2
        dynamic_condition:
          type: input_mass
          specific_mass_flow_rate: {type: const, value: 1}
        normal: {x: 1, y: 0, z: 0}
        faces:
          - bbox_0
        is_lateral: false
      - name: left face (O_LOW_0x30D3000030_HIGH_0xA4000000000000_B0xd3000030_O0xd3000030)
        dynamic_condition:
          type: soft
        normal: {x: 0, y: 1, z: 0}
        faces:
          - bbox_2
        is_lateral: true
      - name: rear face (O_LOW_0x40D3000030_HIGH_0xA4000000000000_B0xd3000030_O0xd3000030)
        dynamic_condition:
          type: soft
        normal: {x: -1, y: 0, z: 0}
        faces:
          - bbox_1
        is_lateral: true
      - name: right face (O_LOW_0x10D3000030_HIGH_0xA4000000000000_B0xd3000030_O0xd3000030)
        dynamic_condition:
          type: soft
        normal: {x: 0, y: -1, z: 0}
        faces:
          - bbox_3
        is_lateral: true
      - name: top face (O_LOW_0x10D3000030_HIGH_0xA3000000000000_B0xd3000030_O0xd3000030)
        dynamic_condition:
          type: soft
        normal: {x: 0, y: 0, z: 1}
        faces:
          - bbox_4
        is_lateral: true
tables: []"""

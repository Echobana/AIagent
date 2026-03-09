"""Pydantic schema for core LBM YAML structure."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict


class Vector3(BaseModel):
    x: float
    y: float
    z: float


class ConstField(BaseModel):
    type: str
    value: Any


class WindTunnel(BaseModel):
    minimum: Vector3
    maximum: Vector3


class GeomData(BaseModel):
    path: str
    wind_tunnel: WindTunnel
    add: bool


class Coprocessor(BaseModel):
    type: str
    id: int


class Substance(BaseModel):
    name: str
    dynamic_viscosity: ConstField
    density: ConstField
    heat_capacity_p: ConstField
    heat_conductivity_coefficient: ConstField
    source: str
    type: str


class LatticeStep(BaseModel):
    real: float
    lattice: float


class MeshSet(BaseModel):
    files: str


class Discretization(BaseModel):
    time_step: LatticeStep
    spatial_step: LatticeStep
    min_spatial_step: LatticeStep
    mesh_sets: List[MeshSet]


class PhysicalModel(BaseModel):
    viscous: str
    reference_temperature: ConstField
    gravity: ConstField


class CollisionOperator(BaseModel):
    type: str
    parameters: Dict[str, Any]


class Solver(BaseModel):
    collision_operator: CollisionOperator


class SolverConfig(BaseModel):
    model_config = ConfigDict(extra="allow")

    app: str
    version: str
    general: Dict[str, Any]
    geom_data: GeomData
    sensors: List[Any]
    coprocessor: Coprocessor
    substances: List[Substance]
    discretization: Discretization
    physical_model: PhysicalModel
    scales: Dict[str, Any]
    solver: Solver
    control: Dict[str, Any]
    regions: List[Dict[str, Any]]
    tables: List[Any]

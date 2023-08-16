"""Technology settings."""
from __future__ import annotations

from typing import Any

from kfactory.kcell import LayerEnum
from pydantic import BaseModel, Field

nm = 1e-3


class LAYER(LayerEnum):
    """Generic layermap based  book.

    Lukas Chrostowski, Michael Hochberg, "Silicon Photonics Design",
    Cambridge University Press 2015, page 353
    You will need to create a new LayerMap with your specific foundry layers.
    """

    WG = (1, 0)
    WAFER = (50, 0)
    WGCLAD = (111, 0)
    SLAB150 = (2, 0)
    SLAB90 = (3, 0)
    SHALLOW_ETCH = (2, 6)
    SHALLOWTRENCH = (5, 0)
    DEEP_ETCH = (3, 6)
    DEEPTRENCH = (4, 0)
    GE = (5, 0)
    UNDERCUT = (6, 0)
    WGN = (34, 0)
    WGN_CLAD = (36, 0)

    N = (20, 0)
    NP = (22, 0)
    NPP = (24, 0)
    P = (21, 0)
    PP = (23, 0)
    PPP = (25, 0)
    GEN = (26, 0)
    GEP = (27, 0)

    HEATER = (47, 0)
    M1 = (41, 0)
    M2 = (45, 0)
    M3 = (49, 0)
    VIAC = (40, 0)
    VIA1 = (44, 0)
    VIA2 = (43, 0)
    PADOPEN = (46, 0)

    DICING = (100, 0)
    NO_TILE_SI = (71, 0)
    PADDING = (67, 0)
    DEVREC = (68, 0)
    FLOORPLAN = (64, 0)
    TEXT = (66, 0)
    PORT = (1, 10)
    PORTE = (1, 11)
    PORTH = (70, 0)
    SHOW_PORTS = (1, 12)
    LABEL = (201, 0)
    LABEL_SETTINGS = (202, 0)
    TE = (203, 0)
    TM = (204, 0)
    DRC_MARKER = (205, 0)
    LABEL_INSTANCE = (206, 0)
    ERROR_MARKER = (207, 0)
    ERROR_PATH = (208, 0)

    SOURCE = (110, 0)
    MONITOR = (101, 0)


PORT_MARKER_LAYER_TO_TYPE = {
    LAYER.PORT: "optical",
    LAYER.PORTE: "dc",
    LAYER.TE: "vertical_te",
    LAYER.TM: "vertical_tm",
}

PORT_LAYER_TO_TYPE = {
    LAYER.WG: "optical",
    LAYER.WGN: "optical",
    LAYER.SLAB150: "optical",
    LAYER.M1: "dc",
    LAYER.M2: "dc",
    LAYER.M3: "dc",
    LAYER.TE: "vertical_te",
    LAYER.TM: "vertical_tm",
}

PORT_TYPE_TO_MARKER_LAYER = {v: k for k, v in PORT_MARKER_LAYER_TO_TYPE.items()}


class LayerLevel(BaseModel):
    """Level for 3D LayerStack.

    Parameters:
        layer: (GDSII Layer number, GDSII datatype).
        thickness: layer thickness in um.
        thickness_tolerance: layer thickness tolerance in um.
        zmin: height position where material starts in um.
        material: material name.
        sidewall_angle: in degrees with respect to normal.
        z_to_bias: parametrizes shrinking/expansion of the design GDS layer
            when extruding from zmin (0) to zmin + thickness (1).
            Defaults no buffering [[0, 1], [0, 0]].
        info: simulation_info and other types of metadata.
            mesh_order: lower mesh order (1) will have priority over higher
                mesh order (2) in the regions where materials overlap.
            refractive_index: refractive_index
                can be int, complex or function that depends on wavelength (um).
            type: grow, etch, implant, or background.
            mode: octagon, taper, round.
                https://gdsfactory.github.io/klayout_pyxs/DocGrow.html
            into: etch into another layer.
                https://gdsfactory.github.io/klayout_pyxs/DocGrow.html
            doping_concentration: for implants.
            resistivity: for metals.
            bias: in um for the etch.
    """

    layer: tuple[int, int] | LAYER
    thickness: float
    thickness_tolerance: float | None = None
    zmin: float
    material: str | None = None
    sidewall_angle: float = 0.0
    z_to_bias: list[list[float]] | None = None
    info: dict[str, Any] = {}


class LayerStack(BaseModel):
    """For simulation and 3D rendering.

    Parameters:
        layers: dict of layer_levels.
    """

    layers: dict[str, LayerLevel] = Field(default_factory=dict)

    def __init__(self, **data: Any):
        """Add LayerLevels automatically for subclassed LayerStacks."""
        super().__init__(**data)

        for field in self.dict():
            val = getattr(self, field)
            if isinstance(val, LayerLevel):
                self.layers[field] = val
                if isinstance(val.layer, LAYER):
                    self.layers[field].layer = (val.layer[0], val.layer[1])

    def get_layer_to_thickness(self) -> dict[tuple[int, int] | LAYER, float]:
        """Returns layer tuple to thickness (um)."""
        return {
            level.layer: level.thickness
            for level in self.layers.values()
            if level.thickness
        }

    def get_layer_to_zmin(self) -> dict[tuple[int, int] | LAYER, float]:
        """Returns layer tuple to z min position (um)."""
        return {
            level.layer: level.zmin for level in self.layers.values() if level.thickness
        }

    def get_layer_to_material(self) -> dict[tuple[int, int] | LAYER, str]:
        """Returns layer tuple to material name."""
        return {
            level.layer: level.material
            for level in self.layers.values()
            if level.thickness and level.material
        }

    def get_layer_to_sidewall_angle(self) -> dict[tuple[int, int] | LAYER, float]:
        """Returns layer tuple to material name."""
        return {
            level.layer: level.sidewall_angle
            for level in self.layers.values()
            if level.thickness
        }

    def get_layer_to_info(self) -> dict[tuple[int, int] | LAYER, dict[str, Any]]:
        """Returns layer tuple to info dict."""
        return {level.layer: level.info for level in self.layers.values()}

    def to_dict(self) -> dict[str, dict[str, Any]]:
        return {level_name: dict(level) for level_name, level in self.layers.items()}

    def __getitem__(self, key: str) -> LayerLevel:
        """Access layer stack elements."""
        if key not in self.layers:
            layers = list(self.layers.keys())
            raise ValueError(f"{key!r} not in {layers}")

        return self.layers[key]


class LayerStackParameters:
    """values used by get_layer_stack and get_process."""

    thickness_wg: float = 220 * nm
    thickness_slab_deep_etch: float = 90 * nm
    thickness_slab_shallow_etch: float = 150 * nm
    sidewall_angle_wg: float = 10.0
    thickness_clad: float = 3.0
    thickness_nitride: float = 350 * nm
    thickness_ge: float = 500 * nm
    gap_silicon_to_nitride: float = 100 * nm
    zmin_heater: float = 1.1
    zmin_metal1: float = 1.1
    thickness_metal1: float = 700 * nm
    zmin_metal2: float = 2.3
    thickness_metal2: float = 700 * nm
    zmin_metal3: float = 3.2
    thickness_metal3: float = 2000 * nm
    substrate_thickness: float = 10.0
    box_thickness: float = 3.0
    undercut_thickness: float = 5.0


def get_layer_stack(
    thickness_wg=LayerStackParameters.thickness_wg,
    thickness_slab_deep_etch=LayerStackParameters.thickness_slab_deep_etch,
    thickness_slab_shallow_etch=LayerStackParameters.thickness_slab_shallow_etch,
    sidewall_angle_wg=LayerStackParameters.sidewall_angle_wg,
    thickness_clad=LayerStackParameters.thickness_clad,
    thickness_nitride=LayerStackParameters.thickness_nitride,
    thickness_ge=LayerStackParameters.thickness_ge,
    gap_silicon_to_nitride=LayerStackParameters.gap_silicon_to_nitride,
    zmin_heater=LayerStackParameters.zmin_heater,
    zmin_metal1=LayerStackParameters.zmin_metal1,
    thickness_metal1=LayerStackParameters.thickness_metal1,
    zmin_metal2=LayerStackParameters.zmin_metal2,
    thickness_metal2=LayerStackParameters.thickness_metal2,
    zmin_metal3=LayerStackParameters.zmin_metal3,
    thickness_metal3=LayerStackParameters.thickness_metal3,
    substrate_thickness=LayerStackParameters.substrate_thickness,
    box_thickness=LayerStackParameters.box_thickness,
    undercut_thickness=LayerStackParameters.undercut_thickness,
) -> LayerStack:
    """Returns generic LayerStack.

    based on paper https://www.degruyter.com/document/doi/10.1515/nanoph-2013-0034/html

    Args:
        thickness_wg: waveguide thickness in um.
        thickness_slab_deep_etch: for deep etched slab.
        thickness_shallow_etch: thickness for the etch in um.
        sidewall_angle_wg: waveguide side angle.
        thickness_clad: cladding thickness in um.
        thickness_nitride: nitride thickness in um.
        thickness_ge: germanium thickness.
        gap_silicon_to_nitride: distance from silicon to nitride in um.
        zmin_heater: TiN heater.
        zmin_metal1: metal1.
        thickness_metal1: metal1 thickness.
        zmin_metal2: metal2.
        thickness_metal2: metal2 thickness.
        zmin_metal3: metal3.
        thickness_metal3: metal3 thickness.
        substrate_thickness: substrate thickness in um.
        box_thickness: bottom oxide thickness in um.
        undercut_thickness: thickness of the silicon undercut.
    """

    thickness_deep_etch = thickness_wg - thickness_slab_deep_etch
    thickness_shallow_etch = thickness_wg - thickness_slab_shallow_etch

    return LayerStack(
        layers=dict(
            substrate=LayerLevel(
                layer=LAYER.WAFER,
                thickness=substrate_thickness,
                zmin=-substrate_thickness - box_thickness,
                material="si",
                mesh_order=101,
                background_doping={"concentration": "1E14", "ion": "Boron"},
                orientation="100",
            ),
            box=LayerLevel(
                layer=LAYER.WAFER,
                thickness=box_thickness,
                zmin=-box_thickness,
                material="sio2",
                mesh_order=9,
            ),
            core=LayerLevel(
                layer=LAYER.WG,
                thickness=thickness_wg,
                zmin=0.0,
                material="si",
                mesh_order=2,
                sidewall_angle=sidewall_angle_wg,
                width_to_z=0.5,
                background_doping_concentration=1e14,
                background_doping_ion="Boron",
                orientation="100",
                info={"active": True},
            ),
            shallow_etch=LayerLevel(
                layer=LAYER.SHALLOW_ETCH,
                thickness=thickness_shallow_etch,
                zmin=0.0,
                material="si",
                mesh_order=1,
                layer_type="etch",
                into=["core"],
                derived_layer=LAYER.SLAB150,
            ),
            deep_etch=LayerLevel(
                layer=LAYER.DEEP_ETCH,
                thickness=thickness_deep_etch,
                zmin=0.0,
                material="si",
                mesh_order=1,
                layer_type="etch",
                into=["core"],
                derived_layer=LAYER.SLAB90,
            ),
            clad=LayerLevel(
                # layer=LAYER.WGCLAD,
                layer=LAYER.WAFER,
                zmin=0.0,
                material="sio2",
                thickness=thickness_clad,
                mesh_order=10,
            ),
            slab150=LayerLevel(
                layer=LAYER.SLAB150,
                thickness=150e-3,
                zmin=0,
                material="si",
                mesh_order=3,
            ),
            slab90=LayerLevel(
                layer=LAYER.SLAB90,
                thickness=thickness_slab_deep_etch,
                zmin=0.0,
                material="si",
                mesh_order=2,
            ),
            nitride=LayerLevel(
                layer=LAYER.WGN,
                thickness=thickness_nitride,
                zmin=thickness_wg + gap_silicon_to_nitride,
                material="sin",
                mesh_order=2,
            ),
            ge=LayerLevel(
                layer=LAYER.GE,
                thickness=thickness_ge,
                zmin=thickness_wg,
                material="ge",
                mesh_order=1,
            ),
            undercut=LayerLevel(
                layer=LAYER.UNDERCUT,
                thickness=-undercut_thickness,
                zmin=-box_thickness,
                material="air",
                z_to_bias=[
                    [0.0, 0.3, 0.6, 0.8, 0.9, 1.0],
                    [-0.0, -0.5, -1.0, -1.5, -2.0, -2.5],
                ],
                mesh_order=1,
            ),
            via_contact=LayerLevel(
                layer=LAYER.VIAC,
                thickness=zmin_metal1 - thickness_slab_deep_etch,
                zmin=thickness_slab_deep_etch,
                material="Aluminum",
                mesh_order=1,
                sidewall_angle=-10.0,
                width_to_z=0,
            ),
            metal1=LayerLevel(
                layer=LAYER.M1,
                thickness=thickness_metal1,
                zmin=zmin_metal1,
                material="Aluminum",
                mesh_order=2,
            ),
            heater=LayerLevel(
                layer=LAYER.HEATER,
                thickness=750e-3,
                zmin=zmin_heater,
                material="TiN",
                mesh_order=2,
            ),
            via1=LayerLevel(
                layer=LAYER.VIA1,
                thickness=zmin_metal2 - (zmin_metal1 + thickness_metal1),
                zmin=zmin_metal1 + thickness_metal1,
                material="Aluminum",
                mesh_order=1,
            ),
            metal2=LayerLevel(
                layer=LAYER.M2,
                thickness=thickness_metal2,
                zmin=zmin_metal2,
                material="Aluminum",
                mesh_order=2,
            ),
            via2=LayerLevel(
                layer=LAYER.VIA2,
                thickness=zmin_metal3 - (zmin_metal2 + thickness_metal2),
                zmin=zmin_metal2 + thickness_metal2,
                material="Aluminum",
                mesh_order=1,
            ),
            metal3=LayerLevel(
                layer=LAYER.M3,
                thickness=thickness_metal3,
                zmin=zmin_metal3,
                material="Aluminum",
                mesh_order=2,
            ),
        )
    )


LAYER_STACK = get_layer_stack()

if __name__ == "__main__":
    print(LAYER.WG)

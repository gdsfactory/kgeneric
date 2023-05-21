"""Technology settings."""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Union

from pydantic import BaseModel, Field

from kfactory.kcell import LayerEnum

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

    layer: Union[Tuple[int, int], LAYER]
    thickness: float
    thickness_tolerance: float | None = None
    zmin: float
    material: str | None = None
    sidewall_angle: float = 0
    z_to_bias: Optional[Tuple[float, ...]] = None
    info: Dict[str, Any] = {}


class LayerStack(BaseModel):
    """For simulation and 3D rendering.

    Parameters:
        layers: dict of layer_levels.
    """

    layers: Dict[str, LayerLevel] = Field(default_factory=dict)

    def __init__(self, **data: Any):
        """Add LayerLevels automatically for subclassed LayerStacks."""
        super().__init__(**data)

        for field in self.dict():
            val = getattr(self, field)
            if isinstance(val, LayerLevel):
                self.layers[field] = val
                if isinstance(val.layer, LAYER):
                    self.layers[field].layer = (val.layer[0], val.layer[1])

    def get_layer_to_thickness(self) -> Dict[Tuple[int, int] | LAYER, float]:
        """Returns layer tuple to thickness (um)."""
        return {
            level.layer: level.thickness
            for level in self.layers.values()
            if level.thickness
        }

    def get_layer_to_zmin(self) -> Dict[Tuple[int, int] | LAYER, float]:
        """Returns layer tuple to z min position (um)."""
        return {
            level.layer: level.zmin for level in self.layers.values() if level.thickness
        }

    def get_layer_to_material(self) -> Dict[Tuple[int, int] | LAYER, str]:
        """Returns layer tuple to material name."""
        return {
            level.layer: level.material
            for level in self.layers.values()
            if level.thickness and level.material
        }

    def get_layer_to_sidewall_angle(self) -> Dict[Tuple[int, int] | LAYER, float]:
        """Returns layer tuple to material name."""
        return {
            level.layer: level.sidewall_angle
            for level in self.layers.values()
            if level.thickness
        }

    def get_layer_to_info(self) -> Dict[Tuple[int, int] | LAYER, Dict[str, Any]]:
        """Returns layer tuple to info dict."""
        return {level.layer: level.info for level in self.layers.values()}

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {level_name: dict(level) for level_name, level in self.layers.items()}

    def __getitem__(self, key: str) -> LayerLevel:
        """Access layer stack elements."""
        if key not in self.layers:
            layers = list(self.layers.keys())
            raise ValueError(f"{key!r} not in {layers}")

        return self.layers[key]


# def get_layer_stack(
thickness_wg = 220 * nm
thickness_slab_deep_etch = 90 * nm
thickness_clad = 3.0
thickness_nitride = 350 * nm
thickness_ge = 500 * nm
gap_silicon_to_nitride = 100 * nm
zmin_heater = 1.1
zmin_metal1 = 1.1
thickness_metal1 = 700 * nm
zmin_metal2 = 2.3
thickness_metal2 = 700 * nm
zmin_metal3 = 3.2
thickness_metal3 = 2000 * nm
substrate_thickness = 10.0
box_thickness = 3.0
undercut_thickness = 5.0
# )
# -> LayerStack:
#     """Returns generic LayerStack.

#     based on paper https://www.degruyter.com/document/doi/10.1515/nanoph-2013-0034/html

#     Args:
#         thickness_wg: waveguide thickness in um.
#         thickness_slab_deep_etch: for deep etched slab.
#         thickness_clad: cladding thickness in um.
#         thickness_nitride: nitride thickness in um.
#         thickness_ge: germanium thickness.
#         gap_silicon_to_nitride: distance from silicon to nitride in um.
#         zmin_heater: TiN heater.
#         zmin_metal1: metal1.
#         thickness_metal1: metal1 thickness.
#         zmin_metal2: metal2.
#         thickness_metal2: metal2 thickness.
#         zmin_metal3: metal3.
#         thickness_metal3: metal3 thickness.
#         substrate_thickness: substrate thickness in um.
#         box_thickness: bottom oxide thickness in um.
#         undercut_thickness: thickness of the silicon undercut.
#     """


class GenericLayerStack(LayerStack):
    substrate = LayerLevel(
        layer=LAYER.WAFER,
        thickness=substrate_thickness,
        zmin=-substrate_thickness - box_thickness,
        material="si",
        info={"mesh_order": 99},
    )
    box = LayerLevel(
        layer=LAYER.WAFER,
        thickness=box_thickness,
        zmin=-box_thickness,
        material="sio2",
        info={"mesh_order": 99},
    )
    core = LayerLevel(
        layer=LAYER.WG,
        thickness=thickness_wg,
        zmin=0.0,
        material="si",
        info={"mesh_order": 1},
        sidewall_angle=10,
        # width_to_z=0.5,
    )
    clad = LayerLevel(
        # layer=LAYER.WGCLAD,
        layer=LAYER.WAFER,
        zmin=0.0,
        material="sio2",
        thickness=thickness_clad,
        info={"mesh_order": 10},
    )
    slab150 = LayerLevel(
        layer=LAYER.SLAB150,
        thickness=150e-3,
        zmin=0,
        material="si",
        info={"mesh_order": 3},
    )
    slab90 = LayerLevel(
        layer=LAYER.SLAB90,
        thickness=thickness_slab_deep_etch,
        zmin=0.0,
        material="si",
        info={"mesh_order": 2},
    )
    nitride = LayerLevel(
        layer=LAYER.WGN,
        thickness=thickness_nitride,
        zmin=thickness_wg + gap_silicon_to_nitride,
        material="sin",
        info={"mesh_order": 2},
    )
    ge = LayerLevel(
        layer=LAYER.GE,
        thickness=thickness_ge,
        zmin=thickness_wg,
        material="ge",
        info={"mesh_order": 1},
    )
    undercut = LayerLevel(
        layer=LAYER.UNDERCUT,
        thickness=-undercut_thickness,
        zmin=-box_thickness,
        material="air",
        # z_to_bias=tuple(
        #     list([0, 0.3, 0.6, 0.8, 0.9, 1]),
        #     list([-0, -0.5, -1, -1.5, -2, -2.5]),
        # ),
        info={"mesh_order": 1},
    )
    via_contact = LayerLevel(
        layer=LAYER.VIAC,
        thickness=zmin_metal1 - thickness_slab_deep_etch,
        zmin=thickness_slab_deep_etch,
        material="Aluminum",
        info={"mesh_order": 1},
        sidewall_angle=-10,
    )
    metal1 = LayerLevel(
        layer=LAYER.M1,
        thickness=thickness_metal1,
        zmin=zmin_metal1,
        material="Aluminum",
        info={"mesh_order": 2},
    )
    heater = LayerLevel(
        layer=LAYER.HEATER,
        thickness=750e-3,
        zmin=zmin_heater,
        material="TiN",
        info={"mesh_order": 1},
    )
    via1 = LayerLevel(
        layer=LAYER.VIA1,
        thickness=zmin_metal2 - (zmin_metal1 + thickness_metal1),
        zmin=zmin_metal1 + thickness_metal1,
        material="Aluminum",
        info={"mesh_order": 2},
    )
    metal2 = LayerLevel(
        layer=LAYER.M2,
        thickness=thickness_metal2,
        zmin=zmin_metal2,
        material="Aluminum",
        info={"mesh_order": 2},
    )
    via2 = LayerLevel(
        layer=LAYER.VIA2,
        thickness=zmin_metal3 - (zmin_metal2 + thickness_metal2),
        zmin=zmin_metal2 + thickness_metal2,
        material="Aluminum",
        info={"mesh_order": 1},
    )
    metal3 = LayerLevel(
        layer=LAYER.M3,
        thickness=thickness_metal3,
        zmin=zmin_metal3,
        material="Aluminum",
        info={"mesh_order": 2},
    )


LAYER_STACK = GenericLayerStack()

if __name__ == "__main__":
    print(LAYER.WG)

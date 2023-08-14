from functools import partial

import kfactory as kf

from kgeneric import gpdk

route_sc = partial(
    kf.routing.optical.route,
    straight_factory=gpdk.straight_dbu_sc,
    bend90_cell=gpdk.bend_euler_sc(),
)


if __name__ == "__main__":
    c = kf.KCell()

    sl = c << gpdk.straight_sc()
    sr = c << gpdk.straight_sc()
    sr.d.move((50, 50))

    route_sc(
        c, p1=sl.ports["o2"], p2=sr.ports["o1"], straight_factory=gpdk.straight_dbu_sc
    )
    c.show()

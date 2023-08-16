import kfactory as kf

from kgeneric import gpdk as pdk

if __name__ == "__main__":
    c = kf.KCell("bend_chain")
    b1 = c << pdk.bend_euler_sc(angle=37)
    b2 = c << pdk.bend_euler_sc(angle=37)
    b2.connect("o1", b1.ports["o2"])
    # b1.flatten()
    # b2.flatten()
    c.flatten()
    c.show()

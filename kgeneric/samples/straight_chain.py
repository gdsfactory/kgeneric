import kfactory as kf

from kgeneric import gpdk as pdk

if __name__ == "__main__":
    nm = 1e-3
    c = kf.KCell("bend_chain")
    s1 = c << pdk.straight_sc(length=1 + 1.5 * nm)
    s2 = c << pdk.straight_sc(length=1)
    s2.connect("o1", s1.ports["o2"])
    # b1.flatten()
    # b2.flatten()
    # c.flatten()
    c.show()

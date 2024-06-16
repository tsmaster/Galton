


def bdg_map(v, in_min, in_max, out_min, out_max):
    t = (v - in_min) / (in_max - in_min)
    return t * (out_max - out_min) + out_min

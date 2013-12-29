# GA144 IO Exception List
# The below dictionary holds places that are
# exceptions to the following rules:
# 1) Top nodes have no u
# 2) Left Nodes Have no l
# 3) Bottom nodes have no d
# 4) Right Nodes Have no r

uIOInterfaces = {
    (7, 1): "serdes",
    (7, 5): "spi",
    (7, 8): "async",
    (7, 9): "analog-tied",
    (7, 13): "analog-tied",
    (7, 15): "gpio",
    (7, 17): "analog-tied"
}

lIOInterfaces = {
    (6, 0): "gpio",
    (5, 0): "gpio",
    (3, 0): "gpio-double",
    (3, 0): "gpio-double",
    (1, 0): "gpio"
}

rIOInterfaces = {
    (6, 17): "gpio-tied-double",
    (6, 17): "gpio-tied-double",
    (5, 17): "gpio-tied",
    (4, 17): "gpio",
    (3, 17): "gpio",
    (2, 17): "analog-tied",
    (1, 17): "analog-tied"
}

dIOInterfaces = {
    (0, 1): "serdes",
    (0, 7): "data",
    (0, 8): "control",
    (0, 9): "address"
}

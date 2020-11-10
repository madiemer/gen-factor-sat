import Karatsuba as k
import WallaceTree as w

strategy = k.Strategy()

x = strategy.int_to_bin(1478697)
y = strategy.int_to_bin(231471874174017448)

kara = k.karatsuba(x, y, strategy)
wall = w.wallace_tree(x, y, strategy)

print(strategy.bin_to_int(kara))
print(strategy.bin_to_int(wall))
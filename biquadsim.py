import matplotlib.pyplot as plt
import numpy as np
a0 = 0.013806011447721036
a1 = 0.02761202289544207
a2 = 0.013806011447721036
b1 = -1.0730986973124192
b2 = 0.12832274310330333
z1 = 0
z2 = 0

def process(i):
    global z1
    global z2
    global x1
    global x2
    out = i * a0 + z1
    z1 = i * a1 + z2 - b1 * out
    z2 = i * a2 - b2 * out

    return out

ivals = [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] * 10
#ivals = [1] * 1000
out = list(map(process,ivals))
print(ivals)
print(out)

print(max(out))
t = np.arange(0.0, len(ivals), 1)

fig, ax = plt.subplots()
ax.plot(t, ivals)
ax.plot(t, out)

ax.grid()

plt.show()

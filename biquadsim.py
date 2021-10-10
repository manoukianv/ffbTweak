import matplotlib.pyplot as plt
import numpy as np
a0 = 0.9999999999999997
a1 = 1.9999999999999993
a2 = 0.9999999999999997
b1 = 1.9999999999999993
b2 = 0.9999999999999994
z1 = 0
z2 = 0
x1 = 0
x2 = 0

# First order : (y[n] = a0*x[n] + a1*x[n-1] + a2*x[n-2] – b1*y[n-1] – b2*y[n-2]
def process(i):
    global z1
    global z2
    global x1
    global x2
    out = i * a0 + z1
    z1 = i * a1 + z2 - b1 * out
    z2 = i * a2 - b2 * out

    return out

#ivals = [0,0,0,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] * 10
ivals = [1] * 1000
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

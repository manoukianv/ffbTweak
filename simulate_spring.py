import matplotlib.pyplot as plt
import numpy as np
import math

# spring scaler
maxPos = (int)(900/2)
scalePos = 32767/maxPos

# effect friction to simulate
offset = 0
deadBand = 0
negativeCoefficient = 32767
positiveCoefficient = 32767
negativeSaturation = 32767
positiveSaturation = 32767

################################### VMA Implementation ###################################
def calcConditionEffectForce_vma(metric, scale) :

    force = 0

	# Effect is only active outside deadband + offset
    if (abs(metric - offset) > deadBand):
        coefficient = negativeCoefficient
        if (metric > offset):
            coefficient = positiveCoefficient
            
        coefficient /= 0x7fff; # rescale the coefficient of effect

        #remove offset/deadband from metric to compute force
        metric = metric - (offset + (deadBand * (-1 if metric < offset else 1)) )

        force = coefficient * scale * (float)(metric)

        if force > positiveSaturation:
            force = positiveSaturation

        if (force < -negativeSaturation):
            force = -negativeSaturation

    return force

def spring_vma(i):
    force = 0
    pos = i * scalePos
    force = calcConditionEffectForce_vma(pos, 1)
    return force


################################### Default Implementation ###################################
def calcConditionEffectForce_default(metric, scale):

    force = 0
	# Effect is only active outside deadband + offset

    if (abs(metric - offset) > deadBand):
        coefficient = negativeCoefficient
        if(metric > offset):
            coefficient = positiveCoefficient
            
        force = coefficient * scale * (float)(metric)

        if force > positiveSaturation:
            force = positiveSaturation

        if (force < -negativeSaturation):
            force = -negativeSaturation
        
    return force

def spring_defaut(i):
    metric = i
    force = 0
    force = calcConditionEffectForce_default(metric, 0.0004)
    return force


######
# compute the Xaxis value : ivals for the effect, and xvals_scaled for the 450° normalized value
# and the 2 frictions scaled effect
nbval = maxPos
ivals = [0] * nbval
xvals_scaled = [0] * nbval
for i in range(nbval) :
    xvals_scaled[i] = i
    ivals[i] = i
out1 = list(map(spring_vma,ivals))

# compute the Xaxis value for the original release, without scaling and the original version
nbval = maxPos
xvals_realspeed = [0] * nbval
ivals = [0] * nbval
for i in range(nbval) :   
    xvals_realspeed[i] = i
    ivals[i] = i * scalePos
out2 = list(map(spring_defaut,ivals))

# draw
fig, ax = plt.subplots()
ax.plot(xvals_scaled, out1, xvals_realspeed, out2)
ax.legend(['spring_vma', 'spring_default'])
ax.set_xlabel('position (°)')
ax.set_ylabel('Torque')
ax.grid(True)
plt.show()


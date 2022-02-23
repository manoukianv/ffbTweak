import matplotlib.pyplot as plt
import numpy as np
import math

# Mesure Accel
# each 1ms Spd - LastSpd
# Spd = Nb                      in encoderPulse / ms
#     = Nb * 360 / 2500.0       in ° / ms
#     = Nb * 360 / 2.5          in ° / s
# So accel :
# Accel = (spd - lastSpd) * 360 / 2.5 in    in (° / s) / ms
#       = (spd - lastSpd) * 360 000 / 2.5   in ° / s²

# scaled for 1500°/s² accel on range 0..32767
maxAccel = 130000 #°/s
maxAccelInMetric = (maxAccel * 2.5) / 360000
scaleAccel = 32767/maxAccelInMetric

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

def inertia_vma(i):
    force = 0
    accel = i * scaleAccel
    force = calcConditionEffectForce_vma(accel, 1)
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

def inertia_defaut(i):
    metric = i * 4
    force = 0
    force = calcConditionEffectForce_default(metric, 0.5)
    return force


######
# compute the Xaxis value : ivals for the effect, and xvals_scaled for the 120rpm normalized value
# and the 2 frictions scaled effect
nbval = maxAccel
ivals = [0] * nbval
xvals_scaled = [0] * nbval
for i in range(nbval) :
    xvals_scaled[i] = i
    ivals[i] = (i * 2.5) / 360000
out1 = list(map(inertia_vma,ivals))

# compute the Xaxis value for the original release, without scaling and the original version
nbval = maxAccel
xvals_realspeed = [0] * nbval
ivals = [0] * nbval
for i in range(nbval) :   
    xvals_realspeed[i] = i
    ivals[i] = ((i * 2.5) / 360000)
out2 = list(map(inertia_defaut,ivals))

# draw
fig, ax = plt.subplots()
ax.plot(xvals_scaled, out1, xvals_realspeed, out2)
ax.legend(['inertia_vma', 'inertia_default'])
ax.set_xlabel('Accel (°/s²)')
ax.set_ylabel('Torque')
ax.grid(True)
plt.show()


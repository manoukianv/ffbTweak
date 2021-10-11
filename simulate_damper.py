import matplotlib.pyplot as plt
import numpy as np
import math

# scaled for 120 rpm with a 2500cpr on 0..32767 value
scaleSpeed = 64

# effect friction to simulate
offset = 0
deadBand = 0
negativeCoefficient = 32767
positiveCoefficient = 32767
negativeSaturation = 32767
positiveSaturation = 32767

################################### VMA buggy Implementation ###################################
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

def damper_vma(i):
    force = 0

    speed = i * scaleSpeed

    force = calcConditionEffectForce_vma(speed, 1)

    return force

def calcConditionEffectForce_default(metric, scale):

    force = 0
	# Effect is only active outside deadband + offset

    if (abs(metric - offset) > deadBand):
        coefficient = negativeCoefficient
        if(metric > offset):
            coefficient = positiveCoefficient
            
        force = coefficient * scale * (float)(metric)
        
    return force

def damper_defaut(i):
    metric = i * .0625
    force = 0
    force = calcConditionEffectForce_default(metric, 0.6)
    return force


######
# compute the Xaxis value : ivals for the effect, and xvals_scaled for the 120rpm normalized value
# and the 2 frictions scaled effect
nbval = (int)(32767 / scaleSpeed)
ivals = [0] * nbval
xvals_scaled = [0] * nbval
for i in range(nbval) :
    ivals[i] = i
    xvals_scaled[i] = 120 * (ivals[i] * scaleSpeed) / 32767

out1 = list(map(damper_vma,ivals))

# compute the Xaxis value for the original release, without scaling and the original version
nbval = 120
xvals_realspeed = [0] * nbval
ivals = [0] * nbval
for i in range(nbval) :   
    xvals_realspeed[i] = i
    ivals[i] = (int)((i * 2500.0) / 60000)
out2 = list(map(damper_defaut,ivals))


# draw
fig, ax = plt.subplots()
ax.plot(xvals_scaled, out1, xvals_realspeed, out2)
ax.legend(['damper_vma', 'damper_default'])
ax.set_xlabel('Speed (rpm)')
ax.set_ylabel('Torque')
ax.grid(True)
plt.show()
import matplotlib.pyplot as plt
import numpy as np
import math

scaleSpeed = 64

def friction_vma_fix(i):
    offset = 0
    deadBand = 0
    negativeCoefficient = 32767
    positiveCoefficient = 32767
    force = 0

    speed = i * scaleSpeed

    speedRampupPct = 0.08 * 32767 # sinusoidal to 30

    # Effect is only active outside deadband + offset
    if (abs(speed - offset) > deadBand):

        # remove offset/deadband from metric to compute force
        speed -= (offset + (deadBand * (-1 if speed < offset else 1)) )

        # check if speed is in the 0..x% to rampup, if is this range, apply a sinusoidale function to smooth the torque (slow near 0, slow around the X% rampup
        rampupFactor = 1.0
        if (abs (speed) < speedRampupPct):	#if speed in the range to rampup we apply a sinus curbe to ramup

            phaseRad = math.pi * ((abs (speed) / speedRampupPct) - 0.5)  # we start to compute the normalized angle (speed / normalizedSpeed@5%) and translate it of -1/2PI to translate sin on 1/2 periode
            rampupFactor = ( 1 + math.sin(phaseRad ) ) / 2;					# sin value is -1..1 range, we translate it to 0..2 and we scale it by 2

        sign = 1 if speed >= 0 else -1
        coeff = negativeCoefficient if speed < 0 else positiveCoefficient
        force = coeff * rampupFactor * sign

    return force


def friction_vma_buggy(i):
    offset = 0
    deadBand = 0
    negativeCoefficient = 32767
    positiveCoefficient = 32767
    force = 0

    speed = i * scaleSpeed

    speedRampupPct = 8 * 64 # sinusoidal to 30

    # Effect is only active outside deadband + offset
    if (abs(speed - offset) > deadBand):

        # remove offset/deadband from metric to compute force
        speed -= (offset + (deadBand * (-1 if speed < offset else 1)) )

        # check if speed is in the 0..x% to rampup, if is this range, apply a sinusoidale function to smooth the torque (slow near 0, slow around the X% rampup
        rampupFactor = 1.0
        if (abs (speed) < speedRampupPct):	#if speed in the range to rampup we apply a sinus curbe to ramup

            phaseRad = math.pi * ((abs (speed) / speedRampupPct) - 0.5)  # we start to compute the normalized angle (speed / normalizedSpeed@5%) and translate it of -1/2PI to translate sin on 1/2 periode
            rampupFactor = ( 1 + math.sin(phaseRad ) ) / 2;					# sin value is -1..1 range, we translate it to 0..2 and we scale it by 2

        sign = 1 if speed >= 0 else -1
        coeff = negativeCoefficient if speed < 0 else positiveCoefficient
        force = coeff * rampupFactor * sign

    return force

def calcConditionEffectForce(metric, gain, pos, scale):
    offset = 0
    deadBand = 0
    negativeCoefficient = 32767
    positiveCoefficient = 32767
    negativeSaturation = 32767
    positiveSaturation = 32767

    force = 0
	
    if abs(pos - offset) > deadBand:
        coefficient = negativeCoefficient
        if pos > offset:
            coefficient = positiveCoefficient
            
        force = coefficient * scale * (float)(metric)
        
        if force > positiveSaturation:
            force = positiveSaturation

        if (force < -negativeSaturation):
            force = -negativeSaturation
            
    return force

def friction_default(i):
    speed = i * .25
    force = calcConditionEffectForce(speed, 1.0 , i, .08)
    return force


######

nbval = (int)(32767 / scaleSpeed)
ivals = [0] * nbval
xvals_scaled = [0] * nbval
for i in range(nbval) :
    ivals[i] = i
    xvals_scaled[i] = 120 * (ivals[i] * scaleSpeed) / 32767

out1 = list(map(friction_vma_buggy,ivals))
out2 = list(map(friction_vma_fix,ivals))

nbval = 120
xvals_realspeed = [0] * nbval
ivals = [0] * nbval
for i in range(nbval) :   
    xvals_realspeed[i] = i
    ivals[i] = (int)((i * 2500.0) / 60000)
out3 = list(map(friction_default,ivals))

#fig, (ax1, ax2) = plt.subplots(2, 1)
fig, ax = plt.subplots()
#ax.plot(xvals_scaled, out1, xvals_scaled, out2,)
#ax.legend(['vma_buggy', 'vma_fixed'])
ax.plot(xvals_scaled, out1, xvals_scaled, out2, xvals_realspeed, out3)
ax.legend(['vma_buggy', 'vma_fixed', 'previous'])
ax.set_xlabel('Speed')
ax.set_ylabel('Torque')
ax.grid(True)
plt.show()
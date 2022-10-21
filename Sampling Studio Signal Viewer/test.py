import neurokit2 as nk  # Load the package
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy import tile, dot, sinc, newaxis
from tqdm import tqdm
import time
init = time.time()

df = pd.read_csv('data/ecg_1000hz_cleaned.csv')
df = df[df.iloc[:, 1] <= 0.5]

# ti = np.arange(1, 100, .001)
# df = pd.DataFrame(np.cos(ti))
# df['Time(s)'] = ti
# df['Amplitude(mV)'] = pd.DataFrame(np.sin(ti))

print(df)


def sample(time, amplitude, fs):
    if len(time) == len(amplitude):
        points_per_indices = int((len(time) / time[-1]) / fs)
        amplitude = amplitude[::points_per_indices]
        time = time[::points_per_indices]
        return time, amplitude


def sinc_interp(x, s, u):
    """
    Interpolates x, sampled at "s" instants
    Output y is sampled at "u" instants ("u" for "upsampled")

    from Matlab:
    http://phaseportrait.blogspot.com/2008/06/sinc-interpolation-in-matlab.html
    """

    if len(x) != len(s):
        raise Exception('x and s must be the same length')

    # Find the period
    T = s[1] - s[0]

    sincM = tile(u, (len(s), 1)) - tile(s[:, newaxis], (1, len(u)))
    y = dot(x, sinc(sincM / T))
    return y


t = np.array(df['Time(s)'])
a = np.array(df['Amplitude(mV)'])
t2, a2 = sample(t, a, 50)


def wsinterp(x, xp, fp):
    """One-dimensional Whittaker-Shannon interpolation.

    This uses the Whittaker-Shannon interpolation formula to interpolate the
    value of fp (array), which is defined over xp (array), at x (array or
    float).

    Returns the interpolated array with dimensions of x.

    """
    # shape = (nxp, nx), nxp copies of x data span axis 1
    u = np.resize(x, (len(xp), len(x)))
    # Must take transpose of u for proper broadcasting with xp.
    # shape = (nx, nxp), v(xp) data spans axis 1
    v = (xp - u.T) / (xp[1] - xp[0])
    # shape = (nx, nxp), m(v) data spans axis 1
    m = fp * np.sinc(v)
    # Sum over m(v) (axis 1)
    fp_at_x = np.sum(m, axis=1)
    return fp_at_x


print(len(t2))
fig, ax = plt.subplots(2)

ax[0].plot(t, a)
ax[0].scatter(t2, a2, c="red")
y = sinc_interp(a2, t2, t)
# y = wsinterp(t, t2, a2)
ax[1].plot(t,y)
print(time.time()-init)
plt.show()


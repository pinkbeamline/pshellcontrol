from mathutils import *
from plotutils import * 

xdata = [ 1.0,  2.0,   3.0,   4.0,   5.0,   6.0,   7.0,   8.0,   9.0,  10.0, 11.0, 12.0]
ydata = [24.0, 36.0, 66.0, 121.0, 474.0, 989.0, 357.0, 175.0,  50.0,  40.0,  30.0, 22.0]

xdata = bb1
#ydata = aa
ydata = [i/1e-9 for i in aa1]

weights = [ 1.0] * len(xdata)
p = plot(ydata, "Data" , xdata)[0]
p.setLegendVisible(True)

#(a, b, amp, com, sigma) = myfit_gaussian_linear(ydata, xdata, None, weights)
(a, b, amp, com, sigma) = fit_gaussian_exp_bkg(ydata, xdata, None, weights)

f = Gaussian(amp, com, sigma)
#gauss = [f.value(i) + a*i + b for i in xdata]
gauss = [f.value(i) + a*math.exp(-(i/b)) for i in xdata]
s = LinePlotSeries("Fit with lin back")    
p.addSeries(s)
s.setData(xdata, gauss)
error=0
for i in range(len(ydata)) : error += abs(ydata[i]-gauss[i])
print "\nFit with linear back: a: ", a , "  b: ",  b , "  amp: ",  amp, " \n com: ",  com, "  sigma: ",  sigma, "  error: ",  error
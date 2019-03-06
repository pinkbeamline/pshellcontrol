


def myfit_gaussian_linear(y, x, start_point = None, weights = None):
    """Fits data into a gaussian with linear background.
       f(x) = a * x +  b  + c * exp(-(pow((x - d), 2) / (2 * pow(e, 2)))) 

    Args:
        x(float array or list): observed points x 
        y(float array or list): observed points y 
        start_point(optional tuple of float): initial parameters (normalization, mean, sigma)
        weights(optional float array or list): weight for each observed point
    Returns:
        Tuples of gaussian parameters: (offset, normalization, mean, sigma)
    """     

    # For normalised gauss curve sigma=1/(amp*sqrt(2*pi))
    if start_point is None:
        off = min(y)  # good enough starting point for offset
        com = x[y.index(max(y))]
        amp = max(y) - off
        sigma = trapz([v-off for v in y], x) / (amp*math.sqrt(2*math.pi))                 
        start_point = [0, off, amp, com, sigma]                                       
        
    class Model(MultivariateJacobianFunction):
        def value(self, variables):
            value = ArrayRealVector(len(x))
            jacobian = Array2DRowRealMatrix(len(x), 5)        
            for i in range(len(x)):
                (a,b,c,d,e) = (variables.getEntry(0), variables.getEntry(1), variables.getEntry(2), variables.getEntry(3), variables.getEntry(4))   
                v = math.exp(-(math.pow((x[i] - d), 2) / (2 * math.pow(e, 2))))
                model = a*x[i] + b + c * v 
                value.setEntry(i, model)                                    
                jacobian.setEntry(i, 0, x[i])               # derivative with respect to p0 = a                        
                jacobian.setEntry(i, 1, 1)                  # derivative with respect to p1 = b
                jacobian.setEntry(i, 2, v)                  # derivative with respect to p2 = c            
                v2 = c*v*((x[i] - d)/math.pow(e, 2))
                jacobian.setEntry(i, 3, v2)                 # derivative with respect to p3 = d        
                jacobian.setEntry(i, 4, v2*(x[i] - d)/e )   # derivative with respect to p4 = e       
            return Pair(value, jacobian)
    
    model = Model()
    target = [v for v in y]      #the target is to have all points at the positios    
    (parameters, residuals, rms, evals, iters) = optimize_least_squares(model, target, start_point, weights)        
    return parameters


def fit_gaussian_exp_bkg(y, x, start_point = None, weights = None):
    """Fits data into a gaussian with linear background.
       f(x) = a * x +  b  + c * exp(-(pow((x - d), 2) / (2 * pow(e, 2)))) 

    Args:
        x(float array or list): observed points x 
        y(float array or list): observed points y 
        start_point(optional tuple of float): initial parameters (normalization, mean, sigma)
        weights(optional float array or list): weight for each observed point
    Returns:
        Tuples of gaussian parameters: (offset, normalization, mean, sigma)
    """     

    # For normalised gauss curve sigma=1/(amp*sqrt(2*pi))
    if start_point is None:
        off = min(y)  # good enough starting point for offset
        #com = x[y.index(max(y))]
        com = 11.9
        amp = max(y) - off
        sigma = trapz([v-off for v in y], x) / (amp*math.sqrt(2*math.pi))                 
        start_point = [0, 1, amp, com, sigma]                                       
        
    class Model(MultivariateJacobianFunction):
        def value(self, variables):
            value = ArrayRealVector(len(x))
            jacobian = Array2DRowRealMatrix(len(x), 5)        
            for i in range(len(x)):
                (a,b,c,d,e) = (variables.getEntry(0), variables.getEntry(1), variables.getEntry(2), variables.getEntry(3), variables.getEntry(4))   
                v = math.exp(-(math.pow((x[i] - d), 2) / (2 * math.pow(e, 2))))
                bkg=math.exp(-(x[i]/b))
                model = a*bkg + c * v 
                value.setEntry(i, model)                                    
                jacobian.setEntry(i, 0, bkg)               # derivative with respect to p0 = a                        
                jacobian.setEntry(i, 1, a*x[i]*bkg/math.pow(b, 2))    # derivative with respect to p1 = b
                jacobian.setEntry(i, 2, v)                  # derivative with respect to p2 = c            
                v2 = c*v*((x[i] - d)/math.pow(e, 2))
                jacobian.setEntry(i, 3, v2)                 # derivative with respect to p3 = d        
                jacobian.setEntry(i, 4, v2*(x[i] - d)/e )   # derivative with respect to p4 = e       
            return Pair(value, jacobian)
    
    model = Model()
    target = [v for v in y]      #the target is to have all points at the positios    
    (parameters, residuals, rms, evals, iters) = optimize_least_squares(model, target, start_point, weights)        
    return parameters
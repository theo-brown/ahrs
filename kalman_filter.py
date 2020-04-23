import numpy as np


class KalmanFilter:
    # For an explanation of this algorithm, see Welch & Bishop, 'An
    # Introduction to the Kalman Filter', University of North Carolina,
    # Jul 2006
    def __init__(self, x_prior, P_prior, A, B, H, Q, R):
        # State equation:
        # x_next = Ax + Bu + w
        # where:
        #    x = state
        #    u = input
        #    w ~ N(0, Q) process noise
        #
        # Measurement equation:
        # z = Hx + v
        # where:
        #    v ~ N(0, R) measurement noise
        #
        # P_prior = E[e e^T]
        # where:
        #    e = x_actual - x_prior
        self.x_prior = np.asarray(x_prior)
        self.x = self.x_prior
        self.P_prior = np.asarray(P_prior)
        self.P = self.P_prior
        self.A = np.asarray(A)
        self.B = np.asarray(B)
        self.H = np.asarray(H)
        self.Q = np.asarray(Q)
        self.R = np.asarray(R)

    def update(self, u_input, z_measurement):
        self.u = np.asarray(u_input)
        self.z = np.asarray(z_measurement)

        ## Predict step:
        # Project state forward one step
        # x_prior = Ax + Bu
        self.x_prior = np.asarray(self.A.dot(self.x) + self.B.dot(self.u))
        # Project covariance forward one step
        # P_prior = APA^T + Q
        self.P_prior = np.asarray(self.A.dot(self.P.dot(self.A.T)) + self.Q)

        ## Update step:
        # Compute Kalman gain
        # K = P_prior H^T (H P_prior H^T + R)^-1
        # We have to do the inverse differently if it's a scalar
        denominator = self.H.dot(self.P_prior.dot(self.H.T) + self.R)
        if denominator.shape is ():
            self.K = np.asarray(self.P_prior.dot(self.H.T) / denominator)
        else:
            self.K = self.P_prior.dot(self.H.T.dot(np.linalg.inv(denominator)))
        # Incorporate measurement
        # x = x_prior + K(z - H x_prior)
        self.x = self.x_prior + self.K.dot(self.z - self.H.dot(self.x_prior))
        # Obtain posterior covariance
        # P = (I - KH) P_prior
        # We have to do the I differently if we're working with scalars
        KH = self.K.dot(self.H)
        if KH.shape is ():
            self.P = np.asarray((1 - KH)*self.P_prior)
        else:
            self.P = (np.eye(KH.shape) - KH).dot(self.P_prior)

        return self.x, self.P

if __name__=='__main__':
    # This example is taken from Welch & Bishop, 'An Introduction to the
    # Kalman Filter', University of North Carolina, Jul 2006

    import matplotlib.pyplot as plt

    filt = KalmanFilter(0, 1, 1, 0, 1, 1e-5, 1)
    n = 100
    x = -0.37727
    z = np.random.normal(x, 0.1, size=n)
    x_out = np.zeros(n)
    P = np.zeros(n)

    for k in range(1, n):
        x_out[k], P[k] = filt.update(0, z[k])

    plt.figure()
    plt.plot(z, 'k+', label='Measurements')
    plt.plot(x_out, 'b-', label='Estimates')
    plt.axhline(x, color='g', label='True value')
    plt.legend()
    plt.title("Estimate of x")
    plt.xlabel('Iteration')
    plt.ylabel('Value')

    plt.figure()
    plt.plot(P[1:])
    plt.title("Estimated a priori error")
    plt.xlabel('Iteration')
    plt.ylabel('Error')

    plt.show()


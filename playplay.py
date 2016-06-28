from scipy.stats import truncnorm
from scipy.stats import norm
from scipy.stats import lognorm


rv_trunc = float(truncnorm.rvs(0.0, 100, loc=2, scale=1, size=1))
rv_norm = norm.stats(loc=2, scale=1)

norm.stats(loc=2, scale=1, moments='mvsk')
truncnorm.stats(0.0, 100.0,loc=2, scale=1, moments='mvsk')


a, b = 0, 100
truncated = truncnorm(a, b)
fig, ax = plt.subplots(1, 1)
x = np.linspace(truncnorm.ppf(0.01, a, b),
                truncnorm.ppf(0.99, a, b), 100)
ax.plot(x, truncated.pdf(x), 'k-', lw=2, label='frozen pdf')


a, b = 0, 100
x = np.linspace(-10, 10, 100)
norm = norm(2.0, 1.0)
fig, ax = plt.subplots(1, 1)
ax.plot(x, norm.pdf(x), 'k-', lw=2, label='frozen pdf')
plt.show()




def positive_normal(mean, var, n):
    l = []
    for i in range(n):
        x  = norm.rvs(loc=mean, scale=var)
        while x < 0.0:
            x = norm.rvs(loc=2, scale=1)
        l.append(x)
    return l
l = positive_normal(1.93,1,100000)
np.mean(l)

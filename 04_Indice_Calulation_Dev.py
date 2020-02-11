def indice_calculation(real_alt,simu_alt):
"""Prints "Hello World".

Returns:
    None
"""
import numpy as np

assert len(real_alt) != 0,"List of real altitude is empty. Error"
assert len(simu_alt) != 0,"List of simu altitude is empty. Error"
assert np.shape(real_alt) == np.shape(simu_alt[0]) ,"Size are uncompatible. Error"


real_alt = np.random.rand(100,100)
simu_alt = [np.random.rand(100,100),np.random.rand(100,100),np.random.rand(100,100),np.random.rand(100,100)]


somme_simus = np.zeros(np.shape(real_alt))
somme_erreurs = np.zeros(np.shape(real_alt))
sommes_erreurs_abs = np.zeros(np.shape(real_alt))

for i in range(len(simu_alt)):
    somme_simus = np.add(simu_alt[i],somme_simus)
    somme_erreurs = np.add(simu_alt[i]-real_alt,somme_erreurs)
    sommes_erreurs_abs = np.add(simu_alt[i]-real_alt,sommes_erreurs_abs)

moyenne_simus = np.divide(somme_simus,len(simu_alt))

standard_dev = np.zeros(np.shape(real_alt))
for i in range(len(simu_alt)):
       standard_dev = np.add(standard_dev,np.power(np.subtract(simu_alt[i],moyenne_simus),2))
standard_dev = np.sqrt(np.divide(standard_dev,len(simu_alt)))

moyenne_err3 = np.zeros(np.shape(real_alt))
for i in range(len(simu_alt)):
       moyenne_err3 =  np.add(np.power(np.divide((simu_alt[i]-real_alt),standard_dev),2),moyenne_err3)


moyenne_err = np.divide(somme_erreurs,len(simu_alt))
moyenne_err_abs = np.divide(sommes_erreurs_abs,len(simu_alt))


I1= np.mean(moyenne_err[standard_dev != 0])
I2= np.mean(moyenne_err_abs[standard_dev != 0])
I3 = np.sum(moyenne_err3/(len(simu_alt*20)))

pro = [I1, I2, I3]

return pro

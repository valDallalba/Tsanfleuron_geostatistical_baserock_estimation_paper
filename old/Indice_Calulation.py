def indice_calculation(real_alt,simu_alt,sim_type):
"""Calculate the quality indices.

Input :
        - NP.ARRAY of the real altitudes
        - LIST of N NP.ARRAY of the N simulated altitudes
        -
Returns:
    A list containing 5 indices.
    I1 : mean of the error.
    I2 : mean of the absolute Error
    I3 : np.sum(moyenne_err3/(len(simu_alt*20)))
    I4 : np array of the per point average
    I5 : np array of the per point standart deviation

    note : The conditioning points are removed for the calculus of I1, I2, and I3
"""
        import numpy as np

        assert len(real_alt) != 0,"List of real altitude is empty. Error"
        assert len(simu_alt) != 0,"List of simu altitude is empty. Error"
        assert np.shape(real_alt) == np.shape(simu_alt[0]) ,"Size are uncompatible. Error"


    if sim_type == 'krig'
        standard_dev = simu_alt[1]
        simu_alt = simu_alt[0]
        
        N = moyenne_simus.shape[0]*moyenne_simus.shape[1]*1

        
        I1= np.mean((simu_alt[standard_dev != 0] - real_alt[standard_dev != 0]))
        I2= np.mean(np.abs(simu_alt[standard_dev != 0] -real_alt[standard_dev != 0]))
        I3 = np.sum(moyenne_err3/(N))

        pro = [I1, I2, I3, moyenne_simus, standard_dev]


        
        
    if sime_type == 'mps'

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
         
        N = standard_dev[standard_dev != 0].shape[0]*standard_dev[standard_dev != 0].shape[1]*len(simu_alt)

        I1= np.mean(moyenne_err[standard_dev != 0])
        I2= np.mean(moyenne_err_abs[standard_dev != 0])
        I3 = np.sum(moyenne_err3/(N)))

        pro = [I1, I2, I3, moyenne_simus, standard_dev]

return pro

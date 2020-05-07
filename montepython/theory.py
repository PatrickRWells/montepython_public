import sys
import io_mp
import numpy as np



def initialize_theory(classy_path=''):

        '''
        Initializes the theory code (currently only Class), first checking to make sure it can be imported

        Params
        ----------

        classy_path: string
            additional path to search for Class, provided by intialiser

        Returns
        --------------
        cosmo: Wraper for classy. Should behave identical to Class in most cases

        '''

        # Inserting the previously found path into the list of folders to
        # search for python modules.

        sys.path.insert(1, classy_path)
        try:
            from classy import Class
        except ImportError:
            raise io_mp.MissingLibraryError(
                "You must have compiled the classy.pyx file. Please go to " +
                "/path/to/class/python and run the command\n " +
                "python setup.py build")

        cosmo = Theory(Class)
        return cosmo

def Theory(base):

    class Theory(base):
        def __init__(self):
            super().__init__()
            self.split = False
            self.split_ell = -1
            self.low_params = {}
            self.high_params = {}
            self.high_spectra = {}
            self.low_spectra = {}

        def set_split(self, split_ell):
            self.split = True
            self.split_ell = split_ell
        def set(self, params):
            if 'split' in params.keys():
                params.pop('split')
            if self.split:
                for key, val in params.items():
                    if 'high' in key:
                        self.high_params.update({'_'.join(key.split('_')[:-1]): val})
                    elif 'low' in key:
                        self.low_params.update({'_'.join(key.split('_')[:-1]): val})
                    else:
                        self.low_params.update({key: val})
                        self.high_params.update({key: val})
            else:
                super().set(params)

        def compute(self, level):

            if self.split:
                super().set(self.low_params)
                super().compute(level)
                self.low_spectra.update({'lensed': super().lensed_cl(), 'raw': super().raw_cl()})
                super().struct_cleanup()
                super().set(self.high_params)
                super().compute(level)
                self.high_spectra.update({'lensed': super().lensed_cl(), 'raw': super().raw_cl()})
            else:
                super().compute(level)
        def lensed_cl(self, lmax):
            if self.split:
                cls = {}
                for key, spectra in self.low_spectra['lensed'].items():
                    cls.update({key: np.append(spectra[:self.split_ell], self.high_spectra['lensed'][key][self.split_ell:])})
                return cls
            else:
                return super().lensed_cl(lmax)
        def raw_cl(self, lmax):
            if self.split:
                cls = {}
                for key, spectra in self.low_spectra['raw'].items():
                    cls.update({key: np.append(spectra[:self.split_ell], self.high_spectra['raw'][key][self.split_ell:])})
                return cls
            else:
                return super().raw_cl(lmax)

        def struct_cleanup(self):
            if self.split:
                self.low_params = {}
                self.high_params = {}
                self.high_spectra = {}
                self.low_spectra = {}
                
            super().struct_cleanup()

    return Theory()

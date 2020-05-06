import sys
import io_mp



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

        def set_split(self, split_ell):
            self.split = True
            self.split_ell = split_ell
        def set(self, params):
            if self.split:
                for key, val in params.items():
                    if 'high' in key:
                        self.high_params.update({'_'.join(key.split('_')[:-1]): val})
                    elif 'low' in key:
                        self.low_params.update({'_'.join(key.split('_')[:-1]): val})
                    else:
                        self.low_params.update({key: val})
                        self.high_params.update({key: val})

                print(self.low_params)
                print(self.high_params)
                print("Don't know how to handle split params yet!")
                exit()
            else:
                super().set(params)
        def compute(self, spectra):
            if self.split:
                print("Don't know how to handle split params yet!")
            else:
                super().compute(spectra)

    return Theory()
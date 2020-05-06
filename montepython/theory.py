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
    
    return Theory()
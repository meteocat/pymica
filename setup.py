'''Standard setup.py file to install the library.
Run python setup.py --help for options
'''
import datetime
import numpy
import setuptools

version = "0.0"
release = "0.0.1"
name = "pymica"

now = datetime.datetime.now()

try:
    from Cython.Build import cythonize
    # If called before, it fails:
    # https://github.com/pypa/setuptools/issues/309#issuecomment-202915959
    from distutils.extension import Extension
except ImportError:
    from distutils.extension import Extension
    has_cython = False
    ext_extention = 'c'
else:
    has_cython = True
    ext_extention = 'pyx'

ext_modules = [Extension("interpolation.inverse_distance",
                         ['interpolation/inverse_distance.' + ext_extention], include_dirs=[numpy.get_include()]),
               Extension("interpolation.inverse_distance_3d",
                         ['interpolation/inverse_distance_3d.' + ext_extention], include_dirs=[numpy.get_include()])]

for e in ext_modules:
    e.cython_directives = {"embedsignature": True}

if has_cython is True:
    ext_modules = cythonize(ext_modules)

setuptools.setup(
    name=name,
    version=version,
    description="pyMICA, Meteorological variable Interpolation based" +
    "on Clustered Analysis",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=['cython', 'numpy', 'scipy', 'scikit-learn'],
    scripts=['bin/pymica_distance_to_sea_calculator',
             'bin/pymica_create_clusters_file',
             'bin/pymica_generate_clusters'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'],
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'copyright': ('setup.py',
                          str(now.year)+",Servei Meteorològic de Catalunya")
            }
        },
    ext_modules=ext_modules
)

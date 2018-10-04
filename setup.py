import setuptools
import datetime

version = "0.0"
release = "0.0.1"
name = "pyMICA"

now = datetime.datetime.now()

setuptools.setup(
    name=name,
    version=version,
    description="pyMICA, Meteorological variable Interpolation based on Clustered Analysis" +
    "on clustered analysis",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'scipy', 'scikit-learn'],
    scripts=['bin/distance_to_coast_calculator'],
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
            }},

)

Scripts
=======

PyMICA installs a bunch of scripts to work with the library. They should be installed with any of the installation options, and are stored under the *bin* directory.

pymica_run
##########

Creates a GeoTIFF file with an interpolated variable from station data.

::

    positional arguments:
    data_file    The file path with the station data
    out_file     The out GeoTIFF file
    config_file  The configuration file

pymica_generate_clusters
########################

Creates clusters from data locations to be used by PyMICA

::

    positional arguments:
    locations_file  The file path with the locations
    num_clusters    The number of clusters to generate

pymica_distance_to_sea_calculator
#################################

Calculates the distance to the coast file from the shore geometry.

::

    positional arguments:
    shore_file            The GeoJSON file path with the shore line
    out_file              The output file name

    optional arguments:
    -h, --help            show this help message and exit
    --epsg EPSG           The output file projection EPSG code. By default,
                            25831
    --size x_size y_size  The output file size in pixels
    --origin x y          The output file origin coordinates
    --pixel_size pixel_x pixel_y
                            The output file pixel size
    --verbose VERBOSE     Output progress

pymica_create_clusters_file
###########################

Creates the cluster files to be used by PyMICA.

::

    positional arguments:
    clusters_file         The GeoJSON file path with the clusters definition
    out_file              The output file name

    optional arguments:
    -h, --help            show this help message and exit
    --epsg EPSG           The output file projection EPSG code. By default,
                            25831
    --size x_size y_size  The output file size in pixels
    --origin x y          The output file origin coordinates
    --pixel_size pixel_x pixel_y
                            The output file pixel size
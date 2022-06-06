from cioos_data_transform.OceanNcFile import CurNcFile

# from cioos_data_transform.OceanNcVar import OceanNcVar
from cioos_data_transform.utils import is_in
import numpy as np

import convert


def write_cur_ncfile(filename, curcls, config={}):
    """
    use data and methods in curcls object to write the current meter data into a netcdf file
    authors:    Pramod Thupaki pramod.thupaki@hakai.org,
                Hana Hourston hana.hourston@dfo-mpo.gc.ca
    inputs:
        filename: output file name to be created in netcdf format
        curcls: cur object. includes methods to read IOS format and stores data
    output:
        NONE
    """
    # Correct filename to lowercase CUR
    if ".CUR" in filename:
        filename = ".cur".join(filename.rsplit(".CUR", 1))

    ncfile = CurNcFile()
    # write global attributes
    config["featureType"] = "timeSeries"
    convert.prepare_ncfile(ncfile, curcls, config, is_current=True)

    convert.convert_channels(ncfile, curcls, ("time",), is_current=True)

    # attach variables to ncfileclass and call method to write netcdf file
    ncfile.write_ncfile(filename)
    print("Finished writing file:", filename, "\n")
    # release_memory(out)
    return 1

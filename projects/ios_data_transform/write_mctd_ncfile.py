from cioos_data_transform.OceanNcFile import MCtdNcFile

# from cioos_data_transform.OceanNcVar import OceanNcVar
from cioos_data_transform.utils import is_in

import convert


def write_mctd_ncfile(filename, ctdcls, config={}):
    """
    use data and methods in ctdcls object to write the CTD data into a netcdf file
    author: Pramod Thupaki pramod.thupaki@hakai.org
    inputs:
        filename: output file name to be created in netcdf format
        ctdcls: ctd object. includes methods to read IOS format and stores data
    output:
        NONE
    """
    date_format = "%Y-%m-%d %H:%M:%S%Z"
    ncfile = MCtdNcFile()
    # write global attributes
    global_attrs = {}
    config["featureType"] = "timeSeries"
    convert.prepare_ncfile(ncfile, ctdcls, config)

    convert.convert_channels(ncfile, ctdcls, ("time",))

    # attach variables to ncfileclass and call method to write netcdf file
    ncfile.write_ncfile(filename)
    print("Finished writing file:", filename, "\n")
    # release_memory(out)
    return 1

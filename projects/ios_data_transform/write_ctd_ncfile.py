from datetime import datetime
from pytz import timezone
import math
import json
from cioos_data_transform.OceanNcFile import CtdNcFile

# from cioos_data_transform.OceanNcVar import OceanNcVar
from cioos_data_transform.utils import is_in


def write_ctd_ncfile(filename, ctdcls, config={}):
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
    ncfile = CtdNcFile()
    # write global attributes
    global_attrs = {}
    ncfile.global_attrs = global_attrs

    global_attrs["featureType"] = "profile"
    global_attrs["summary"] = config.get("summary")
    global_attrs["title"] = config.get("title")
    global_attrs["institution"] = config.get("institution")
    global_attrs["infoUrl"] = config.get("infoUrl")
    global_attrs["description"] = config.get("description")
    global_attrs["keywords"] = config.get("keywords")
    global_attrs["acknowledgement"] = config.get("acknowledgement")
    global_attrs["naming_authority"] = "COARDS"
    global_attrs["comment"] = config.get("comment")
    global_attrs["creator_name"] = config.get("creator_name")
    global_attrs["creator_email"] = config.get("creator_email")
    global_attrs["creator_url"] = config.get("creator_url")
    global_attrs["license"] = config.get("license")
    global_attrs["keywords"] = config.get("keywords")
    global_attrs["keywords_vocabulary"] = config.get("keywords_vocabulary")
    global_attrs["Conventions"] = config.get("Conventions")
    global_attrs["cdm_data_type"] = "Profile"
    global_attrs["cdm_profile_variables"] = "profile, filename"
    global_attrs["date_created"] = datetime.now(timezone("UTC")).strftime(date_format)
    global_attrs["processing_level"] = config.get("processing_level")
    global_attrs["time_coverage_duration"] = 0.0
    global_attrs["time_coverage_resolution"] = "n/a"
    global_attrs["standard_name_vocabulary"] = config.get("standard_name_vocabulary")

    # write full original header, as json dictionary
    global_attrs["header"] = json.dumps(
        ctdcls.get_complete_header(), ensure_ascii=False, indent=False
    )
    # initcreate dimension variable
    global_attrs["nrec"] = int(ctdcls.file.number_of_records)
    # add filename as string variable and as ncfile global attribute
    global_attrs["filename"] = ctdcls.filename.split("/")[-1]
    ncfile.add_var("str_id", "filename", None, ctdcls.filename.split("/")[-1])

    # add administration variables
    country = ctdcls.administration.country.strip()
    ncfile.add_var("str_id", "country", None, country)
    global_attrs["country"] = country

    if ctdcls.administration.mission != "n/a":
        mission_id = ctdcls.administration.mission.strip()
    else:
        mission_id = ctdcls.administration.cruise.strip()
    buf = mission_id.split("-")
    mission_id = "{:04d}-{:03d}".format(int(buf[0]), int(buf[1]))
    global_attrs["mission"] = mission_id
    ncfile.add_var("str_id", "mission_id", None, mission_id)

    scientist = ctdcls.administration.scientist.strip()
    global_attrs["scientist"] = scientist
    ncfile.add_var("str_id", "scientist", None, scientist)

    project = ctdcls.administration.project.strip()
    global_attrs["project"] = project
    ncfile.add_var("str_id", "project", None, project)

    agency = ctdcls.administration.agency.strip()
    global_attrs["agency"] = agency
    ncfile.add_var("str_id", "agency", None, agency)

    platform = ctdcls.administration.platform.strip()
    global_attrs["platform"] = platform
    ncfile.add_var("str_id", "platform", None, platform)

    # add instrument type
    if ctdcls.instrument.type != "n/a":
        ncfile.add_var(
            "str_id",
            "instrument_type",
            None,
            ctdcls.instrument.type.strip(),
        )
    if ctdcls.instrument.model != "n/a":
        ncfile.add_var(
            "str_id",
            "instrument_model",
            None,
            ctdcls.instrument.model.strip(),
        )
    if ctdcls.instrument.serial_number != "n/a":
        ncfile.add_var(
            "str_id",
            "instrument_serial_number",
            None,
            ctdcls.instrument.serial_number.strip(),
        )
    # add locations variables
    ncfile.add_var(
        "lat",
        "latitude",
        "degrees_north",
        ctdcls.location.latitude,
    )
    global_attrs["geospatial_lat_min"] = ctdcls.location.latitude
    global_attrs["geospatial_lat_max"] = ctdcls.location.latitude
    ncfile.add_var(
        "lon",
        "longitude",
        "degrees_east",
        ctdcls.location.longitude,
    )
    global_attrs["geospatial_lon_min"] = ctdcls.location.longitude
    global_attrs["geospatial_lon_max"] = ctdcls.location.longitude
    global_attrs["geospatial_bounds"] = "POINT ({}, {})".format(
        ctdcls.location.longitude, ctdcls.location.latitude
    )
    ncfile.add_var("str_id", "geographic_area", None, ctdcls.geo_code)
    if ctdcls.location.event_number > 0:
        event_id = "{:04d}".format(ctdcls.location.event_number)
    else:
        print("Event number not found!" + ctdcls.filename)
        try:
            event_id = ctdcls.filename.split("-")[-1][:-4]
            print("Guessing ...", ctdcls.filename, "; event id = ", event_id)
        except Exception as e:
            print('Unable to guess event_id from file name. Using "0000" !')
            event_id = "0000"

    ncfile.add_var("str_id", "event_number", None, event_id)
    # add time variable
    profile_id = "{:04d}-{:03d}-{}".format(int(buf[0]), int(buf[1]), event_id.zfill(4))
    # print(profile_id)
    ncfile.add_var(
        "profile",
        "profile",
        None,
        profile_id,
        attributes={"cf_role": "profile_id"},
    )
    global_attrs["id"] = profile_id

    ncfile.add_var("time", "time", None, [ctdcls.file.start_time])
    global_attrs["time_coverage_start"] = ctdcls.file.start_time.strftime(date_format)
    global_attrs["time_coverage_end"] = ctdcls.file.start_time.strftime(date_format)
    # go through channels and add each variable depending on type
    for i, channel in enumerate(ctdcls.file.channels):
        try:
            null_value = ctdcls.file.channel_details[i].pad
        except Exception as e:
            if not math.isnan(ctdcls.file.pad):
                null_value = ctdcls.file.pad
                print(
                    "Channel Details missing. Setting Pad value to: ",
                    null_value,
                )
            else:
                print("Channel Details missing. Setting Pad value to ' ' ...")
                null_value = "' '"
        data = [row[i] for row in ctdcls.data]
        if is_in(["depth"], channel.name) and not is_in(["nominal"], channel.name):
            ncfile.add_var(
                "depth",
                "depth",
                channel.units,
                data,
                ("z"),
                null_value,
                attributes={"featureType": "profile"},
            )
        elif is_in(["depth"], channel.name) and is_in(["nominal"], channel.name):
            ncfile.add_var(
                "depth",
                "depth_nominal",
                channel.units,
                data,
                ("z"),
                null_value,
                attributes={"featureType": "profile"},
            )
        elif is_in(["pressure"], channel.name):
            ncfile.add_var(
                "pressure",
                "pressure",
                channel.units,
                data,
                ("z"),
                null_value,
                attributes={"featureType": "profile"},
            )
        elif is_in(["temperature"], channel.name) and not is_in(
            ["flag", "rinko", "bottle"], channel.name
        ):
            ncfile.add_var(
                "temperature",
                channel.name,
                channel.units,
                data,
                ("z"),
                null_value,
                attributes={"featureType": "profile"},
            )
        elif is_in(["salinity"], channel.name) and not is_in(["flag"], channel.name):
            ncfile.add_var(
                "salinity",
                channel.name,
                channel.units,
                data,
                ("z"),
                null_value,
                attributes={"featureType": "profile"},
            )
        elif is_in(["oxygen"], channel.name) and not is_in(
            [
                "flag",
                "bottle",
                "rinko",
                "temperature",
                "current",
                "isotope",
                "saturation",
                "voltage",
            ],
            channel.name,
        ):
            ncfile.add_var(
                "oxygen",
                channel.name,
                channel.units,
                data,
                ("z"),
                null_value,
                attributes={"featureType": "profile"},
            )
        elif is_in(["conductivity"], channel.name):
            ncfile.add_var(
                "conductivity",
                channel.name,
                channel.units,
                data,
                ("z"),
                null_value,
                attributes={"featureType": "profile"},
            )
        #     Nutrients in bottle files
        elif is_in(
            ["nitrate_plus_nitrite", "silicate", "phosphate"], channel.name
        ) and not is_in(["flag"], channel.name):
            try:
                ncfile.add_var(
                    "nutrient",
                    channel.name,
                    channel.units,
                    data,
                    ("z"),
                    null_value,
                    attributes={"featureType": "profile"},
                )
            except Exception as e:
                print(e)
        #  other
        elif (
            is_in(
                [
                    "chlorophyll:extracted",
                    "fluorescence",
                    "transmissivity",
                    "ammonium",
                    "speed:sound",
                    "ph:",
                    "par",
                    "turbidity:seapoint",
                ],
                channel.name,
            )
            or channel.name.lower() == "ph"
        ) and not is_in(["flag"], channel.name):
            try:
                ncfile.add_var(
                    "other",
                    channel.name,
                    channel.units,
                    data,
                    ("z"),
                    null_value,
                    attributes={"featureType": "profile"},
                )
            except Exception as e:
                print(e)
        else:
            if not is_in(["record", "sample", "date", "time"], channel.name):
                print(
                    channel.name,
                    channel.units,
                    "not transferred to netcdf file !",
                )
            # raise Exception('not found !!')

    # attach variables to ncfileclass and call method to write netcdf file
    ncfile.write_ncfile(filename)
    print("Finished writing file:", filename, "\n")
    # release_memory(out)
    return 1

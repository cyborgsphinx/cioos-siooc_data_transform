import datetime
import json
import logging
import math
from pytz import timezone

from cioos_data_transform.utils import is_in
import numpy as np

def prepare_ncfile(ncfile, shell, config, is_current=False):
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
    global_attrs = {}
    ncfile.global_attrs = global_attrs

    feature_type = config.get("featureType")
    global_attrs["featureType"] = feature_type
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

    if feature_type is not None and feature_type == "profile":
        global_attrs["cdm_data_type"] = "Profile"
        global_attrs["cdm_profile_variables"] = "profile, filename"
        global_attrs["time_coverage_duration"] = 0.0
        global_attrs["time_coverage_resolution"] = "n/a"
    elif feature_type is not None and feature_type == "timeSeries":
        global_attrs["cdm_data_type"] = "TimeSeries"
        global_attrs["cdm_timeseries_variables"] = "profile"
    else:
        logging.warn("Unknown feature type: {}".format(feature_type))

    global_attrs["date_created"] = datetime.datetime.now(timezone("UTC")).strftime(date_format)
    global_attrs["processing_level"] = config.get("processing_level")
    global_attrs["standard_name_vocabulary"] = config.get("standard_name_vocabulary")

    global_attrs["header"] = json.dumps(shell.get_complete_header(), ensure_ascii=False, indent=False)

    global_attrs["nrec"] = shell.file.number_of_records

    original_filename = shell.filename.split("/")[-1]
    global_attrs["filename"] = original_filename
    ncfile.add_var("str_id", "filename", None, original_filename)

    country = shell.administration.country.strip()
    global_attrs["country"] = country
    ncfile.add_var("str_id", "country", None, country)

    if shell.administration.mission != "n/a":
        mission_id = shell.administration.mission.strip()
    elif feature_type == "profile":
        mission_id = shell.administration.cruise.strip()
    elif shell.deployment is not None and shell.deployment.mission != "n/a":
        mission_id = shell.deployment.mission
    else:
        logging.warn("Mission ID not available in {}".format(shell.filename))
        mission_id = "{:04d}-000".format(shell.file.start_time.year)

    buf = mission_id.split("-")
    mission_id = "{:04d}-{:03d}".format(int(buf[0]), int(buf[1]))
    global_attrs["mission"] = mission_id
    if is_current:
        ncfile.add_var("str_id", "deployment_mission_id", None, mission_id)
    else:
        ncfile.add_var("str_id", "mission_id", None, mission_id)

    if shell.location.event_number > 0:
        event_id = shell.location.event_number
    else:
        logging.warn("Event number not found in {}".format(shell.filename))
        event_id = 0
    ncfile.add_var("str_id", "event_number", None, "{:04}".format(event_id))

    profile_attributes = {}
    if feature_type == "profile":
        profile_attributes["cf_role"] = "profile_id"
    elif not is_current:
        profile_attributes["cf_role"] = "timeSeries_id"
    profile_id = "{}-{:04d}".format(mission_id, event_id)
    global_attrs["id"] = profile_id
    ncfile.add_var("profile", "profile", None, profile_id, attributes=profile_attributes)

    scientist = shell.administration.scientist.strip()
    global_attrs["scientist"] = scientist
    ncfile.add_var("str_id", "scientist", None, scientist)

    project = shell.administration.project.strip()
    global_attrs["project"] = project
    ncfile.add_var("str_id", "project", None, project)

    agency = shell.administration.agency.strip()
    global_attrs["agency"] = agency
    ncfile.add_var("str_id", "agency", None, agency)

    platform = shell.administration.platform.strip()
    global_attrs["platform"] = platform
    ncfile.add_var("str_id", "platform", None, platform)

    if shell.instrument is not None:
        if shell.instrument.type != "n/a":
            ncfile.add_var(
                "str_id",
                "instrument_type",
                None,
                shell.instrument.type.strip(),
            )
        if shell.instrument.model != "n/a":
            ncfile.add_var(
                "str_id",
                "instrument_model",
                None,
                shell.instrument.model.strip(),
            )
        if shell.instrument.serial_number != "n/a":
            ncfile.add_var(
                "str_id",
                "instrument_serial_number",
                None,
                shell.instrument.serial_number.strip(),
            )
        if feature_type == "timeSeries" and shell.instrument.depth != "n/a":
            ncfile.add_var(
                "instr_depth",
                "instrument_depth",
                None,
                shell.instrument.depth,
            )

    ncfile.add_var(
        "lat",
        "latitude",
        "degrees_north",
        shell.location.latitude,
    )
    global_attrs["geospatial_lat_min"] = shell.location.latitude
    global_attrs["geospatial_lat_max"] = shell.location.latitude
    ncfile.add_var(
        "lon",
        "longitude",
        "degrees_east",
        shell.location.longitude,
    )
    global_attrs["geospatial_lon_min"] = shell.location.longitude
    global_attrs["geospatial_lon_max"] = shell.location.longitude
    global_attrs["geospatial_bounds"] = "POINT ({}, {})".format(
        shell.location.longitude, shell.location.latitude
    )

    ncfile.add_var("str_id", "geographic_area", None, shell.geo_code)

    global_attrs["time_coverage_start"] = shell.file.start_time.strftime(date_format)
    global_attrs["time_coverage_end"] = shell.file.start_time.strftime(date_format)

    if feature_type == "timeSeries":
        obs_time = shell.get_obs_time()
        global_attrs["time_coverage_duration"] = str(obs_time[-1] - obs_time[0])
        global_attrs["time_coverage_resolution"] = str(obs_time[1] - obs_time[0])
        ncfile.add_var("time", "time", None, obs_time, vardim=("time"))
        global_attrs["time_coverage_start"] = obs_time[0].strftime(date_format)
        global_attrs["time_coverage_end"] = obs_time[-1].strftime(date_format)
    else:
        ncfile.add_var("time", "time", None, [shell.file.start_time])


def add_ne_speed(speed, direction):
    """
    calculate the North and East speed components of current meter speed and add these variables to
    the output netCDF file
    author: Hana Hourston hana.hourston@dfo-mpo.gc.ca
    input:
        - speed: speed data
        - direction: direction(to) data (measured clockwise from North)
    output:
        None
    """
    east_comp = np.zeros(len(speed), dtype="float32")
    north_comp = np.zeros(len(speed), dtype="float32")

    for i in range(len(speed)):
        east_comp[i] = np.round(
            speed[i] * np.cos(np.deg2rad(90 - direction[i])), decimals=3
        )
        north_comp[i] = np.round(
            speed[i] * np.sin(np.deg2rad(90 - direction[i])), decimals=3
        )

    return east_comp, north_comp


def convert_channels(ncfile, shell, dimensions, is_current=False):
    # flags used for current files
    flag_ne_speed = 0  # flag to determine if north and east speed components are vars in the .cur file
    flag_cndc = 0  # flag to check for conductivity
    flag_cndc_ratio = 0  # flag to check for conductivity ratio
    temp_count = 0  # counter for the number of "Temperature" channels

    for i, channel in enumerate(shell.file.channels):
        try:
            null_value = shell.file.channel_details[i].pad
        except Exception as e:
            if not math.isnan(shell.file.pad):
                null_value = shell.file.pad
                logging.warn(
                    f"Channel Details missing. Setting Pad value to: {null_value}"
                )
            else:
                logging.warn("Channel Details missing. Setting Pad value to ' '")
                null_value = "' '"
        data = [row[i] for row in shell.data]

        if is_in(["depth"], channel.name) and not is_in(["nominal"], channel.name):
            ncfile.add_var(
                "depth",
                "depth",
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["depth"], channel.name) and is_in(["nominal"], channel.name):
            ncfile.add_var(
                "depth",
                "depth_nominal",
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["pressure"], channel.name):
            ncfile.add_var(
                "pressure",
                "pressure",
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["temperature:low_res"], channel.name):
            ncfile.add_var(
                "temperature:cur:low_res",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["temperature:high_res"], channel.name):
            ncfile.add_var(
                "temperature:cur:high_res",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["temperature"], channel.name) and not is_in(
            ["flag", "rinko"], channel.name
        ):
            if is_current:
                temp_count += 1
                if temp_count == 1:
                    ncfile.add_var(
                        "temperature:cur",
                        channel.name,
                        channel.units,
                        data,
                        dimensions,
                        null_value,
                        attributes={"featureType": ncfile.global_attrs["featureType"]},
                    )
                elif temp_count == 2:
                    ncfile.add_var(
                        "temperature:cur:high_res",
                        channel.name,
                        channel.units,
                        data,
                        dimensions,
                        null_value,
                        attributes={"featureType": ncfile.global_attrs["featureType"]},
                    )
            else:
                ncfile.add_var(
                    "temperature",
                    channel.name,
                    channel.units,
                    data,
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
                )

        elif is_in(["salinity"], channel.name) and not is_in(["flag"], channel.name):
            if is_current:
                ncfile.add_var(
                    "salinity:cur",
                    channel.name,
                    channel.units,
                    data,
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
                )

            else:
                ncfile.add_var(
                    "salinity",
                    channel.name,
                    channel.units,
                    data,
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
                )

        elif is_in(["oxygen"], channel.name) and not is_in(
            [
                "flag",
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
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif all(is_in([name], channel.name) for name in ["oxygen", "saturation"]) and not is_in(
            [
                "flag",
                "temperature",
                "current",
                "isotope",
                "voltage",
            ],
            channel.name
        ):
            ncfile.add_var(
                "oxygen saturation",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif all(is_in([name], channel.name) for name in ["oxygen", "isotope"]) and not is_in(
            [
                "flag",
            ],
            channel.name
        ):
            ncfile.add_var(
                "isotope",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["conductivity", "conductance"], channel.name):
            if not is_current:
                ncfile.add_var(
                    "conductivity",
                    channel.name,
                    channel.units,
                    data,
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
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
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
                )
            except Exception as e:
                logging.error(e)

        elif is_in(["speed:east", "ew_comp"], channel.name):
            flag_ne_speed += 1
            ncfile.add_var(
                "speed:east",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["speed:north", "ns_comp"], channel.name):
            ncfile.add_var(
                "speed:north",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["speed:up"], channel.name):
            ncfile.add_var(
                "speed:up",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["amplitude:beam1"], channel.name):
            ncfile.add_var(
                "amplitude:beam1",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["amplitude:beam2"], channel.name):
            ncfile.add_var(
                "amplitude:beam2",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["amplitude:beam3"], channel.name):
            ncfile.add_var(
                "amplitude:beam3",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["speed:sound"], channel.name) and not is_in(
            ["speed:sound:1", "speed:sound:2"], channel.name
        ):
            ncfile.add_var(
                "speed:sound",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["speed:sound:1"], channel.name):
            ncfile.add_var(
                "speed:sound:1",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["speed:sound:2"], channel.name):
            ncfile.add_var(
                "speed:sound:2",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["heading"], channel.name):
            ncfile.add_var(
                "heading",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["pitch"], channel.name):
            ncfile.add_var(
                "pitch",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["roll"], channel.name):
            ncfile.add_var(
                "roll",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["speed"], channel.name):
            ncfile.add_var(
                "speed",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )
            index_speed = i

        elif is_in(["direction:geog(to)", "direction:current"], channel.name):
            ncfile.add_var(
                "direction:geog(to)",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )
            index_direction = i

        elif is_in(["density"], channel.name):
            ncfile.add_var(
                "density",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["sigma-t"], channel.name):
            ncfile.add_var(
                "sigma-t",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["chlorofluorocarbon"], channel.name) and not is_in(["flag"], channel.name):
            ncfile.add_var(
                "chlorofluorocarbon",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["transmissivity"], channel.name):
            ncfile.add_var(
                "other",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["alkalinity"], channel.name) and not is_in(["flag"], channel.name):
            ncfile.add_var(
                "other",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["carbon:dissolved"], channel.name) and not is_in(["flag"], channel.name):
            ncfile.add_var(
                "other",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["carbon:isotope"], channel.name) and not is_in(["flag"], channel.name):
            ncfile.add_var(
                "isotope",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["phytoplankton:volume"], channel.name) and not is_in(["flag"], channel.name):
            ncfile.add_var(
                "other",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        #  other
        elif (
            is_in(
                [
                    "chlorophyll:extracted",
                    "chlorophyll_plus_phaeo-pigment:extracted",
                    "fluorescence",
                    "ammonium",
                    "ph:",
                    "par",
                    "turbidity:seapoint",
                    "ethane",
                    "propane",
                    "ethylene",
                ],
                channel.name,
            )
            or channel.name.lower() == "ph"
            # methane in water body not yet supported
        ) and not is_in(["flag"], channel.name):
            try:
                ncfile.add_var(
                    "other",
                    channel.name,
                    channel.units,
                    data,
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
                )
            except Exception as e:
                logging.error(e)

        elif is_in(["flag"], channel.name):
            ncfile.add_var(
                "flag",
                channel.name,
                channel.units,
                data,
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        else:
            if not is_in(["record", "sample", "date", "time"], channel.name):
                logging.warn(
                    f"{channel.name} ({channel.units}) not transferred to netcdf file !"
                )

    if is_current:
        # Calculate North and East components of speed if missing
        try:
            if flag_ne_speed == 0:
                if isinstance(shell.data[0][index_speed], bytes) and isinstance(
                    shell.data[0][index_direction], bytes
                ):
                    speed_decoded = np.array(
                        [float(row[index_speed].decode("ascii")) for row in shell.data]
                    )
                    direction_decoded = np.array(
                        [float(row[index_direction].decode("ascii")) for row in shell.data]
                    )
                    speed_east, speed_north = add_ne_speed(speed_decoded, direction_decoded)
                else:
                    speed_east, speed_north = add_ne_speed(
                        [row[index_speed] for row in shell.data],
                        [row[index_direction] for row in shell.data],
                    )

                null_value = "' '"
                ncfile.add_var(
                    "speed:east",
                    "Speed:East",
                    shell.file.channels[index_speed].units,
                    speed_east,
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
                )

                ncfile.add_var(
                    "speed:north",
                    "Speed:North",
                    shell.file.channels[index_speed].units,
                    speed_north,
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
                )
                logging.info("Calculated east and north speed components ...")
        except UnboundLocalError as e:
            logging.warn("Speed and speed component channels not found in file !")

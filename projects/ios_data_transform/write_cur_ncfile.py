from datetime import datetime
from pytz import timezone
import math
import json
from cioos_data_transform.OceanNcFile import CurNcFile

# from cioos_data_transform.OceanNcVar import OceanNcVar
from cioos_data_transform.utils import is_in
import numpy as np


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

    date_format = "%Y-%m-%d %H:%M:%S%Z"
    ncfile = CurNcFile()
    # write global attributes
    global_attrs = {}
    ncfile.global_attrs = global_attrs

    global_attrs["featureType"] = "timeSeries"

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
    global_attrs["cdm_data_type"] = "TimeSeries"
    global_attrs["cdm_timeseries_variables"] = "profile"
    global_attrs["date_created"] = datetime.now(timezone("UTC")).strftime(date_format)
    global_attrs["processing_level"] = config.get("processing_level")
    global_attrs["standard_name_vocabulary"] = config.get("standard_name_vocabulary")
    # write full original header, as json dictionary
    global_attrs["header"] = json.dumps(
        curcls.get_complete_header(), ensure_ascii=False, indent=False
    )
    # initcreate dimension variable
    global_attrs["nrec"] = curcls.file.number_of_records
    # add variable profile_id (dummy variable)
    global_attrs["filename"] = curcls.filename.split("/")[-1]
    ncfile.add_var("str_id", "filename", None, curcls.filename.split("/")[-1])
    # add administration variables
    country = curcls.administration.country.strip()
    global_attrs["country"] = country
    ncfile.add_var("str_id", "country", None, country)
    # create mission id
    if curcls.administration.mission != "n/a":
        mission_id = curcls.administration.mission.strip()
    elif curcls.deployment is not None and curcls.deployment.mission != "n/a":
        mission_id = curcls.deployment.mission.strip()
    else:
        mission_id = "n/a"

    if mission_id.lower() == "n/a":
        print("Mission ID not available !", curcls.filename)
    else:
        buf = mission_id.split("-")
        mission_id = "{:4d}-{:03d}".format(int(buf[0]), int(buf[1]))
    global_attrs["mission"] = mission_id
    ncfile.add_var("str_id", "deployment_mission_id", None, mission_id)

    # create event and profile ID
    if curcls.location.event_number > 0:
        event_id = curcls.location.event_number
    else:
        print("Event number not found!" + curcls.filename)
        event_id = 0

    ncfile.add_var("str_id", "event_number", None, "{:04d}".format(event_id))

    obs_time = curcls.get_obs_time()
    if mission_id is None or mission_id == "n/a":
        year_string = obs_time[0].strftime("%Y")
        profile_id = "{}-000-{:04d}".format(year_string, event_id)
    else:
        profile_id = "{:04d}-{:03d}-{:04d}".format(int(buf[0]), int(buf[1]), event_id)
    # print(profile_id)
    ncfile.add_var("profile", "profile", None, profile_id)
    global_attrs["id"] = profile_id

    scientist = curcls.administration.scientist.strip()
    global_attrs["scientist"] = scientist
    ncfile.add_var("str_id", "scientist", None, scientist)

    project = curcls.administration.project.strip()
    global_attrs["project"] = project
    ncfile.add_var("str_id", "project", None, project)

    agency = curcls.administration.agency.strip()
    global_attrs["agency"] = agency
    ncfile.add_var("str_id", "agency", None, agency)

    platform = curcls.administration.platform.strip()
    global_attrs["platform"] = platform
    ncfile.add_var("str_id", "platform", None, platform)

    # add instrument type
    if curcls.instrument.type != "n/a":
        ncfile.add_var(
            "str_id",
            "instrument_type",
            None,
            curcls.instrument.type.strip(),
        )

    if curcls.instrument.model != "n/a":
        ncfile.add_var(
            "str_id",
            "instrument_model",
            None,
            curcls.instrument.model.strip(),
        )

    if curcls.instrument.serial_number != "n/a":
        ncfile.add_var(
            "str_id",
            "instrument_serial_number",
            None,
            curcls.instrument.serial_number.strip(),
        )

    if curcls.instrument.depth != "n/a":
        ncfile.add_var(
            "instr_depth",
            "instrument_depth",
            None,
            float(curcls.instrument.depth),
        )
    # add locations variables
    ncfile.add_var(
        "lat",
        "latitude",
        "degrees_north",
        curcls.location.latitude,
    )
    global_attrs["geospatial_lat_min"] = curcls.location.latitude
    global_attrs["geospatial_lat_max"] = curcls.location.latitude
    ncfile.add_var(
        "lon",
        "longitude",
        "degrees_east",
        curcls.location.longitude,
    )
    global_attrs["geospatial_lon_min"] = curcls.location.longitude
    global_attrs["geospatial_lon_max"] = curcls.location.longitude
    global_attrs["geospatial_bounds"] = "POINT ({}, {})".format(
        curcls.location.longitude, curcls.location.latitude
    )

    ncfile.add_var("str_id", "geographic_area", None, curcls.geo_code)

    # add time variables and attributes
    global_attrs["time_coverage_duration"] = str(obs_time[-1] - obs_time[0])

    global_attrs["time_coverage_resolution"] = str(obs_time[1] - obs_time[0])

    ncfile.add_var("time", "time", None, obs_time, vardim=("time"))
    global_attrs["time_coverage_start"] = obs_time[0].strftime(date_format)
    global_attrs["time_coverage_end"] = obs_time[-1].strftime(date_format)
    # direction_index = None
    # for i, channel in enumerate(curcls.channels['Name']):
    #     if is_in(['direction:geog(to)'], channel):
    #         direction_index = i
    # if direction_index is not None:
    #     if len(curcls.obs_time) <= len(curcls.data[:, direction_index]):
    #         ncfile_var_list.append(OceanNcVar('time', 'time', None, None, None, curcls.obs_time, vardim=('time')))
    #     else:
    #         print('Time range length ({}) greater than direction:geog(to) length ({}) !'.format(
    #             len(curcls.obs_time), len(curcls.data[:, direction_index])))
    #         out.nrec = len(curcls.data[:, direction_index]) #correct number of records
    #         ncfile_var_list.append(OceanNcVar('time', 'time', None, None, None,
    #                                           curcls.obs_time[:len(curcls.data[:, direction_index])], vardim=('time')))

    flag_ne_speed = 0  # flag to determine if north and east speed components are vars in the .cur file
    flag_cndc = 0  # flag to check for conductivity
    flag_cndc_ratio = 0  # flag to check for conductivity ratio
    temp_count = 0  # counter for the number of "Temperature" channels

    # go through channels and add each variable depending on type
    for i, channel in enumerate(curcls.file.channels):
        try:
            null_value = curcls.file.channel_details[i].pad
        except Exception as e:
            if not math.isnan(curcls.file.pad):
                null_value = curcls.file.pad
                print(
                    "Channel Details missing. Setting Pad value to: ",
                    null_value,
                )
            else:
                print("Channel Details missing. Setting Pad value to ' ' ...")
                null_value = "' '"
        data = [row[i] for row in curcls.data]
        if is_in(["depth"], channel.name):
            ncfile.add_var(
                "depth",
                "depth",
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["pressure"], channel.name):
            ncfile.add_var(
                "pressure",
                "pressure",
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["temperature:low_res"], channel.name):
            ncfile.add_var(
                "temperature:cur:low_res",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["temperature"], channel.name) and not is_in(
            ["temperature:high_res", "temperature:low_res"], channel.name
        ):
            temp_count += 1
            if temp_count == 1:
                ncfile.add_var(
                    "temperature:cur",
                    channel.name,
                    channel.units,
                    data,
                    ("time"),
                    null_value,
                    attributes={"featureType": "timeSeries"},
                )
            elif temp_count == 2:
                ncfile.add_var(
                    "temperature:cur:high_res",
                    channel.name,
                    channel.units,
                    data,
                    ("time"),
                    null_value,
                    attributes={"featureType": "timeSeries"},
                )
        elif is_in(["temperature:high_res"], channel.name):
            ncfile.add_var(
                "temperature:cur:high_res",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )
        elif is_in(["salinity"], channel.name):
            ncfile.add_var(
                "salinity:cur",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["oxygen"], channel.name) and not is_in(
            ["flag", "bottle", "rinko", "temperature", "current"], channel.name
        ):
            ncfile.add_var(
                "oxygen",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["conductivity"], channel.name) and not is_in(
            ["conductivity_ratio", "conductivity ratio"], channel.name
        ):
            pass

        elif is_in(["conductivity_ratio", "conductivity ratio"], channel.name):
            pass

        elif is_in(["speed:east", "ew_comp"], channel.name):
            flag_ne_speed += 1
            ncfile.add_var(
                "speed:east",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["speed:north", "ns_comp"], channel.name):
            ncfile.add_var(
                "speed:north",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["speed:up"], channel.name):
            ncfile.add_var(
                "speed:up",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["amplitude:beam1"], channel.name):
            ncfile.add_var(
                "amplitude:beam1",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["amplitude:beam2"], channel.name):
            ncfile.add_var(
                "amplitude:beam2",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["amplitude:beam3"], channel.name):
            ncfile.add_var(
                "amplitude:beam3",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["speed:sound"], channel.name) and not is_in(
            ["speed:sound:1", "speed:sound:2"], channel.name
        ):
            ncfile.add_var(
                "speed:sound",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["speed:sound:1"], channel.name):
            ncfile.add_var(
                "speed:sound:1",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["speed:sound:2"], channel.name):
            ncfile.add_var(
                "speed:sound:2",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["heading"], channel.name):
            ncfile.add_var(
                "heading",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["pitch"], channel.name):
            ncfile.add_var(
                "pitch",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["roll"], channel.name):
            ncfile.add_var(
                "roll",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

        elif is_in(["speed"], channel.name):
            ncfile.add_var(
                "speed",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )
            index_speed = i

        elif is_in(["direction:geog(to)", "direction:current"], channel.name):
            ncfile.add_var(
                "direction:geog(to)",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )
            index_direction = i

        elif is_in(["sigma-t"], channel.name):
            ncfile.add_var(
                "sigma-t",
                channel.name,
                channel.units,
                data,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )
        else:
            if not is_in(["record", "sample", "date", "time"], channel.name):
                print(channel.name, "not transferred to netcdf file !")

    # Calculate North and East components of speed if missing
    try:
        if flag_ne_speed == 0:
            if isinstance(curcls.data[0][index_speed], bytes) and isinstance(
                curcls.data[0][index_direction], bytes
            ):
                speed_decoded = np.array(
                    [float(row[index_speed].decode("ascii")) for row in curcls.data]
                )
                direction_decoded = np.array(
                    [float(row[index_direction].decode("ascii")) for row in curcls.data]
                )
                speed_east, speed_north = add_ne_speed(speed_decoded, direction_decoded)
            else:
                speed_east, speed_north = add_ne_speed(
                    [row[index_speed] for row in curcls.data],
                    [row[index_direction] for row in curcls.data],
                )

            null_value = "' '"
            ncfile.add_var(
                "speed:east",
                "Speed:East",
                curcls.file.channels[index_speed].units,
                speed_east,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )

            ncfile.add_var(
                "speed:north",
                "Speed:North",
                curcls.file.channels[index_speed].units,
                speed_north,
                ("time"),
                null_value,
                attributes={"featureType": "timeSeries"},
            )
            print("Calculated east and north speed components ...")
    except UnboundLocalError as e:
        print("Speed and speed component channels not found in file !")

    # attach variables to ncfileclass and call method to write netcdf file
    ncfile.write_ncfile(filename)
    print("Finished writing file:", filename, "\n")
    # release_memory(out)
    return 1

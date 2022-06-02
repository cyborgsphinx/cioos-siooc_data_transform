import logging
import math

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


def convert_channels(shell, ncfile, dimensions, is_current=False):
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
            ["flag", "rinko", "bottle"], channel.name
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

        elif is_in(["salinity"], channel.name) and not is_in(["flag", "bottle"], channel.name):
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
                dimensions,
                null_value,
                attributes={"featureType": ncfile.global_attrs["featureType"]},
            )

        elif is_in(["conductivity"], channel.name):
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

        #  other
        elif (
            is_in(
                [
                    "chlorophyll:extracted",
                    "fluorescence",
                    "ammonium",
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
                    dimensions,
                    null_value,
                    attributes={"featureType": ncfile.global_attrs["featureType"]},
                )
            except Exception as e:
                logging.error(e)

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

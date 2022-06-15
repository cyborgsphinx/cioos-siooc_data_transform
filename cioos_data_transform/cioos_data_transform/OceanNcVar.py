# class to describe any variable that goes into a netcdf file
# will include bodc code generation
from datetime import datetime
from pytz import timezone
import numpy as np


class OceanNcVar(object):
    def __init__(
        self,
        vartype,
        varname,
        varunits,
        varval,
        vardim=(),
        varnull=float("nan"),
        conv_to_BODC=True,
        attributes={},
    ):
        self.cf_role = None
        self.name = varname
        self.type = vartype
        self.standard_name = None
        self.long_name = None
        self.units = varunits
        self.datatype = ""
        self.null_value = varnull
        self.dimensions = vardim
        self.data = varval
        self.conv_to_BODC = conv_to_BODC
        self.attributes = attributes
        # from existing varlist. get all variables that are going to be written into the ncfile
        # this will be checked to make sure new variable name does not conflict with existing ones
        # varlist = []
        # for v in varclslist:
        #     varlist.append(v.name)
        # self.add_var(varlist)

    def add_var(self, varlist):
        """
        add variable to netcdf file using variables passed as inputs
        author: Pramod Thupaki pramod.thupaki@hakai.org
        input:
            ncfile: Dataset object where variables will be added
            vartype: variable type
            varname: nominal name of variable being passed. this can be IOS_dataname.
                    can be used to determine BODC codes
            varunits: Units specifications from IOS file
            varmin: minimum value of variable as specified in IOS file
            varmax: maximum value of variable as specified in IOS file
        output:
            NONE
        """
        if self.type == "str_id":
            self.datatype = str
        elif self.type == "profile":
            self.datatype = str
        elif self.type == "instr_depth":
            self.datatype = "float32"
            self.long_name = "Instrument Depth"
            self.standard_name = "instrument_depth"
            self.units = "m"
        elif self.type == "lat":
            self.datatype = "float32"
            self.long_name = "Latitude"
            self.standard_name = "latitude"
            self.units = "degrees_north"
        elif self.type == "lon":
            self.datatype = "float32"
            self.long_name = "Longitude"
            self.standard_name = "longitude"
            self.units = "degrees_east"
        elif self.type == "time":
            self.datatype = "double"
            self.standard_name = "time"
            self.long_name = "time"
            self.units = "seconds since 1970-01-01 00:00:00+0000"
            dt = np.asarray(
                self.data
            )  # datetime.datetime.strptime(self.data, '%Y/%m/%d %H:%M:%S.%f %Z')
            buf = dt - timezone("UTC").localize(datetime(1970, 1, 1, 0, 0, 0))
            self.data = [i.total_seconds() for i in buf]
            # self.data = (dt - datetime.datetime(1970, 1, 1).astimezone(timezone('UTC'))).total_seconds()
        elif self.type == "depth":
            self.datatype = "float32"
            # self.dimensions = ('z')
            self.long_name = "Depth below surface"
            if self.name.strip().lower() == "depth":
                self.standard_name = "depth"
            if self.name.strip().lower() == "depth_nominal":
                self.standard_name = "depth_nominal"
            self.units = "m"
            self.attributes = {"positive": "down", "axis": "Z"}
            self.__set_null_val()
        elif self.type == "pressure":
            if self.units.strip().lower() in ["kpascal", "kilopascal"]:
                self.__convert_units(self.type, self.name, self.units)
            self.name = "PRESPR01"
            self.datatype = "float32"
            # self.dimensions = ('z')
            self.long_name = "Pressure"
            if self.units.strip().lower() in [
                "dbar",
                "dbars",
                "decibar",
                "decibars",
            ]:
                self.units = "decibar"
            elif self.units.strip().lower() in [
                "count",
                "counts",
            ]:  # TODO add different long_name?
                self.units = "counts"
            else:
                raise Exception("Unclear units for pressure!")
            self.standard_name = "sea_water_pressure"
            self.__set_null_val()
        elif self.type == "temperature":
            self.datatype = "float32"
            # self.dimensions = ('z')
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Sea Water Temperature"
            self.standard_name = "sea_water_temperature"
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "temperature:cur:low_res":
            self.datatype = "float32"
            # self.dimensions = ('z')
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Sea Water Temperature (Low Resolution)"
            self.standard_name = "sea_water_temperature"
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "temperature:cur":
            self.datatype = "float32"
            # self.dimensions = ('z')
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Sea Water Temperature"
            self.standard_name = "sea_water_temperature"
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "temperature:cur:high_res":
            self.datatype = "float32"
            # self.dimensions = ('z')
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Sea Water Temperature (High Resolution)"
            self.standard_name = "sea_water_temperature"
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "salinity":
            self.datatype = "float32"
            # self.dimensions = ('z')
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Sea Water Practical Salinity"
            self.standard_name = "sea_water_practical_salinity"
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "salinity:cur":
            self.datatype = "float32"
            # self.dimensions = ('z')
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Sea Water Practical Salinity"
            self.standard_name = "sea_water_practical_salinity"
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "oxygen":
            self.datatype = "float32"
            # self.dimensions = ('z')
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Oxygen concentration"
            self.standard_name = "dissolved_oxygen_concentration"
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "oxygen saturation":
            self.datatype = "float32"
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Oxygen saturation"
            self.standard_name = "dissolved_oxygen_saturation"
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "conductivity":
            self.datatype = "float32"
            # self.dimensions = ('z')
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            if "Conductance:Specific" == self.name:
                self.long_name = "Sea Water Electrical Conductivity Corrected to 25° C"
            else:
                self.long_name = "Sea Water Electrical Conductivity"
                self.standard_name = "sea_water_electrical_conductivity"
            self.name = bodc_code
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "conductivity_gsw":  # TODO
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.long_name = "Sea Water Electrical Conductivity gsw"
            # self.standard_name = ''
            self.units = bodc_units
        elif self.type == "nutrient":
            self.datatype = "float32"
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "other":
            self.datatype = "float32"
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.units = bodc_units
            self.__set_null_val()
        elif self.type == "speed:east":
            self.datatype = "float32"
            if self.units.strip().lower() in [
                "cm/s"
            ] and self.units.strip().lower() not in ["m/s"]:
                self.__convert_units(self.type, self.name, self.units)
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "eastward_sea_water_velocity"
            self.units = bodc_units
        elif self.type == "speed:north":
            self.datatype = "float32"
            if self.units.strip().lower() in [
                "cm/s"
            ] and self.units.strip().lower() not in ["m/s"]:
                self.__convert_units(self.type, self.name, self.units)
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "northward_sea_water_velocity"
            self.units = bodc_units
        elif self.type == "speed:up":
            self.datatype = "float32"
            if self.units.strip().lower() in [
                "cm/s"
            ] and self.units.strip().lower() not in ["m/s"]:
                self.__convert_units(self.type, self.name, self.units)
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "upward_sea_water_velocity"
            self.units = bodc_units
        elif self.type == "amplitude:beam1":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "signal_intensity_from_multibeam_acoustic_doppler_velocity_sensor_in_sea_water"
            self.units = bodc_units
        elif self.type == "amplitude:beam2":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "signal_intensity_from_multibeam_acoustic_doppler_velocity_sensor_in_sea_water"
            self.units = bodc_units
        elif self.type == "amplitude:beam3":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "signal_intensity_from_multibeam_acoustic_doppler_velocity_sensor_in_sea_water"
            self.units = bodc_units
        elif self.type == "speed:sound":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "speed_of_sound_in_sea_water"
            self.units = bodc_units
        elif self.type == "speed:sound:1":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "speed_of_sound_in_sea_water"
            self.units = bodc_units
        elif self.type == "speed:sound:2":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "speed_of_sound_in_sea_water"
            self.units = bodc_units
        elif self.type == "heading":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "platform_orientation"
            self.units = bodc_units
        elif self.type == "pitch":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "platform_pitch"
            self.units = bodc_units
        elif self.type == "roll":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "platform_roll"
            self.units = bodc_units
        elif self.type == "speed":
            self.datatype = "float32"
            if self.units.strip().lower() in [
                "cm/s"
            ] and self.units.strip().lower() not in ["m/s"]:
                self.__convert_units(self.type, self.name, self.units)
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "sea_water_speed"
            self.units = bodc_units
        elif self.type == "direction:geog(to)":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.standard_name = "sea_water_velocity_to_direction"
            self.units = bodc_units
        elif self.type == "density":
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            # self.standard_name = ''
            self.long_name = "Density (neutral)"
            self.units = bodc_units
        elif self.type == "sigma-t":  # TODO
            self.datatype = "float32"
            for i in range(
                4
            ):  # will try to get a unique variable name at least 4 times
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            # self.standard_name = ''
            self.long_name = "Sigma-theta"
            self.units = bodc_units
        elif self.type == "chlorofluorocarbon":
            self.datatype = "float32"
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.units = bodc_units
        elif self.type == "isotope":
            self.datatype = "float32"
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.units = bodc_units
        elif self.type == "pigment":
            self.datatype = "float32"
            for i in range(4):
                bodc_code, bodc_units = self.__get_bodc_code(
                    self.type, self.name, self.units, i
                )
                if bodc_code not in varlist:
                    break
            self.name = bodc_code
            self.units = bodc_units
        elif self.type in ['DOUB', 'SING', 'SYTM', 'INTE']:
            type_mapping = {'DOUB': 'float64',
                            'SING': 'float32',
                            'SYTM': 'float64',
                            'INTE': 'int32'}
            self.datatype= type_mapping[self.type]
        elif self.type == "flag":
            last = varlist[-1]
            # BODC names should be all caps and contain no '_'
            if last.upper() == last and "_" not in last:
                self.name = varlist[-1] + "_QC"
            else:
                print("Not converting flag value {} seemingly for {}".format(self.name, last))
            self.datatype = "float32"
        else:
            print("Do not know how to define this variable..")
            raise Exception("Fatal Error")

    def __set_null_val(self):
        self.data = np.asarray(self.data, dtype=float)
        try:
            self.data[self.data == float(self.null_value)] = float("nan")
        except Exception as e:
            # print("Pad field is empty. Setting FillValue to NaN ...")
            self.null_value = np.nan

    def __get_bodc_code(self, vartype, ios_varname, varunits, iter):
        """
        return the correct BODC code based on variable type, units and ios variable name
        author: Pramod Thupaki pramod.thupaki@hakai.org
        inputs:
            varname:
            vartype: list. [0] = vartype, [1]=instance details (primary/secondary etc)
            varunits:
        output:
            BODC code
        """
        from .utils import is_in

        if not self.conv_to_BODC:
            # do not convert varname, varunits ot BODC. instead just return original values
            # use this option on datasets where variables are not named using this convention or
            # using a different method to define variable names and types
            return self.name, self.units

        bodc_code = ""
        bodc_units = ""
        if vartype == "temperature":
            if is_in(["reversing"], ios_varname) and is_in(
                ["deg c"], varunits
            ):
                bodc_code = "TEMPRTN"
                bodc_units = "deg_C"
                bodc_code = "{}{:01d}".format(bodc_code, iter + 1)
            elif is_in(["ITS90", "ITS-90"], varunits):
                bodc_code = "TEMPS9"
                bodc_units = "deg_C"
                bodc_code = "{}{:02d}".format(bodc_code, iter + 1)
            elif is_in(["IPTS-68", "IPTS68"], varunits):
                bodc_code = "TEMPS6"
                bodc_units = "deg_C"
                bodc_code = "{}{:02d}".format(bodc_code, iter + 1)
            elif is_in(["deg c", "degc"], varunits):
                bodc_code = "TEMPST"
                bodc_units = "deg_C"
                bodc_code = "{}{:02d}".format(bodc_code, iter + 1)
            else:  # if varunits does not specify type of temperature
                raise Exception(
                    "Temperature type not defined",
                    ios_varname,
                    varunits,
                    vartype,
                )

        elif vartype == "temperature:cur:low_res":
            if is_in(["deg c", "degc"], varunits):
                bodc_code = "TEMPPR03"
                bodc_units = "deg_C"
            elif is_in(["deg C (IPTS68)"], varunits):
                bodc_code = "TEMPP683"  # TODO
                bodc_units = "deg_C"
            else:
                raise Exception(
                    "Temperature type not defined",
                    ios_varname,
                    varunits,
                    vartype,
                )

        elif vartype == "temperature:cur":
            if is_in(["deg c", "degc"], varunits):
                bodc_code = "TEMPPR01"
                bodc_units = "deg_C"
            elif is_in(["deg C (IPTS68)"], varunits):
                bodc_code = "TEMPP681"
                bodc_units = "deg_C"
            else:  # if varunits does not specify type of temperature
                raise Exception(
                    "Temperature type not defined",
                    ios_varname,
                    varunits,
                    vartype,
                )

        elif vartype == "temperature:cur:high_res":
            if is_in(["deg c", "degc"], varunits):
                bodc_code = "TEMPPR02"
                bodc_units = "deg_C"
            elif is_in(["deg C (IPTS68)"], varunits):
                bodc_code = "TEMPP682"  # TODO
                bodc_units = "deg_C"
            else:  # if varunits does not specify type of temperature
                raise Exception(
                    "Temperature type not defined",
                    ios_varname,
                    varunits,
                    vartype,
                )

        elif vartype == "salinity":
            if not is_in(["bottle"], ios_varname) and is_in(
                ["PSS-78"], varunits
            ):
                bodc_code = "PSALST"
                bodc_units = "PSS-78"
                bodc_code = "{}{:02d}".format(bodc_code, iter + 1)
            elif not is_in(["bottle"], ios_varname) and is_in(
                ["ppt"], varunits
            ):
                bodc_code = "SSALST"
                bodc_units = "PPT"
                bodc_code = "{}{:02d}".format(bodc_code, iter + 1)
            elif is_in(["bottle"], ios_varname) and is_in(
                ["PSS-78"], varunits
            ):
                bodc_code = "PSALBST"
                bodc_units = "PSS-78"
                bodc_code = "{}{:01d}".format(bodc_code, iter + 1)
            elif is_in(["bottle"], ios_varname) and is_in(["ppt"], varunits):
                bodc_code = "ODSDM021"
                bodc_units = "PPT"

            else:
                raise Exception(
                    "Salinity type not defined", ios_varname, varunits, vartype
                )

        elif vartype == "salinity:cur":
            if is_in(["PSS-78"], varunits):
                bodc_code = "PSLTZZ01"
                bodc_units = "PSS-78"
            elif is_in(["ppt"], varunits):
                bodc_code = "ODSDM021"
                bodc_units = "PPT"
            else:
                raise Exception(
                    "Current meter salinity units not defined",
                    ios_varname,
                    varunits,
                    vartype,
                )

        elif vartype == "chlorofluorocarbon":
            if ios_varname.endswith("_11") and is_in(["pmol/kg"], varunits):
                bodc_code = "FR11GCKG"
                bodc_units = "pmol/kg"
                self.long_name = "Concentration of trichlorofluoromethane per unit mass of the water body"
            elif ios_varname.endswith("_11") and is_in(["pmol/l"], varunits):
                bodc_code = "FR11GCTX"
                bodc_units = "pmol/L"
                self.long_name = "Concentration of trichlorofluoromethane per unit volume of the water body"
            elif ios_varname.endswith("_12") and is_in(["pmol/kg"], varunits):
                bodc_code = "FR12GCKG"
                bodc_units = "pmol/kg"
                self.long_name = "Concentration of dichlorodifluoromethane per unit mass of the water body"
            elif ios_varname.endswith("_12") and is_in(["pmol/l"], varunits):
                bodc_code = "FR12GCTX"
                bodc_units = "pmol/L"
                self.long_name = "Concentration of dichlorodifluoromethane per unit volume of the water body"
            elif ios_varname.endswith("_113") and is_in(["pmol/l"], varunits):
                bodc_code = "F113GCTX"
                bodc_units = "pmol/L"
                self.long_name = "Concentration of 1,1,2-trichloro-1,2,2-trifluoroethane per unit volume of the water body"
            else:
                raise Exception(
                    "Chlorofluorocarbon not defined", ios_varname, varunits, vartype
                )

        elif vartype == "oxygen":
            if is_in(["ml/l"], varunits):
                bodc_code = "DOXYZZ"
                bodc_units = "mL/L"
            elif is_in(["umol/kg"], varunits):
                bodc_code = "DOXMZZ"
                bodc_units = "umol/kg"
            elif is_in(["umol/L"], varunits):
                bodc_code = "DOXY"
                bodc_units = "umol/L"
            else:
                raise Exception(
                    "Oxygen units not defined", ios_varname, varunits, vartype
                )
            bodc_code = "{}{:02d}".format(bodc_code, iter + 1)
        elif vartype == "oxygen saturation":
            if is_in(["%"], varunits):
                bodc_code = "OXYSZZ"
                bodc_units = "%"
            else:
                raise Exception(
                    "Oxygen saturation units not defined", ios_varname, varunits, vartype
                )
            bodc_code = "{}{:02d}".format(bodc_code, iter + 1)
        elif vartype == "isotope":
            if all(is_in([name], ios_varname) for name in ["oxygen", "18"]) and is_in(["/mille"], varunits):
                bodc_code = "D18OMXWT"
                bodc_units = "PPT"
            elif all(is_in([name], ios_varname) for name in ["carbon", "13"]) and is_in(["/mille"], varunits):
                bodc_code = "D13CMICX"
                bodc_units = "PPT"
            elif all(is_in([name], ios_varname) for name in ["carbon", "14"]) and is_in(["/mille"], varunits):
                bodc_code = "D14CMIXX"
                bodc_units = "PPT"
            else:
                raise Exception(
                    "Isotope units not defined", ios_varname, varunits, vartype
                )
        elif vartype == "pigment":
            if is_in(["chl-c3"], ios_varname):
                bodc_code = "CLC3MHP1"
                self.long_name = "Concentration of chlorophyll-c3 per unit volume of the water body"
            elif is_in(["chlide-a"], ios_varname):
                bodc_code = "CIDAMHP1"
                self.long_name = "Concentration of chlorophyllide-a per unit volume of the water body"
            elif is_in(["chl-c2"], ios_varname):
                bodc_code = "COCHWA01"
                self.long_name = "Concentration of chlorophyll-c2 per unit volume of the water body"
            elif is_in(["peri"], ios_varname):
                bodc_code = "PERIMHP1"
                self.long_name = "Concentration of peridinin per unit volume of the water body"
            elif is_in(["pheide-a"], ios_varname):
                bodc_code = "PBAXXXP1"
                self.long_name = "Concentration of phaeophorbide-a per unit volume of the water body"
            elif is_in(["but-fuco"], ios_varname):
                bodc_code = "BUTAMHP1"
                self.long_name = "Concentration of 19'-butanoyloxyfucoxanthin per unit volume of the water body"
            elif is_in(["fuco"], ios_varname) and not is_in(["but-", "hex-"], ios_varname):
                bodc_code = "FUCXMHP1"
                self.long_name = "Concentration of fucoxanthin per unit volume of the water body"
            elif is_in(["neo"], ios_varname):
                bodc_code = "NEOXMHP1"
                self.long_name = "Concentration of neoxanthin per unit volume of the water body"
            elif is_in(["pras"], ios_varname):
                bodc_code = "COPRWA11"
                self.long_name = "Concentration of prasinoxanthin per unit volume of the water body"
            elif is_in(["viola"], ios_varname):
                bodc_code = "VILXMHP1"
                self.long_name = "Concentration of violaxanthin per unit volume of the water body"
            elif is_in(["hex-fuco"], ios_varname):
                bodc_code = "HEXAMHP1"
                self.long_name = "Concentration of 19'-hexanoyloxyfucoxanthin per unit volume of the water body"
            elif is_in(["diadino"], ios_varname):
                bodc_code = "DIADMHP1"
                self.long_name = "Concentration of diadinoxanthin per unit volume of the water body"
            elif is_in(["allo"], ios_varname):
                bodc_code = "ALLOMHP1"
                self.long_name = "Concentration of alloxanthin per unit volume of the water body"
            elif is_in(["diato"], ios_varname):
                bodc_code = "DIATMHP1"
                self.long_name = "Concentration of diatoxanthin per unit volume of the water body"
            elif is_in(["zea"], ios_varname):
                bodc_code = "ZEAXMHP1"
                self.long_name = "Concentration of zeaxanthin per unit volume of the water body"
            elif is_in(["lut"], ios_varname):
                bodc_code = "LUTNMHP1"
                self.long_name = "Concentration of lutein per unit volume of the water body"
            else:
                raise Exception(
                    "Pigment not defined", ios_varname, varunits, vartype
                )
            # common across all pigments
            bodc_units = "ng/L"
            if is_in(["ng/L"], varunits):
                conversion_rate = 1.0
            elif is_in(["mg/m^3"], varunits):
                conversion_rate = 1000.0
            else:
                raise Exception("No known conversion from {} to ng/L".format(varunits))
            self.data = conversion_rate * np.asarray(self.data, dtype=float)
        elif vartype == "conductivity":
            if is_in(["s/m"], varunits):
                bodc_code = "CNDCST"
                bodc_units = "S/m"
            elif is_in(["ms/cm"], varunits):
                bodc_code = "CNDCSTX"
                bodc_units = "mS/cm"
            elif is_in(["counts", "count"], varunits):
                bodc_code = "CNDCZZ"
                bodc_units = "counts"
            else:
                raise Exception(
                    "Conductivity units not compatible with BODC code",
                    ios_varname,
                    varunits,
                    vartype,
                )
            bodc_code = "{}{:02d}".format(bodc_code, iter + 1)
        elif vartype == "conductivity_gsw":
            bodc_code = "CNDC_RATIO"  # TODO
            bodc_units = "n/a"
        elif vartype == "nutrient":
            if is_in(["nitrate_plus_nitrite"], ios_varname) and is_in(
                ["umol/l"], varunits
            ):
                bodc_code = "NTRZAAZ"
                bodc_units = "umol/L"
                self.standard_name = (
                    "mole_concentration_of_nitrate_and_nitrite_in_sea_water"
                )
                self.long_name = (
                    "Mole Concentration of Nitrate and Nitrite in Sea Water"
                )
            elif is_in(["phosphate"], ios_varname) and is_in(
                ["umol/l"], varunits
            ):
                bodc_code = "PHOSAAZ"
                bodc_units = "umol/L"
                self.standard_name = (
                    "mole_concentration_of_phosphate_in_sea_water"
                )
                self.long_name = "Mole Concentration of Phosphate in Sea Water"
            elif is_in(["silicate"], ios_varname) and is_in(
                ["umol/l"], varunits
            ):
                bodc_code = "SLCAAAZ"
                bodc_units = "umol/L"
                self.standard_name = (
                    "mole_concentration_of_silicate_in_sea_water"
                )
                self.long_name = "Mole Concentration of Silicate in Sea Water"
            else:
                raise Exception(
                    "Nutrient units not compatible with BODC code",
                    ios_varname,
                    varunits,
                    vartype,
                )
            bodc_code = "{}{:01d}".format(bodc_code, iter + 1)
        elif vartype == "other":
            if is_in(["chlorophyll_plus_phaeo-pigment"], ios_varname) and is_in(["mg/m^3"], varunits):
                bodc_code = "CPPHFLP1"
                bodc_units = "mg/m^3"
                self.long_name = "Concentration of chlorophyll+phaeopigments per unit volume of the water body"
            elif is_in(["chlorophyll"], ios_varname) and is_in(
                ["mg/m^3"], varunits
            ):
                bodc_code = "CPHLFLP"
                bodc_units = "mg/m^3"
                self.standard_name = (
                    "concentration_of_chlorophyll-a_in_water_body"
                )
                self.long_name = "Concentration of chlorophyll-a {chl-a CAS 479-61-8} per unit volume of the water body [particulate >GF/F phase] by filtration, acetone extraction and fluorometry"
            elif is_in(["fluorescence:calibrated"], ios_varname) and is_in(["mg/m^3"], varunits):
                bodc_code = "CPHLPS01"
                bodc_units = "mg/m^3"
                self.standard_name = "mass_concentration_of_chlorophyll_a_in_water_body"
                self.long_name = "Concentration of chlorophyll-a {chl-a CAS 479-61-8} per unit volume of the water body [particulate >unknown phase] by in-situ chlorophyll fluorometer and calibration against sample data"
            elif is_in(["fluorescence"], ios_varname) and is_in(["mg/m^3"], varunits):
                bodc_code = "CPHLPR01"
                bodc_units = "mg/m^3"
                self.standard_name = "mass_concentration_of_chlorophyll_a_in_water_body"
                self.long_name = "Concentration of chlorophyll-a {chl-a CAS 479-61-8} per unit volume of the water body [particulate >unknown phase] by in-situ chlorophyll fluorometer"
            elif is_in(["transmissivity"], ios_varname) and is_in(["%/metre"], varunits):
                bodc_code = "POPTPZ01"
                bodc_units = "%/metre"
                self.long_name = "Transmittance (unspecified wavelength) per unit length of the water body by transmissometer and correction to a path length of 1m"
            elif is_in(["transmissivity"], ios_varname) and varunits.strip() == "%":
                bodc_code = "POPTZZ01"
                bodc_units = "%"
                self.long_name = "Transmittance (unspecified wavelength) per unspecified length of the water body by transmissometer"
            elif is_in(["ammonium"], ios_varname) and is_in(["umol/l"], varunits):
                bodc_code = "AMONZZXX"
                bodc_units = "umol/L"
                self.long_name = "Concentration of ammonium {NH4+ CAS 14798-03-9} per unit volume of the water body [unknown phase]"
            elif is_in(["carbon:dissolved:organic"], ios_varname) and is_in(["umol/l"], varunits):
                bodc_code = "IC000083"
                bodc_units = "umol/L"
                self.long_name = "Concentration of dissolved organic carbon per unit volume of the water body"
            elif is_in(["carbon:particulate:organic"], ios_varname) and is_in(["umol/l"], varunits):
                bodc_code = "MDMAP010"
                bodc_units = "umol/L"
                self.long_name = "Concentration of particulate organic carbon per unit volume of the water body"
            elif is_in(["carbon:dissolved:inorganic"], ios_varname) and is_in(["umol/kg"], varunits):
                bodc_code = "TCO2MSXX"
                bodc_units = "umol/kg"
                self.long_name = "Concentration of total inorganic carbon per unit mass of the water body"
            elif is_in(["carbon:dissolved:inorganic"], ios_varname) and is_in(["mg/l"], varunits):
                bodc_code = "TCO2POTX"
                bodc_units = "mg/L"
                self.long_name = "Concentration of total inorganic carbon per unit volume of the water body"
            elif ios_varname.lower() == "ph" or ios_varname.lower().startswith("ph:"):
                bodc_code = "PHXXPR01"
                bodc_units = "n/a"
                self.long_name = "pH (unspecified scale) of the water body by pH electrode"
            elif is_in(["par:reference"], ios_varname) and is_in(["ue/m^2/sec"], varunits):
                bodc_code = "IRRDSV01"
                bodc_units = "ue/m^2/sec"
                self.long_name = "Downwelling vector irradiance as photons of electromagnetic radiation (PAR wavelengths) in the atmosphere by cosine-collector radiometer"
            elif is_in(["par"], ios_varname) and is_in(["ue/m^2/sec"], varunits):
                bodc_code = "PFDPAR01"
                bodc_units = "ue/m^2/sec"
                self.long_name = "Irradiance as photons of electromagnetic radiation (PAR wavelengths)"
            elif is_in(["turbidity:seapoint"], ios_varname) and is_in(["ntu", "ftu", "stu"], varunits):
                bodc_code = "TURBSP01"
                bodc_units = "ntu"
                self.standard_name = "sea_water_turbidity"
                self.long_name = "Turbidity of water in the water body by SeaPoint turbidity meter and laboratory calibration against formazin"
            # umol/L is likely a mistake, assume it is actually umol/kg
            elif is_in(["alkalinity:total"], ios_varname) and is_in(["umol/kg", "umol/L"], varunits):
                bodc_code = "MDMAP014"
                bodc_units = "umol/kg"
                self.long_name = "Total alkalinity per unit mass of the water body"
            elif is_in(["alkalinity:carbonate"], ios_varname) and is_in(["umol/kg"], varunits):
                bodc_code = "CRBTWCAL"
                bodc_units = "umol/kg"
                self.long_name = "Concentration of carbonate ions {CO3} per unit mass of the water body by computation"
            elif is_in(["phytoplankton:volume"], ios_varname) and is_in(["mm^3/m^3"], varunits):
                bodc_code = "SDBIOL13"
                bodc_units = "mm^3/m^3"
                self.long_name = "Biovolume of phytoplankton in the water body"
            elif is_in(["methane"], ios_varname) and is_in(["nmol/l"], varunits):
                bodc_code = "CH4CGCXX"
                bodc_units = "nmol/L"
                self.long_name = "Concentration of methane per unit volume of the water body"
            elif is_in(["ethane"], ios_varname) and is_in(["mol/l"], varunits):
                bodc_code = "AX02GCTX"
                bodc_units = "pmol/L"
                self.long_name = "Concentration of ethane per unit volume of the water body"
                if is_in(["pmol/l"], varunits):
                    conversion_rate = 1.0
                elif is_in(["nmol/l"], varunits):
                    conversion_rate = 1000.0
                else:
                    raise Exception("No known conversion from {} to picomoles/L".format(varunits))
                self.data = conversion_rate * np.asarray(self.data, dtype=float)
            elif is_in(["propane"], ios_varname) and is_in(["mol/l"], varunits):
                bodc_code = "AX03GCTX"
                bodc_units = "pmol/L"
                self.long_name = "Concentration of propane per unit volume of the water body"
                if is_in(["pmol/l"], varunits):
                    conversion_rate = 1.0
                elif is_in(["nmol/l"], varunits):
                    conversion_rate = 1000.0
                else:
                    raise Exception("No known conversion from {} to picomoles/L".format(varunits))
                self.data = conversion_rate * np.asarray(self.data, dtype=float)
            elif is_in(["ethylene"], ios_varname) and is_in(["mol/l"], varunits):
                bodc_code = "AW02GCTX"
                bodc_units = "pmol/L"
                self.long_name = "Concentration of ethene (ethylene) per unit volume of the water body"
                if is_in(["pmol/l"], varunits):
                    conversion_rate = 1.0
                elif is_in(["nmol/l"], varunits):
                    conversion_rate = 1000.0
                else:
                    raise Exception("No known conversion from {} to picomoles/L".format(varunits))
                self.data = conversion_rate * np.asarray(self.data, dtype=float)
            elif is_in(["dimethylsulfoniopropionate_dissolved"], ios_varname) and is_in(["mol/l"], varunits):
                bodc_code = "DMSPGCD1"
                bodc_units = "nmol/L"
                self.long_name = "Concentration of dimethylsulphoniopropionate per unit volume of the water body"
                if is_in(["nmol/l"], varunits):
                    conversion_rate = 1.0
                elif is_in(["umol/l"], varunits):
                    conversion_rate = 1000.0
                else:
                    raise Exception("No known conversion from {} to nanomoles/L".format(varunits))
                self.data = conversion_rate * np.asarray(self.data, dtype=float)
            elif is_in(["dimethylsulfoniopropionate_total"], ios_varname) and is_in(["mol/l"], varunits):
                bodc_code = "DMSPPTR3"
                bodc_units = "nmol/L"
                self.long_name = "Total concentration of dimethylsulphoniopropionate per unit volume of the water body"
                if is_in(["nmol/l"], varunits):
                    conversion_rate = 1.0
                elif is_in(["umol/l"], varunits):
                    conversion_rate = 1000.0
                else:
                    raise Exception("No known conversion from {} to nanomoles/L".format(varunits))
                self.data = conversion_rate * np.asarray(self.data, dtype=float)
            elif is_in(["dimethyl_sulphide"], ios_varname) and is_in(["nmol/l"], varunits):
                bodc_code = "DMSXGCD4"
                bodc_units = "nmol/L"
                self.long_name = "Concentration of dimethyl sulphide in the water body"
            elif is_in(["carbontetrachloride"], ios_varname) and is_in(["pmol/l"], varunits):
                bodc_code = "QCMXMASS"
                bodc_units = "pmol/L"
                self.long_name = "Concentration of carbontetrachloride in the water body"
            elif is_in(["barium:dissolved"], ios_varname) and is_in(["nmol/l"], varunits):
                bodc_code = "RWS00147"
                bodc_units = "nmol/L"
                self.long_name = "Concentration of barium per unit volume in the water body"
            elif is_in(["total_suspended_solids"], ios_varname) and is_in(["ug/l"], varunits):
                bodc_code = "RBYJLY26"
                bodc_units = "ug/L"
                self.long_name = "Total concentration of solids per unit volume in the water body"
            elif is_in(["bacteria"], ios_varname) and is_in(["/ml"], varunits):
                bodc_code = "P18318A9"
                bodc_units = "/mL"
                self.long_name = "Abundance of bacteria per unit volume of the water body"
            elif is_in(["picophytoplankton"], ios_varname) and is_in(["/ml"], varunits):
                bodc_code = "PU00A02Z"
                bodc_units = "/mL"
                self.long_name = "Abundance of picophytoplankton per unit volume of the water body"
            elif is_in(["nanophytoplankton"], ios_varname) and is_in(["/ml"], varunits):
                bodc_code = "PU00A01B"
                bodc_units = "/mL"
                self.long_name = "Abundance of nanophytoplankton per unit volume of the water body"
            elif is_in(["phaeo-pigment:extracted"], ios_varname) and is_in(["mg/m^3"], varunits):
                bodc_code = "PHAEFLPZ"
                bodc_units = "mg/m^3"
                self.long_name = "Concentration of phaeopigments per unit volume of the water body"
            else:
                raise Exception(
                    "'Other' units not compatible with BODC code",
                    ios_varname,
                    varunits,
                    vartype,
                )
            bodc_code = "{}{:01d}".format(bodc_code, iter + 1)

        elif vartype == "speed:east":
            if is_in(["m/s", "metres/sec"], varunits):
                bodc_code = "LCEWEL01"
                bodc_units = "m/s"
            else:
                raise Exception(
                    "'speed:east' units not compatible with BODC code",
                    ios_varname,
                    varunits,
                    vartype,
                )
        elif vartype == "speed:north":
            if is_in(["m/s", "metres/sec"], varunits):
                bodc_code = "LCNSEL01"
                bodc_units = "m/s"
            else:
                raise Exception(
                    "'speed:north' units not compatible with BODC code",
                    ios_varname,
                    varunits,
                    vartype,
                )
        elif vartype == "speed:up":
            if is_in(["m/s", "metres/sec"], varunits):
                bodc_code = "LRZASP01"
                bodc_units = "m/s"
            else:
                raise Exception(
                    "'speed:up' units not compatible with BODC code",
                    ios_varname,
                    varunits,
                    vartype,
                )
        elif vartype == "amplitude:beam1":
            bodc_code = "ISCMBMA1"
            bodc_units = "counts"
        elif vartype == "amplitude:beam2":
            bodc_code = "ISCMBMA2"
            bodc_units = "counts"
        elif vartype == "amplitude:beam3":
            bodc_code = "ISCMBMA3"
            bodc_units = "counts"
        elif vartype == "speed:sound":
            bodc_code = "SVELCV01"
            bodc_units = "m/s"
        elif vartype == "speed:sound:1":
            bodc_code = "SVELCV01"
            bodc_units = "m/s"
        elif vartype == "speed:sound:2":
            bodc_code = "SVELCV02"
            bodc_units = "m/s"
        elif vartype == "heading":
            bodc_code = "HEADCM01"
            bodc_units = "deg"
        elif vartype == "pitch":
            bodc_code = "PTCHEI01"
            bodc_units = "deg"
        elif vartype == "roll":
            bodc_code = "ROLLEI01"
            bodc_units = "deg"
        elif vartype == "speed":
            if is_in(["m/s", "metres/sec"], varunits):
                bodc_code = "LCSAEL01"
                bodc_units = "m/s"
            else:
                raise Exception(
                    "'speed' units not compatible with BODC code",
                    ios_varname,
                    varunits,
                    vartype,
                )
        elif vartype == "direction:geog(to)":
            bodc_code = "LCDAEL01"
            bodc_units = "deg"
        elif vartype == "density":
            bodc_code = "NEUTDENS"
            bodc_units = "kg/m^3"
        elif vartype == "sigma-t":
            bodc_code = "SIGTEQST"
            bodc_units = "n/a"
        else:
            raise Exception(
                "Cannot find BODC code for this variable",
                ios_varname,
                varunits,
                vartype,
            )
        return bodc_code, bodc_units

    def __convert_units(self, vartype, ios_varname, varunits):
        """
        convert units of variables going into output netCDF file
        author: Hana Hourston hana.hourston@dfo-mpo.gc.ca
        input:
            - vartype: list. [0] = vartype, [1]=instance details (primary/secondary etc)
            - ios_varname:
            - varunits:
        output:
            NONE
        """
        if self.units.strip().lower() in ["cm/s"]:
            cm2m = 0.01
            self.data = cm2m * np.asarray(self.data, dtype=float)
            self.units = "m/s"
        elif self.units.strip().lower() in ["kpascal", "kilopascal"]:
            kpascal2dbar = 0.1
            self.data = kpascal2dbar * np.asarray(self.data, dtype=float)
            self.units = "decibar"
        else:
            raise Exception(
                "Input units not understood !", ios_varname, varunits, vartype
            )
        return

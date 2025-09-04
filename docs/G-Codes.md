# G-Codes

This document describes the commands that Kalico supports. These are
commands that one may enter into the OctoPrint terminal tab.

Sections and commands marked with an ⚠️ show commands that are new or behave differently from Klipper

## G-Code commands

Kalico supports the following standard G-Code commands:
- Move (G0 or G1): `G1 [X<pos>] [Y<pos>] [Z<pos>] [E<pos>] [F<speed>]`
- Dwell: `G4 P<milliseconds>`
- Move to origin: `G28 [X] [Y] [Z]`
- Turn off motors: `M18` or `M84`
- Wait for current moves to finish: `M400`
- Use absolute/relative distances for extrusion: `M82`, `M83`
- Use absolute/relative coordinates: `G90`, `G91`
- Set position: `G92 [X<pos>] [Y<pos>] [Z<pos>] [E<pos>]`
- Set speed factor override percentage: `M220 S<percent>`
- Set extrude factor override percentage: `M221 S<percent>`
- Set acceleration: `M204 S<value>` OR `M204 P<value> T<value>`
  - Note: If S is not specified and both P and T are specified, then
    the acceleration is set to the minimum of P and T. If only one of
    P or T is specified, the command has no effect.
- Get extruder temperature: `M105`
- Set extruder temperature: `M104 [T<index>] [S<temperature>]`
- Set extruder temperature and wait: `M109 [T<index>] S<temperature>`
  - Note: M109 always waits for temperature to settle at requested
    value
- Set bed temperature: `M140 [S<temperature>]`
- Set bed temperature and wait: `M190 S<temperature>`
  - Note: M190 always waits for temperature to settle at requested
    value
- Set fan speed: `M106 S<value>`
- Turn fan off: `M107`
- Emergency stop: `M112`
- Get current position: `M114`
- Get firmware version: `M115`

For further details on the above commands see the
[RepRap G-Code documentation](http://reprap.org/wiki/G-code).

Kalico's goal is to support the G-Code commands produced by common
3rd party software (eg, OctoPrint, Printrun, Slic3r, Cura, etc.) in
their standard configurations. It is not a goal to support every
possible G-Code command. Instead, Kalico prefers human readable
["extended G-Code commands"](#additional-commands). Similarly, the
G-Code terminal output is only intended to be human readable - see the
[API Server document](API_Server.md) if controlling Kalico from
external software.

If one requires a less common G-Code command then it may be possible
to implement it with a custom
[gcode_macro config section](Config_Reference.md#gcode_macro). For
example, one might use this to implement: `G12`, `G29`, `G30`, `G31`,
`M42`, `M80`, `M81`, `T1`, etc.

## Additional Commands

Kalico uses "extended" G-Code commands for general configuration and
status. These extended commands all follow a similar format - they
start with a command name and may be followed by one or more
parameters. For example: `SET_SERVO SERVO=myservo ANGLE=5.3`. In this
document, the commands and parameters are shown in uppercase, however
they are not case sensitive. (So, "SET_SERVO" and "set_servo" both run
the same command.)

This section is organized by Kalico module name, which generally
follows the section names specified in the
[printer configuration file](Config_Reference.md). Note that some
modules are automatically loaded.

### [adxl345]

The following commands are available when an
[adxl345 config section](Config_Reference.md#adxl345) is enabled.

#### ACCELEROMETER_MEASURE
`ACCELEROMETER_MEASURE [CHIP=<config_name>] [NAME=<value>]`: Starts
accelerometer measurements at the requested number of samples per
second. If CHIP is not specified it defaults to "adxl345". The command
works in a start-stop mode: when executed for the first time, it
starts the measurements, next execution stops them. The results of
measurements are written to a file named
`/tmp/adxl345-<chip>-<name>.csv` where `<chip>` is the name of the
accelerometer chip (`my_chip_name` from `[adxl345 my_chip_name]`) and
`<name>` is the optional NAME parameter. If NAME is not specified it
defaults to the current time in "YYYYMMDD_HHMMSS" format. If the
accelerometer does not have a name in its config section (simply
`[adxl345]`) then `<chip>` part of the name is not generated.

#### ACCELEROMETER_QUERY
`ACCELEROMETER_QUERY [CHIP=<config_name>] [RATE=<value>]
[SAMPLES=<value>] [RETURN=<value>]`: queries
accelerometer for the current value. If CHIP is not specified it
defaults to "adxl345". If RATE is not specified, the default value is
used. This command is useful to test the connection to the ADXL345
accelerometer: one of the returned values should be a free-fall
acceleration (+/- some noise of the chip). The `SAMPLES` parameter
can be set to sample multiple readings from the sensor. The readings
will be averaged together. The default is to collect a single sample.
The `RETURN` parameter can take on the values `vector`(the default) or
`tilt`. In `vector` mode, the raw free-fall acceleration vector is
returned. In `tilt` mode, X and Y angles of a plane perpendicular to
the free-fall vector are calculated and displayed.

#### ACCELEROMETER_DEBUG_READ
`ACCELEROMETER_DEBUG_READ [CHIP=<config_name>] REG=<register>`:
queries ADXL345 register "register" (e.g. 44 or 0x2C). Can be useful
for debugging purposes.

#### ACCELEROMETER_DEBUG_WRITE
`ACCELEROMETER_DEBUG_WRITE [CHIP=<config_name>] REG=<register>
VAL=<value>`: Writes raw "value" into a register "register". Both
"value" and "register" can be a decimal or a hexadecimal integer. Use
with care, and refer to ADXL345 data sheet for the reference.

### [angle]

The following commands are available when an
[angle config section](Config_Reference.md#angle) is enabled.

#### ANGLE_CALIBRATE
`ANGLE_CALIBRATE CHIP=<chip_name>`: Perform angle calibration on the
given sensor (there must be an `[angle chip_name]` config section that
has specified a `stepper` parameter). IMPORTANT - this tool will
command the stepper motor to move without checking the normal
kinematic boundary limits. Ideally the motor should be disconnected
from any printer carriage before performing calibration. If the
stepper can not be disconnected from the printer, make sure the
carriage is near the center of its rail before starting calibration.
(The stepper motor may move forwards or backwards two full rotations
during this test.) After completing this test use the `SAVE_CONFIG`
command to save the calibration data to the config file. In order to
use this tool the Python "numpy" package must be installed (see the
[measuring resonance document](Measuring_Resonances.md#software-installation)
for more information).

#### ANGLE_CHIP_CALIBRATE
`ANGLE_CHIP_CALIBRATE CHIP=<chip_name>`: Perform internal sensor calibration,
if implemented (MT6826S/MT6835).

- **MT68XX**: The motor should be disconnected
from any printer carriage before performing calibration.
After calibration, the sensor should be reset by disconnecting the power.

#### ANGLE_DEBUG_READ
`ANGLE_DEBUG_READ CHIP=<config_name> REG=<register>`: Queries sensor
register "register" (e.g. 44 or 0x2C). Can be useful for debugging
purposes. This is only available for tle5012b chips.

#### ANGLE_DEBUG_WRITE
`ANGLE_DEBUG_WRITE CHIP=<config_name> REG=<register> VAL=<value>`:
Writes raw "value" into register "register". Both "value" and
"register" can be a decimal or a hexadecimal integer. Use with care,
and refer to sensor data sheet for the reference. This is only
available for tle5012b chips.

### [axis_twist_compensation]

The following commands are available when the
[axis_twist_compensation config
section](Config_Reference.md#axis_twist_compensation) is enabled.

#### AXIS_TWIST_COMPENSATION_CALIBRATE
`AXIS_TWIST_COMPENSATION_CALIBRATE [AXIS=<X|Y>]
[SAMPLE_COUNT=<value>] [<probe_parameter>=<value>]`:

Calibrates axis twist compensation by specifying the target axis or
enabling automatic calibration.

- **SAMPLE_COUNT:** Number of points tested during the calibration.
If not specified, it defaults to 3.

- **AXIS:** Define the axis (`X` or `Y`) for which the twist compensation
will be calibrated. If not specified, the axis defaults to `'X'`.

### [bed_mesh]

The following commands are available when the
[bed_mesh config section](Config_Reference.md#bed_mesh) is enabled
(also see the [bed mesh guide](Bed_Mesh.md)).

#### BED_MESH_CALIBRATE
`BED_MESH_CALIBRATE [PROFILE=<name>] [METHOD=manual] [HORIZONTAL_MOVE_Z=<value>]
[<probe_parameter>=<value>] [<mesh_parameter>=<value>] [ADAPTIVE=1]
[ADAPTIVE_MARGIN=<value>]`: This command probes the bed using generated points
specified by the parameters in the config. After probing, a mesh is generated
and z-movement is adjusted according to the mesh.
The mesh will be saved into a profile specified by the `PROFILE` parameter,
or `default` if unspecified.
See the PROBE command for details on the optional probe parameters. If
METHOD=manual is specified then the manual probing tool is activated - see the
MANUAL_PROBE command above for details on the additional commands available
while this tool is active. The optional `HORIZONTAL_MOVE_Z` value overrides the
`horizontal_move_z` option specified in the config file. If ADAPTIVE=1 is
specified then the objects defined by the Gcode file being printed will be used
to define the probed area. The optional `ADAPTIVE_MARGIN` value overrides the
`adaptive_margin` option specified in the config file.

#### BED_MESH_OUTPUT
`BED_MESH_OUTPUT PGP=[<0:1>]`: This command outputs the current probed
z values and current mesh values to the terminal.  If PGP=1 is
specified the X, Y coordinates generated by bed_mesh, along with their
associated indices, will be output to the terminal.

#### BED_MESH_MAP
`BED_MESH_MAP`: Like to BED_MESH_OUTPUT, this command prints the
current state of the mesh to the terminal.  Instead of printing the
values in a human readable format, the state is serialized in json
format. This allows octoprint plugins to easily capture the data and
generate height maps approximating the bed's surface.

#### BED_MESH_CLEAR
`BED_MESH_CLEAR`: This command clears the mesh and removes all z
adjustment.  It is recommended to put this in your end-gcode.

#### BED_MESH_PROFILE
`BED_MESH_PROFILE LOAD=<name> SAVE=<name> REMOVE=<name>`: This command
provides profile management for mesh state. LOAD will restore the mesh
state from the profile matching the supplied name. SAVE will save the
current mesh state to a profile matching the supplied name. Remove
will delete the profile matching the supplied name from persistent
memory. Note that after SAVE or REMOVE operations have been run the
SAVE_CONFIG gcode must be run to make the changes to persistent memory
permanent.

#### BED_MESH_OFFSET
`BED_MESH_OFFSET [X=<value>] [Y=<value>] [ZFADE=<value]`: Applies X, Y,
and/or ZFADE offsets to the mesh lookup. This is useful for printers with
independent extruders, as an offset is necessary to produce correct Z
adjustment after a tool change.  Note that a ZFADE offset does not apply
additional z-adjustment directly, it is used to correct the `fade`
calculation when a `gcode offset` has been applied to the Z axis.

#### BED_MESH_CHECK
`BED_MESH_CHECK [MAX_DEVIATION=<value>] [MAX_SLOPE=<value>]`: Validates the
current bed mesh against specified criteria. If MAX_DEVIATION is specified,
checks that the difference between the highest and lowest mesh points does not
exceed the provided value. If MAX_SLOPE is specified, checks that the maximum
slope between adjacent mesh points does not exceed the provided value (in mm/mm).
The command will raise an error if any specified check fails, or display a message
confirming the mesh is valid if all checks pass. If no parameters are specified,
the command will list the available validation checks.

### [bed_screws]

The following commands are available when the
[bed_screws config section](Config_Reference.md#bed_screws) is enabled
(also see the
[manual level guide](Manual_Level.md#adjusting-bed-leveling-screws)).

#### BED_SCREWS_ADJUST
`BED_SCREWS_ADJUST`: This command will invoke the bed screws
adjustment tool. It will command the nozzle to different locations (as
defined in the config file) and allow one to make adjustments to the
bed screws so that the bed is a constant distance from the nozzle.

### [bed_tilt]

The following commands are available when the
[bed_tilt config section](Config_Reference.md#bed_tilt) is enabled.

#### BED_TILT_CALIBRATE
`BED_TILT_CALIBRATE [METHOD=manual] [HORIZONTAL_MOVE_Z=<value>]
[<probe_parameter>=<value>]`: This command will probe the points specified in
the config and then recommend updated x and y tilt adjustments. See the PROBE
command for details on the optional probe parameters. If METHOD=manual is
specified then the manual probing tool is activated - see the MANUAL_PROBE
command above for details on the additional commands available while this tool
is active. The optional `HORIZONTAL_MOVE_Z` value overrides the
`horizontal_move_z` option specified in the config file.

### [belay]

The following commands are available when a
[belay config section](Config_Reference.md#belay) is enabled.

#### QUERY_BELAY
`QUERY_BELAY BELAY=<config_name>`: Queries the state of the belay
specified by `BELAY`.

#### BELAY_SET_MULTIPLIER
`BELAY_SET_MULTIPLIER BELAY=<config_name> [HIGH=<multiplier_high>]
[LOW=<multiplier_low>]`: Sets the values of multiplier_high and/or
multiplier_low for the belay specified by `BELAY`, overriding their
values from the corresponding
[belay config section](Config_Reference.md#belay). Values set by this
command will not persist across restarts.

#### BELAY_SET_STEPPER
`BELAY_SET_STEPPER BELAY=<config_name> STEPPER=<extruder_stepper_name>`: Selects
the extruder_stepper whose multiplier will be controlled by the belay specified
by `BELAY`. The multiplier for the previous stepper will be reset back
to 1 before switching to the new stepper. Stepper selections made by this
command will not persist across restarts. This command is only available if
extruder_type is set to 'extruder_stepper' in the corresponding
[belay config section](Config_Reference.md#belay).

### [bltouch]

The following command is available when a
[bltouch config section](Config_Reference.md#bltouch) is enabled (also
see the [BL-Touch guide](BLTouch.md)).

#### BLTOUCH_DEBUG
`BLTOUCH_DEBUG COMMAND=<command>`: This sends a command to the
BLTouch. It may be useful for debugging. Available commands are:
`pin_down`, `touch_mode`, `pin_up`, `self_test`, `reset`. A BL-Touch
V3.0 or V3.1 may also support `set_5V_output_mode`,
`set_OD_output_mode`, `output_mode_store` commands.

#### BLTOUCH_STORE
`BLTOUCH_STORE MODE=<output_mode>`: This stores an output mode in the
EEPROM of a BLTouch V3.1 Available output_modes are: `5V`, `OD`

### [configfile]

The configfile module is automatically loaded.

#### SAVE_CONFIG
`SAVE_CONFIG [RESTART=0|1]`: This command will overwrite the main printer config
file and restart the host software. This command is used in
conjunction with other calibration commands to store the results of
calibration tests.
If RESTART is set to 0, no restart will be performed !!USE WITH CAUTION!!.

### [delayed_gcode]

The following command is enabled if a
[delayed_gcode config section](Config_Reference.md#delayed_gcode) has
been enabled (also see the
[template guide](Command_Templates.md#delayed-gcodes)).

#### UPDATE_DELAYED_GCODE
`UPDATE_DELAYED_GCODE [ID=<name>] [DURATION=<seconds>]`: Updates the
delay duration for the identified [delayed_gcode] and starts the timer
for gcode execution. A value of 0 will cancel a pending delayed gcode
from executing.

### [delta_calibrate]

The following commands are available when the
[delta_calibrate] config section is enabled (also see the
[delta calibrate guide](Delta_Calibrate.md)).

#### DELTA_CALIBRATE
`DELTA_CALIBRATE [METHOD=manual] [HORIZONTAL_MOVE_Z=<value>]
[<probe_parameter>=<value>]`: This command will probe seven points on the bed
and recommend updated endstop positions, tower angles, and radius. See the
PROBE command for details on the optional probe parameters. If METHOD=manual is
specified then the manual probing tool is activated - see the MANUAL_PROBE
command above for details on the additional commands available while this tool
is active. The optional `HORIZONTAL_MOVE_Z` value overrides the
`horizontal_move_z` option specified in the config file.

#### DELTA_ANALYZE
`DELTA_ANALYZE`: This command is used during enhanced delta
calibration. See [Delta Calibrate](Delta_Calibrate.md) for details.

### [display]

The following command is available when a
[display config section](Config_Reference.md#gcode_macro) is enabled.

#### SET_DISPLAY_GROUP
`SET_DISPLAY_GROUP [DISPLAY=<display>] GROUP=<group>`: Set the active
display group of an lcd display. This allows to define multiple
display data groups in the config, e.g. `[display_data <group>
<elementname>]` and switch between them using this extended gcode
command. If DISPLAY is not specified it defaults to "display" (the
primary display).

### [display_status]

The display_status module is automatically loaded if a
[display config section](Config_Reference.md#display) is enabled. It
provides the following standard G-Code commands:
- Display Message: `M117 <message>`
- Set build percentage: `M73 P<percent>`

Also provided is the following extended G-Code command:
- `SET_DISPLAY_TEXT MSG=<message>`: Performs the equivalent of M117,
  setting the supplied `MSG` as the current display message.  If
  `MSG` is omitted the display will be cleared.

## [dockable_probe]

In addition to the normal commands available for a `[probe]`, the following
commands are available when a
[dockable_probe config section](Config_Reference.md#dockable_probe) is enabled
(also see the [Dockable Probe guide](Dockable_Probe.md)):

- `ATTACH_PROBE`: Move to dock and attach probe to the toolhead, the toolhead
  will return to its previous position after attaching.
- `DETACH_PROBE`: Move to dock and detach probe from the toolhead, the toolhead
  will return to its previous position after detaching.
- `QUERY_DOCKABLE_PROBE`: Respond with current probe state. This is useful for
  verifying configuration settings are working as intended.
- `SET_DOCKABLE_PROBE AUTO_ATTACH_DETACH=0|1`: Enable/Disable the automatic
  attaching/detaching of the probe during actions that require the probe.
- `MOVE_TO_APPROACH_PROBE`: Move to approach the probe dock.
- `MOVE_TO_DOCK_PROBE`: Move to the probe dock (this should trigger the probe
  to attach).
- `MOVE_TO_EXTRACT_PROBE`: Move to leave the dock with the probe attached.
- `MOVE_TO_INSERT_PROBE`: Move to insert position near the dock
  with the probe attached.
- `MOVE_TO_DETACH_PROBE`: Move away from the dock to disconnect the probe
  from the toolhead.
- `MOVE_AVOIDING_DOCK [X=<value>] [Y=<value>] [SPEED=<value>]`: Move to the
  defined point (absolute coordinates) avoiding the safe dock area

### [dual_carriage]

The following command is available when the
[dual_carriage config section](Config_Reference.md#dual_carriage) is
enabled.

#### SET_DUAL_CARRIAGE
`SET_DUAL_CARRIAGE CARRIAGE=[0|1] [MODE=[PRIMARY|COPY|MIRROR]]`:
This command will change the mode of the specified carriage.
If no `MODE` is provided it defaults to `PRIMARY`. Setting the mode
to `PRIMARY` deactivates the other carriage and makes the specified
carriage execute subsequent G-Code commands as-is. `COPY` and `MIRROR`
modes are supported only for `CARRIAGE=1`. When set to either of these
modes, carriage 1 will then track the subsequent moves of the carriage 0
and either copy relative movements of it (in `COPY` mode) or execute them
in the opposite (mirror) direction (in `MIRROR` mode).

#### SAVE_DUAL_CARRIAGE_STATE
`SAVE_DUAL_CARRIAGE_STATE [NAME=<state_name>]`: Save the current positions
of the dual carriages and their modes. Saving and restoring DUAL_CARRIAGE
state can be useful in scripts and macros, as well as in homing routine
overrides. If NAME is provided it allows one to name the saved state
to the given string. If NAME is not provided it defaults to "default".

#### RESTORE_DUAL_CARRIAGE_STATE
`RESTORE_DUAL_CARRIAGE_STATE [NAME=<state_name>] [MOVE=[0|1] [MOVE_SPEED=<speed>]]`:
Restore the previously saved positions of the dual carriages and their modes,
unless "MOVE=0" is specified, in which case only the saved modes will be
restored, but not the positions of the carriages. If positions are being
restored and "MOVE_SPEED" is specified, then the toolhead moves will be
performed with the given speed (in mm/s); otherwise the toolhead move will
use the rail homing speed. Note that the carriages restore their positions
only over their own axis, which may be necessary to correctly restore COPY
and MIRROR mode of the dual carraige.

### [endstop_phase]

The following commands are available when an
[endstop_phase config section](Config_Reference.md#endstop_phase) is
enabled (also see the [endstop phase guide](Endstop_Phase.md)).

#### ENDSTOP_PHASE_CALIBRATE
`ENDSTOP_PHASE_CALIBRATE [STEPPER=<config_name>]`: If no STEPPER
parameter is provided then this command will reports statistics on
endstop stepper phases during past homing operations. When a STEPPER
parameter is provided it arranges for the given endstop phase setting
to be written to the config file (in conjunction with the SAVE_CONFIG
command).

### [exclude_object]

The following commands are available when an
[exclude_object config section](Config_Reference.md#exclude_object) is
enabled (also see the [exclude object guide](Exclude_Object.md)):

#### `EXCLUDE_OBJECT`
`EXCLUDE_OBJECT [NAME=object_name] [CURRENT=1] [RESET=1]`:
With no parameters, this will return a list of all currently excluded objects.

When the `NAME` parameter is given, the named object will be excluded from
printing.

When the `CURRENT` parameter is given, the current object will be excluded from
printing.

When the `RESET` parameter is given, the list of excluded objects will be
cleared. Additionally including `NAME` will only reset the named object. This
**can** cause print failures, if layers were already skipped.

#### `EXCLUDE_OBJECT_DEFINE`
`EXCLUDE_OBJECT_DEFINE [NAME=object_name [CENTER=X,Y] [POLYGON=[[x,y],...]]
[RESET=1] [JSON=1]`:
Provides a summary of an object in the file.

With no parameters provided, this will list the defined objects known to
Kalico. Returns a list of strings, unless the `JSON` parameter is given,
when it will return object details in json format.

When the `NAME` parameter is included, this defines an object to be excluded.

  - `NAME`: This parameter is required.  It is the identifier used by other
    commands in this module.
  - `CENTER`: An X,Y coordinate for the object.
  - `POLYGON`: An array of X,Y coordinates that provide an outline for the
    object.

When the `RESET` parameter is provided, all defined objects will be cleared, and
the `[exclude_object]` module will be reset.

#### `EXCLUDE_OBJECT_START`
`EXCLUDE_OBJECT_START NAME=object_name`:
This command takes a `NAME` parameter and denotes the start of the gcode for an
object on the current layer.

#### `EXCLUDE_OBJECT_END`
`EXCLUDE_OBJECT_END [NAME=object_name]`:
Denotes the end of the object's gcode for the layer. It is paired with
`EXCLUDE_OBJECT_START`. A `NAME` parameter is optional, and will only warn when
the provided name does not match the current object.

### [extruder]

The following commands are available if an
[extruder config section](Config_Reference.md#extruder) is enabled:

#### ACTIVATE_EXTRUDER
`ACTIVATE_EXTRUDER EXTRUDER=<config_name>`: In a printer with multiple
[extruder](Config_Reference.md#extruder) config sections, this command
changes the active hotend.

#### SET_PRESSURE_ADVANCE
`SET_PRESSURE_ADVANCE [EXTRUDER=<config_name>]
[ADVANCE=<pressure_advance>]
[SMOOTH_TIME=<pressure_advance_smooth_time>]`: Set pressure advance
parameters of an extruder stepper (as defined in an
[extruder](Config_Reference.md#extruder) or
[extruder_stepper](Config_Reference.md#extruder_stepper) config section).
If EXTRUDER is not specified, it defaults to the stepper defined in
the active hotend.

#### SET_EXTRUDER_ROTATION_DISTANCE
`SET_EXTRUDER_ROTATION_DISTANCE EXTRUDER=<config_name>
[DISTANCE=<distance>]`: Set a new value for the provided extruder
stepper's "rotation distance" (as defined in an
[extruder](Config_Reference.md#extruder) or
[extruder_stepper](Config_Reference.md#extruder_stepper) config section).
If the rotation distance is a negative number then the stepper motion
will be inverted (relative to the stepper direction specified in the
config file). Changed settings are not retained on Kalico reset. Use
with caution as small changes can result in excessive pressure between
extruder and hotend. Do proper calibration with filament before use.
If 'DISTANCE' value is not provided then this command will return the
current rotation distance.

#### SYNC_EXTRUDER_MOTION
`SYNC_EXTRUDER_MOTION EXTRUDER=<name> MOTION_QUEUE=<name>`: This
command will cause the stepper specified by EXTRUDER (as defined in an
[extruder](Config_Reference.md#extruder) or
[extruder_stepper](Config_Reference.md#extruder_stepper) config section)
to become synchronized to the movement of an extruder specified by
MOTION_QUEUE (as defined in an [extruder](Config_Reference.md#extruder)
config section). If MOTION_QUEUE is an empty string then the stepper
will be desynchronized from all extruder movement.

### [mixing_extruder]

The following commands are available when a
[mixingextruder config section](Config_Reference.md#mixing_extruder) is
enabled:

#### SET_MIXING_EXTRUDER
`SET_MIXING_EXTRUDER [FACTORS=<factor1>[:<factor2>[:<factor3>...]]]
[ENABLE=[0|1]]`:
This command activates the specified mixing extruder. Subsequent G1 commands
use the mixing defined by the factors. FACTORS defines the mixing by providing
a number of positive values. The number of values should correspond to the
number of steppers defined in the configuration. The values are normalized
internally to add up to 1 and the extrusion of the corresponding stepper is
multiplied by that value. If ENABLED is omitted the current mixing state is
not changed.
If neither FACTORS nor ENABLE is provided the current mixing status is
displayed.

#### SET_MIXING_EXTRUDER_GRADIENT
`SET_MIXING_EXTRUDER_GRADIENT [START_FACTORS=<s1>[,<s2>[,<s3>...]]
END_FACTORS=<e1>[,<e2>[,<e3>...]] START_HEIGHT=<start> END_HEIGHT=<end>`]
[ENABLE=[0|1|RESET]] [METHOD=[linear|spherical] [VECTOR=<x>,<y>,<z>]]`: When
START_FACTORS, END_FACTORS, START_HEIGHT, END_HEIGHT is provided
then an gradient configuration is added. The START_FACTORS define the mixing
below and up to the START_HEIGHT. The END_FACTORS respectively the mixing
from the END_HEIGHT onward. The mixing in between is linearly interpolated.
When ENABLE is either 0 or 1 or METHOD is specified the mixing gradient is
turned off or on and the gradient method (METHOD) which should be used is
selected. All previously added gradients are used when enabled. The optional
VECTOR configures a parameter depending on the METHOD: eg. for linear VECTOR
defines the up direction and for spherical it defines the origin of the
spheres.
When ENABLE is RESET all configured gradients are removed and the gradient
handling is disabled.
When no parameter is provided the current mixing gradient status is displayed.

### [heated_fan]

The following command is available when a
[heated_fan](Config_Reference.md#heated_fan) is
enabled.

### SET_HEATED_FAN_TARGET
`SET_HEATED_FAN_TARGET TARGET=<temperature>`: Override the `heater_temp`
setting in the [heated_fan config section](Config_Reference.md#heated_fan)
until Kalico is restarted. Useful for slicers to set different heated fan
temperatures at different layers.

### [fan_generic]

The following command is available when a
[fan_generic config section](Config_Reference.md#fan_generic) is
enabled.

#### SET_FAN_SPEED
`SET_FAN_SPEED FAN=config_name SPEED=<speed>` This command sets the
speed of a fan. "speed" must be between 0.0 and 1.0.

### [filament_switch_sensor]

The following command is available when a
[filament_switch_sensor](Config_Reference.md#filament_switch_sensor)
or
[filament_motion_sensor](Config_Reference.md#filament_motion_sensor)
config section is enabled.

#### QUERY_FILAMENT_SENSOR
`QUERY_FILAMENT_SENSOR SENSOR=<sensor_name>`: Queries the current
status of the filament sensor. The data displayed on the terminal will
depend on the sensor type defined in the configuration.

#### SET_FILAMENT_SENSOR
###### For filament_switch_sensor:
`SET_FILAMENT_SENSOR SENSOR=<sensor_name> [ENABLE=0|1] [RESET=0|1]
[RUNOUT_DISTANCE=<mm>] [SMART=0|1] [ALWAYS_FIRE_EVENTS=0|1] [CHECK_ON_PRINT_START=0|1]`:
Sets values for the filament sensor.
If all parameters are omitted, the current stats will be reported. <br>
ENABLE sets the filament sensor on/off. If ENABLE is set to 0, the
filament sensor will be disabled, if set to 1 it is enabled. If the state
of the sensor changes, a reset will be triggered. <br>
RESET removes all pending runout_gcodes and pauses and force a reevaluation
of the sensor state. <br>
RUNOUT_DISTANCE sets the runout_distance. <br>
SMART sets the smart parameter. <br>
ALWAYS_FIRE_EVENTS sets the always_fire_events parameter, if set to true,
a reset of the sensor will be triggered. <br>
CHECK_ON_PRINT_START sets the check_on_print_start parameter.

###### For filament_motion_sensor:
`SET_FILAMENT_SENSOR SENSOR=<sensor_name> [ENABLE=0|1] [RESET=0|1]
[DETECTION_LENGTH=<mm>] [SMART=0|1] [ALWAYS_FIRE_EVENTS=0|1]`:
Sets values for the filament sensor.
If all parameters are omitted, the current stats will be reported. <br>
ENABLE sets the filament sensor on/off. If ENABLE is set to 0, the
filament sensor will be disabled, if set to 1 it is enabled. If the sensor
was previously disabled and gets enabled, a reset will be triggered. <br>
RESET resets the state of the sensor and sets it to filament detected. <br>
DETECTION_LENGTH sets the detection_length, if the new detection length is
different from the old one, a reset will be triggered. <br>
SMART sets the smart parameter. <br>
ALWAYS_FIRE_EVENTS sets the always_fire_events parameter, no reset will
be triggered.

### [firmware_retraction]

The following standard G-Code commands are available when the
[firmware_retraction config section](Config_Reference.md#firmware_retraction)
is enabled. These commands allow utilizing the firmware
retraction feature available in many slicers. Retraction is a strategy to
reduce stringing during travel moves (non-extrusion) from one part of the
print to another. Note that pressure advance should be properly configured
before retraction parameters are tuned to ensure optimal results.
- `G10`: Retracts the filament using the currently configured
  parameters. If z_hop_height is set to a value greater zero,
  besides retracting the filament, the nozzle is lifted by set value.
- `G11`: Unretracts the filament using the currently configured
  parameters. If z_hop_height is set to a value greater zero,
  besides unretracting the filament, the nozzle is lowered back on the print
  with a vertical movement.

The following additional commands are also available.

#### SET_RETRACTION
`SET_RETRACTION [RETRACT_LENGTH=<mm>] [RETRACT_SPEED=<mm/s>]
[UNRETRACT_EXTRA_LENGTH=<mm>] [UNRETRACT_SPEED=<mm/s>] [Z_HOP_HEIGHT=<mm>]`:
Adjust the parameters used by firmware retraction. RETRACT_LENGTH determines the
length of filament to retract (the minimum as well as standard value is 0 mm).
RETRACT_SPEED determines the speed of the filament retraction move (the minimum
value is 1 mm/s, the standard value is 20 mm/s). This value is typically set
relatively high (>40 mm/s), except for soft and/or oozy filaments like TPU and
PETG (20 to 30 mm/s).
UNRETRACT_SPEED sets the speed of the filament unretract move (the minimum value
is 1 mm/s, the standard value is 10 mm/s). This parameter is not particularly
critical, although often lower than RETRACT_SPEED.
UNRETRACT_EXTRA_LENGTH allows to add a small amount of length to the filament
unretract move to prime the nozzle or to subtract a small amount of length from
the filament unretract move to reduce blobbing at seams (the minimum value is
-1 mm (2.41 mm3 volume for 1.75 mm filament), the standard value is 0 mm).
Z_HOP_HEIGHT determines the vertical height by which the nozzle is lifted from
the print to prevent collisions with the print during travel moves (the
minimum value is 0 mm, the standard value is 0 mm, which disables Z-Hop moves).
If a parameter is set when retracted, the new value will be taken into
account only after G11 or CLEAR_RETRACTION event.
SET_RETRACTION is commonly set as part of slicer per-filament configuration, as
different filaments require different parameter settings. The command can be
issued at runtime.

#### GET_RETRACTION
`GET_RETRACTION`: Queries the current parameters used by the firmware retraction
module as well as the retract state. RETRACT_LENGTH, RETRACT_SPEED,
UNRETRACT_EXTRA_LENGTH, UNRETRACT_SPEED, Z_HOP_HEIGHT, RETRACT_STATE (True, if
retracted), ZHOP_STATE (True, if zhop offset currently applied) are displayed on
the terminal.

#### CLEAR_RETRACTION
`CLEAR_RETRACTION`: Clears the current retract state without extruder or
motion system movement. All flags related to the retract state are reset to
False.

NOTE: The zhop state is also reset to False when the steppers are disabled (M84,
typically part of end gcode and standard behavior of OctoPrint if a print is
canceled) or the printer is homed (G28, typically part of start gcode). Hence,
upon ending or canceling a print as well as starting a new print via GCode
streaming or virtual SD card, the toolhead will not apply `z_hop_height` until
next G11 if filament is retracted.
Nevertheless, it is recommended to add `CLEAR_RETRACTION` to your start and end
gcode to make sure the retract state is reset before and after each print.

#### RESET_RETRACTION
`RESET_RETRACTION`: All changes to retraction parameters made via previous
SET_RETRACTION commands are reset to config values.

NOTE: It is recommended to add `RESET_RETRACTION` to your start and end gcode
(with a possible override in your filament start gcode to set filament-specific
overrides of firmware retraction defaults via `SET_RETRACTION`).

### [force_move]

The force_move module is automatically loaded, however some commands
require setting `enable_force_move` in the
[printer config](Config_Reference.md#force_move).

#### STEPPER_BUZZ
`STEPPER_BUZZ STEPPER=<config_name>`: Move the given stepper forward
one mm and then backward one mm, repeated 10 times. This is a
diagnostic tool to help verify stepper connectivity.

#### FORCE_MOVE
`FORCE_MOVE STEPPER=<config_name> DISTANCE=<value> VELOCITY=<value>
[ACCEL=<value>]`: This command will forcibly move the given stepper
the given distance (in mm) at the given constant velocity (in mm/s).
If ACCEL is specified and is greater than zero, then the given
acceleration (in mm/s^2) will be used; otherwise no acceleration is
performed. No boundary checks are performed; no kinematic updates are
made; other parallel steppers on an axis will not be moved. Use
caution as an incorrect command could cause damage! Using this command
will almost certainly place the low-level kinematics in an incorrect
state; issue a G28 afterwards to reset the kinematics. This command is
intended for low-level diagnostics and debugging.

#### SET_KINEMATIC_POSITION
`SET_KINEMATIC_POSITION [X=<value>] [Y=<value>] [Z=<value>]
[CLEAR=<[X][Y][Z]>]`: Force the low-level kinematic code to believe the
toolhead is at the given cartesian position. This is a diagnostic and
debugging command; use SET_GCODE_OFFSET and/or G92 for regular axis
transformations. If an axis is not specified then it will default to the
position that the head was last commanded to. Setting an incorrect or
invalid position may lead to internal software errors. Use the CLEAR
parameter to forget the homing state for the given axes. Note that CLEAR
will not override the previous functionality; if an axis is not specified
to CLEAR it will have its kinematic position set as per above. This
command may invalidate future boundary checks; issue a G28 afterwards to
reset the kinematics.

### [gcode]

The gcode module is automatically loaded.

#### RESTART
`RESTART`: This will cause the host software to reload its config and
perform an internal reset. This command will not clear error state
from the micro-controller (see FIRMWARE_RESTART) nor will it load new
software (see
[the FAQ](FAQ.md#how-do-i-upgrade-to-the-latest-software)).

#### FIRMWARE_RESTART
`FIRMWARE_RESTART`: This is similar to a RESTART command, but it also
clears any error state from the micro-controller.

#### HEATER_INTERRUPT
`HEATER_INTERRUPT`: Interrupts a TEMPERATURE_WAIT command.

#### LOG_ROLLOVER
`LOG_ROLLOVER`: Trigger a klippy.log rollover and generate a new log file.

#### STATUS
`STATUS`: Report the Kalico host software status.

#### HELP
`HELP`: Report the list of available extended G-Code commands.

### [gcode_arcs]

The following standard G-Code commands are available if a
[gcode_arcs config section](Config_Reference.md#gcode_arcs) is
enabled:
- Arc Move Clockwise (G2), Arc Move Counter-clockwise (G3): `G2|G3 [X<pos>] [Y<pos>] [Z<pos>]
  [E<pos>] [F<speed>] I<value> J<value>|I<value> K<value>|J<value> K<value>`
- Arc Plane Select: G17 (XY plane), G18 (XZ plane), G19 (YZ plane)

### [gcode_macro]

The following command is available when a
[gcode_macro config section](Config_Reference.md#gcode_macro) is
enabled (also see the
[command templates guide](Command_Templates.md)).

#### SET_GCODE_VARIABLE
`SET_GCODE_VARIABLE MACRO=<macro_name> VARIABLE=<name> VALUE=<value>`:
This command allows one to change the value of a gcode_macro variable
at run-time. The provided VALUE is parsed as a Python literal.

#### RELOAD_GCODE_MACROS
`RELOAD_GCODE_MACROS`: This command reads the config files and reloads
all previously loaded gcode templates. It does not load new `[gcode_macro]`
objects or unload deleted ones. Variables modified with SET_GCODE_VARIABLE
remain unaffected.

### [gcode_move]

The gcode_move module is automatically loaded.

#### GET_POSITION
`GET_POSITION`: Return information on the current location of the
toolhead. See the developer documentation of
[GET_POSITION output](Code_Overview.md#coordinate-systems) for more
information.

#### SET_GCODE_OFFSET
`SET_GCODE_OFFSET [X=<pos>|X_ADJUST=<adjust>]
[Y=<pos>|Y_ADJUST=<adjust>] [Z=<pos>|Z_ADJUST=<adjust>] [MOVE=1
[MOVE_SPEED=<speed>]]`: Set a positional offset to apply to future
G-Code commands. This is commonly used to virtually change the Z bed
offset or to set nozzle XY offsets when switching extruders. For
example, if "SET_GCODE_OFFSET Z=0.2" is sent, then future G-Code moves
will have 0.2mm added to their Z height. If the X_ADJUST style
parameters are used, then the adjustment will be added to any existing
offset (eg, "SET_GCODE_OFFSET Z=-0.2" followed by "SET_GCODE_OFFSET
Z_ADJUST=0.3" would result in a total Z offset of 0.1). If "MOVE=1" is
specified then a toolhead move will be issued to apply the given
offset (otherwise the offset will take effect on the next absolute
G-Code move that specifies the given axis). If "MOVE_SPEED" is
specified then the toolhead move will be performed with the given
speed (in mm/s); otherwise the toolhead move will use the last
specified G-Code speed.

#### SAVE_GCODE_STATE
`SAVE_GCODE_STATE [NAME=<state_name>]`: Save the current g-code
coordinate parsing state. Saving and restoring the g-code state is
useful in scripts and macros. This command saves the current g-code
absolute coordinate mode (G90/G91), absolute extrude mode (M82/M83),
origin (G92), offset (SET_GCODE_OFFSET), speed override (M220),
extruder override (M221), move speed, current XYZ position, and
relative extruder "E" position. If NAME is provided it allows one to
name the saved state to the given string. If NAME is not provided it
defaults to "default".

#### RESTORE_GCODE_STATE
`RESTORE_GCODE_STATE [NAME=<state_name>] [MOVE=1
[MOVE_SPEED=<speed>]]`: Restore a state previously saved via
SAVE_GCODE_STATE. If "MOVE=1" is specified then a toolhead move will
be issued to move back to the previous XYZ position. If "MOVE_SPEED"
is specified then the toolhead move will be performed with the given
speed (in mm/s); otherwise the toolhead move will use the restored
g-code speed.

### [hall_filament_width_sensor]

The following commands are available when the
[tsl1401cl filament width sensor config section](Config_Reference.md#tsl1401cl_filament_width_sensor)
or [hall filament width sensor config section](Config_Reference.md#hall_filament_width_sensor)
is enabled (also see [TSLl401CL Filament Width Sensor](TSL1401CL_Filament_Width_Sensor.md)
and [Hall Filament Width Sensor](Hall_Filament_Width_Sensor.md)):

#### QUERY_FILAMENT_WIDTH
`QUERY_FILAMENT_WIDTH`: Return the current measured filament width.

#### RESET_FILAMENT_WIDTH_SENSOR
`RESET_FILAMENT_WIDTH_SENSOR`: Clear all sensor readings. Helpful
after filament change.

#### DISABLE_FILAMENT_WIDTH_SENSOR
`DISABLE_FILAMENT_WIDTH_SENSOR`: Turn off the filament width sensor
and stop using it for flow control.

#### ENABLE_FILAMENT_WIDTH_SENSOR
`ENABLE_FILAMENT_WIDTH_SENSOR`: Turn on the filament width sensor and
start using it for flow control.

#### QUERY_RAW_FILAMENT_WIDTH
`QUERY_RAW_FILAMENT_WIDTH`: Return the current ADC channel readings
and RAW sensor value for calibration points.

#### ENABLE_FILAMENT_WIDTH_LOG
`ENABLE_FILAMENT_WIDTH_LOG`: Turn on diameter logging.

#### DISABLE_FILAMENT_WIDTH_LOG
`DISABLE_FILAMENT_WIDTH_LOG`: Turn off diameter logging.

### [load_cell]

The following commands are enabled if a
[load_cell config section](Config_Reference.md#load_cell) has been enabled.

### LOAD_CELL_DIAGNOSTIC
`LOAD_CELL_DIAGNOSTIC [LOAD_CELL=<config_name>]`: This command collects 10
seconds of load cell data and reports statistics that can help you verify proper
operation of the load cell. This command can be run on both calibrated and
uncalibrated load cells.

### LOAD_CELL_CALIBRATE
`LOAD_CELL_CALIBRATE [LOAD_CELL=<config_name>]`: Start the guided calibration
utility. Calibration is a 3 step process:
1. First you remove all load from the load cell and run the `TARE` command
1. Next you apply a known load to the load cell and run the
`CALIBRATE GRAMS=nnn` command
1. Finally use the `ACCEPT` command to save the results

You can cancel the calibration process at any time with `ABORT`.

### LOAD_CELL_TARE
`LOAD_CELL_TARE [LOAD_CELL=<config_name>]`: This works just like the tare button
on digital scale. It sets the current raw reading of the load cell to be the
zero point reference value. The response is the percentage of the sensors range
that was read and the raw value in counts.

### LOAD_CELL_READ load_cell="name"
`LOAD_CELL_READ [LOAD_CELL=<config_name>]`:
This command takes a reading from the load cell. The response is the percentage
of the sensors range that was read and the raw value in counts. If the load cell
is calibrated a force in grams is also reported.


### [heaters]

The heaters module is automatically loaded if a heater is defined in
the config file.

#### TURN_OFF_HEATERS
`TURN_OFF_HEATERS`: Turn off all heaters.

#### TEMPERATURE_WAIT
`TEMPERATURE_WAIT SENSOR=<config_name> [MINIMUM=<target>]
[MAXIMUM=<target>]`: Wait until the given temperature sensor is at or
above the supplied MINIMUM and/or at or below the supplied MAXIMUM.

#### SET_HEATER_TEMPERATURE
`SET_HEATER_TEMPERATURE HEATER=<heater_name>
[TARGET=<target_temperature>]`: Sets the target temperature for a
heater. If a target temperature is not supplied, the target is 0.

#### SET_SMOOTH_TIME
`SET_SMOOTH_TIME HEATER=<heater_name> [SMOOTH_TIME=<smooth_time>]
[SAVE_TO_PROFILE=0|1]`: Sets the smooth_time of the specified heater.
If SMOOTH_TIME is omitted, the smooth_time will be reset to the value
from the config.
If SAVE_TO_PROFILE is set to 1, the new value will be written to the
current PID_PROFILE.

### [idle_timeout]

The idle_timeout module is automatically loaded.

#### SET_IDLE_TIMEOUT
`SET_IDLE_TIMEOUT [TIMEOUT=<timeout>]`: Allows the user to set the
idle timeout (in seconds).

### [input_shaper]

The following command is enabled if an
[input_shaper config section](Config_Reference.md#input_shaper) has
been enabled (also see the
[resonance compensation guide](Resonance_Compensation.md)).

#### SET_INPUT_SHAPER
`SET_INPUT_SHAPER [SHAPER_FREQ_X=<shaper_freq_x>]
[SHAPER_FREQ_Y=<shaper_freq_y>] [DAMPING_RATIO_X=<damping_ratio_x>]
[DAMPING_RATIO_Y=<damping_ratio_y>] [SHAPER_TYPE=<shaper>]
[SHAPER_TYPE_X=<shaper_type_x>] [SHAPER_TYPE_Y=<shaper_type_y>]`:
Modify input shaper parameters. Note that SHAPER_TYPE parameter resets
input shaper for both X and Y axes even if different shaper types have
been configured in [input_shaper] section. SHAPER_TYPE cannot be used
together with either of SHAPER_TYPE_X and SHAPER_TYPE_Y parameters.
See [config reference](Config_Reference.md#input_shaper) for more
details on each of these parameters.

### [manual_probe]

The manual_probe module is automatically loaded.

#### MANUAL_PROBE
`MANUAL_PROBE [SPEED=<speed>]`: Run a helper script useful for
measuring the height of the nozzle at a given location. If SPEED is
specified, it sets the speed of TESTZ commands (the default is
5mm/s). During a manual probe, the following additional commands are
available:
- `ACCEPT`: This command accepts the current Z position and concludes
  the manual probing tool.
- `ABORT`: This command terminates the manual probing tool.
- `TESTZ Z=<value>`: This command moves the nozzle up or down by the
  amount specified in "value". For example, `TESTZ Z=-.1` would move
  the nozzle down .1mm while `TESTZ Z=.1` would move the nozzle up
  .1mm. The value may also be `+`, `-`, `++`, or `--` to move the
  nozzle up or down an amount relative to previous attempts.

#### Z_ENDSTOP_CALIBRATE
`Z_ENDSTOP_CALIBRATE [SPEED=<speed>]`: Run a helper script useful for
calibrating a Z position_endstop config setting. See the MANUAL_PROBE
command for details on the parameters and the additional commands
available while the tool is active.

#### Z_OFFSET_APPLY_ENDSTOP
`Z_OFFSET_APPLY_ENDSTOP`: Take the current Z Gcode offset (aka,
babystepping), and subtract it from the stepper_z endstop_position.
This acts to take a frequently used babystepping value, and "make it
permanent". Requires a `SAVE_CONFIG` to take effect.

### [manual_stepper]

The following command is available when a
[manual_stepper config section](Config_Reference.md#manual_stepper) is
enabled.

#### MANUAL_STEPPER
`MANUAL_STEPPER STEPPER=config_name [ENABLE=[0|1]]
[SET_POSITION=<pos>] [SPEED=<speed>] [ACCEL=<accel>] [MOVE=<pos>
[STOP_ON_ENDSTOP=[1|2|-1|-2]] [SYNC=0]]`: This command will alter the
state of the stepper. Use the ENABLE parameter to enable/disable the
stepper. Use the SET_POSITION parameter to force the stepper to think
it is at the given position. Use the MOVE parameter to request a
movement to the given position. If SPEED and/or ACCEL is specified
then the given values will be used instead of the defaults specified
in the config file. If an ACCEL of zero is specified then no
acceleration will be performed. If STOP_ON_ENDSTOP=1 is specified then
the move will end early should the endstop report as triggered (use
STOP_ON_ENDSTOP=2 to complete the move without error even if the
endstop does not trigger, use -1 or -2 to stop when the endstop
reports not triggered). Normally future G-Code commands will be
scheduled to run after the stepper move completes, however if a manual
stepper move uses SYNC=0 then future G-Code movement commands may run
in parallel with the stepper movement.

### [mcp4018]

The following command is available when a
[mcp4018 config section](Config_Reference.md#mcp4018) is
enabled.

#### SET_DIGIPOT

`SET_DIGIPOT DIGIPOT=config_name WIPER=<value>`: This command will
change the current value of the digipot.  This value should typically
be between 0.0 and 1.0, unless a 'scale' is defined in the config.
When 'scale' is defined, then this value should be  between 0.0 and
'scale'.

### [led]

The following command is available when any of the
[led config sections](Config_Reference.md#leds) are enabled.

#### SET_LED
`SET_LED LED=<config_name> RED=<value> GREEN=<value> BLUE=<value>
WHITE=<value> [INDEX=<index>] [TRANSMIT=0] [SYNC=1]`: This sets the
LED output. Each color `<value>` must be between 0.0 and 1.0. The
WHITE option is only valid on RGBW LEDs. If the LED supports multiple
chips in a daisy-chain then one may specify INDEX to alter the color
of just the given chip (1 for the first chip, 2 for the second,
etc.). If INDEX is not provided then all LEDs in the daisy-chain will
be set to the provided color. If TRANSMIT=0 is specified then the
color change will only be made on the next SET_LED command that does
not specify TRANSMIT=0; this may be useful in combination with the
INDEX parameter to batch multiple updates in a daisy-chain. By
default, the SET_LED command will sync it's changes with other ongoing
gcode commands.  This can lead to undesirable behavior if LEDs are
being set while the printer is not printing as it will reset the idle
timeout. If careful timing is not needed, the optional SYNC=0
parameter can be specified to apply the changes without resetting the
idle timeout.

#### SET_LED_TEMPLATE
`SET_LED_TEMPLATE LED=<led_name> TEMPLATE=<template_name>
[<param_x>=<literal>] [INDEX=<index>]`: Assign a
[display_template](Config_Reference.md#display_template) to a given
[LED](Config_Reference.md#leds). For example, if one defined a
`[display_template my_led_template]` config section then one could
assign `TEMPLATE=my_led_template` here. The display_template should
produce a comma separated string containing four floating point
numbers corresponding to red, green, blue, and white color settings.
The template will be continuously evaluated and the LED will be
automatically set to the resulting colors. One may set
display_template parameters to use during template evaluation
(parameters will be parsed as Python literals). If INDEX is not
specified then all chips in the LED's daisy-chain will be set to the
template, otherwise only the chip with the given index will be
updated. If TEMPLATE is an empty string then this command will clear
any previous template assigned to the LED (one can then use `SET_LED`
commands to manage the LED's color settings).

### [output_pin]

The following command is available when an
[output_pin config section](Config_Reference.md#output_pin) or
[pwm_tool config section](Config_Reference.md#pwm_tool) is
enabled.

#### SET_PIN
`SET_PIN PIN=config_name VALUE=<value>`: Set the pin to the given
output `VALUE`. VALUE should be 0 or 1 for "digital" output pins. For
PWM pins, set to a value between 0.0 and 1.0, or between 0.0 and
`scale` if a scale is configured in the output_pin config section.

### [palette2]

The following commands are available when the
[palette2 config section](Config_Reference.md#palette2) is enabled.

Palette prints work by embedding special OCodes (Omega Codes) in the
GCode file:
- `O1`...`O32`: These codes are read from the GCode stream and processed
  by this module and passed to the Palette 2 device.

The following additional commands are also available.

#### PALETTE_CONNECT
`PALETTE_CONNECT`: This command initializes the connection with the
Palette 2.

#### PALETTE_DISCONNECT
`PALETTE_DISCONNECT`: This command disconnects from the Palette 2.

#### PALETTE_CLEAR
`PALETTE_CLEAR`: This command instructs the Palette 2 to clear all of
the input and output paths of filament.

#### PALETTE_CUT
`PALETTE_CUT`: This command instructs the Palette 2 to cut the
filament currently loaded in the splice core.

#### PALETTE_SMART_LOAD
`PALETTE_SMART_LOAD`: This command start the smart load sequence on
the Palette 2. Filament is loaded automatically by extruding it the
distance calibrated on the device for the printer, and instructs the
Palette 2 once the loading has been completed. This command is the
same as pressing **Smart Load** directly on the Palette 2 screen after
the filament load is complete.

### [pid_calibrate]

The pid_calibrate module is automatically loaded if a heater is defined
in the config file.

#### PID_CALIBRATE
`PID_CALIBRATE HEATER=<config_name> TARGET=<temperature>
[WRITE_FILE=1] [TOLERANCE=0.02]`: Perform a PID calibration test. The
specified heater will be enabled until the specified target temperature
is reached, and then the heater will be turned off and on for several
cycles. If the WRITE_FILE parameter is enabled, then the file
/tmp/heattest.csv will be created with a log of all temperature samples
taken during the test. TOLERANCE defaults to 0.02 if not passed in. The
tighter the tolerance the better the calibration result will be, but how
tight you can achieve depends on how clean your sensor readings are. low
noise readings might allow 0.01, to be used, while noisy reading might
require a value of 0.03 or higher.

#### SET_HEATER_PID
`SET_HEATER_PID HEATER=<heater_name> KP=<kp> KI=<ki> KD=<kd>`: Will
allow one to manually change PID parameters of heaters without a
reload of the firmware.
HEATER takes the short name (so for `heater_generic chamber` you would only
write `chamber`)

### [pid_profile]

The PID_PROFILE module is automatically loaded if a heater is defined
in the config file.

HEATER generally takes the short name (so for `heater_generic chamber` you would
only write `chamber`)

#### PID_PROFILE
`PID_PROFILE LOAD=<profile_name> HEATER=<heater_name> [DEFAULT=<profile_name>]
[VERBOSE=<verbosity>] [KEEP_TARGET=0|1] [LOAD_CLEAN=0|1]`:
Loads the given PID_PROFILE for the specified heater. If DEFAULT is specified,
the Profile specified in DEFAULT will be loaded when then given Profile for LOAD
can't be found (like a getOrDefault method). If VERBOSE is set to LOW, minimal
info will be written in console.
If set to NONE, no console outputs will be given.
If KEEP_TARGET is set to 1, the heater will keep it's target temperature,
if set to 0, the target temperature will be set to 0.
By default the target temperature of the heater will be set to 0 so the
algorithm has time to settle in.
If LOAD_CLEAN is set to 1, the profile would be loaded as if the printer just
started up, if set to 0, the profile will retain previous heating information.
By default the information will be kept to reduce overshoot, change this value
if you encounter weird behaviour while switching profiles.

`PID_PROFILE SAVE=<profile_name> HEATER=<heater_name>`:
Saves the currently loaded profile of the specified heater to the config under
the given name.

`PID_PROFILE REMOVE=<profile_name> HEATER=<heater_name>`:
Removes the given profile from the profiles List for the current session and
config if SAVE_CONFIG is issued afterwards.

`PID_PROFILE SET_VALUES=<profile_name> HEATER=<heater_name> TARGET=<target_temp>
TOLERANCE=<tolerance>
CONTROL=<control_type> KP=<kp> KI=<ki> KD=<kd> [RESET_TARGET=0|1] [LOAD_CLEAN=0|1]`:
Creates a new profile with the given PID values, CONTROL must either be `pid` or
`pid_v`, TOLERANCE and TARGET must be specified to create a valid profile,
though the values themselves don't matter.
If KEEP_TARGET is set to 1, the heater will keep it's target temperature,
if set to 0, the target temperature will be set to 0.
By default the target temperature of the heater will be set to 0 so the
algorithm has time to settle in.
If LOAD_CLEAN is set to 1, the profile would be loaded as if the printer just
started up, if set to 0, the profile will retain previous heating information.
By default the information will be kept to reduce overshoot, change this value
if you encounter weird behaviour while switching profiles.

`PID_PROFILE GET_VALUES HEATER=<heater_name>`:
Outputs the values of the current loaded pid_profile of the given heater to the console.

### [pause_resume]

The following commands are available when the
[pause_resume config section](Config_Reference.md#pause_resume) is
enabled:

#### PAUSE
`PAUSE`: Pauses the current print. The current position is captured
for restoration upon resume.

#### RESUME
`RESUME [VELOCITY=<value>]`: Resumes the print from a pause, first
restoring the previously captured position. The VELOCITY parameter
determines the speed at which the tool should return to the original
captured position.

#### CLEAR_PAUSE
`CLEAR_PAUSE`: Clears the current paused state without resuming the
print. This is useful if one decides to cancel a print after a
PAUSE. It is recommended to add this to your start gcode to make sure
the paused state is fresh for each print.

#### CANCEL_PRINT
`CANCEL_PRINT`: Cancels the current print.

### [print_stats]

The print_stats module is automatically loaded.

#### SET_PRINT_STATS_INFO
`SET_PRINT_STATS_INFO [TOTAL_LAYER=<total_layer_count>] [CURRENT_LAYER=
<current_layer>]`: Pass slicer info like layer act and total to Kalico.
Add `SET_PRINT_STATS_INFO [TOTAL_LAYER=<total_layer_count>]` to your
slicer start gcode section and `SET_PRINT_STATS_INFO [CURRENT_LAYER=
<current_layer>]` at the layer change gcode section to pass layer
information from your slicer to Kalico.

### [probe]

The following commands are available when a
[probe config section](Config_Reference.md#probe) or
[bltouch config section](Config_Reference.md#bltouch) is enabled (also
see the [probe calibrate guide](Probe_Calibrate.md)).

#### PROBE
`PROBE [PROBE_SPEED=<mm/s>] [LIFT_SPEED=<mm/s>] [SAMPLES=<count>]
[SAMPLE_RETRACT_DIST=<mm>] [SAMPLES_TOLERANCE=<mm>]
[SAMPLES_TOLERANCE_RETRIES=<count>] [SAMPLES_RESULT=median|average]`:
Move the nozzle downwards until the probe triggers. If any of the
optional parameters are provided they override their equivalent
setting in the [probe config section](Config_Reference.md#probe).

#### QUERY_PROBE
`QUERY_PROBE`: Report the current status of the probe ("triggered" or
"open").

#### PROBE_ACCURACY
`PROBE_ACCURACY [PROBE_SPEED=<mm/s>] [SAMPLES=<count>]
[SAMPLE_RETRACT_DIST=<mm>]`: Calculate the maximum, minimum, average,
median, and standard deviation of multiple probe samples. By default,
10 SAMPLES are taken. Otherwise the optional parameters default to
their equivalent setting in the probe config section.

#### PROBE_CALIBRATE
`PROBE_CALIBRATE [SPEED=<speed>] [<probe_parameter>=<value>]`: Run a
helper script useful for calibrating the probe's z_offset. See the
PROBE command for details on the optional probe parameters. See the
MANUAL_PROBE command for details on the SPEED parameter and the
additional commands available while the tool is active. Please note,
the PROBE_CALIBRATE command uses the speed variable to move in XY
direction as well as Z.

#### Z_OFFSET_APPLY_PROBE
`Z_OFFSET_APPLY_PROBE`: Take the current Z Gcode offset (aka,
babystepping), and subtract if from the probe's z_offset.  This acts
to take a frequently used babystepping value, and "make it permanent".
Requires a `SAVE_CONFIG` to take effect.

### [probe_eddy_current]

The following commands are available when a
[probe_eddy_current config section](Config_Reference.md#probe_eddy_current)
is enabled.

#### PROBE_EDDY_CURRENT_CALIBRATE
`PROBE_EDDY_CURRENT_CALIBRATE CHIP=<config_name>`: This starts a tool
that calibrates the sensor resonance frequencies to corresponding Z
heights. The tool will take a couple of minutes to complete. After
completion, use the SAVE_CONFIG command to store the results in the
printer.cfg file.

#### LDC_CALIBRATE_DRIVE_CURRENT
`LDC_CALIBRATE_DRIVE_CURRENT CHIP=<config_name>` This tool will
calibrate the ldc1612 DRIVE_CURRENT0 register. Prior to using this
tool, move the sensor so that it is near the center of the bed and
about 20mm above the bed surface. Run this command to determine an
appropriate DRIVE_CURRENT for the sensor. After running this command
use the SAVE_CONFIG command to store that new setting in the
printer.cfg config file.

### [pwm_cycle_time]

The following command is available when a
[pwm_cycle_time config section](Config_Reference.md#pwm_cycle_time)
is enabled.

#### SET_PIN
`SET_PIN PIN=config_name VALUE=<value> [CYCLE_TIME=<cycle_time>]`:
This command works similarly to [output_pin](#output_pin) SET_PIN
commands. The command here supports setting an explicit cycle time
using the CYCLE_TIME parameter (specified in seconds). Note that the
CYCLE_TIME parameter is not stored between SET_PIN commands (any
SET_PIN command without an explicit CYCLE_TIME parameter will use the
`cycle_time` specified in the pwm_cycle_time config section).

### [quad_gantry_level]

The following commands are available when the
[quad_gantry_level config section](Config_Reference.md#quad_gantry_level)
is enabled.

#### QUAD_GANTRY_LEVEL
`QUAD_GANTRY_LEVEL [RETRIES=<value>] [RETRY_TOLERANCE=<value>]
[HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>]`: This command
will probe the points specified in the config and then make
independent adjustments to each Z stepper to compensate for tilt. See
the PROBE command for details on the optional probe parameters. The
optional `RETRIES`, `RETRY_TOLERANCE`, `HORIZONTAL_MOVE_Z` and
`ENFORCE_LIFT_SPEED` values override those options specified in the config file.

### [query_adc]

The query_adc module is automatically loaded.

#### QUERY_ADC
`QUERY_ADC [NAME=<config_name>] [PULLUP=<value>]`: Report the last
analog value received for a configured analog pin. If NAME is not
provided, the list of available adc names are reported. If PULLUP is
provided (as a value in Ohms), the raw analog value along with the
equivalent resistance given that pullup is reported.

### [query_endstops]

The query_endstops module is automatically loaded. The following
standard G-Code commands are currently available, but using them is
not recommended:
- Get Endstop Status: `M119` (Use QUERY_ENDSTOPS instead.)

#### QUERY_ENDSTOPS
`QUERY_ENDSTOPS`: Probe the axis endstops and report if they are
"triggered" or in an "open" state. This command is typically used to
verify that an endstop is working correctly.

### [resonance_tester]

The following commands are available when a
[resonance_tester config section](Config_Reference.md#resonance_tester)
is enabled (also see the
[measuring resonances guide](Measuring_Resonances.md)).

#### MEASURE_AXES_NOISE
`MEASURE_AXES_NOISE`: Measures and outputs the noise for all axes of
all enabled accelerometer chips.

#### TEST_RESONANCES
`TEST_RESONANCES AXIS=<axis> [OUTPUT=<resonances,raw_data>]
[NAME=<name>] [FREQ_START=<min_freq>] [FREQ_END=<max_freq>]
[HZ_PER_SEC=<hz_per_sec>] [CHIPS=<chip_name>]
[POINT=x,y,z] [ACCEL_PER_HZ=<accel_per_hz>] [INPUT_SHAPING=<0:1>]`: Runs
the resonance test in all configured probe points for the requested "axis" and
measures the acceleration using the accelerometer chips configured for
the respective axis. "axis" can either be X or Y, or specify an
arbitrary direction as `AXIS=dx,dy`, where dx and dy are floating
point numbers defining a direction vector (e.g. `AXIS=X`, `AXIS=Y`, or
`AXIS=1,-1` to define a diagonal direction). Note that `AXIS=dx,dy`
and `AXIS=-dx,-dy` is equivalent. `chip_name` can be one or
more configured accel chips, delimited with comma, for example
`CHIPS="adxl345, adxl345 rpi"`. If POINT or ACCEL_PER_HZ are specified,
they will override the corresponding fields configured in `[resonance_tester]`.
If `INPUT_SHAPING=0` or not set(default), disables input shaping for the resonance
testing, because it is not valid to run the resonance testing with the input shaper
enabled. `OUTPUT` parameter is a comma-separated list of which outputs
will be written. If `raw_data` is requested, then the raw
accelerometer data is written into a file or a series of files
`/tmp/raw_data_<axis>_[<chip_name>_][<point>_]<name>.csv` with
(`<point>_` part of the name generated only if more than 1 probe point
is configured or POINT is specified). If `resonances` is specified, the
frequency response is calculated (across all probe points) and written into
`/tmp/resonances_<axis>_<name>.csv` file. If unset, OUTPUT defaults to
`resonances`, and NAME defaults to the current time in
"YYYYMMDD_HHMMSS" format.

#### SHAPER_CALIBRATE
`SHAPER_CALIBRATE [AXIS=<axis>] [NAME=<name>] [FREQ_START=<min_freq>]
[FREQ_END=<max_freq>] [ACCEL_PER_HZ=<accel_per_hz>] [HZ_PER_SEC=<hz_per_sec>]
[CHIPS=<chip_name>] [MAX_SMOOTHING=<max_smoothing>] [INPUT_SHAPING=<0:1>]`:
Similarly to `TEST_RESONANCES`, runs the resonance test as configured, and tries
to find the optimal parameters for the input shaper for the requested axis
(or both X and Y axes if `AXIS` parameter is unset). If `MAX_SMOOTHING` is unset,
its value is taken from `[resonance_tester]` section, with the default being unset.
See the [Max smoothing](Measuring_Resonances.md#max-smoothing) of the
measuring resonances guide for more information on the use of this
feature. The results of the tuning are printed to the console, and the
frequency responses and the different input shapers values are written
to a CSV file(s) `/tmp/calibration_data_<axis>_<name>.csv`. Unless
specified, NAME defaults to the current time in "YYYYMMDD_HHMMSS"
format. Note that the suggested input shaper parameters can be
persisted in the config by issuing `SAVE_CONFIG` command, and if
`[input_shaper]` was already enabled previously, these parameters
take effect immediately.

### [respond]

The following standard G-Code commands are available when the
[respond config section](Config_Reference.md#respond) is enabled:
- `M118 <message>`: echo the message prepended with the configured
  default prefix (or `echo: ` if no prefix is configured).

The following additional commands are also available.

#### RESPOND
- `RESPOND MSG="<message>"`: echo the message prepended with the
  configured default prefix (or `echo: ` if no prefix is configured).
- `RESPOND TYPE=echo MSG="<message>"`: echo the message prepended with
  `echo: `.
- `RESPOND TYPE=echo_no_space MSG="<message>"`: echo the message prepended with
  `echo:` without a space between prefix and message, helpful for compatibility with some octoprint plugins that expect very specific formatting.
- `RESPOND TYPE=command MSG="<message>"`: echo the message prepended
  with `// `.  OctoPrint can be configured to respond to these messages
  (e.g.  `RESPOND TYPE=command MSG=action:pause`).
- `RESPOND TYPE=error MSG="<message>"`: echo the message prepended
  with `!! `.
- `RESPOND PREFIX=<prefix> MSG="<message>"`: echo the message
  prepended with `<prefix>`. (The `PREFIX` parameter will take
  priority over the `TYPE` parameter)

### [save_variables]

The following command is enabled if a
[save_variables config section](Config_Reference.md#save_variables)
has been enabled.

#### SAVE_VARIABLE
`SAVE_VARIABLE VARIABLE=<name> VALUE=<value>`: Saves the variable to
disk so that it can be used across restarts. All stored variables are
loaded into the `printer.save_variables.variables` dict at startup and
can be used in gcode macros. The provided VALUE is parsed as a Python
literal.

### [screws_tilt_adjust]

The following commands are available when the
[screws_tilt_adjust config section](Config_Reference.md#screws_tilt_adjust)
is enabled (also see the
[manual level guide](Manual_Level.md#adjusting-bed-leveling-screws-using-the-bed-probe)).

#### SCREWS_TILT_CALCULATE
`SCREWS_TILT_CALCULATE [DIRECTION=CW|CCW] [MAX_DEVIATION=<value>]
[HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>]`: This command will
invoke the bed screws adjustment tool. It will command the nozzle to different
locations (as defined in the config file) probing the z height and calculate
the number of knob turns to adjust the bed level. If DIRECTION is specified,
the knob turns will all be in the same direction, clockwise (CW) or
counterclockwise (CCW). See the PROBE command for details on the optional probe
parameters. IMPORTANT: You MUST always do a G28 before using this command. If
MAX_DEVIATION is specified, the command will raise a gcode error if any
difference in the screw height relative to the base screw height is greater
than the value provided. The optional `HORIZONTAL_MOVE_Z` value overrides the
`horizontal_move_z` option specified in the config file.

### [sdcard_loop]

When the [sdcard_loop config section](Config_Reference.md#sdcard_loop)
is enabled, the following extended commands are available.

#### SDCARD_LOOP_BEGIN
`SDCARD_LOOP_BEGIN COUNT=<count>`: Begin a looped section in the SD
print. A count of 0 indicates that the section should be looped
indefinitely.

#### SDCARD_LOOP_END
`SDCARD_LOOP_END`: End a looped section in the SD print.

#### SDCARD_LOOP_DESIST
`SDCARD_LOOP_DESIST`: Complete existing loops without further
iterations.

### [servo]

The following commands are available when a
[servo config section](Config_Reference.md#servo) is enabled.

#### SET_SERVO
`SET_SERVO SERVO=config_name [ANGLE=<degrees> | WIDTH=<seconds>]`: Set
the servo position to the given angle (in degrees) or pulse width (in
seconds). Use `WIDTH=0` to disable the servo output.

### [skew_correction]

The following commands are available when the
[skew_correction config section](Config_Reference.md#skew_correction)
is enabled (also see the [Skew Correction](Skew_Correction.md) guide).

#### SET_SKEW
`SET_SKEW [XY=<ac_length,bd_length,ad_length>] [XZ=<ac,bd,ad>]
[YZ=<ac,bd,ad>] [CLEAR=<0|1>]`: Configures the [skew_correction]
module with measurements (in mm) taken from a calibration print.  One
may enter measurements for any combination of planes, planes not
entered will retain their current value. If `CLEAR=1` is entered then
all skew correction will be disabled.

#### GET_CURRENT_SKEW
`GET_CURRENT_SKEW`: Reports the current printer skew for each plane in
both radians and degrees. The skew is calculated based on parameters
provided via the `SET_SKEW` gcode.

#### CALC_MEASURED_SKEW
`CALC_MEASURED_SKEW [AC=<ac_length>] [BD=<bd_length>]
[AD=<ad_length>]`: Calculates and reports the skew (in radians and
degrees) based on a measured print. This can be useful for determining
the printer's current skew after correction has been applied. It may
also be useful before correction is applied to determine if skew
correction is necessary. See [Skew Correction](Skew_Correction.md) for
details on skew calibration objects and measurements.

#### SKEW_PROFILE
`SKEW_PROFILE [LOAD=<name>] [SAVE=<name>] [REMOVE=<name>]`: Profile
management for skew_correction. LOAD will restore skew state from the
profile matching the supplied name. SAVE will save the current skew
state to a profile matching the supplied name. Remove will delete the
profile matching the supplied name from persistent memory. Note that
after SAVE or REMOVE operations have been run the SAVE_CONFIG gcode
must be run to make the changes to persistent memory permanent.

### ⚠️ [smart_effector]

Several commands are available when a
[smart_effector config section](Config_Reference.md#smart_effector) is enabled.
Be sure to check the official documentation for the Smart Effector on the
[Duet3D Wiki](https://duet3d.dozuki.com/Wiki/Smart_effector_and_carriage_adapters_for_delta_printer)
before changing the Smart Effector parameters. Also check the
[probe calibration guide](Probe_Calibrate.md).

#### SET_SMART_EFFECTOR
`SET_SMART_EFFECTOR [SENSITIVITY=<sensitivity>] [ACCEL=<accel>]
[RECOVERY_TIME=<time>]`: Set the Smart Effector parameters. When
`SENSITIVITY` is specified, the respective value is written to the
SmartEffector EEPROM (requires `control_pin` to be provided).
Acceptable `<sensitivity>` values are 0..255, the default is 50. Lower
values require less nozzle contact force to trigger (but there is a
higher risk of false triggering due to vibrations during probing), and
higher values reduce false triggering (but require larger contact
force to trigger). Since the sensitivity is written to EEPROM, it is
preserved after the shutdown, and so it does not need to be configured
on every printer startup. `ACCEL` and `RECOVERY_TIME` allow to
override the corresponding parameters at run-time, see the
[config section](Config_Reference.md#smart_effector) of Smart Effector
for more info on those parameters.

#### RESET_SMART_EFFECTOR
`RESET_SMART_EFFECTOR`: Resets Smart Effector sensitivity to its factory
settings. Requires `control_pin` to be provided in the config section.

### [stepper_enable]

The stepper_enable module is automatically loaded.

#### SET_STEPPER_ENABLE
`SET_STEPPER_ENABLE STEPPER=<config_name> ENABLE=[0|1]`: Enable or
disable only the given stepper. This is a diagnostic and debugging
tool and must be used with care. Disabling an axis motor does not
reset the homing information. Manually moving a disabled stepper may
cause the machine to operate the motor outside of safe limits. This
can lead to damage to axis components, hot ends, and print surface.

### [temperature_fan]

The following command is available when a
[temperature_fan config section](Config_Reference.md#temperature_fan)
is enabled.

#### SET_TEMPERATURE_FAN_TARGET
`SET_TEMPERATURE_FAN_TARGET temperature_fan=<temperature_fan_name>
[target=<target_temperature>] [min_speed=<min_speed>]
[max_speed=<max_speed>]`: Sets the target temperature for a
temperature_fan. If a target is not supplied, it is set to the
specified temperature in the config file. If speeds are not supplied,
no change is applied.

### [tmcXXXX]

The following commands are available when any of the
[tmcXXXX config sections](Config_Reference.md#tmc-stepper-driver-configuration)
are enabled.

#### DUMP_TMC
`DUMP_TMC STEPPER=<name> [REGISTER=<name>]`: This command will read all TMC
driver registers and report their values. If a REGISTER is provided, only
the specified register will be dumped.

#### INIT_TMC
`INIT_TMC STEPPER=<name>`: This command will initialize the TMC
registers. Needed to re-enable the driver if power to the chip is
turned off then back on.

#### SET_TMC_CURRENT
`SET_TMC_CURRENT STEPPER=<name> CURRENT=<amps> HOLDCURRENT=<amps>`:
This will adjust the run and hold currents of the TMC driver.
`HOLDCURRENT` is not applicable to tmc2660 drivers.
When used on a driver which has the `globalscaler` field (tmc5160 and tmc2240),
if StealthChop2 is used, the stepper must be held at standstill for >130ms so
that the driver executes the AT#1 calibration.

#### SET_TMC_FIELD
`SET_TMC_FIELD STEPPER=<name> FIELD=<field> VALUE=<value> VELOCITY=<value>`:
This will alter the value of the specified register field of the TMC driver.
This command is intended for low-level diagnostics and debugging only
because changing the fields during run-time can lead to undesired and
potentially dangerous behavior of your printer. Permanent changes
should be made using the printer configuration file instead. No sanity
checks are performed for the given values.
A VELOCITY can also be specified instead of a VALUE. This velocity is
converted to the 20bit TSTEP based value representation. Only use the VELOCITY
argument for fields that represent velocities.

### [toolhead]

The toolhead module is automatically loaded.

#### SET_VELOCITY_LIMIT
`SET_VELOCITY_LIMIT [VELOCITY=<value>] [ACCEL=<value>]
[MINIMUM_CRUISE_RATIO=<value>] [SQUARE_CORNER_VELOCITY=<value>]
[X_VELOCITY=<value>] [X_ACCEL=<value>] [Y_VELOCITY=<value>] [Y_ACCEL=<value>]
[Z_VELOCITY=<value>] [Z_ACCEL=<value>]`: This
command can alter the velocity limits that were specified in the
printer config file. See the
[printer config section](Config_Reference.md#printer) for a
description of each parameter.
X_VELOCITY, X_ACCEL, Y_VELOCITY, Y_ACCEL, Z_VELOCITY and Z_ACCEL are only
available if the kinematic supports it.

### RESET_VELOCITY_LIMIT
`RESET_VELOCITY_LIMIT`: This command resets the velocity limits to the values
specified in the printer config file. See the
[printer config section](Config_Reference.md#printer) for a
description of each parameter.

#### ⚠️ SET_KINEMATICS_LIMIT

`SET_KINEMATICS_LIMIT [<X,Y,Z>_ACCEL=<value>] [<X,Y,Z>_VELOCITY=<value>]
[SCALE=<0:1>]`: change the per-axis limits.

This command is only available when `kinematics` is set to either
[`limited_cartesian`](./Config_Reference.md#cartesian-kinematics-with-limits-for-x-and-y-axes)
or
[`limited_corexy`](./Config_Reference.md#corexy-kinematics-with-limits-for-x-and-y-axes).
The velocity argument is not available on CoreXY. With no arguments, this
command responds with the movement direction with the most acceleration or
velocity.

### ⚠️ [tools_calibrate]

The following commands are available when the
[tools_calibrate config section](Config_Reference.md#tools_calibrate) is enabled.

#### TOOL_CALIBRATE_QUERY_PROBE
`TOOL_CALIBRATE_QUERY_PROBE`: Query the current calibration probe state.

#### TOOL_LOCATE_SENSOR
`TOOL_LOCATE_SENSOR`: Locate the sensor relative to the initial tool. The initial
tool is the 0 offset, which other tools are calibrated against.

Before running `TOOL_LOCATE_SENSOR`, position your primary toolhead centered over
the calibration probe.

#### TOOL_CALIBRATE_TOOL_OFFSET
`TOOL_CALIBRATE_TOOL_OFFSET`: After locating the sensor with your initial tool,
position each additional tool over the sensor and run `TOOL_CALIBRATE_TOOL_OFFSET`
to find their offsets.

#### TOOL_CALIBRATE_SAVE_TOOL_OFFSET
`TOOL_CALIBRATE_SAVE_TOOL_OFFSET MACRO=<macro_name> VARIABLE=<variable_name> [VALUE="({x:0.6f}, {y:0.6f}, {z:0.6f})"]`:
Save the last calibration result to a macro variable.

`TOOL_CALIBRATE_SAVE_TOOL_OFFSET SECTION= ATTRIBUTE= [VALUE="{x:0.6f}, {y:0.6f}, {z:0.6f}"]`:
Save the last calibration result to a field in your configuration. Calibration data saved this way will not take effect until after a `RESTART` of your printer.

### [trad_rack]

The following commands are available when the
[trad_rack config section](Config_Reference.md#trad_rack) is enabled.

#### TR_HOME
`TR_HOME`: Homes the selector.

#### TR_GO_TO_LANE
`TR_GO_TO_LANE LANE=<lane index>`: Moves the selector to the specified
lane.

#### TR_LOAD_LANE
`TR_LOAD_LANE LANE=<lane index> [RESET_SPEED=<0|1>]`: Ensures filament
is loaded into the module for the specified lane by prompting the user
to insert filament, loading filament from the module into the
selector, and retracting the filament back into the module.
If RESET_SPEED is 1, the bowden move speed used for the
specified LANE will be reset to spool_pull_speed from the
[trad_rack config section](Config_Reference.md#trad_rack)
(see [bowden speeds](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Tuning.md#bowden-speeds)
for details on how the bowden speed settings are used). If not
specified, RESET_SPEED defaults to 1.

#### TR_LOAD_TOOLHEAD
`TR_LOAD_TOOLHEAD LANE=<lane index>|TOOL=<tool index>
[MIN_TEMP=<temperature>] [EXACT_TEMP=<temperature>]
[BOWDEN_LENGTH=<mm>] [EXTRUDER_LOAD_LENGTH=<mm>]
[HOTEND_LOAD_LENGTH=<mm>]`: Loads filament from the specified lane or
tool into the toolhead*. Either LANE or TOOL must be specified. If
both are specified, then LANE takes precedence. If there is already an
"active lane" because the toolhead has been loaded beforehand, it will
be unloaded before loading the new filament. If `MIN_TEMP` is
specified and it is higher than the extruder's current temperature,
then the extruder will be heated to at least `MIN_TEMP` before
unloading/loading; the current extruder temperature target may be used
instead if it is higher than `MIN_TEMP`, and if not then
[tr_last_heater_target](https://github.com/Annex-Engineering/TradRack/blob/main/docs/kalico/Save_Variables.md)
may be used. If `EXACT_TEMP` is specified, the extruder will be heated
to `EXACT_TEMP` before unloading/loading, regardless of any other
temperature setting. If any of the optional length parameters are
specified, they override the corresponding settings in the
[trad_rack config section](Config_Reference.md#trad_rack).

\* see the [Tool Mapping document](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Tool_Mapping.md)
for details on the difference between lanes and tools and how they
relate to each other.

#### T0, T1, T2, etc.
`T<tool index>`: Equivalent to calling
`TR_LOAD_TOOLHEAD TOOL=<tool index>`. All of the optional parameters
accepted by the TR_LOAD_TOOLHEAD command can also be used with these
commands.

#### TR_UNLOAD_TOOLHEAD
`TR_UNLOAD_TOOLHEAD [MIN_TEMP=<temperature>]
[EXACT_TEMP=<temperature>]`: Unloads filament from the toolhead and
back into its module. If `MIN_TEMP` is specified and it is higher than
the extruder's current temperature, then the extruder will be heated
to at least `MIN_TEMP` before unloading; the current extruder
temperature target may be used instead if it is higher than
`MIN_TEMP`, and if not then
[tr_last_heater_target](https://github.com/Annex-Engineering/TradRack/blob/main/docs/kalico/Save_Variables.md)
may be used. If `EXACT_TEMP` is specified, the extruder will be heated
to `EXACT_TEMP` before unloading/loading, regardless of any other
temperature setting.

#### TR_SERVO_DOWN
`TR_SERVO_DOWN [FORCE=<0|1>]`: Moves the servo to bring the drive gear
down. The selector must be moved to a valid lane before using this
command, unless FORCE is 1. If not specified, FORCE defaults to 0. The
FORCE parameter is unsafe for normal use and should only be used when
the servo is not attached to Trad Rack's carriage.

#### TR_SERVO_UP
`TR_SERVO_UP`: Moves the servo to bring the drive gear up.

#### TR_SET_ACTIVE_LANE
`TR_SET_ACTIVE_LANE LANE=<lane index>`: Tells Trad Rack to assume the
toolhead has been loaded with filament from the specified lane. The
selector's position will also be inferred from this lane, and the
selector motor will be enabled if it isn't already.

#### TR_RESET_ACTIVE_LANE
`TR_RESET_ACTIVE_LANE`: Tells Trad Rack to assume the toolhead has
not been loaded.

#### TR_RESUME
`TR_RESUME`: Completes necessary actions for Trad Rack to recover
(and/or checks that Trad Rack is ready to continue), then resumes the
print if all of those actions complete successfully. For example, if
the print was paused due to a failed toolchange, then this command
would retry the toolchange and then resume the print if the toolchange
completes successfully. You will be prompted to use this command if
Trad Rack has paused the print and requires user interaction or
confirmation before attempting to recover and resume.

#### TR_LOCATE_SELECTOR
`TR_LOCATE_SELECTOR`: Ensures the position of Trad Rack's selector is
known so that it is ready for a print. If the user needs to take an
action, they will be prompted to do so and the print will be paused
(for example if the selector sensor is triggered but no active lane is
set). The user_wait_time config option from the
[trad_rack config section](Config_Reference.md#trad_rack) determines
how long Trad Rack will wait for user action before automatically
unloading the toolhead and resuming. In addition, the save_active_lane
config option determines whether this command can infer the "active
lane" from a value saved before the last restart if the selector
filament sensor is triggered but no active lane is currently set.
It is recommended to call this command in the print start gcode.

#### TR_NEXT
`TR_NEXT`: You will be prompted to use this command if Trad Rack
requires user confirmation before continuing an action.

#### TR_SYNC_TO_EXTRUDER
`TR_SYNC_TO_EXTRUDER`: Syncs Trad Rack's filament driver to the
extruder during printing, as well as during any extrusion moves within
toolhead loading or unloading that would normally involve only the
extruder. See the
[Extruder syncing document](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Extruder_Syncing.md)
for more details. If you want the filament driver to be synced to the extruder
on every startup without having to call this command, you can set
sync_to_extruder to True in the
[trad_rack config section](Config_Reference.md#trad_rack).

#### TR_UNSYNC_FROM_EXTRUDER
`TR_UNSYNC_FROM_EXTRUDER`: Unsyncs Trad Rack's filament driver from
the extruder during printing, as well as during any extrusion moves
within toolhead loading or unloading that normally involve only the
extruder. This is the default behavior unless you have set
sync_to_extruder to True in the
[trad_rack config section](Config_Reference.md#trad_rack).

#### TR_SERVO_TEST
`TR_SERVO_TEST [ANGLE=<degrees>]`: Moves the servo to the specified
ANGLE relative to the down position. If ANGLE is not specified, the
servo will be moved to the up position defined by servo_up_angle from
the [trad_rack config section](Config_Reference.md#trad_rack).
This command is meant for testing different servo angles in order
to find the correct value for servo_up_angle.

#### TR_CALIBRATE_SELECTOR
`TR_CALIBRATE_SELECTOR`: Initiates the process of calibrating
lane_spacing, as well as the min, endstop, and max positions of the
selector motor. You will be guided through the selector calibration
process via messages in the console.

#### TR_SET_HOTEND_LOAD_LENGTH
`TR_SET_HOTEND_LOAD_LENGTH VALUE=<value>|ADJUST=<adjust>`: Sets the
value of hotend_load_length, overriding its value from the
[trad_rack config section](Config_Reference.md#trad_rack). Does not
persist across restarts. If the VALUE parameter is used,
hotend_load_length will be set to the value passed in. If the ADJUST
parameter is used, the adjustment will be added to the current value
of hotend_load_length.

#### TR_DISCARD_BOWDEN_LENGTHS
`TR_DISCARD_BOWDEN_LENGTHS [MODE=[ALL|LOAD|UNLOAD]]`: Discards saved
values for "bowden_load_length" and/or "bowden_unload_length" (see
[bowden lengths](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Tuning.md#bowden-lengths)
for details on how these settings are used). These settings will each
be reset to the value of `bowden_length` from the
[trad_rack config section](Config_Reference.md#trad_rack), and empty
dictionaries will be saved for
[tr_calib_bowden_load_length and tr_calib_bowden_unload_length](https://github.com/Annex-Engineering/TradRack/blob/main/docs/kalico/Save_Variables.md).
"bowden_load_length" and tr_calib_bowden_load_length will be
affected if MODE=LOAD is specified, "bowden_unload_length" and
tr_calib_bowden_unload_length will be affected if MODE=UNLOAD is
specified, and all 4 will be affected if MODE=ALL is specified. If not
specified, MODE defaults to ALL.

#### TR_ASSIGN_LANE
`TR_ASSIGN_LANE LANE=<lane index> TOOL=<tool index>
[SET_DEFAULT=<0|1>]`:
Assigns the specified LANE to the specified TOOL. If SET_DEFAULT is 1,
LANE will become the default lane for the tool. If not specified,
SET_DEFAULT defaults to 0.

#### TR_SET_DEFAULT_LANE
`TR_SET_DEFAULT_LANE LANE=<lane index> [TOOL=<tool index>]`: If TOOL
is specified, LANE will be set as the default lane for the tool. If
TOOL is not specified, LANE will be set as the default lane for its
currently-assigned tool.

#### TR_RESET_TOOL_MAP
`TR_RESET_TOOL_MAP`: Resets lane/tool mapping. Each tool will be
mapped to a lane group consisting of a single lane with the same index
as the tool.

#### TR_PRINT_TOOL_MAP
`TR_PRINT_TOOL_MAP`: Prints a table of the lane/tool mapping to the
console, with rows corresponding to tools and columns corresponding to
lanes.

#### TR_PRINT_TOOL_GROUPS
`TR_PRINT_TOOL_GROUPS`: Prints a list of lanes assigned to each tool
to the console. If a tool has multiple lanes assigned to it, the
default lane will be indicated.

### [tuning_tower]

The tuning_tower module is automatically loaded.

#### TUNING_TOWER
`TUNING_TOWER COMMAND=<command> PARAMETER=<name> START=<value>
[SKIP=<value>] [FACTOR=<value> [BAND=<value>]] | [STEP_DELTA=<value>
STEP_HEIGHT=<value>]`: A tool for tuning a parameter on each Z height
during a print. The tool will run the given `COMMAND` with the given
`PARAMETER` assigned to a value that varies with `Z` according to a
formula. Use `FACTOR` if you will use a ruler or calipers to measure
the Z height of the optimum value, or `STEP_DELTA` and `STEP_HEIGHT`
if the tuning tower model has bands of discrete values as is common
with temperature towers. If `SKIP=<value>` is specified, the tuning
process doesn't begin until Z height `<value>` is reached, and below
that the value will be set to `START`; in this case, the `z_height`
used in the formulas below is actually `max(z - skip, 0)`.  There are
three possible combinations of options:
- `FACTOR`: The value changes at a rate of `factor` per millimeter.
  The formula used is: `value = start + factor * z_height`. You can
  plug the optimum Z height directly into the formula to determine the
  optimum parameter value.
- `FACTOR` and `BAND`: The value changes at an average rate of
  `factor` per millimeter, but in discrete bands where the adjustment
  will only be made every `BAND` millimeters of Z height.
  The formula used is:
  `value = start + factor * ((floor(z_height / band) + .5) * band)`.
- `STEP_DELTA` and `STEP_HEIGHT`: The value changes by `STEP_DELTA`
  every `STEP_HEIGHT` millimeters. The formula used is:
  `value = start + step_delta * floor(z_height / step_height)`.
  You can simply count bands or read tuning tower labels to determine
  the optimum value.

### [virtual_sdcard]

Kalico supports the following standard G-Code commands if the
[virtual_sdcard config section](Config_Reference.md#virtual_sdcard) is
enabled:
- List SD card: `M20`
- Initialize SD card: `M21`
- Select SD file: `M23 <filename>`
- Start/resume SD print: `M24`
- Pause SD print: `M25`
- Set SD position: `M26 S<offset>`
- Report SD print status: `M27`

In addition, the following extended commands are available when the
"virtual_sdcard" config section is enabled.

#### SDCARD_PRINT_FILE
`SDCARD_PRINT_FILE FILENAME=<filename>`: Load a file and start SD
print.

#### SDCARD_RESET_FILE
`SDCARD_RESET_FILE`: Unload file and clear SD state.

### [z_thermal_adjust]

The following commands are available when the
[z_thermal_adjust config section](Config_Reference.md#z_thermal_adjust)
is enabled.

#### SET_Z_THERMAL_ADJUST
`SET_Z_THERMAL_ADJUST [ENABLE=<0:1>] [TEMP_COEFF=<value>] [REF_TEMP=<value>]`:
Enable or disable the Z thermal adjustment with `ENABLE`. Disabling does not
remove any adjustment already applied, but will freeze the current adjustment
value - this prevents potentially unsafe downward Z movement. Re-enabling can
potentially cause upward tool movement as the adjustment is updated and applied.
`TEMP_COEFF` allows run-time tuning of the adjustment temperature coefficient
(i.e. the `TEMP_COEFF` config parameter). `TEMP_COEFF` values are not saved to
the config. `REF_TEMP` manually overrides the reference temperature typically
set during homing (for use in e.g. non-standard homing routines) - will be reset
automatically upon homing.

### ⚠️ [z_calibration]

The following commands are available when a
[z_calibration config section](Config_Reference.md#z_calibration) is enabled
(also see the [Z-Calibration guide](Z_Calibration.md)):
- `CALIBRATE_Z`: This calibrates the current offset between the nozzle and
  the print surface.
- `PROBE_Z_ACCURACY [PROBE_SPEED=<mm/s>] [LIFT_SPEED=<mm/s>] [SAMPLES=<count>]
  [SAMPLE_RETRACT_DIST=<mm>]`: Calculate the maximum, minimum,
  average, median, and standard deviation of multiple probe
  samples. By default, 10 SAMPLES are taken. Otherwise the optional
  parameters default to their equivalent setting in the z_calibration or probe
  config section.
*Note* that appropriate macros and/or configurations are needed to attach
and detach a mag-probe for these commands!

### [z_tilt]

The following commands are available when the
[z_tilt config section](Config_Reference.md#z_tilt) is enabled.

#### Z_TILT_ADJUST
`Z_TILT_ADJUST [HORIZONTAL_MOVE_Z=<value>] [ENFORCE_LIFT_SPEED=0|1]
[<probe_parameter>=<value>]`: This command will probe the points specified in the
config and then make independent adjustments to each Z stepper to compensate for tilt.
See the PROBE command for details on the optional probe parameters. The optional
`HORIZONTAL_MOVE_Z` and `ENFORCE_LIFT_SPEED` values override those options specified in
the config file

### [z_tilt_ng]

The following commands are available when the
[z_tilt_ng config section](Config_Reference.md#z_tilt_ng) is enabled.

#### Z_TILT_ADJUST
`Z_TILT_ADJUST [HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>]
[INCREASING_THRESHOLD=<value>]`: This
command will probe the points specified in the config and then make independent
adjustments to each Z stepper to compensate for tilt. See the PROBE command for
details on the optional probe parameters. The optional `HORIZONTAL_MOVE_Z`
value overrides the `horizontal_move_z` option specified in the config file.
INCREASING_THRESHOLD sets the increasing_threshold parameter of z_tilt.
The follwing commands are availabe when the parameter "extra_points" is
configured in the z_tilt_ng section:
- `Z_TILT_CALIBRATE [AVGLEN=<value>]`: This command does multiple probe
  runs similar to Z_TILT_ADJUST, but with the additional points given in
  "extra_points". This leads to a more balanced bed adjustment in case the
  bed is not perfectly flat. The command averages the error over multiple
  runs and continues until the error does not decrease any further. It
  calculates values for the z_offsets config parameter, which will in turn
  be used by T_TILT_ADJUST to achieve the same accuracy without the extra
  points.
- `Z_TILT_AUTODETECT [AVGLEN=<value>] [DELTA=<value>]`: This command
  determines the positions of the pivot points for each stepper motor.
  It works silimar to Z_TILT_CALIBRATE, but it probes the bed with intential
  small misalgnments of the steppers. The amount of misalignment can be
  configured with the DELTA paramter. It iterates until the calculated
  positions cannot be improved any further. This is can be lengthy procedure.

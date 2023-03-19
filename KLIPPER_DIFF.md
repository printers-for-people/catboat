# Differences from Klipper

We list all of our changes from Klipper here. We separate these into two
sections: user-visible changes, which provide new capabilities that Klipper
(currently) lacks, such as new configuration options, new board support, etc;
and implementation changes, which are not user-visible, but improve the codebase
in ways implementers and tinkerers with Catboat itself would be interested in.

## User-visible changes

### Support for Anycubic Trigorilla boards

Due to a manufacturing flaw, Trigorilla boards (used in the Anycubiv Kobra,
Kobra Max and Kobra Plus) cannot run Klipper without physical modifications. We
introduce a `tmctrigorilla` configuration section, allowing configuring stepper
drivers for these boards. This allows us to support any printer controlled by
such a board.

As part of this, we added a config file for the Anycubic Kobra. While in theory,
we could also support the Kobra Max and Kobra Plus, someone would have to
contribute a tested config.

## Implementation changes

### No Python 2

Python 2 is unsupported, and has been for a while. It has no place being used
anywhere, for anything. We've removed any use of Python 2 from Catboat.

### Fix `newlib-4.3.0` support on STM boards

Previously, ARM-targeted firmware (especially on STM boards) would fail to link
with `newlib-4.3.0`. As this is the default version shipping on at least one
distro, this is an issue that will only get worse with time. We fixed this by
adding an exception index table, which allows us to compile normally, at a small
size penalty.

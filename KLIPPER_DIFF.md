# Differences from Klipper

We list all of our changes from Klipper here. We separate these into two
sections: user-visible changes, which provide new capabilities that Klipper
(currently) lacks, such as new configuration options, new board support, etc;
and implementation changes, which are not user-visible, but improve the codebase
in ways implementers and tinkerers with Catboat itself would be interested in.

## User-visible changes

### Support for unmodded Anycubic Kobra

This is related to the Trigorilla driver support. In current Klipper, supporting
the Anycubic Kobra's board without modifying the hardware is not possible; we
introduce a workaround, which allows us to support this board (and printer) out
of the box.

In theory, we could also support the Kobra Max and Kobra Plus, but this would
require a contributed config.

### Support for Anycubic Trigorilla boards

Due to a manufacturing flaw, Trigorilla boards (used in the Kobra, Kobra Max and
Kobra Plus) cannot run Klipper without physical modifications. We introduce a
`tmctrigorilla` section, allowing configuring stepper drives for these boards,
which allows support for any printer running such a board.

## Implementation changes

### No Python 2

Python 2 is unsupported, and has been for a while. It has no place being used
anywhere, for anything. We've removed any use of Python 2 from Catboat.

### Fix `newlib-4.3.0` support on STM boards

Previously, STM-targeted firmware would fail with `newlib-4.3.0`, which
currently ships as default on at least one distro. We've fixed this by adding an
exception index table, which allows us to compile normally, at a small size
penalty.

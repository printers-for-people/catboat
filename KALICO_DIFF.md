# Differences from Kalico

We list all of our changes from Kalico here. We separate these into two
sections: user-visible changes, which provide new capabilities that Kalico
(currently) lacks, such as new configuration options, new board support, etc;
and implementation changes, which are not user-visible, but improve the codebase
in ways implementers and tinkerers with Catboat itself would be interested in.

## User-visible changes

### Support for Anycubic Trigorilla boards

Due to a manufacturing flaw, Trigorilla boards (used in the Anycubic Kobra,
Kobra Max and Kobra Plus) cannot run Kalico without physical modifications. We
introduce a `tmctrigorilla` configuration section, allowing configuring stepper
drivers for these boards. This allows us to support any printer controlled by
such a board.

As part of this, we added a config file for the Anycubic Kobra.
We have also ported the mainline Kalico configs for the Kobra Plus to use the
tmctrigorilla configuration.
While in theory we could also support the Kobra Max, someone would have to
contribute a tested config.

### Arch install

The old Arch installation script has been removed. Instead, there are new
installation instructions [on the wiki][arch-install]. While these are aimed
primarily at Arch Linux ARM, they should work for baseline Arch as well.

### Systemd unit file

A new unit file is provided in `catboat.service`. In particular, the file
follows proper practices, including logging to the systemd journal instead of a
file.

[arch-install]: https://github.com/printers-for-people/catboat/wiki/Arch-Linux-ARM-install

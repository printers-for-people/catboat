# Catboat

## What is this?

An improved 3D printer control firmware, forked from
[Klipper](https://www.klipper3d.org), designed to support a large range of
printers. Unlike other firmware, Catboat uses a combination of a 3D printer
control board (for basic movement, heating, etc) and a standalone separate
computer (usually an [SBC](https://en.wikipedia.org/wiki/Single-board_computer))
for anything more complex like interpreting G-code, configuration etc.

Catboat is designed to be easy to set up, easy to configure, and to support the
same hardware as Klipper.

## What are the goals of this project?

### Convenience for 'non-techies'

Setting up Klipper, unless you're going for a _very_ specific setup, is
frustrating, time-consuming, and requires far more technical knowledge than
should be necessary. Furthermore, the 'blessed' setup method is
under-documented, hard to diagnose issues with, and _needlessly_ so. This is
because Klipper currently fails to use some well-established distribution
technologies which could make this effortless, or nearly so. Furthermore,
certain aspects of the Klipper setup are needlessly complex even _if_ you use a
blessed setup.

Catboat aims to make the process of its setup as easy as possible: you don't
have to know anything about how Linux works, or even what an IP address is in
most cases. Furthermore, we provide pre-made setups (of varying levels of
'pre-made') for those who just want a plug-and-play solution. At the same time,
we don't neglect the needs of the more technically-oriented. Throughout, we aim
for documentational clarity: _everything_ should be spelled out in enough detail
that someone could replicate our work, and see the logic behind it, without
having to guess or experiment.

### Klipper compatibility

Klipper is, on the whole, a brilliant idea, and continues to improve. We don't
want to exclude ourselves (or our users) from these improvements. Additionally,
we want to make moving from Klipper to Catboat as effortless as possible. We
make it a goal that 'any valid Klipper config is also a valid Catboat config';
all you have to do is copy over your old config, and you're golden.

We also regularly merge upstream Klipper into Catboat: no feature in upstream
Klipper should be missing from Catboat for long.

### Ecosystem diversity

Klipper suffers from extreme ecosystemic homogeny: if you don't want to fund the
RPi Foundation (and there are good reasons not to), you're left out in the cold.
Furthermore, even in this case, the documentation is spotty at best, and
misleading at worst. This is 100% a problem that _could_ be solved, and Catboat
aims to do so. In particular, we aim to provide two things:

* A very general, easy-to-run configuration that works on _any_ Linux-capable
  SBC; and
* A collection of _multiple_ 'blessed' devices, which we have tested and ensure
  work, and provide additional 'plug-and-play' levels of support for.

We want to give our users options, and not chain them to a single source, which
is brittle at best, dangerous at worst. We have the means to do so, and Catboat
aims to be the end by which we do it.

### Feature richness, even for more niche cases

Klipper has historically been quite strict in which features it will and won't
include, aiming to support only those features that would be useful to a very
general use case. While this is understandable, we also feel it is needlessly
limiting, as Klipper's strongest feature is its ability to improve existing
printers with very little change needed. Additionally, what is niche to one
person may be _very_ core to others, and it's arguable that Klipper's definition
of 'niche' is somewhat skewed.

Catboat, on the other hand, tries to provide features that are useful, even if
they're somewhat niche. This includes workarounds for tricky printer boards,
additional capabilities that may not often be useful, and additional devices
which Klipper may deem not fitting their goals. This is not to say we accept any
and every feature: merely that we seek to cater to use cases that Klipper may
not consider central enough to their goals.

## How do I use this?

Look at the wiki for more information.

## How is this different from Klipper?

See the [description file](KLIPPER_DIFF). At the same time, Catboat maintains
the principle of 'any valid Klipper config is also a valid Catboat config'; if
you have a working Klipper config, you can use it with Catboat and still expect
it to work. If this doesn't happen, it's a bug: please report it!

## I want to help - what should I do?

## Licensing and other such things

We maintain the same license as Klipper, which we you can find in the [license
file](COPYING). This is `GPLv3-only` according to SPDX code. 

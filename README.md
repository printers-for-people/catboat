# Catboat

## What is this?

An improved 3D printer control firmware, forked from
[Kalico](https://kalico.gg), designed to support a large range of
printers. Unlike other firmware, Catboat uses a combination of a 3D printer
control board (for basic movement, heating, etc) and a standalone separate
computer (usually an [SBC](https://en.wikipedia.org/wiki/Single-board_computer))
for anything more complex like interpreting G-code, configuration etc.

Catboat is designed to be easy to set up, easy to configure, and to support the
same hardware as Kalico.

## What are the goals of this project?

### Convenience for 'non-techies'

Setting up Kalico, unless you're going for a _very_ specific setup, is
frustrating, time-consuming, and requires far more technical knowledge than
should be necessary. Furthermore, the 'blessed' setup method is
under-documented, hard to diagnose issues with, and _needlessly_ so. This is
because Kalico currently fails to use some well-established distribution
technologies which could make this effortless, or nearly so. Furthermore,
certain aspects of the Kalico setup are needlessly complex even _if_ you use a
blessed setup.

Catboat aims to make the process of its setup as easy as possible: you don't
have to know anything about how Linux works, or even what an IP address is in
most cases. Furthermore, we provide pre-made setups (of varying levels of
'pre-made') for those who just want a plug-and-play solution. At the same time,
we don't neglect the needs of the more technically-oriented. Throughout, we aim
for documentational clarity: _everything_ should be spelled out in enough detail
that someone could replicate our work, and see the logic behind it, without
having to guess or experiment.

### Kalico compatibility

Kalico is, on the whole, a brilliant idea, and continues to improve. We don't
want to exclude ourselves (or our users) from these improvements. Additionally,
we want to make moving from Kalico to Catboat as effortless as possible. We
make it a goal that 'any valid Kalico config is also a valid Catboat config';
all you have to do is copy over your old config, and you're golden.

We also regularly merge upstream Kalico into Catboat: no feature in upstream
Kalico should be missing from Catboat for long.

### Ecosystem diversity

Kalico suffers from extreme ecosystemic homogeny: if you don't want to fund the
RPi Foundation (and there are good reasons not to), you're left out in the cold.
Furthermore, even in this case, the documentation is spotty at best, and
misleading at worst. This is 100% a problem that _could_ be solved, and Catboat
aims to do so. In particular, we aim to provide two things:

* A general, easy-to-run configuration process, which works on most
  Linux-capable devices; and
* A collection of _multiple_ 'blessed' devices, which we have tested and ensure
  work, and provide additional 'plug-and-play' levels of support for.

We want to give our users options, and not chain them to a single source, which
is brittle at best, dangerous at worst. We have the means to do so, and Catboat
aims to be the end by which we do it.

### Feature richness, even for more niche cases

Kalico has historically been quite strict in which features it will and won't
include, aiming to support only those features that would be useful to a very
general use case. While this is understandable, we also feel it is needlessly
limiting, as Kalico's strongest feature is its ability to improve existing
printers with very little change needed. Additionally, what is niche to one
person may be _very_ core to others, and it's arguable that Kalico's definition
of 'niche' is somewhat skewed.

Catboat, on the other hand, tries to provide features that are useful, even if
they're somewhat niche. This includes workarounds for tricky printer boards,
additional capabilities that may not often be useful, and additional devices
which Kalico may deem not fitting their goals. This is not to say we accept any
and every feature: merely that we seek to cater to use cases that Kalico may
not consider central enough to their goals.

## How do I use this?

For a jump start, try a [KIAUH Install](https://github.com/printers-for-people/catboat/wiki/KIAUH-Install). Look at the [Catboat wiki](https://github.com/printers-for-people/catboat/wiki) for more information.

## How is this different from Kalico?

See the [description file](KALICO_DIFF.md). At the same time, Catboat maintains
the principle of 'any valid Kalico config is also a valid Catboat config'; if
you have a working Kalico config, you can use it with Catboat and still expect
it to work. If this doesn't happen, it's a bug: please report it!

## I want to help - what should I do?

Test the code on your printer and provide feedback to [Catboat issues](https://github.com/printers-for-people/catboat/issues), good or bad.

## Licensing and other such things

We maintain the same license as Kalico, which we you can find in the [license
file](COPYING). This is `GPLv3-only` according to SPDX code. 

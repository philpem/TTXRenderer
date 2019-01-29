Pardus remote client (Satellite)
================================

Pardus is a digital signage and display platform for the Raspberry Pi. It allows a fleet of displays (called *Satellites*) to display content which is centrally managed from a central server (the *Uplink*). Satellites may be assigned *selector codes* to allow them to be addressed individually or as a group.

Satellites can be pre-synchronised in advance, or receive data (graphical 'assets', text templates and text content) from the Uplink. This allows displays to be updated rapidly, with a minimum of bandwidth consumed. Display changes can be scheduled well in advance, or sent for immediate display.

This is effectively a Python-based ground-up reimplementation of the idea behind Infobeamer, but with tweaks to allow greater bandwidth efficiency when slow Uplink-to-Satellite links are in use (e.g. 8-20kbaud short-range ISM-band radio).

**This repository contains the code for the Satellites.**


Installation
------------

TODO: Write this when Satellite has been completely developed

  - Install the fonts in `~/.fonts` (symlinking may also work)
  - Copy all your assets (images, templates, etc.) into the `assets` directory
  - Configure Satellite's sync method and timing
  - Sync once to download the Carousel
  - Set up some kind of init script to make Satellite run on boot
  - Reboot


TODO
----

  - Viewtext renderer: add support for the Bedstead font
    * This will require support for font switching (using the Condensed variant at twice the pixel size for double-height)
    * This will also require a change to the font mapping



Credits
-------

  * `MODE7GX*.TTF` (Galax Teletext) font by Galax, http://www.galax.xyz/TELETEXT/INDEX.HTM
  * Bedstead font (CC0 Public Domain) by Ben Harris, Simon Tatham and Marnanel Thurman, https://bjh21.me.uk/bedstead/

[modeline]: # ( vim: set expandtab fenc=utf-8 spell spl=en: )

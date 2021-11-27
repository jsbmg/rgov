

# rgov - Recreation.gov Campground Checker

[![img](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

`rgov` is a command line program to check for campground availability on Recreation.gov. It is intended to be easy to use, and provides an interactive mode for easily searching for and checking multiple campgrounds for availability at once. It can also be used as a unix daemon that sends push notifications to your phone or other device when available sites are found.  

## Installation

Requires: Python 3.6+

From pypi:

$ `pip install rgov`

Manually:

$ `git clone https://github.com/jsbmg/rgov`

$ `cd rgov`

$ `pip install . pyproject.toml`

In order to receive notifications, you will need to make an account with Pushsafer and configure it for use with your phone or device of choice. 

https://www.pushsafer.com/

## Quick Start
The easiest way to run rgov is with the `run` command. Use it to build a list of campgrounds, enter your dates of stay, and start checking for available sites:

`$ rgov run` 

The `search`, `check`, and `daemon` commands provide the same functionality as above but non-interactively.

Run $ `rgov` to see a list of all commands, and $ `rgov help <command>` to see more information about each one. 

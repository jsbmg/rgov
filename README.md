
# Table of Contents

1.  [rgov - Recreation.gov Campground Checker](#orgef9b9d8)
    1.  [Installation](#org9713277)
    2.  [Quick Start](#org44d7cf0)
    3.  [Commands](#orgb1d63b5)
        1.  [Search](#org637d06c)
        2.  [Check](#org3990b98)
        3.  [Daemon](#orgaad63e2)
        4.  [Reindex](#org9b91123)
    4.  [Todo](#org3da19f3)


<a id="orgef9b9d8"></a>

# rgov - Recreation.gov Campground Checker

[![img](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)

`rgov` is a command line program to check for campground availability on
Recreation.gov. While other recreation.gov scrapers exist, this one aims to
also provide a simple search command for quickly finding the campsite ids that
are necessary for checking campgrounds. It also includes a daemon to check for
availability automatically.

It is becoming increasingly more difficult to find campsites on Recreation.gov,
so if you use this tool, please use it with discretion!


<a id="org9713277"></a>

## Installation

Requires: Python 3.6+

With pip:

$ `pip install rgov`


<a id="org44d7cf0"></a>

## Quick Start

First, find your campgrounds id (usually a six-digit number):

$ `rgov search <campground>`

You can also find the id in the url of the campgound's page on Recreation.gov.

To check if there are available sites (separate multiple ids with spaces):

$ `rgov check <campground id(s)> --date <mm-dd-yyyy> --length <number of nights>`

If there aren't, you can run automated checks. Start the daemon with your
preferred method of notification (either a notification program or your own
shell command):

$ `rgov daemon <campground id(s)> --date <...> --length <...> --command <your command>`

This will check every five minutes.


<a id="orgb1d63b5"></a>

## Commands


<a id="org637d06c"></a>

### Search

Search for campground ids for user with the `check` and `daemon` commands:

$ `rgov search <search term(s)>`

Once you get the id, you can use that to check for availability.

If the index has been built with descriptions (see the reindex command),
you can search in the campground descriptions like this:

$ `rgov search <search term(s)> --descriptions`


<a id="org3990b98"></a>

### Check

The check command quickly searches campgrouns for availability and prints which
sites are available, if any.

$ `rgov check <campground id(s)> -date <mm-dd-yyyy> -length <nights>`

1.  Options

    <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


    <colgroup>
    <col  class="org-left" />

    <col  class="org-left" />
    </colgroup>
    <tbody>
    <tr>
    <td class="org-left"><code>--date[-d]</code></td>
    <td class="org-left">The date to check (mm-dd-yyyy)</td>
    </tr>


    <tr>
    <td class="org-left"><code>--length[-l]</code></td>
    <td class="org-left">The number of days you'll be staying</td>
    </tr>


    <tr>
    <td class="org-left"><code>--url[-u]</code></td>
    <td class="org-left">Show the url of campground</td>
    </tr>
    </tbody>
    </table>


<a id="orgaad63e2"></a>

### Daemon

Similiar to the `check` command, the `daemon` command starts a daemon that
checks for availability every five minutes in the background. The method of
notification is up to you, and can either be a notification program or custom
shell command.

$ `rgov daemon <campground id(s)> --date <mm-dd-yyyy> --length <nights> --notifier <notification program> --command <shell command>`

1.  Options

    <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


    <colgroup>
    <col  class="org-left" />

    <col  class="org-left" />
    </colgroup>
    <tbody>
    <tr>
    <td class="org-left"><code>--date[-d]</code></td>
    <td class="org-left">The date to check (mm-dd-yyyy)</td>
    </tr>


    <tr>
    <td class="org-left"><code>--length[-l]</code></td>
    <td class="org-left">The number of days you'll be staying</td>
    </tr>


    <tr>
    <td class="org-left"><code>--notifier[-n]</code></td>
    <td class="org-left">Specify a notification program to use (e.g. herbe)</td>
    </tr>


    <tr>
    <td class="org-left"><code>--command[-c]</code></td>
    <td class="org-left">The shell command to run if site(s) are found</td>
    </tr>
    </tbody>
    </table>


<a id="org9b91123"></a>

### Reindex

This only needs to be run if you wish to search for campgrounds by description,
which is useful for finding campground by city, region, or park name. It will
download the facility data from recreation.gov, and build the index from that.

You can add the descriptions to the search index like this:

$ `rgov reindex --with-descriptions`

For any reason, you can remove the descriptions with:

$ `rgov reindex`


<a id="org3da19f3"></a>

## Todo

[ ] Add additional ways for notifications to be sent (e.g. phone/email)

[ ] Write more testing

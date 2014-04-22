#
# Copyright 2014 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import ConfigParser
import sys
import os
from copy import copy

import cProfile
from line_profiler import LineProfiler
import datetime

import zipline
from zipline import run_algo

DEFAULTS = {
    'start': '2012-01-01',
    'end': '2012-12-31',
    'data_frequency': 'daily',
    'capital_base': '10e6',
    'source': 'yahoo',
    'symbols': 'AAPL'
}

def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Parse any conf_file specification
    # We make this parser with add_help=False so that
    # it doesn't parse -h and print help.
    conf_parser = argparse.ArgumentParser(
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
        )
    conf_parser.add_argument("-c", "--conf_file",
                             help="Specify config file",
                             metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = copy(DEFAULTS)

    if args.conf_file:
        config = ConfigParser.SafeConfigParser()
        config.read([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        description="Zipline version %s." % zipline.__version__,
        parents=[conf_parser]
    )

    parser.set_defaults(**defaults)

    parser.add_argument('--algofile', '-f')
    parser.add_argument('--data-frequency',
                        choices=('minute', 'daily'))
    parser.add_argument('--start', '-s')
    parser.add_argument('--end', '-e')
    parser.add_argument('--capital_base')
    parser.add_argument('--source', choices=('yahoo',))
    parser.add_argument('--symbols')
    parser.add_argument('--profiler-type', choices=('cProfile',
                                                    'line_profiler'))
    args = parser.parse_args(remaining_argv)

    run_algo(**vars(args))

    return(0)

if __name__ == "__main__":
    sys.exit(main())

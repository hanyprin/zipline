import argparse
import ConfigParser
import sys
sys.path.append('qexec')
import os

import pandas as pd

import cProfile
from line_profiler import LineProfiler
import datetime

import zipline
from zipline import TradingAlgorithm

try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import TerminalFormatter
    from pygments.styles import STYLE_MAP
    PYGMENTS = True
except:
    PYGMENTS = False

def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Parse any conf_file specification
    # We make this parser with add_help=False so that
    # it doesn't parse -h and print help.
    conf_parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Turn off help, so we print all options in response to -h
        add_help=False
        )
    conf_parser.add_argument("-c", "--conf_file",
                             help="Specify config file",
                             metavar="FILE")
    args, remaining_argv = conf_parser.parse_known_args()

    defaults = {
            'start': '2012-01-01',
            'end': '2012-12-31',
            'data_frequency': 'daily',
            'capital_base': '10e6',
            'source': 'yahoo',
            'symbols': 'AAPL'
    }

    if args.conf_file:
        config = ConfigParser.SafeConfigParser()
        config.read([args.conf_file])
        defaults.update(dict(config.items("Defaults")))

    # Parse rest of arguments
    # Don't suppress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
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

    print args
    setup(args)

    return(0)

def setup(args):
    start = pd.Timestamp(args.start, tz='UTC')
    end = pd.Timestamp(args.end, tz='UTC')

    symbols = args.symbols.split(',')

    if args.source == 'yahoo':
        source = zipline.data.load_bars_from_yahoo(stocks=symbols, start=start, end=end)
    else:
        raise NotImplementedError('Source %s not implemented.' % args.source)

    with open(args.algofile, 'r') as fd:
        algo_text = fd.read()

    analyze_fname = os.path.splitext(args.algofile)[0] + '_analyze.py'
    if os.path.exists(analyze_fname):
        with open(analyze_fname, 'r') as fd:
            # Simply append
            algo_text += fd.read()

    if PYGMENTS:
        highlight(algo_text, PythonLexer(), TerminalFormatter(), outfile=sys.stdout)
    else:
        print algo_text

    algo = TradingAlgorithm(script=algo_text,
                            capital_base=float(args.capital_base))

    perf = algo.run(source)

if __name__ == "__main__":
    sys.exit(main())

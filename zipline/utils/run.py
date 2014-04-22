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

import pandas as pd
import os
import sys

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


def run_algo(**kwargs):
    start = pd.Timestamp(kwargs['start'], tz='UTC')
    end = pd.Timestamp(kwargs['end'], tz='UTC')

    symbols = kwargs['symbols'].split(',')

    if kwargs['source'] == 'yahoo':
        source = zipline.data.load_bars_from_yahoo(stocks=symbols, start=start, end=end)
    else:
        raise NotImplementedError('Source %s not implemented.' % kwargs['source'])

    algo_fname = kwargs['algofile']
    with open(algo_fname, 'r') as fd:
        algo_text = fd.read()

    analyze_fname = os.path.splitext(algo_fname)[0] + '_analyze.py'
    if os.path.exists(analyze_fname):
        with open(analyze_fname, 'r') as fd:
            # Simply append
            algo_text += fd.read()

    if PYGMENTS:
        highlight(algo_text, PythonLexer(), TerminalFormatter(), outfile=sys.stdout)
    else:
        print algo_text

    algo = TradingAlgorithm(script=algo_text,
                            capital_base=float(kwargs['capital_base']))

    perf = algo.run(source)

    return perf

import argparse

def parse(pargs=None):

    parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                      description='Sample for Signal concepts')

    parser.add_argument('-c', required=True,
                        default='rand1',
                        help=('Specific data to be read in, 1. xx.SH, 2. randN, 3. xx.list\n'
                            'For example:\n'
                            '    -c xxx'
                            ))

    parser.add_argument('--fdate', required=False, default='20150101',
                        help='Starting date in YYYYMMDD format')

    parser.add_argument('--tdate', required=False, default='20210831',
                        help='Ending date in YYYYMMDD format')

    parser.add_argument('--cash', required=False, action='store',
                        type=float, default=100000,
                        help=('Cash to start with'))

    parser.add_argument('--plot', '-p', nargs='?', required=False,
                        metavar='kwargs', const=True,
                        help=('Plot the read data applying any kwargs passed\n'
                              '\n'
                              'For example:\n'
                              '\n'
                              '  --plot style="candle" (to plot candles)\n'))

    if pargs is not None:
        return parser.parse_args(pargs)

    return parser.parse_args()

#!/usr/bin/python3
"""
Test program for the time_finder, date_finder, and
size_measurement_finder modules.

Run from the nlp/finder folder.

"""

import re
import os
import sys
import json
import argparse
from collections import namedtuple

import time_finder as tf
import date_finder as df

_VERSION_MAJOR = 0
_VERSION_MINOR = 3
_MODULE_NAME = 'test_finder.py'

#
# time results
#

_TIME_RESULT_FIELDS = [
    'text',
    'hours',
    'minutes',
    'seconds',
    'fractional_seconds',
    'am_pm',
    'timezone',
    'gmt_delta_sign',
    'gmt_delta_hours',
    'gmt_delta_minutes'
]
_TimeResult = namedtuple('_TimeResult', _TIME_RESULT_FIELDS)
_TimeResult.__new__.__defaults__ = (None,) * len(_TimeResult._fields)

#
# date results
#

_DATE_RESULT_FIELDS = [
    'text',
    'year',
    'month',
    'day'
]
_DateResult = namedtuple('_DateResult', _DATE_RESULT_FIELDS)
_DateResult.__new__.__defaults__ = (None,) * len(_DateResult._fields)


_MODULE_TIME = 'time'
_MODULE_DATE = 'date'
_MODULE_MEAS = 'meas'


###############################################################################
def _compare_results(
        computed_values,
        expected_values,
        sentence,
        field_list):

    # check that len(computed) == len(expected)
    if len(computed_values) != len(expected_values):
        print('\tMismatch in computed vs. expected results: ')
        print('\tSentence: {0}'.format(sentence))
        print('\tComputed: ')
        for v in computed_values:
            print('\t\t{0}'.format(v))
        print('\tExpected: ')
        for v in expected_values:
            print('\t\t{0}'.format(v))

        print('NAMEDTUPLE: ')
        for k,v in v._asdict().items():
            print('{0} => {1}'.format(k,v))

        return

    # check fields for each result
    failures = []
    for i, t in enumerate(computed_values):
        # iterate over fields of current result
        for field, value in t._asdict().items():
            expected = expected_values[i]._asdict()
            # compare only those fields in _RESULT_FIELDS
            if field in field_list:
                if value != expected[field]:
                    # append as namedtuples
                    failures.append( (t, expected_values[i]) )

    if len(failures) > 0:
        print(sentence)
        for f in failures:
            # extract fields with values not equal to None
            c = [ (k,v) for k,v in f[0]._asdict().items()
                  if v is not None and k in field_list]
            e = [ (k,v) for k,v in f[1]._asdict().items() if v is not None]
            print('\tComputed: {0}'.format(c))
            print('\tExpected: {0}'.format(e))
    

###############################################################################
def _run_tests(module_type, test_data):

    for sentence, expected_values in test_data.items():

        if _MODULE_TIME == module_type:

            # run time_finder, get JSON result, convert to TimeValue list
            json_result = tf.run(sentence)
            json_data = json.loads(json_result)
            computed_values = [tf.TimeValue(**d) for d in json_data]

            # check computed vs. expected results
            _compare_results(
                computed_values,
                expected_values,
                sentence,
                _TIME_RESULT_FIELDS
            )

        elif _MODULE_DATE == module_type:

            # run date_finder on the next test sentence
            json_result = df.run(sentence)
            json_data = json.loads(json_result)
            computed_values = [df.DateValue(**d) for d in json_data]

            _compare_results(
                computed_values,
                expected_values,
                sentence,
                _DATE_RESULT_FIELDS
            )


###############################################################################
def _test_time_finder():

    # h12_am_pm format
    test_data = {
        'The times are 4 am, 5PM, 10a.m, 8 a.m, 9 pm., .':[
            _TimeResult(text='4 am',  hours=4,  am_pm=tf.STR_AM),
            _TimeResult(text='5PM',   hours=5,  am_pm=tf.STR_PM),
            _TimeResult(text='10a.m', hours=10, am_pm=tf.STR_AM),
            _TimeResult(text='8 a.m', hours=8,  am_pm=tf.STR_AM),
            _TimeResult(text='9 pm.', hours=9,  am_pm=tf.STR_PM)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h12m format
    test_data = {
        'The times are 4:08, 10:14, and 11:59':[
            _TimeResult(text='4:08',  hours=4,  minutes=8),
            _TimeResult(text='10:14', hours=10, minutes=14),
            _TimeResult(text='11:59', hours=11, minutes=59)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h12m_am_pm format
    test_data = {
        'The times are 5:09 am, 9:41 P.M., and 10:02 AM.':[
            _TimeResult(text='5:09 am',
                        hours=5,  minutes=9,  am_pm=tf.STR_AM),
            _TimeResult(text='9:41 P.M.',
                        hours=9,  minutes=41, am_pm=tf.STR_PM),
            _TimeResult(text='10:02 AM.',
                        hours=10, minutes=2,  am_pm=tf.STR_AM)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h12ms_am_pm format
    test_data = {
        'The times are 06:10:37 am, 10:19:36P.M., and 1:02:03AM':[
            _TimeResult(text='06:10:37 am',
                        hours=6,  minutes=10, seconds=37, am_pm=tf.STR_AM),
            _TimeResult(text='10:19:36P.M.',
                        hours=10, minutes=19, seconds=36, am_pm=tf.STR_PM),
            _TimeResult(text='1:02:03AM',
                        hours=1,  minutes=2,  seconds=3,  am_pm=tf.STR_AM)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h12msf_am_pm format
    test_data = {
        'The times are 7:11:39:012345 am and 11:41:22.22334p.m..':[
            _TimeResult(text='7:11:39:012345 am',
                        hours=7, minutes=11, seconds=39,
                        fractional_seconds='012345', am_pm=tf.STR_AM),
            _TimeResult(text='11:41:22.22334p.m.',
                        hours=11, minutes=41, seconds=22,
                        fractional_seconds='22334', am_pm=tf.STR_PM)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h24m format
    test_data = {
        'The times are 14:12, 01:27, 10:27, and T23:43.':[
            _TimeResult(text='14:12',  hours=14, minutes=12),
            _TimeResult(text='01:27',  hours=1,  minutes=27),
            _TimeResult(text='10:27',  hours=10,  minutes=27),
            _TimeResult(text='T23:43', hours=23, minutes=43)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)
    
    # h24ms format
    test_data = {
        'The times are 01:03:24 and t14:15:16.':[
            _TimeResult(text='01:03:24',  hours=1,  minutes=3,  seconds=24),
            _TimeResult(text='t14:15:16', hours=14, minutes=15, seconds=16)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h24ms_with_timezone format
    test_data = {
        'The times are 040837CEST, 112345 PST, and T093000 Z':[
            _TimeResult(text='040837CEST',
                        hours=4,  minutes=8,  seconds=37, timezone='CEST'),
            _TimeResult(text='112345 PST',
                        hours=11, minutes=23, seconds=45, timezone='PST'),
            _TimeResult(text='T093000 Z',
                        hours=9,  minutes=30, seconds=0, timezone='UTC')
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h24ms with GMT delta
    test_data = {
        'The times are T192021-0700 and 14:45:15+03:30':[
            _TimeResult(text='T192021-0700',
                        hours=19, minutes=20, seconds=21, gmt_delta_sign='-',
                        gmt_delta_hours=7, gmt_delta_minutes=0),
            _TimeResult(text='14:45:15+03:30',
                        hours=14, minutes=45, seconds=15, gmt_delta_sign='+',
                        gmt_delta_hours=3, gmt_delta_minutes=30)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h24msf format
    test_data = {
        'The times are 04:08:37.81412, 19:20:21.532453, and 08:11:40:123456':[
            _TimeResult(text='04:08:37.81412',
                        hours=4,  minutes=8,  seconds=37,
                        fractional_seconds='81412'),
            _TimeResult(text='19:20:21.532453',
                        hours=19, minutes=20, seconds=21,
                        fractional_seconds='532453'),
            _TimeResult(text='08:11:40:123456',
                        hours=8, minutes=11, seconds=40,
                        fractional_seconds='123456'),
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # ISO 8601 format
    test_data = {
        'The times are 04, 0622, 11:23, 08:23:32Z, 09:24:33+12, ' \
        '10:25:34-04:30, and 11:26:35.012345+0600':[
            _TimeResult(text='04', hours=4),
            _TimeResult(text='0622', hours=6,  minutes=22),
            _TimeResult(text='11:23', hours=11, minutes=23),
            _TimeResult(text='08:23:32Z',
                        hours=8, minutes=23, seconds=32, timezone='UTC'),
            _TimeResult(text='09:24:33+12',
                        hours=9, minutes=24, seconds=33,
                        gmt_delta_sign='+', gmt_delta_hours=12),
            _TimeResult(text='10:25:34-04:30',
                        hours=10, minutes=25, seconds=34, gmt_delta_sign='-',
                        gmt_delta_hours=4, gmt_delta_minutes=30),
            _TimeResult(text='11:26:35.012345+0600',
                        hours=11, minutes=26, seconds=35,
                        fractional_seconds='012345', gmt_delta_sign='+',
                        gmt_delta_hours=6, gmt_delta_minutes=0)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)

    # h24m and h24ms (no colon) formats
    test_data = {
        'The times are 0613, t0613, 0613Z, 0613-03:30, 0613-0330, 0613+03, ' \
        '1124, 232120, 010203, and 120000':[
            _TimeResult(text='0613',  hours=6,  minutes=13),
            _TimeResult(text='t0613', hours=6,  minutes=13),
            _TimeResult(text='0613Z', hours=6,  minutes=13, timezone='UTC'),
            _TimeResult(text='0613-03:30',
                        hours=6, minutes=13, gmt_delta_sign='-',
                        gmt_delta_hours=3, gmt_delta_minutes=30),
            _TimeResult(text='0613-0330',
                        hours=6, minutes=13, gmt_delta_sign='-',
                        gmt_delta_hours=3, gmt_delta_minutes=30),
            _TimeResult(text='0613+03',
                        hours=6, minutes=13, gmt_delta_sign='+',
                        gmt_delta_hours=3),
            _TimeResult(text='1124',   hours=11, minutes=24),
            _TimeResult(text='232120', hours=23, minutes=21,  seconds=20),
            _TimeResult(text='010203', hours=1,  minutes=2,   seconds=3),
            _TimeResult(text='120000', hours=12, minutes=0,   seconds=0)
        ]
    }

    _run_tests(_MODULE_TIME, test_data)


###############################################################################
def _test_date_finder():

    # ISO 8601 8-digit format
    test_data = {
        'The date 20121128 is in iso_8 format.':[
            _DateResult(text='20121128', year=2012, month=11, day=28)
        ]
    }

    _run_tests(_MODULE_DATE, test_data)

    # ISO YYYYMMDD format
    test_data = {
        'The dates 2012/07/11 and 2014/03/15 are in iso_YYYYMMDD format.':[
            _DateResult(text='2012/07/11', year=2012, month=7, day=11),
            _DateResult(text='2014/03/15', year=2014, month=3, day=15)
        ]
    }

    _run_tests(_MODULE_DATE, test_data)    

    # ISO YYMMDD format
    test_data = {
        'The dates 16-01-04 and 19-02-28 are in iso_YYMMDD format.':[
            _DateResult(text='16-01-04', year=16, month=1, day=4),
            _DateResult(text='19-02-28', year=19, month=2, day=28)
        ]
    }

    _run_tests(_MODULE_DATE, test_data)    

    # ISO sYYYYMMDD format
    test_data = {
        'The date +2012-11-28 is in iso_sYYYYMMDD format.':[
            _DateResult(text='2012-11-28', year=2012, month=11, day=28),            
        ]
    }

    _run_tests(_MODULE_DATE, test_data)    

    # American month/day/year format
    test_data = {
        'The dates 11/28/2012, 1/3/2012, and 02/17/15 are in ' \
        'American month/day/year format.':[
            _DateResult(text='11/28/2012', year=2012, month=11, day=28),
            _DateResult(text='1/3/2012',   year=2012, month=1,  day=3),
            _DateResult(text='02/17/15',   year=15,   month=2,  day=17)
        ]
    }

    _run_tests(_MODULE_DATE, test_data)
    
    
###############################################################################
def _get_version():
    return '{0} {1}.{2}'.format(_MODULE_NAME, _VERSION_MAJOR, _VERSION_MINOR)


###############################################################################
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Run validation tests on the time finder module.'
    )
    
    parser.add_argument('-v', '--version',
                        help='show version and exit',
                        action='store_true')
    parser.add_argument('-d', '--debug',
                        help='print debug information to stdout',
                        action='store_true')

    args = parser.parse_args()

    if 'version' in args and args.version:
        print(_get_version())
        sys.exit(0)

    if 'debug' in args and args.debug:
        tf.enable_debug()

        
    _test_time_finder()
    _test_date_finder()

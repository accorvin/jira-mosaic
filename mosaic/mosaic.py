#! /usr/bin/env python3

import argparse
import datetime
import jira
import logging
import sys

from .queries import query_map


log = logging.getLogger('mosaic')
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(('%(asctime)s - %(name)s - '
                               '%(levelname)s - %(message)s'))
ch.setFormatter(formatter)
log.addHandler(ch)

DEFAULT_TYPES = 'bug, story, task'


def parse_args():
    desc = 'A utility for calculating various metrics from JIRA data'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-s', '--server',
                        default='https://projects.engineering.redhat.com',
                        help='The JIRA server to connect to')
    parser.add_argument('-c', '--cert',
                        default='/etc/pki/tls/certs/ca-bundle.crt',
                        help=('The path to the certification bundle to use '
                              'when connecting to the JIRA server'))
    parser.add_argument('-p', '--project', default='FACTORY',
                        help='The JIRA project to get metrics for')

    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=14)
    parser.add_argument('-b', '--begin-date', default=str(two_weeks_ago),
                        help=('The beginning of the date range to calculate '
                              'metrics for'))
    parser.add_argument('-e', '--end-date', default=str(today),
                        help=('The end of the date range to calculate '
                              'metrics for'))

    parser.add_argument('-q', '--query', action='append',
                        help=('The query to execute. Specify multiple '
                              'arguments by repeating this argument'))
    parser.add_argument('-a', '--query-argument', default=None,
                        help=('The argument to be passed to the query. This '
                              'will be passed to all queries if multiple are '
                              'specified'))
    parser.add_argument('-v', '--verbose', default=False,
                        action='store_true',
                        help='Enable debug logging')
    parser.add_argument('-l', '--list', action='store_true',
                        default=False,
                        help='Print a list of available queries')
    parser.add_argument('-r', '--rolling', action='store_true',
                        default=False,
                        help=('Use data for currently in progress stories '
                              'when performing calculations for date ranges '
                              'that include today. Not supported by all '
                              'queries'))
    parser.add_argument('--query-append', default='',
                        help=('An additional string to be appended to all '
                              'JIRA search queries'))
    parser.add_argument('-t', '--types', default=DEFAULT_TYPES,
                        help=('An optional comma separated string argument '
                              'to query for specific types of tickets '
                              'eg:\'bug, story\' '))

    return vars(parser.parse_args())


def check_queries(queries):
    for query in queries:
        if query not in query_map:
            msg = ('No known query exists for query named {query}. '
                   'Supported queries are {query_options}')
            raise Exception(msg.format(query=query,
                                       query_options=str(query_map.keys())))


def run(args, client=None):
    if not client:
        client_args = {
            'server': args['server'],
            'options': dict(verify=args['cert']),
            'kerberos': True
        }
        client = jira.client.JIRA(**client_args)

    query_vars = {
        'project': args['project'],
        'begin_date': args['begin_date'],
        'end_date': args['end_date'],
        'argument': args['query_argument'],
        'rolling': args.get('rolling', False),
        'query_append': args.get('query_append', ''),
        'types': args.get('types', DEFAULT_TYPES)
    }

    check_queries(args['query'])
    queries = []
    for query in args['query']:
        queries.append(query_map[query](query, client, query_vars, log))

    for query in queries:
        query.set_defaults()
        query.build_query()
        query.run()
        query.build_results()

    if 'auto_mode' in args and args['auto_mode']:
        return queries[0].result
    else:
        for query in queries:
            query.print_results()


def main():
    args = parse_args()
    if args['verbose']:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    if args['list']:
        msg = 'The following queries are supported: [{queries}]'
        queries = ', '.join(query_map.keys())
        log.info(msg.format(queries=queries))
        sys.exit(0)
    elif 'query' not in args or len(args['query']) == 0:
        msg = 'You must specify at least one query with the -q argument.'
        log.error(msg)
        sys.exit(1)
    run(args)


if __name__ == '__main__':
    main()

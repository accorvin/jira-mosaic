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


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--server',
                        default='https://projects.engineering.redhat.com')
    parser.add_argument('-c', '--cert',
                        default='/etc/pki/tls/certs/ca-bundle.crt')
    parser.add_argument('-p', '--project', default='FACTORY')

    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=14)
    parser.add_argument('-b', '--begin-date', default=str(two_weeks_ago))
    parser.add_argument('-e', '--end-date', default=str(today))

    parser.add_argument('-q', '--query', action='append')
    parser.add_argument('-a', '--query-argument', default=None)
    parser.add_argument('-v', '--verbose', default=False,
                        action='store_true',
                        help='Enable debug logging')
    parser.add_argument('-l', '--list', action='store_true',
                        help='Print a list of available queries')

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
        'argument': args['query_argument']
    }

    check_queries(args['query'])
    queries = []
    for query in args['query']:
        queries.append(query_map[query](query, client, query_vars))

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
    elif 'queries' not in args or len(args['queries']) == 0:
        msg = 'You must specify at least one query with the -q argument.'
        log.error(msg)
        sys.exit(1)
    run(args)


if __name__ == '__main__':
    main()

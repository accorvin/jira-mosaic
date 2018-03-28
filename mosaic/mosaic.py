#! /usr/bin/env python3

import argparse
import datetime
import jira
import logging

from .queries import query_map


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

    parser.add_argument('-q', '--query', required=True, action='append')
    parser.add_argument('-a', '--query-argument', default=None)
    parser.add_argument('-v', '--verbose', default=False,
                        action='store_true',
                        help='Enable debug logging')

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
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    run(args)


if __name__ == '__main__':
    main()

#! /usr/bin/env python3

import argparse
import datetime
import jira
import logging

from queries import query_map


logging.basicConfig(level=logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--server',
                        default='https://projects.engineering.redhat.com')
    parser.add_argument('-c', '--cert', default=None)
    parser.add_argument('-p', '--project', default='FACTORY')

    today = datetime.date.today()
    two_weeks_ago = today - datetime.timedelta(days=14)
    parser.add_argument('-b', '--begin-date', default=str(two_weeks_ago))
    parser.add_argument('-e', '--end-date', default=str(today))

    parser.add_argument('-q', '--query', required=True, action='append')

    return parser.parse_args()


def check_queries(queries):
    for query in queries:
        if query not in query_map:
            msg = ('No known query exists for query named {query}. '
                   'Supported queries are {query_options}')
            raise Exception(msg.format(query=query,
                                       query_options=str(query_map.keys())))


def main():
    args = parse_args()
    client_args = {
        'server': args.server,
        'options': dict(verify=args.cert),
        'kerberos': True
    }
    client = jira.client.JIRA(**client_args)

    query_vars = {
        'project': args.project,
        'begin_date': args.begin_date,
        'end_date': args.end_date
    }

    check_queries(args.query)
    queries = []
    for query in args.query:
        queries.append(query_map[query](query, client, query_vars))

    for query in queries:
        query.set_defaults()
        query.build_query()
        query.run()
        query.build_results()

    for query in queries:
        query.print_results()


if __name__ == '__main__':
    main()

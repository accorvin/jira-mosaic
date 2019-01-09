import yaml


def results_to_text(query, results):
    for result in results:
        yield query.template.format(**result)


def results_to_csv(query, results):
    templ = "{begin_date},{end_date},{value},{project},{qualifier},{rolling}"
    for result in results:
        # Set a default value
        result['qualifier'] = result.get('qualifier', '')
        yield templ.format(
            project=query.vars['project'],
            rolling=query.rolling,
            **result)


def results_to_yaml(query, results):
    yield yaml.dumps(results)
    yield "---"


renderer_map = {
    'text': results_to_text,
    'csv': results_to_csv,
    'yaml': results_to_yaml,
}

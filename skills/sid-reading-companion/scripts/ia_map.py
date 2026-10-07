"""Optional IA graph checks and Mermaid projection; no semantic/source verification.

Learning-order proposals never modify Knowledge Compiler prerequisites.
"""
import argparse
import json
from pathlib import Path
import re

RELATIONS = {'is_a', 'part_of', 'supports', 'contrasts', 'limits', 'references', 'conflicts', 'depends_on'}
BASES = {'source_explicit', 'source_interpretation', 'pedagogical_proposal', 'unresolved'}


class InvalidMap(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidMap(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def acyclic(ids, edges):
    adjacency = {node: [] for node in ids}
    for edge in edges:
        adjacency[edge['from']].append(edge['to'])
    active, done = set(), set()
    def visit(node):
        if node in active:
            return False
        if node in done:
            return True
        active.add(node)
        if not all(visit(child) for child in adjacency[node]):
            return False
        active.remove(node)
        done.add(node)
        return True
    return all(visit(node) for node in adjacency)


def label(value):
    # Prevent caller labels from becoming Mermaid syntax. Keep Unicode.
    return value.replace('#', '#35;').replace('&', '#38;').replace('"', '#quot;').replace('<', '#60;').replace('>', '#62;').replace('\n', ' ').replace('\r', ' ').replace('|', '#124;')


def compile_map(data):
    require(isinstance(data, dict), 'Map must be an object')
    require(text(data.get('goal')), 'Missing learning goal')
    views = data.get('views', [])
    require(isinstance(views, list) and bool(views) and len(set(views)) == len(views) and all(v in {'conceptual', 'learning'} for v in views), 'Invalid views')
    values = data.get('nodes')
    require(isinstance(values, list) and 0 < len(values) <= 256, 'Invalid node batch')
    nodes = {}
    for node in values:
        require(isinstance(node, dict), 'Invalid node')
        nid = node.get('id')
        require(isinstance(nid, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', nid) and nid not in nodes, 'Invalid/duplicate node ID')
        require(nid.lower() != 'end', 'Reserved Mermaid node ID')
        require(text(node.get('label_vi')) and text(node.get('definition')), 'Missing label/definition')
        require(node.get('source_status') == 'read' and isinstance(node.get('source_locators'), list) and bool(node['source_locators']) and all(text(x) for x in node['source_locators']), 'Diagram claim requires read source with locators')
        require(node.get('knowledge_level') in {'L1', 'L2', 'L3', 'L4'}, 'Invalid knowledge task level')
        require(node.get('in_scope') is True, 'Node outside selected scope')
        nodes[nid] = node
    edge_ids = set()
    unresolved = []
    projected = {'conceptual': [], 'learning': []}
    for view, field in [('conceptual', 'relations'), ('learning', 'learning_order')]:
        edges = data.get(field, [])
        require(isinstance(edges, list), 'Invalid edge list')
        for edge in edges:
            require(isinstance(edge, dict), 'Invalid edge')
            require(text(edge.get('id')) and edge['id'] not in edge_ids, 'Duplicate/missing edge ID')
            edge_ids.add(edge['id'])
            require(edge.get('from') in nodes and edge.get('to') in nodes, 'Unknown edge endpoint')
            require(text(edge.get('label_vi')), 'Missing edge label')
            require(edge.get('basis') in BASES, 'Missing/invalid edge basis')
            if view == 'conceptual':
                require(edge.get('relation_type') in RELATIONS, 'Invalid conceptual relation')
                require(edge['basis'] != 'pedagogical_proposal', 'Pedagogical edges belong in learning_order')
            else:
                require(edge.get('relation_type') in {'suggested_order', 'learning_prerequisite'}, 'Invalid learning relation')
                require(text(edge.get('reason')), 'Learning relation needs reason')
                if edge['relation_type'] == 'suggested_order':
                    require(edge['basis'] in {'pedagogical_proposal', 'unresolved'}, 'Suggested order must be labelled proposal')
            locators = edge.get('source_locators', [])
            require(isinstance(locators, list) and all(text(x) for x in locators), 'Invalid edge locators')
            if edge['basis'] in {'source_explicit', 'source_interpretation'}:
                require(bool(locators), 'Source-based edge requires locator')
            if edge['basis'] == 'unresolved':
                unresolved.append({'view': view, **edge})
            else:
                projected[view].append(edge)
    if 'learning' in views:
        require(acyclic(nodes, projected['learning']), 'Learning-order cycle; review affected branch before rendering')
    diagrams = {}
    for view in views:
        lines = ['flowchart LR']
        for nid, node in nodes.items():
            lines.append(f'    {nid}["{label(node["label_vi"])}"]')
        for edge in projected[view]:
            qualifier = 'đề xuất: ' if edge['basis'] == 'pedagogical_proposal' else 'diễn giải: ' if edge['basis'] == 'source_interpretation' else ''
            lines.append(f'    {edge["from"]} -->|"{label(qualifier + edge["label_vi"])}"| {edge["to"]}')
        diagrams[view] = '\n'.join(lines)
    return {'views': diagrams, 'edges': projected, 'unresolved': unresolved,
            'warnings': ['Select a focused subset if the diagram is hard to read.'],
            'semantic_verified': False, 'source_locators_verified': False,
            'mermaid_render_verified': False, 'learner_evidence': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        source, output = Path(args.input).resolve(), Path(args.output).resolve()
        require(source != output and not output.exists(), 'Output must be a new file')
        result = compile_map(json.loads(source.read_text(encoding='utf-8-sig')))
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
        print(json.dumps({'ok': True, 'semantic_verified': False}))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=True))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

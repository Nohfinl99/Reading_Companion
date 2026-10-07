"""Compile caller-grounded knowledge nodes into a bounded reading plan.

Checks graph/route/artifact invariants; does not retrieve or judge semantic truth.
"""
import argparse
import json
import re
from pathlib import Path

TASKS = {'explain', 'extract', 'compare', 'map', 'assess', 'transfer', 'continue'}
LEVELS = {'L1', 'L2', 'L3', 'L4'}
RELATIONS = {'supports', 'contrasts', 'limits', 'references', 'conflicts'}


class InvalidPlan(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidPlan(message)


def registry():
    path = Path(__file__).resolve().parents[1] / 'references/reading-protocols.md'
    content = path.read_text(encoding='utf-8')
    blocks = re.findall(r'<!-- ARTIFACT_REGISTRY_START -->\s*```json\s*(.*?)\s*```\s*<!-- ARTIFACT_REGISTRY_END -->', content, re.S)
    require(len(blocks) == 1, 'Canonical artifact registry missing/duplicate; no legacy fallback')
    rows = json.loads(blocks[0])['artifacts']
    require(len({x['id'] for x in rows}) == len(rows), 'Duplicate artifact ID')
    return {row['id']: row for row in rows}


def reference_plan(task, mode, validated_content=False, ia_views=None, portable=False):
    """Retrieval plan only; the caller must actually retrieve and check each section."""
    route(task, mode, validated_content, ia_views)  # Reuse the canonical API guards.
    refs = {'master-instruction.md': ['M05']}
    if task == 'assess':
        sections = ['R04', 'R06']
    elif validated_content:
        sections = ['R09', 'R07', 'R06']
        if ia_views:
            sections.insert(0, 'R08')
    else:
        refs['knowledge-compiler.md'] = ['KC01', 'KC02', 'KC03', 'KC04', 'KC05']
        sections = {
            'explain': ['R01', 'R06'],
            'extract': ['R02', 'R07', 'R09', 'R06'],
            'compare': ['R03', 'R09', 'R06', 'R07'],
            'map': ['R08', 'R09'],
            'transfer': ['R09', 'R04', 'R06'],
            'continue': ['R11', 'R12', 'R07'],
        }[task]
        if mode == 'combined' and task == 'extract':
            sections.insert(0, 'R01')
    if portable and 'R12' not in sections:
        sections.append('R12')
    refs['reading-protocols.md'] = sections
    return [{'file': 'references/' + path, 'section_ids': ids} for path, ids in refs.items()]


def event_plan(event, mode):
    """Fast-path routing for reading events; does not compile content or mutate state."""
    require(mode in {'deep', 'extract', 'combined'}, 'Invalid event mode')
    if event in {'next', 'back', 'jump', 'return', 'read', 'pause', 'resume', 'style', 'progress'}:
        sections, compiler = ['R10', 'R11'], []
    elif event == 'term':
        sections, compiler = ['R06'], []
    elif event == 'connect':
        sections, compiler = ['R10', 'R07'], ['KC01', 'KC03']
    elif event in {'quick', 'chill', 'challenger'}:
        sections = ['R10', 'R02' if mode == 'extract' else 'R01', 'R06']
        compiler = ['KC01', 'KC04']
    else:
        raise InvalidPlan('Unknown reading event')
    refs = [{'file': 'references/master-instruction.md', 'section_ids': ['M05']},
            {'file': 'references/reading-protocols.md', 'section_ids': sections}]
    if compiler:
        refs.append({'file': 'references/knowledge-compiler.md', 'section_ids': compiler})
    return {'event': event, 'mode': mode, 'reference_plan': refs,
            'content_recompile': False, 'retrieval_verified': False, 'state_mutated': False}


def select_artifacts(task, explicit=None, portable=False):
    require(task in TASKS, 'Unknown task')
    rows = registry()
    selected = []
    if explicit is not None:
        require(isinstance(explicit, str) and explicit in rows, 'Unknown artifact')
        require(task in rows[explicit]['tasks'], 'Artifact incompatible with task')
        selected.append(explicit)
    else:
        selected.extend(row['id'] for row in rows.values() if row['default'] and task in row['tasks'])
    if portable and 'RA-09' not in selected:
        selected.append('RA-09')
    return [{'id': item, 'required': rows[item]['required'], 'format': rows[item]['format']} for item in selected]


def route(task, mode, validated_content=False, ia_views=None):
    require(task in TASKS and mode in {'deep', 'extract', 'combined'}, 'Invalid task/mode')
    ia_views = [] if ia_views is None else ia_views
    require(isinstance(ia_views, list) and all(view in {'conceptual', 'learning'} for view in ia_views)
            and len(set(ia_views)) == len(ia_views), 'Invalid IA views')
    require(not ia_views or task == 'map', 'IA views require map task; assess/other fast paths stay unchanged')
    if ia_views:
        if validated_content:
            return ['IA_REUSE_CHECK', 'IA_SELECT_VIEW', 'SELECT_ARTIFACT', 'BUILD_ARTIFACT',
                    'CURRENCY_REUSE_CHECK', 'IA_SEMANTIC_CHECK', 'IA_STRUCTURE_CHECK', 'VALIDATE',
                    'HUMANIZE', 'LANGUAGE_PRESERVATION_CHECK', 'STYLE_CHECK', 'IA_DISPLAY_CHECK', 'RENDER']
        return ['SOURCE_CHECK', 'SOURCE_SEGMENT_CHECK', 'TERMINOLOGY_CONTEXT', 'COMPILE',
                'MAP', 'IA_RELATIONS', 'IA_SELECT_VIEW', 'SELECT_ARTIFACT', 'VIETNAMESE_DRAFT',
                'BILINGUAL_REVIEW', 'CURRENCY_REVIEW', 'BUILD_ARTIFACT', 'IA_SEMANTIC_CHECK',
                'IA_STRUCTURE_CHECK', 'VALIDATE', 'HUMANIZE', 'LANGUAGE_PRESERVATION_CHECK',
                'STYLE_CHECK', 'IA_DISPLAY_CHECK', 'RENDER']
    if task == 'assess':
        require(mode != 'extract', 'Assessment requires an explicitly chosen learning mode')
        return ['ASSESS', 'FEEDBACK_LANGUAGE_REVIEW', 'VALIDATE', 'HUMANIZE',
                'LANGUAGE_PRESERVATION_CHECK', 'STYLE_CHECK', 'RENDER']
    if validated_content:
        return ['SELECT_ARTIFACT', 'BUILD_ARTIFACT', 'CURRENCY_REUSE_CHECK', 'VALIDATE',
                'HUMANIZE', 'LANGUAGE_PRESERVATION_CHECK', 'STYLE_CHECK', 'RENDER']
    stage = {'explain': 'DEEP_READ', 'extract': 'EXTRACT', 'compare': 'COMPARE',
             'map': 'MAP', 'transfer': 'TRANSFER', 'continue': 'RESTORE_CONTEXT'}[task]
    currency = ['CURRENCY_REVIEW'] if task != 'map' else []
    language_source = ['SOURCE_SEGMENT_CHECK', 'TERMINOLOGY_CONTEXT'] if task != 'map' else []
    language_draft = ['VIETNAMESE_DRAFT', 'BILINGUAL_REVIEW'] if task != 'map' else []
    return ['SOURCE_CHECK'] + language_source + ['COMPILE', stage] + language_draft + currency + [
            'SELECT_ARTIFACT', 'BUILD_ARTIFACT', 'VALIDATE', 'HUMANIZE',
            'LANGUAGE_PRESERVATION_CHECK', 'STYLE_CHECK', 'RENDER']


class BlockedBranch(Exception):
    def __init__(self, reason):
        self.reason = reason


def compile_plan(request):
    require(isinstance(request, dict), 'Request must be an object')
    task, mode = request.get('task'), request.get('mode')
    require(task in TASKS and mode in {'deep', 'extract', 'combined'}, 'Invalid task/mode; clarify first')
    require(request.get('learner_level', 'unknown') in LEVELS | {'unknown'}, 'Invalid learner level')
    require(type(request.get('portable_requested', False)) is bool, 'portable_requested must be boolean')
    require(type(request.get('validated_content', False)) is bool, 'validated_content must be boolean')
    artifacts = select_artifacts(task, request.get('requested_artifact'), request.get('portable_requested', False))
    stages = route(task, mode, request.get('validated_content', False), request.get('ia_views'))
    values = request.get('nodes', [])
    require(isinstance(values, list) and len(values) <= 256, 'nodes must be a list of at most 256 per batch')
    nodes = {}
    for value in values:
        require(isinstance(value, dict), 'Node must be an object')
        nid = value.get('id')
        require(isinstance(nid, str) and nid.strip() and nid not in nodes, 'Missing/duplicate node ID')
        require(isinstance(value.get('title'), str) and value['title'].strip(), 'Missing node title')
        require(value.get('knowledge_level') in LEVELS, 'Invalid knowledge level')
        require(value.get('source_status') in {'read', 'identified', 'missing'}, 'Invalid source status')
        require(isinstance(value.get('locator'), str), 'locator must be text')
        require(value['source_status'] == 'missing' or value['locator'].strip(), 'Available source requires locator')
        require(type(value.get('in_scope')) is bool, 'in_scope must be boolean')
        require(value.get('relevance') in {'high', 'medium', 'low'}, 'Invalid relevance')
        edges = value.get('prerequisites')
        require(isinstance(edges, list) and all(isinstance(x, str) and x for x in edges), 'Invalid prerequisites')
        relations = value.get('relations', [])
        require(isinstance(relations, list), 'relations must be a list')
        for relation in relations:
            require(isinstance(relation, dict) and relation.get('type') in RELATIONS and
                    isinstance(relation.get('target'), str), 'Invalid semantic relation')
        nodes[nid] = value
    for value in nodes.values():
        for relation in value.get('relations', []):
            require(relation['target'] in nodes, 'Unknown semantic relation target')
    # Structural evidence is required before skipping a prerequisite. Semantic validity remains caller-reviewed.
    demonstrated = set()
    demonstrations = request.get('demonstrations', [])
    require(isinstance(demonstrations, list), 'demonstrations must be a list')
    for record in demonstrations:
        require(isinstance(record, dict) and record.get('node_id') in nodes, 'Unknown demonstration node')
        require(record.get('support') == 'none' and record.get('result') == 'independent' and
                isinstance(record.get('response'), str) and record['response'].strip(),
                'Demonstration must contain an independent raw response')
        demonstrated.add(record['node_id'])
    ids = request.get('demonstrated_ids', [])
    require(isinstance(ids, list) and all(x in demonstrated for x in ids), 'Unsubstantiated demonstrated_ids')
    targets = request.get('target_ids', [])
    require(isinstance(targets, list) and all(isinstance(x, str) for x in targets), 'Invalid target_ids')
    require(len(set(targets)) == len(targets), 'Duplicate target IDs')
    if not targets:
        targets = [nid for nid, value in nodes.items() if value['in_scope'] and
                   value['source_status'] == 'read' and value['relevance'] in {'high', 'medium'}]
        targets.sort(key=lambda nid: 0 if nodes[nid]['relevance'] == 'high' else 1)
    order, bridges, blocked, cycles, skipped = [], [], [], [], []
    provisional = False

    def visit(nid, stack, local):
        nonlocal provisional
        if nid in stack:
            cycle = stack[stack.index(nid):] + [nid]
            if cycle not in cycles:
                cycles.append(cycle)
            raise BlockedBranch({'type': 'prerequisite_cycle', 'node': nid, 'cycle': cycle})
        if nid in local:
            return
        if nid not in nodes:
            raise BlockedBranch({'type': 'missing_prerequisite_node', 'node': nid})
        node = nodes[nid]
        if not node['in_scope']:
            raise BlockedBranch({'type': 'outside_scope', 'node': nid})
        if node['source_status'] == 'missing' or (node['source_status'] == 'identified' and task != 'map'):
            raise BlockedBranch({'type': 'source_not_read', 'node': nid})
        if node['source_status'] == 'identified':
            provisional = True
        if nid in demonstrated and nid not in targets and task in {'explain', 'compare', 'transfer'}:
            if nid not in skipped:
                skipped.append(nid)
            return
        # Extraction keeps dependency metadata without forcing prerequisite lessons.
        if task in {'explain', 'compare', 'transfer'}:
            for prerequisite in node['prerequisites']:
                visit(prerequisite, stack + [nid], local)
        local.append(nid)

    for target in targets:
        local = []
        try:
            visit(target, [], local)
            for nid in local:
                if nid not in order:
                    order.append(nid)
                if nid not in targets and nid not in bridges:
                    bridges.append(nid)
        except BlockedBranch as error:
            blocked.append({'target': target, **error.reason})
    if task == 'assess' or request.get('validated_content', False):
        require(not values and not targets, 'Fast path must use validated content or assessment context, not recompile nodes')
        status = 'READY'
    else:
        status = 'BLOCKED' if not order else 'PARTIAL' if blocked else 'PROVISIONAL' if provisional else 'READY'
    return {'status': status, 'task': task, 'mode': mode, 'target_ids': targets, 'order': order,
            'bridges': bridges, 'skipped_demonstrated': skipped, 'blocked': blocked, 'cycles': cycles,
            'knowledge_levels': {nid: nodes[nid]['knowledge_level'] for nid in order},
            'prerequisite_metadata': {nid: nodes[nid]['prerequisites'] for nid in order},
            'artifact_plan': artifacts, 'stages': stages,
            'reference_plan': reference_plan(task, mode, request.get('validated_content', False),
                request.get('ia_views'), request.get('portable_requested', False)),
            'learner_level': request.get('learner_level', 'unknown'),
            'semantic_verified': False, 'source_locators_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        source, output = Path(args.input).resolve(), Path(args.output).absolute()
        require(source != output.resolve() and not output.exists() and not output.is_symlink(), 'Output must be a new file')
        plan = compile_plan(json.loads(source.read_text(encoding='utf-8-sig')))
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as stream:
            json.dump(plan, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        print(json.dumps({'ok': True, 'status': plan['status'], 'semantic_verified': False}))
        return 0
    except (InvalidPlan, ValueError, TypeError, KeyError, OSError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

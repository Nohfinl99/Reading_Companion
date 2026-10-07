"""Optional reading-session extension. Source/structure guards, not learning evidence.

CLI uses checkpoint.save for atomic revision-guarded persistence. Never fetches web.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlparse

STYLES = {'standard', 'quick', 'chill', 'challenger'}


class InvalidSession(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise InvalidSession(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def locator(value, sources):
    need(isinstance(value, dict), 'Locator must be an object')
    need(set(value) == {'source_id', 'chapter_id', 'line_start', 'line_end'}, 'Invalid locator fields')
    need(value['source_id'] in sources and text(value['chapter_id']), 'Unknown locator source/chapter')
    a, b = value['line_start'], value['line_end']
    need(type(a) is int and type(b) is int and 1 <= a <= b <= len(sources[value['source_id']]), 'Invalid locator lines')


def question(value):
    need(isinstance(value, dict) and set(value) == {'id', 'prompt'}, 'Question must contain only id/prompt')
    need(all(text(v) for v in value.values()), 'Empty question')


def checked_at(value):
    try:
        stamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (TypeError, ValueError, AttributeError):
        raise InvalidSession('Invalid evidence timestamp')
    need(stamp.tzinfo is not None and stamp <= datetime.now(timezone.utc), 'Invalid/future evidence time')


def validate(session, sources, units, pending):
    need(isinstance(session, dict), 'reading_session must be an object')
    fields = {'version', 'reading_style', 'chapter_index', 'cursor', 'return_position',
              'navigation_history', 'visited', 'paused_questions', 'pending_context', 'connections'}
    need(set(session) == fields and type(session['version']) is int and session['version'] == 1, 'Unsupported session version/fields')
    need(session['reading_style'] in STYLES, 'Invalid reading style')
    index = session['chapter_index']
    need(isinstance(index, dict) and set(index) == {'status', 'scope', 'chapters'}, 'Invalid chapter index')
    need(index['status'] in {'unknown', 'partial', 'complete'} and text(index['scope']), 'Invalid index status/scope')
    need(isinstance(index['chapters'], list), 'chapters must be a list')
    need(index['status'] != 'unknown' or not index['chapters'], 'Unknown index cannot assert chapters')
    need(index['status'] != 'complete' or bool(index['chapters']), 'Complete index cannot be empty')
    chapters, orders = {}, set()
    previous = {}
    for chapter in index['chapters']:
        need(isinstance(chapter, dict) and set(chapter) == {'id', 'title', 'ordinal', 'locator', 'heading_excerpt'}, 'Invalid chapter fields')
        cid, pos = chapter['id'], chapter['ordinal']
        need(text(cid) and cid not in chapters and text(chapter['title']), 'Duplicate/empty chapter')
        need(type(pos) is int and pos >= 1, 'Invalid chapter ordinal')
        locator(chapter['locator'], sources)
        loc = chapter['locator']
        need(loc['chapter_id'] == cid and text(chapter['heading_excerpt']), 'Chapter locator mismatch')
        key = (loc['source_id'], pos)
        need(key not in orders, 'Duplicate chapter ordinal')
        orders.add(key)
        lines = sources[loc['source_id']]
        need(chapter['heading_excerpt'] in lines[loc['line_start'] - 1], 'Chapter heading not at start locator')
        # Preserve explicit order; page markers or arbitrary chunks must not be labeled chapters.
        old = previous.get(loc['source_id'])
        need(old is None or (pos > old['ordinal'] and loc['line_start'] > old['locator']['line_end']), 'Unordered/overlapping chapter index')
        previous[loc['source_id']] = chapter
        chapters[cid] = chapter

    def in_chapter(loc):
        locator(loc, sources)
        need(loc['chapter_id'] in chapters, 'Locator chapter missing from index')
        bound = chapters[loc['chapter_id']]['locator']
        need(loc['source_id'] == bound['source_id'] and
             bound['line_start'] <= loc['line_start'] <= loc['line_end'] <= bound['line_end'], 'Locator outside chapter')

    for key in ('cursor', 'return_position'):
        if session[key] is not None:
            in_chapter(session[key])
    for key in ('navigation_history', 'visited', 'paused_questions', 'connections'):
        need(isinstance(session[key], list), f'{key} must be a list')
    for loc in session['visited']:
        in_chapter(loc)
    need(len(session['visited']) == len({json.dumps(x, sort_keys=True) for x in session['visited']}), 'Duplicate visited locator')
    last = None
    for row in session['navigation_history']:
        need(isinstance(row, dict) and set(row) == {'action', 'from', 'to', 'resume_note'}, 'Invalid navigation event')
        need(row['action'] in {'next', 'back', 'jump', 'return', 'read'} and text(row['resume_note']), 'Invalid navigation action/note')
        if row['from'] is not None:
            in_chapter(row['from'])
        in_chapter(row['to'])
        need(row['from'] == last, 'Navigation history must form a continuous path')
        if row['action'] in {'next', 'back'}:
            need(row['from'] is not None and row['from']['source_id'] == row['to']['source_id'], 'Adjacent navigation needs same source')
            before = chapters[row['from']['chapter_id']]['ordinal']
            after = chapters[row['to']['chapter_id']]['ordinal']
            need(after - before == (1 if row['action'] == 'next' else -1), 'Navigation skipped an unverified chapter')
        need(row['to'] in session['visited'], 'History target must be a visited locator')
        last = row['to']
    need(session['cursor'] == last, 'Cursor must match navigation history')
    need(all(any(loc == r['to'] for r in session['navigation_history']) for loc in session['visited']), 'Visited locator lacks access history')
    ids = set()
    for row in session['paused_questions']:
        need(isinstance(row, dict) and set(row) == {'question', 'cursor', 'resume_note', 'support', 'reason'}, 'Invalid paused question')
        question(row['question'])
        qid = row['question']['id']
        need(qid not in ids and (pending is None or qid != pending['id']), 'Duplicate active/paused question')
        ids.add(qid)
        if row['cursor'] is not None:
            in_chapter(row['cursor'])
        need(text(row['resume_note']) and row['reason'] in {'navigation', 'skip', 'mode_change', 'user_pause'}, 'Invalid pause note/reason')
        need(row['support'] in {'unknown', 'none', 'hint', 'worked_example'}, 'Invalid question support')
    context = session['pending_context']
    if context is not None:
        need(pending is not None and isinstance(context, dict) and set(context) == {'cursor', 'resume_note', 'support'}, 'Invalid pending context')
        if context['cursor'] is not None:
            in_chapter(context['cursor'])
        need(text(context['resume_note']) and context['support'] in {'unknown', 'none', 'hint', 'worked_example'}, 'Invalid pending support/note')
    connection_ids = set()
    unit_ids = {u['id'] for u in units}
    for row in session['connections']:
        need(isinstance(row, dict) and set(row) == {'id', 'from', 'to', 'type', 'basis', 'purpose', 'rationale', 'evidence'}, 'Invalid connection fields')
        need(text(row['id']) and row['id'] not in connection_ids, 'Duplicate/empty connection ID')
        connection_ids.add(row['id'])
        need(row['from'] in unit_ids and row['to'] in unit_ids and row['from'] != row['to'], 'Broken connection unit')
        need(row['type'] in {'supports', 'contrasts', 'limits', 'references', 'conflicts', 'prerequisite'}, 'Invalid connection type')
        need(row['basis'] in {'source_explicit', 'source_interpretation', 'hypothesis'}, 'Invalid connection basis')
        need(text(row['purpose']) and text(row['rationale']), 'Connection needs purpose/rationale')
        need(isinstance(row['evidence'], list) and bool(row['evidence']), 'Connection evidence required')
        for evidence in row['evidence']:
            need(isinstance(evidence, dict) and evidence.get('kind') in {'book', 'external'}, 'Invalid connection evidence')
            need(text(evidence.get('finding')), 'Evidence finding required')
            if evidence['kind'] == 'book':
                need(set(evidence) == {'kind', 'locator', 'excerpt', 'finding'}, 'Invalid book evidence fields')
                in_chapter(evidence['locator'])
                loc = evidence['locator']
                need(text(evidence['excerpt']) and evidence['excerpt'] in '\n'.join(sources[loc['source_id']][loc['line_start'] - 1:loc['line_end']]), 'Connection excerpt not found')
            else:
                need(set(evidence) == {'kind', 'url', 'title', 'checked_at', 'finding'}, 'Invalid external evidence fields')
                url = urlparse(evidence['url'])
                need(url.scheme in {'http', 'https'} and bool(url.netloc) and text(evidence['title']), 'Invalid external evidence URL/title')
                checked_at(evidence['checked_at'])
    return session


def enable(state, index):
    need('reading_session' not in state, 'Reading session already enabled')
    out = deepcopy(state)
    out['revision'] += 1
    out['reading_session'] = {'version': 1, 'reading_style': 'standard', 'chapter_index': deepcopy(index),
        'cursor': None, 'return_position': None, 'navigation_history': [], 'visited': [],
        'paused_questions': [], 'pending_context': None, 'connections': []}
    return out


def pause(state, note, reason='user_pause'):
    session = state['reading_session']
    if state['pending_question'] is not None:
        context = session['pending_context'] or {'cursor': session['cursor'], 'resume_note': note, 'support': 'unknown'}
        session['paused_questions'].append({'question': deepcopy(state['pending_question']),
            'cursor': deepcopy(context['cursor']), 'resume_note': context['resume_note'],
            'support': context['support'], 'reason': reason})
        state['pending_question'] = None
        session['pending_context'] = None


def operate(state, action, *, value=None, note='Tiếp tục tại vị trí đã lưu.'):
    need('reading_session' in state, 'Enable reading session first')
    out = deepcopy(state)
    session = out['reading_session']
    need(text(note), 'Resume note required')
    if action == 'style':
        need(value in STYLES, 'Invalid reading style')
        session['reading_style'] = value
    elif action == 'pause':
        need(out['pending_question'] is not None, 'No pending question')
        pause(out, note)
    elif action == 'resume':
        need(out['pending_question'] is None, 'Resolve/pause active question before resuming another')
        rows = session['paused_questions']
        match = next((r for r in rows if r['question']['id'] == value), None)
        need(match is not None, 'Paused question not found')
        out['pending_question'] = deepcopy(match['question'])
        session['pending_context'] = {k: deepcopy(match[k]) for k in ('cursor', 'resume_note', 'support')}
        rows.remove(match)
    elif action == 'connect':
        need(isinstance(value, dict), 'Connection record required')
        session['connections'].append(deepcopy(value))
    elif action in {'next', 'back', 'jump', 'return', 'read'}:
        current = session['cursor']
        chapters = session['chapter_index']['chapters']
        if action == 'read':
            target = deepcopy(value)
        elif action == 'return':
            need(session['return_position'] is not None, 'No return position')
            target = deepcopy(session['return_position'])
        else:
            need(bool(chapters), 'Chapter index unavailable')
            if action in {'next', 'back'}:
                need(current is not None, 'Reading cursor required')
                now = next(c for c in chapters if c['id'] == current['chapter_id'])
                pos = now['ordinal'] + (1 if action == 'next' else -1)
                selected = next((c for c in chapters if c['ordinal'] == pos and c['locator']['source_id'] == current['source_id']), None)
                need(selected is not None, 'Adjacent chapter unavailable or boundary reached')
            else:
                selected = next((c for c in chapters if c['id'] == value), None)
                need(selected is not None, 'Requested chapter unavailable')
            # Restore the last accessed segment of the destination chapter, not its completion status.
            target = None
            for event in reversed(session['navigation_history']):
                # The position being left is more recent than the same event's arrival elsewhere.
                for loc in (event['from'], event['to']):
                    if loc is not None and loc['chapter_id'] == selected['id']:
                        target = deepcopy(loc)
                        break
                if target is not None:
                    break
            if target is None:
                target = deepcopy(selected['locator'])
                target['line_end'] = target['line_start']
        need(isinstance(target, dict), 'Target locator required')
        if target == current:
            return out  # No mutation/no revision on repeated jump/read.
        pause(out, note, 'navigation')
        session['return_position'] = deepcopy(current)
        session['cursor'] = target
        session['navigation_history'].append({'action': action, 'from': deepcopy(current), 'to': deepcopy(target), 'resume_note': note})
        if target not in session['visited']:
            session['visited'].append(deepcopy(target))
    else:
        raise InvalidSession('Unknown session action')
    if out != state:
        out['revision'] = state['revision'] + 1
    return out


def progress(state):
    session = state.get('reading_session')
    accessed = [] if session is None else sorted({loc['chapter_id'] for loc in session['visited']})
    total = None
    if session and session['chapter_index']['status'] == 'complete':
        total = len(session['chapter_index']['chapters'])
    return {'cursor': None if session is None else session['cursor'],
        'reading_style': 'standard' if session is None else session['reading_style'],
        'accessed_chapters': accessed, 'chapter_count_in_verified_scope': total,
        'scope': state['scope'] if session is None else session['chapter_index']['scope'],
        'processed_sections': [r for r in state['coverage'] if r['status'] in {'analyzed', 'merged'}],
        'remaining_recorded_sections': [r for r in state['coverage'] if r['status'] in {'unprocessed', 'missing_source'}],
        'observed_assessments': deepcopy(state['assessments']), 'pending_question': state['pending_question'],
        'paused_questions': [] if session is None else session['paused_questions'],
        'progress_basis': 'accessed locators / existing coverage / observed task responses; no book or mastery percentage'}


def guard_transition(old, new):
    a, b = old.get('reading_session'), new.get('reading_session')
    if a is None:
        if b is not None:
            need(all(new.get(k) == v for k, v in old.items() if k != 'revision'), 'Enable must preserve existing checkpoint')
            need(b['cursor'] is None and b['return_position'] is None and b['pending_context'] is None and
                 all(not b[k] for k in ('navigation_history', 'visited', 'paused_questions', 'connections')), 'Enable cannot invent session history')
        return
    need(b is not None, 'Reading session cannot disappear')
    need(a['chapter_index'] == b['chapter_index'], 'Index replacement requires a new session/reimport')
    need(b['navigation_history'][:len(a['navigation_history'])] == a['navigation_history'], 'Navigation history cannot disappear/change')
    need(all(loc in b['visited'] for loc in a['visited']), 'Visited locators cannot disappear')
    need(all(row in b['connections'] for row in a['connections']), 'Connection records cannot disappear/change')
    need(b['cursor'] == a['cursor'] or len(b['navigation_history']) > len(a['navigation_history']), 'Cursor movement needs navigation event')
    if len(b['navigation_history']) > len(a['navigation_history']):
        for key in ('mode', 'goal', 'scope', 'units', 'coverage', 'assessments'):
            need(new[key] == old[key], 'Navigation cannot mutate content/coverage/assessment/mode')
        need(b['cursor'] == b['navigation_history'][-1]['to'], 'Navigation cursor must match final event')
    questions = [r['question'] for r in a['paused_questions']]
    if old['pending_question'] is not None:
        questions.append(old['pending_question'])
    new_questions = [r['question'] for r in b['paused_questions']]
    if new['pending_question'] is not None:
        new_questions.append(new['pending_question'])
    added_assessments = new['assessments'][len(old['assessments']):]
    need(new['assessments'][:len(old['assessments'])] == old['assessments'], 'Observed assessments cannot disappear/change')
    for q in questions:
        resolved = any(r['question_id'] == q['id'] and text(r['response']) for r in added_assessments)
        need(q in new_questions or resolved, 'Unanswered question cannot disappear/change')
    for row in a['paused_questions']:
        newer = next((r for r in b['paused_questions'] if r['question']['id'] == row['question']['id']), None)
        if newer is not None:
            need(newer == row, 'Paused question context cannot change')
        elif new['pending_question'] == row['question']:
            need(b['pending_context'] == {k: row[k] for k in ('cursor', 'resume_note', 'support')}, 'Resumed question must preserve context/support')
        for result in added_assessments:
            if result['question_id'] == row['question']['id']:
                need(row['support'] == 'none' or result['support'] != 'none', 'Assessment cannot erase paused question support')
    if old['pending_question'] is not None and a['pending_context'] is None:
        for row in b['paused_questions']:
            if row['question'] == old['pending_question']:
                need(row['support'] == 'unknown', 'Legacy question support must remain unknown')
    if old['pending_question'] is not None and a['pending_context'] is not None:
        context = a['pending_context']
        if new['pending_question'] == old['pending_question']:
            newer = b['pending_context']
            need(newer is not None and newer['cursor'] == context['cursor'] and newer['resume_note'] == context['resume_note'], 'Pending context cannot disappear/change')
            support = {'none': 0, 'hint': 1, 'worked_example': 2, 'unknown': 3}
            need(support[newer['support']] >= support[context['support']], 'Question support cannot decrease')
        for row in b['paused_questions']:
            if row['question'] == old['pending_question']:
                need(all(row[k] == context[k] for k in ('cursor', 'resume_note', 'support')), 'Pause must preserve context/support')
        for result in added_assessments:
            if result['question_id'] == old['pending_question']['id']:
                need(context['support'] == 'none' or result['support'] != 'none', 'Assessment cannot erase question support')


def main():
    import checkpoint as cp
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['enable', 'style', 'next', 'back', 'jump', 'return', 'read', 'pause', 'resume', 'connect', 'progress'])
    parser.add_argument('--state', required=True)
    parser.add_argument('--value')
    parser.add_argument('--input', help='JSON chapter index, locator, or connection')
    parser.add_argument('--note', default='Tiếp tục tại vị trí đã lưu.')
    args = parser.parse_args()
    try:
        state = cp.validate(cp.read_json(args.state))
        if args.action == 'progress':
            print(json.dumps(progress(state), ensure_ascii=False))
            return 0
        value = cp.read_json(args.input) if args.input else args.value
        candidate = enable(state, value) if args.action == 'enable' else operate(state, args.action, value=value, note=args.note)
        cp.validate(candidate)
        if candidate == state:
            print(json.dumps({'ok': True, 'revision': state['revision'], 'changed': False}))
            return 0
        # Existing atomic writer + transition guard; candidate retained only inside a temporary directory.
        import tempfile
        with tempfile.TemporaryDirectory(prefix='sid-session-') as folder:
            path = Path(folder) / 'candidate.json'
            path.write_text(json.dumps(candidate, ensure_ascii=False), encoding='utf-8')
            cp.save(args.state, path)
        print(json.dumps({'ok': True, 'revision': candidate['revision'], 'semantic_verified': False}))
        return 0
    except (InvalidSession, cp.InvalidCheckpoint, OSError, ValueError, TypeError, KeyError, StopIteration) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

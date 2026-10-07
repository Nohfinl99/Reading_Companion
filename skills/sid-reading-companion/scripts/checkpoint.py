"""Optional local checkpoint helper. Structure/source checks, not a semantic judge."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from datetime import datetime, timezone
from urllib.parse import urlparse
import importlib.util

_session_spec = importlib.util.spec_from_file_location('sid_reading_session', Path(__file__).with_name('reading_session.py'))
reading_session = importlib.util.module_from_spec(_session_spec)
_session_spec.loader.exec_module(reading_session)


class InvalidCheckpoint(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidCheckpoint(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def timestamp(value, label):
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        require(parsed.tzinfo is not None, f'{label} needs timezone')
        return parsed
    except (ValueError, TypeError, AttributeError):
        raise InvalidCheckpoint(f'Invalid {label} timestamp')


def validate_currency(record):
    """Validate provenance/timing only; never establish that a claim is true."""
    require(isinstance(record, dict), 'currency must be an object')
    require(record.get('sensitivity') in {'stable', 'dynamic', 'historical', 'unknown'},
            'Invalid currency sensitivity')
    status = record.get('status')
    require(status in {'stable_core', 'confirmed', 'changed', 'historical', 'unresolved', 'not_checked'},
            'Invalid currency status')
    for key in ('rationale', 'original_claim', 'current_conclusion', 'applicability'):
        require(isinstance(record.get(key), str) and record[key].strip(), f'currency needs {key}')
    assessed = timestamp(record.get('assessed_at'), 'assessed_at')
    require(assessed <= datetime.now(timezone.utc), 'assessed_at cannot be in the future')
    verified = record.get('verified_at')
    verified = timestamp(verified, 'verified_at') if verified is not None else None
    if verified is not None:
        require(verified <= assessed, 'verified_at must not follow assessed_at')
    evidence = record.get('evidence')
    require(isinstance(evidence, list), 'currency evidence must be a list')
    for item in evidence:
        require(isinstance(item, dict), 'currency evidence must be an object')
        url = urlparse(item.get('url', ''))
        require(url.scheme in {'http', 'https'} and bool(url.netloc), 'Invalid currency evidence URL')
        for key in ('title', 'finding'):
            require(isinstance(item.get(key), str) and item[key].strip(), f'Evidence needs {key}')
        checked = timestamp(item.get('checked_at'), 'evidence checked_at')
        require(checked <= assessed, 'Evidence checked_at must not follow assessed_at')
        if verified is not None:
            require(checked <= verified, 'Evidence checked_at must not follow verified_at')
    if status in {'confirmed', 'changed'}:
        require(verified is not None and bool(evidence), 'Verified currency needs timestamp and evidence')
    if status == 'not_checked':
        require(verified is None and not evidence, 'not_checked cannot claim verification')
    if status == 'stable_core':
        require(record['sensitivity'] == 'stable', 'stable_core needs stable sensitivity')
    if status == 'historical':
        require(record['sensitivity'] == 'historical', 'historical needs historical sensitivity')
    due = record.get('review_after')
    if due is not None:
        require(timestamp(due, 'review_after') > assessed, 'review_after must follow assessed_at')
    return record


def currency_due(record, now=None):
    due = record.get('review_after')
    return bool(due and timestamp(due, 'review_after') <= (now or datetime.now(timezone.utc)))


def validate(state):
    require(isinstance(state, dict), 'State must be an object')
    require(state.get('schema_version') == 1, 'Unsupported schema_version')
    require(type(state.get('revision')) is int and state['revision'] >= 1, 'Invalid revision')
    require(state.get('mode') in {'unselected', 'deep', 'extract', 'combined'}, 'Invalid mode')
    for key in ('scope', 'goal'):
        require(isinstance(state.get(key), str), f'{key} must be text')
    for key in ('sources', 'units', 'coverage', 'assessments', 'limitations'):
        require(isinstance(state.get(key), list), f'{key} must be a list')
    require(all(isinstance(x, str) for x in state['limitations']), 'Limitations must be text')
    sources = {}
    require(bool(state['sources']), 'At least one source required')
    for source in state['sources']:
        require(isinstance(source, dict), 'Source must be an object')
        sid = source.get('id')
        require(isinstance(sid, str) and re.fullmatch(r'S[0-9A-Za-z_-]+', sid), 'Invalid source ID')
        require(sid not in sources, 'Duplicate source ID')
        require(isinstance(source.get('path'), str), 'Source path must be text')
        path = Path(source['path'])
        require(path.is_absolute() and path.is_file(), f'Source unavailable: {sid}')
        require(source.get('sha256') == sha256(path), f'Source changed: {sid}; reimport required')
        content = path.read_text(encoding='utf-8-sig')
        require(bool(content.strip()), f'Empty source: {sid}')
        sources[sid] = content.splitlines()
    ids = set()
    require(all(isinstance(x, dict) for x in state['units']), 'Units must be objects')
    for unit in state['units']:
        uid = unit.get('id')
        require(isinstance(uid, str) and re.fullmatch(r'K[0-9A-Za-z_-]+', uid), 'Invalid unit ID')
        require(uid not in ids, 'Duplicate unit ID')
        ids.add(uid)
    for unit in state['units']:
        require(type(unit.get('revision')) is int and unit['revision'] >= 1, 'Invalid unit revision')
        for key in ('title', 'content'):
            require(isinstance(unit.get(key), str) and unit[key].strip(), f'Empty {key}')
        kind = unit.get('kind')
        require(kind in {'book', 'interpretation', 'new_example', 'current_source'}, 'Invalid kind')
        if 'currency' in unit:
            validate_currency(unit['currency'])
        require(isinstance(unit.get('conditions'), list) and
                all(isinstance(x, str) for x in unit['conditions']), 'Invalid conditions')
        require(isinstance(unit.get('related'), list) and
                all(isinstance(x, str) and x in ids and x != unit['id'] for x in unit['related']), 'Broken related ID')
        if 'knowledge_level' in unit:
            require(unit['knowledge_level'] in {'L1', 'L2', 'L3', 'L4'}, 'Invalid knowledge_level')
        if 'prerequisites' in unit:
            require(isinstance(unit['prerequisites'], list) and
                    all(isinstance(x, str) and x in ids and x != unit['id'] for x in unit['prerequisites']),
                    'Broken prerequisite ID')
        if 'relations' in unit:
            require(isinstance(unit['relations'], list), 'relations must be a list')
            for edge in unit['relations']:
                require(isinstance(edge, dict) and edge.get('type') in
                        {'supports', 'contrasts', 'limits', 'references', 'conflicts'} and
                        edge.get('target') in ids, 'Invalid typed relation')
        citations = unit.get('citations')
        require(isinstance(citations, list), 'citations must be a list')
        require(kind not in {'book', 'interpretation'} or bool(citations), 'Grounded unit requires citation')
        if kind == 'current_source':
            require(isinstance(unit.get('url'), str), 'Current source URL required')
            url = urlparse(unit['url'])
            require(url.scheme in {'http', 'https'} and bool(url.netloc), 'Invalid current source URL')
            try:
                date = datetime.fromisoformat(unit.get('checked_at', '').replace('Z', '+00:00'))
                require(date.tzinfo is not None, 'checked_at needs timezone')
            except (ValueError, TypeError):
                raise InvalidCheckpoint('Invalid checked_at timestamp')
        for citation in citations:
            require(isinstance(citation, dict), 'Citation must be an object')
            sid = citation.get('source_id')
            require(isinstance(sid, str) and sid in sources, 'Unknown source ID')
            start, end = citation.get('line_start'), citation.get('line_end')
            require(type(start) is int and type(end) is int and
                    1 <= start <= end <= len(sources[sid]), 'Invalid line range')
            excerpt = citation.get('excerpt')
            require(isinstance(excerpt, str) and excerpt.strip(), 'Empty excerpt')
            require(excerpt in '\n'.join(sources[sid][start-1:end]), 'Excerpt not found in cited lines')
    for row in state['coverage']:
        require(isinstance(row, dict) and row.get('source_id') in sources, 'Invalid coverage source')
        require(isinstance(row.get('section'), str) and row['section'].strip(), 'Missing coverage section')
        require(row.get('status') in {'analyzed', 'merged', 'unprocessed', 'missing_source'}, 'Invalid coverage status')
        require(isinstance(row.get('unit_ids'), list) and all(x in ids for x in row['unit_ids']), 'Broken coverage unit')
        if row['status'] in {'analyzed', 'merged'}:
            require(bool(row['unit_ids']), 'Analyzed coverage requires units')
            selected = [u for u in state['units'] if u['id'] in row['unit_ids']]
            require(any(c['source_id'] == row['source_id'] for u in selected for c in u['citations']),
                    'Coverage lacks a citation to its source')
        if row['status'] == 'merged':
            require(isinstance(row.get('reason'), str) and row['reason'].strip(), 'Merged coverage requires reason')
    for assessment in state['assessments']:
        require(isinstance(assessment, dict), 'Assessment must be an object')
        require(isinstance(assessment.get('question_id'), str) and assessment['question_id'].strip(), 'Missing question ID')
        result = assessment.get('result')
        require(result in {'unassessed', 'assisted', 'independent', 'needs_work'}, 'Invalid assessment result')
        require(assessment.get('support') in {'none', 'hint', 'worked_example'}, 'Invalid support')
        response = assessment.get('response')
        require(isinstance(response, str), 'response must be text')
        require(result == 'unassessed' or bool(response.strip()), 'Cannot assess without response')
        require(result != 'independent' or assessment['support'] == 'none', 'Assisted answer cannot be independent')
    pending = state.get('pending_question')
    if pending is not None:
        require(isinstance(pending, dict) and set(pending) == {'id', 'prompt'}, 'Pending question must contain only id/prompt')
        require(all(isinstance(pending[x], str) and pending[x].strip() for x in pending), 'Empty pending question')
        require(state['mode'] in {'deep', 'combined'}, 'Pending quiz incompatible with mode')
    if 'reading_session' in state:
        try:
            reading_session.validate(state['reading_session'], sources, state['units'], pending)
        except reading_session.InvalidSession as error:
            raise InvalidCheckpoint(str(error)) from error
    return state


def validate_transition(old, new):
    validate(old)
    validate(new)
    require(new['revision'] == old['revision'] + 1, 'State revision must increment by one')
    require(new['sources'] == old['sources'], 'Source identity cannot change; create a new session')
    try:
        reading_session.guard_transition(old, new)
    except reading_session.InvalidSession as error:
        raise InvalidCheckpoint(str(error)) from error
    before = {u['id']: u for u in old['units']}
    after = {u['id']: u for u in new['units']}
    require(before.keys() <= after.keys(), 'Existing units cannot disappear')
    for uid, previous in before.items():
        current = after[uid]
        if current != previous:
            require(current['revision'] == previous['revision'] + 1, 'Changed unit must increment revision')


def write_atomic(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.is_symlink(), 'Refuse symlink state target')
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def initialize(source, target, mode):
    source, target = Path(source).resolve(), Path(target).absolute()
    require(not target.exists() and not target.is_symlink(), 'State target already exists')
    require(target.resolve() != source, 'State target must differ from source')
    require(source.is_file(), 'Source file unavailable')
    state = {'schema_version': 1, 'revision': 1, 'mode': mode, 'scope': '', 'goal': '',
             'sources': [{'id': 'S01', 'path': str(source), 'sha256': sha256(source)}],
             'units': [], 'coverage': [], 'assessments': [], 'pending_question': None, 'limitations': []}
    validate(state)
    write_atomic(target, state)
    return state


def save(target, candidate):
    target, candidate = Path(target).absolute(), Path(candidate).resolve()
    require(not target.is_symlink(), 'Refuse symlink state target')
    require(target.resolve() != candidate, 'Candidate must differ from state')
    old, new = read_json(target), read_json(candidate)
    require(target.resolve() not in {Path(s['path']).resolve() for s in new.get('sources', [])},
            'State must not overwrite source')
    validate_transition(old, new)
    write_atomic(target, new)
    return new


def export(target, output):
    state = validate(read_json(target))
    output = Path(output).absolute()
    require(not output.exists() and not output.is_symlink(), 'Export target already exists')
    require(output.resolve() not in {Path(s['path']).resolve() for s in state['sources']}, 'Cannot overwrite source')
    lines = ['# SID — Bản bàn giao', '', f"Chế độ: {state['mode']} · Phiên bản: {state['revision']}",
             f"Mục tiêu: {state['goal']}", f"Phạm vi: {state['scope']}", '',
             'Helper đã kiểm cấu trúc/vị trí nguồn; chưa xác nhận ngữ nghĩa hoặc khả năng người học.', '', '## Nguồn']
    lines.extend(f"- {s['id']}: {s['path']} · SHA-256: {s['sha256']}" for s in state['sources'])
    for unit in state['units']:
        lines.extend(['', f"## {unit['id']} — {unit['title']} (v{unit['revision']}, {unit['kind']})", unit['content']])
        if 'knowledge_level' in unit:
            lines.append('- Tầng tri thức: ' + unit['knowledge_level'])
        if unit.get('prerequisites'):
            lines.append('- Tiên quyết: ' + ', '.join(unit['prerequisites']))
        if unit.get('relations'):
            lines.append('- Quan hệ: ' + json.dumps(unit['relations'], ensure_ascii=False))
        lines.extend('- Điều kiện: ' + x for x in unit['conditions'])
        lines.extend(f"- Nguồn: {c['source_id']} dòng {c['line_start']}–{c['line_end']}; {c['excerpt']}" for c in unit['citations'])
        if unit['kind'] == 'current_source':
            lines.append(f"- Nguồn ngoài: {unit['url']} · Kiểm tra: {unit['checked_at']}")
        if 'currency' in unit:
            currency = unit['currency']
            lines.append('- Kiểm thời sự: ' + json.dumps(currency, ensure_ascii=False))
            if currency_due(currency):
                lines.append('- ĐẾN HẠN KIỂM LẠI: kết luận chỉ được xác minh tại thời điểm đã ghi; '
                             'cần đọc lại nguồn trước khi dùng như thông tin hiện tại.')
        if unit['related']:
            lines.append('- Liên quan: ' + ', '.join(unit['related']))
    lines.extend(['', '## Độ bao quát', json.dumps(state['coverage'], ensure_ascii=False), '',
                  '## Đánh giá quan sát được', json.dumps(state['assessments'], ensure_ascii=False), '',
                  '## Câu đang chờ', json.dumps(state['pending_question'], ensure_ascii=False), '',
                  '## Phần thiếu và bước tiếp theo'])
    lines.extend('- ' + x for x in state['limitations'])
    if 'reading_session' in state:
        lines.extend(['', '## Phiên đọc và điểm quay lại',
                      json.dumps(state['reading_session'], ensure_ascii=False, indent=2),
                      '', '## Tiến trình đọc / xử lý / phản hồi quan sát được',
                      json.dumps(reading_session.progress(state), ensure_ascii=False, indent=2)])
    lines.append('Phiên mới cần nguồn tương ứng; bản bàn giao không thay cho quyền truy cập sách.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        stream.write('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('init', 'check', 'save', 'export'):
        p = sub.add_parser(command)
        p.add_argument('--state', required=True)
        if command == 'init':
            p.add_argument('--source', required=True)
            p.add_argument('--mode', choices=['unselected', 'deep', 'extract', 'combined'], default='unselected')
        if command == 'save':
            p.add_argument('--candidate', required=True)
        if command == 'export':
            p.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'init':
            state = initialize(args.source, args.state, args.mode)
        elif args.command == 'save':
            state = save(args.state, args.candidate)
        elif args.command == 'export':
            export(args.state, args.output)
            state = read_json(args.state)
        else:
            state = validate(read_json(args.state))
        print(json.dumps({'ok': True, 'revision': state['revision'], 'semantic_verified': False}))
    except (InvalidCheckpoint, OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())


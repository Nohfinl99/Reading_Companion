"""Regression coverage for checkpoint question and assessment continuity."""
from copy import deepcopy

import pytest

from conftest import Q01


def transition(cp, rs, old, new):
    rs.guard_transition(old, new)
    cp.validate_transition(old, new)


def bump(old):
    new = deepcopy(old)
    new['revision'] += 1
    return new


@pytest.mark.parametrize('through_checkpoint', [False, True])
def test_legacy_pending_question_cannot_disappear(cp, rs, fx, through_checkpoint):
    old = fx.state(pending_question=deepcopy(Q01))
    new = bump(old)
    new['pending_question'] = None
    fn = cp.validate_transition if through_checkpoint else rs.guard_transition
    with pytest.raises((rs.InvalidSession, cp.InvalidCheckpoint), match='Unanswered question cannot disappear'):
        fn(old, new)


@pytest.mark.parametrize('with_session', [False, True])
def test_unassessed_response_does_not_resolve_pending_question(cp, rs, fx, with_session):
    old = (fx.state_pending('hint') if with_session
           else fx.state(pending_question=deepcopy(Q01)))
    new = bump(old)
    new['pending_question'] = None
    if with_session:
        new['reading_session']['pending_context'] = None
    new['assessments'].append({'question_id': Q01['id'], 'response': 'A considered response.',
                               'support': 'hint', 'result': 'unassessed'})
    with pytest.raises((rs.InvalidSession, cp.InvalidCheckpoint), match='Unanswered question cannot disappear'):
        cp.validate_transition(old, new)


def test_assessment_history_cannot_be_erased(cp, rs, fx):
    assessment = {'question_id': 'Q00', 'response': 'Prior response.', 'support': 'hint', 'result': 'assisted'}
    old = fx.state(assessments=[assessment])
    new = bump(old)
    new['assessments'] = []
    with pytest.raises((rs.InvalidSession, cp.InvalidCheckpoint), match='Observed assessments cannot disappear/change'):
        cp.validate_transition(old, new)


def test_legacy_unknown_support_cannot_be_resolved_as_none(cp, rs, fx):
    old = fx.state(pending_question=deepcopy(Q01))
    new = bump(old)
    new['pending_question'] = None
    new['assessments'].append({'question_id': Q01['id'], 'response': 'A considered response.',
                               'support': 'none', 'result': 'independent'})
    with pytest.raises((rs.InvalidSession, cp.InvalidCheckpoint), match='Assessment cannot erase question support'):
        cp.validate_transition(old, new)


def test_session_unknown_support_cannot_be_resolved_as_none(cp, rs, fx):
    old = fx.state_pending('unknown')
    new = bump(old)
    new['pending_question'] = None
    new['reading_session']['pending_context'] = None
    new['assessments'].append({'question_id': Q01['id'], 'response': 'A considered response.',
                               'support': 'none', 'result': 'independent'})
    with pytest.raises(cp.InvalidCheckpoint, match='Assessment cannot erase question support'):
        cp.validate_transition(old, new)


def test_legacy_question_can_be_kept_and_later_assessed_with_support(cp, rs, fx):
    old = fx.state(pending_question=deepcopy(Q01))
    kept = bump(old)
    assert transition(cp, rs, old, kept) is None
    resolved = bump(old)
    resolved['pending_question'] = None
    resolved['assessments'].append({'question_id': Q01['id'], 'response': 'A considered response.',
                                    'support': 'hint', 'result': 'assisted'})
    assert transition(cp, rs, old, resolved) is None


def test_assessment_history_can_be_appended(cp, rs, fx):
    prior = {'question_id': 'Q00', 'response': 'Prior response.', 'support': 'hint', 'result': 'assisted'}
    old = fx.state(assessments=[prior])
    new = bump(old)
    new['assessments'].append({'question_id': 'Q01', 'response': 'New considered response.',
                               'support': 'none', 'result': 'unassessed'})
    assert transition(cp, rs, old, new) is None


def test_enable_and_pause_resume_keep_question_continuity(cp, rs, fx):
    legacy = fx.state(pending_question=deepcopy(Q01))
    enabled = bump(legacy)
    enabled['reading_session'] = rs.enable(legacy, fx.index2())['reading_session']
    assert transition(cp, rs, legacy, enabled) is None

    old = fx.state_pending('hint')
    paused = bump(old)
    paused['reading_session'] = deepcopy(old['reading_session'])
    paused['pending_question'] = None
    paused['reading_session']['pending_context'] = None
    paused['reading_session']['paused_questions'] = [{
        'question': deepcopy(Q01), 'cursor': deepcopy(old['reading_session']['cursor']),
        'resume_note': 'Đang chờ trả lời.', 'support': 'hint', 'reason': 'user_pause'}]
    assert transition(cp, rs, old, paused) is None
    resumed = bump(paused)
    resumed['reading_session'] = rs.operate(paused, 'resume', value=Q01['id'])['reading_session']
    resumed['pending_question'] = deepcopy(Q01)
    assert transition(cp, rs, paused, resumed) is None

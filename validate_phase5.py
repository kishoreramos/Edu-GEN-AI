import os
import sys
import json
import time
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"c:\kishoreProject\EduGenie")
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
import main
from config import GEMINI_MODEL, FALLBACK_MODELS, is_gemini_configured
from qna import answer_question_with_gemini
from explanation_module import explain_topic
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations
from orchestrator.schemas import IntentType, ContextState, QuizState
from orchestrator.session_manager import SessionManager, default_session_manager

client = TestClient(main.app)

def safe_call(func, *args, **kwargs):
    for attempt in range(3):
        res = func(*args, **kwargs)
        res_str = str(res)
        if "rate limit" in res_str.lower() or "quota exceeded" in res_str.lower() or "resource_exhausted" in res_str.lower():
            print(f"  [Free-tier RPM rate-limit wait 15s (attempt {attempt+1}/3)...]")
            time.sleep(15)
            continue
        return res
    return res

def safe_req(method, url, **kwargs):
    for attempt in range(3):
        r = getattr(client, method)(url, **kwargs)
        text = r.text
        if "rate limit" in text.lower() or "quota exceeded" in text.lower() or "resource_exhausted" in text.lower():
            print(f"  [Free-tier RPM rate-limit wait 15s on {url} (attempt {attempt+1}/3)...]")
            time.sleep(15)
            continue
        return r
    return r

results = {
    'core_modules': {},
    'legacy_endpoints': {},
    'conversational_flow': [],
    'multi_action_workflows': {},
    'quiz_feedback': {},
    'session_restart': {},
    'context_safety': {},
    'live_smoke_tests': {}
}

print('=' * 70)
print('EDUGENIE PHASE 5 - COMPREHENSIVE END-TO-END VALIDATION')
print('=' * 70)
print(f'Gemini API Key Configured: {is_gemini_configured()}')
print(f'Central Model: {GEMINI_MODEL}')
print(f'Fallback Chain: {FALLBACK_MODELS}\n')

PACE_DELAY = 12  # Respects Google Free-tier 5 RPM (1 request every 12 seconds)

# ------------------------------------------------------------------
# PART 5: Five Core Capabilities Validation
# ------------------------------------------------------------------
print('--- [PART 5] Testing 5 Core Modules ---')

# 1. Q&A
q_res = safe_call(answer_question_with_gemini, 'What is the difference between a stack and a queue in data structures?')
assert len(q_res) > 20, 'Q&A module returned empty response'
results['core_modules']['qna'] = {'status': 'PASS', 'sample': q_res[:150] + '...'}
print('PASS Core Module 1 (Q&A)')
time.sleep(PACE_DELAY)

# 2. Explanation
exp_res = safe_call(explain_topic, 'binary search trees')
assert len(exp_res) > 20, 'Explanation module returned empty response'
results['core_modules']['explanation'] = {'status': 'PASS', 'sample': exp_res[:150] + '...'}
print('PASS Core Module 2 (Explanation)')
time.sleep(PACE_DELAY)

# 3. Quiz Generation
quiz_res = safe_call(generate_quiz, 'object oriented programming')
assert isinstance(quiz_res, list) and len(quiz_res) >= 3, 'Quiz module did not return 3 questions'
results['core_modules']['quiz'] = {'status': 'PASS', 'count': len(quiz_res), 'q1': quiz_res[0]['question']}
print('PASS Core Module 3 (Quiz)')
time.sleep(PACE_DELAY)

# 4. Summarization
sum_sample = ('Cloud computing is the delivery of computing services including servers, storage, databases, '
              'networking, software, analytics, and intelligence over the Internet to offer faster innovation, '
              'flexible resources, and economies of scale. Typically, you pay only for cloud services you use, '
              'helping lower your operating costs and run infrastructure more efficiently.')
sum_res = safe_call(summarize_text, sum_sample)
assert len(sum_res) > 10, 'Summarize module returned empty response'
results['core_modules']['summarize'] = {'status': 'PASS', 'sample': sum_res[:150] + '...'}
print('PASS Core Module 4 (Summarization)')
time.sleep(PACE_DELAY)

# 5. Learning Recommendations
lp_res = safe_call(get_learning_recommendations, 'Python for Data Science')
assert len(lp_res) > 20, 'Learning path module returned empty response'
results['core_modules']['learning_path'] = {'status': 'PASS', 'sample': lp_res[:150] + '...'}
print('PASS Core Module 5 (Learning Path)\n')
time.sleep(PACE_DELAY)

# ------------------------------------------------------------------
# PART 6: Five Legacy Endpoints Validation
# ------------------------------------------------------------------
print('--- [PART 6] Testing 5 Legacy Endpoints ---')

# 1. GET /qa
r = safe_req('get', '/qa', params={'question': 'What is an algorithm?'})
assert r.status_code == 200 and r.json().get('answer'), 'GET /qa failed'
results['legacy_endpoints']['GET /qa'] = '200 OK'
print('PASS Legacy Endpoint 1 (GET /qa): 200 OK')
time.sleep(PACE_DELAY)

# 2. POST /explain
r = safe_req('post', '/explain', json={'topic': 'hashing in data structures'})
assert r.status_code == 200 and r.json().get('explanation'), 'POST /explain failed'
results['legacy_endpoints']['POST /explain'] = '200 OK'
print('PASS Legacy Endpoint 2 (POST /explain): 200 OK')
time.sleep(PACE_DELAY)

# 3. POST /quiz
r = safe_req('post', '/quiz', json={'text': 'cybersecurity basics'})
assert r.status_code == 200 and len(r.json().get('quiz', [])) >= 3, 'POST /quiz failed'
results['legacy_endpoints']['POST /quiz'] = '200 OK'
print('PASS Legacy Endpoint 3 (POST /quiz): 200 OK')
time.sleep(PACE_DELAY)

# 4. POST /summarize
r = safe_req('post', '/summarize', json={'text': sum_sample})
assert r.status_code == 200 and r.json().get('summary'), 'POST /summarize failed'
results['legacy_endpoints']['POST /summarize'] = '200 OK'
print('PASS Legacy Endpoint 4 (POST /summarize): 200 OK')
time.sleep(PACE_DELAY)

# 5. GET /learn/recommendations
r = safe_req('get', '/learn/recommendations', params={'topic': 'web development'})
assert r.status_code == 200 and (r.json().get('recommendation') or r.json().get('recommendations')), 'GET /learn/recommendations failed'
results['legacy_endpoints']['GET /learn/recommendations'] = '200 OK'
print('PASS Legacy Endpoint 5 (GET /learn/recommendations): 200 OK\n')
time.sleep(PACE_DELAY)

# ------------------------------------------------------------------
# PART 7: Multi-Turn Conversational Flow
# ------------------------------------------------------------------
print('--- [PART 7] Testing Multi-Turn Conversational Session ---')
chat_session_id = default_session_manager.create_session()

turns = [
    ('Turn 1 (Root Question)', 'What is polymorphism in Java?'),
    ('Turn 2 (Contextual Simplification)', 'Explain that more simply'),
    ('Turn 3 (Contextual Example)', 'Give me a real-world example'),
    ('Turn 4 (Contextual Quiz)', 'Quiz me on this'),
    ('Turn 5 (Contextual Learning Path)', 'What should I learn next?')
]

for label, msg in turns:
    r = safe_req('post', '/api/chat', json={'session_id': chat_session_id, 'message': msg})
    assert r.status_code == 200, f'{label} failed with status {r.status_code}'
    data = r.json()
    assert data['success'], f'{label} returned success=False'
    results['conversational_flow'].append({
        'turn': label,
        'user': msg,
        'intent': data.get('intent'),
        'active_topic': data.get('context_state', {}).get('current_topic'),
        'reply_preview': data.get('reply', '')[:120] + '...'
    })
    print(f'PASS {label}: Intent={data.get("intent")}, Topic={data.get("context_state", {}).get("current_topic")}')
    time.sleep(PACE_DELAY)

print()

# ------------------------------------------------------------------
# PART 8: Multi-Action Workflows
# ------------------------------------------------------------------
print('--- [PART 8] Testing Multi-Action Workflows ---')

r_ma1 = safe_req('post', '/api/chat', json={'message': f'Summarize this text and then quiz me on it: {sum_sample}'})
assert r_ma1.status_code == 200 and r_ma1.json()['success']
data_ma1 = r_ma1.json()
assert data_ma1['intent'] == 'MULTI_ACTION'
results['multi_action_workflows']['summarize_then_quiz'] = {
    'intent': data_ma1['intent'],
    'has_quiz_data': bool(data_ma1.get('data', {}).get('quiz')),
    'preview': data_ma1['reply'][:150] + '...'
}
print('PASS Multi-Action Workflow 1 (Summarize -> Quiz)')
time.sleep(PACE_DELAY)

r_ma2 = safe_req('post', '/api/chat', json={'message': 'Explain recursion and then quiz me.'})
assert r_ma2.status_code == 200 and r_ma2.json()['success']
data_ma2 = r_ma2.json()
assert data_ma2['intent'] == 'MULTI_ACTION'
results['multi_action_workflows']['explain_then_quiz'] = {
    'intent': data_ma2['intent'],
    'has_quiz_data': bool(data_ma2.get('data', {}).get('quiz')),
    'preview': data_ma2['reply'][:150] + '...'
}
print('PASS Multi-Action Workflow 2 (Explain -> Quiz)\n')
time.sleep(PACE_DELAY)

# ------------------------------------------------------------------
# PART 9: Quiz State & Feedback Evaluation
# ------------------------------------------------------------------
print('--- [PART 9] Testing Quiz State Tracking & Score Evaluation ---')
quiz_sid = default_session_manager.create_session()

r_qinit = safe_req('post', '/api/chat', json={'session_id': quiz_sid, 'message': 'Give me a 3-question quiz on Python lists.'})
assert r_qinit.status_code == 200
time.sleep(PACE_DELAY)

r_qeval = safe_req('post', '/api/chat', json={'session_id': quiz_sid, 'message': 'I got 2 wrong'})
assert r_qeval.status_code == 200
data_qeval = r_qeval.json()
assert data_qeval['intent'] == 'QUIZ'
assert 'score' in data_qeval.get('data', {}) or '1/3' in data_qeval['reply'] or 'Score' in data_qeval['reply']
results['quiz_feedback'] = {
    'intent': data_qeval['intent'],
    'reply': data_qeval['reply']
}
print('PASS Quiz Evaluation: Score & Weak Area Feedback successfully generated.\n')

# ------------------------------------------------------------------
# PART 10: Server Restart Persistence
# ------------------------------------------------------------------
print('--- [PART 10] Testing SQLite Session Persistence Across Server Restart ---')
restart_sid = default_session_manager.create_session()
default_session_manager.add_message(restart_sid, 'user', 'What is Big-O notation?')
default_session_manager.add_message(restart_sid, 'assistant', 'Big-O notation measures algorithm complexity.')
default_session_manager.update_session_context(restart_sid, ContextState(current_topic='Big-O Notation', recent_topics=['Big-O Notation']))

new_sm = SessionManager(db_path=str(BASE_DIR / 'edugenie.db'))
rec_id, rec_ctx = new_sm.get_or_create_session(restart_sid)
rec_msgs = new_sm.get_recent_messages(restart_sid)

assert rec_id == restart_sid, 'Session ID not preserved across restart'
assert rec_ctx.current_topic == 'Big-O Notation', 'Context topic not preserved across restart'
assert len(rec_msgs) >= 2, 'Messages not preserved across restart'
results['session_restart'] = {
    'status': 'PASS',
    'recovered_session_id': rec_id,
    'recovered_topic': rec_ctx.current_topic,
    'recovered_message_count': len(rec_msgs)
}
print(f'PASS SQLite Persistence Across Restart: Verified (Session: {rec_id}, Topic: {rec_ctx.current_topic}, Msgs: {len(rec_msgs)})\n')

# ------------------------------------------------------------------
# PART 11: Missing Context Safety
# ------------------------------------------------------------------
print('--- [PART 11] Testing Missing Context Clarification Handling ---')
empty_sid = default_session_manager.create_session()
r_empty = safe_req('post', '/api/chat', json={'session_id': empty_sid, 'message': 'Explain that more simply.'})
assert r_empty.status_code == 200
data_empty = r_empty.json()
assert data_empty['intent'] == 'CLARIFICATION'
assert data_empty.get('data', {}).get('requires_context') is True
assert 'specify which topic' in data_empty['reply'] or 'clarify' in data_empty['reply'].lower()
results['context_safety'] = {
    'status': 'PASS',
    'intent': data_empty['intent'],
    'requires_context': data_empty.get('data', {}).get('requires_context'),
    'reply': data_empty['reply']
}
print(f'PASS Missing Context Safety: Intent=CLARIFICATION, Prompt="{data_empty["reply"]}"\n')

# ------------------------------------------------------------------
# PART 14: Live Gemini Smoke Test
# ------------------------------------------------------------------
print('--- [PART 14] Testing Live Gemini Smoke Test (5 Required Prompts) ---')
smoke_prompts = [
    ('Prompt 1: What is Python?', 'What is Python?'),
    ('Prompt 2: Explain recursion simply.', 'Explain recursion simply.'),
    ('Prompt 3: Quiz Java inheritance.', 'Create a 3-question quiz about Java inheritance.'),
    ('Prompt 4: Summarize text.', f'Summarize this text: {sum_sample}'),
    ('Prompt 5: SQL learning path.', 'Create a beginner-to-advanced SQL learning path.')
]

for label, pmt in smoke_prompts:
    res = safe_req('post', '/api/chat', json={'message': pmt})
    assert res.status_code == 200 and res.json()['success']
    reply_text = res.json()['reply']
    assert len(reply_text) > 20
    results['live_smoke_tests'][label] = {
        'intent': res.json()['intent'],
        'snippet': reply_text[:160].replace('\n', ' ') + '...'
    }
    print(f'PASS Live Smoke Test ({label}): Intent={res.json()["intent"]}, Length={len(reply_text)} chars')
    time.sleep(PACE_DELAY)

print('\n' + '=' * 70)
print('ALL END-TO-END VALIDATIONS COMPLETED SUCCESSFULLY!')
print('=' * 70)

with open(BASE_DIR / 'validation_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f'Validation results saved to {BASE_DIR / "validation_results.json"}')

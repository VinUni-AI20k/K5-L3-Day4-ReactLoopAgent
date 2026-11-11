"""Kiểm tra giới hạn retry 429 và rút gọn dữ liệu nhiễu của agent, không gọi LLM API."""
import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'bonus'))
from agent import run_agent, MAX_RATE_LIMITED
from bonus.tools import BonusTools
from test_agent import ScriptedProvider, call, final


class RetryLimitTests(unittest.TestCase):
    def test_persistent_429_is_blocked_after_limit(self):
        tools = BonusTools(scenario='rate_limit_always')
        script = [call(str(i), 'get_vercel_status', {}) for i in range(MAX_RATE_LIMITED + 1)] + [final('Vercel chưa kiểm tra được')]
        provider = ScriptedProvider(script)
        result = run_agent('Kiểm tra Vercel', provider, tools, max_steps=6)
        self.assertEqual(result['status'], 'completed')
        errors = [t['result']['error'] for t in result['trace'] if t['event'] == 'tool']
        self.assertEqual(errors, ['RATE_LIMITED'] * MAX_RATE_LIMITED + ['RETRY_LIMIT_REACHED'])
        # Lần bị chặn không gọi API: bộ đếm của tools chỉ tăng đúng MAX_RATE_LIMITED lần.
        self.assertEqual(tools.calls[('get_vercel_status', 'vercel')], MAX_RATE_LIMITED)

    def test_noisy_list_is_compacted_before_model(self):
        tools = BonusTools(scenario='noisy')
        provider = ScriptedProvider([call('a', 'get_vercel_status', {}), final()])
        run_agent('Kiểm tra Vercel', provider, tools, max_steps=3)
        content = json.loads(provider.histories[1][-1]['content'])
        self.assertEqual(len(content['distractors']), 5)
        self.assertEqual(content['distractors_omitted'], 155)
        self.assertEqual(content['provider'], 'vercel')


if __name__ == '__main__':
    unittest.main()

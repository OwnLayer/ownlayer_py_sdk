import unittest
from ownlayer.calculate_cost import calculate_cost

class TestCalculateCost(unittest.TestCase):

    def test_claude35_sonet_cost(self):
        cost = calculate_cost('claude-3-5-sonnet-20240620', 10, 30)
        input = 10 * 3 / 1000000
        output = 30 * 15 / 1000000
        self.assertEqual(cost, input + output)

    def test_claude35_opus_cost(self):
        cost = calculate_cost('claude-3-5-opus-20240620', 10, 30)
        input = 10 * 15 / 1000000
        output = 30 * 75 / 1000000
        self.assertEqual(cost, input + output)

    def test_claude35_haiku_cost(self):
        cost = calculate_cost('claude-3-5-haiku-20240620', 10, 30)
        input = 10 * 0.25 / 1000000
        output = 30 * 1.25 / 1000000
        self.assertEqual(cost, input + output)

    def test_gpt4o_cost(self):
        cost = calculate_cost('gpt-4o', 10, 30)
        input = 10 * 5 / 1000000
        output = 30 * 15 / 1000000
        self.assertEqual(cost, input + output)

    def test_gpt4o_august_cost(self):
        cost = calculate_cost('gpt-4o-2024-08-06', 10, 30)
        input = 10 * 2.5 / 1000000
        output = 30 * 10 / 1000000
        self.assertEqual(cost, input + output)

    def test_gpt4o_may_cost(self):
        cost = calculate_cost('gpt-4o-2024-05-13', 10, 30)
        input = 10 * 5 / 1000000
        output = 30 * 15 / 1000000
        self.assertEqual(cost, input + output)

    def test_gpt4o_mini_cost(self):
        cost = calculate_cost('gpt-4o-mini', 10, 30)
        input = 10 * 0.15 / 1000000
        output = 30 * 0.6 / 1000000
        self.assertEqual(cost, input + output)

    def test_gpt4o_mini_old_cost(self):
        cost = calculate_cost('gpt-4o-mini-2024-07-18', 10, 30)
        input = 10 * 0.15 / 1000000
        output = 30 * 0.6 / 1000000
        self.assertEqual(cost, input + output)

    def test_unkown_cost(self):
        cost = calculate_cost('unkown', 10, 30)
        self.assertEqual(cost, None)

if __name__ == '__main__':
    unittest.main()
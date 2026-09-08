import unittest
from coursepilot.validators import estimate_grading_workload, validate_assessment_names, validate_assessment_weeks, validate_assessment_weights

class ValidatorTests(unittest.TestCase):
    def test_valid_weights(self):
        self.assertTrue(validate_assessment_weights([{"name":"A","weight":40},{"name":"B","weight":60}])["valid"])
    def test_invalid_weights(self):
        result=validate_assessment_weights([{"name":"A","weight":40},{"name":"B","weight":65}])
        self.assertFalse(result["valid"]); self.assertEqual(result["total_weight"],105.0)
    def test_duplicate_names(self):
        self.assertEqual(validate_assessment_names([{"name":"Lab"},{"name":"Lab"}])["duplicates"],["Lab"])
    def test_week_bounds(self):
        self.assertFalse(validate_assessment_weeks([{"name":"Presentation","week":14}],13)["valid"])
    def test_workload(self):
        self.assertEqual(estimate_grading_workload(100,1,12)["estimated_hours"],20.0)

if __name__=="__main__": unittest.main()

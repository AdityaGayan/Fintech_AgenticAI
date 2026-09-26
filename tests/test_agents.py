import unittest
from src.agents.re_agent import process_requirements
from src.agents.sdlc_agent import recommend_sdlc

class TestRefactoredAgents(unittest.TestCase):
    
    def test_super_re_agent(self):
        """Tests if the RE agent returns the combined schema properly."""
        raw_text = "The app needs to process payments instantly, and must encrypt data. Also, it should be fast."
        reqs = process_requirements(raw_text, "Payments")
        
        self.assertIsInstance(reqs, list)
        if len(reqs) > 0:
            first_req = reqs[0]
            self.assertIn("id", first_req)
            self.assertIn("compliance_mapping", first_req)
            self.assertIn("business_justification", first_req)

    def test_sdlc_agent(self):
        """Tests the SDLC recommendation engine."""
        result = recommend_sdlc("Digital Banking", "High security needs, vague initial scope.", "High")
        
        self.assertIn("recommended_model", result)
        self.assertIn("confidence_percentage", result)
        self.assertIn("justification", result)

if __name__ == '__main__':
    unittest.main()
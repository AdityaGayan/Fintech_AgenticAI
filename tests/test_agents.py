import unittest
from unittest.mock import patch
from types import SimpleNamespace
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

    @patch("src.agents.sdlc_agent.invoke_gemini_safely", return_value=None)
    def test_sdlc_agent(self, _invoke):
        """Tests the SDLC recommendation engine."""
        result = recommend_sdlc(
            requirements_summary="High security needs, vague initial scope, must encrypt all data."
        )
        
        self.assertIn("recommended_model", result)
        self.assertIn("confidence_percentage", result)
        self.assertIn("justification", result)
        self.assertIn("key_phases", result)
        # The model must be one of the allowed values
        allowed = {"Waterfall", "V-Shaped", "Incremental",
                   "Rapid Application Development", "Prototyping",
                   "Spiral", "Agile"}
        self.assertIn(result["recommended_model"], allowed)

    @patch("src.agents.sdlc_agent.invoke_gemini_safely", return_value=None)
    def test_sdlc_waterfall_signal(self, _invoke):
        """Tests that clear, fixed-scope, regulatory requirements lean toward Waterfall."""
        result = recommend_sdlc(
            requirements_summary=(
                "The system shall log out users after 10 minutes of inactivity. "
                "All requirements are fixed and well-defined. The deadline is contractual."
            )
        )
        # With these signals the fallback should NOT default to Incremental
        self.assertIn(result["recommended_model"], {"Waterfall", "V-Shaped"})

    @patch("src.agents.sdlc_agent.invoke_gemini_safely")
    def test_sdlc_returns_agent_response(self, invoke):
        """An available AI response must not be replaced by local canned text."""
        agent_response = SimpleNamespace(
            model_dump=lambda: {
                "recommended_model": "Spiral",
                "confidence_percentage": 61,
                "justification": "Agent-generated justification",
                "key_phases": "Agent-generated phases",
            }
        )
        invoke.return_value = agent_response

        result = recommend_sdlc(requirements_summary="A changing fraud-detection scope")

        self.assertEqual(result, {**agent_response.model_dump(), "selection_source": "AI"})
        invoke.assert_called_once()

if __name__ == '__main__':
    unittest.main()

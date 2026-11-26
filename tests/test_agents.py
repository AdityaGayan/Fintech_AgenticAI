import unittest
from unittest.mock import patch
from types import SimpleNamespace
from src.agents.re_agent import SRSDocument, generate_srs_document, process_requirements
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
    def test_sdlc_requires_agent_response(self, _invoke):
        """SDLC generation must not silently use a local fallback."""
        with self.assertRaises(RuntimeError):
            recommend_sdlc(requirements_summary="High security needs")

    @patch("src.agents.sdlc_agent.invoke_gemini_safely")
    def test_sdlc_returns_agent_response(self, invoke):
        """An available AI response must not be replaced by local canned text."""
        agent_response = SimpleNamespace(
            model_dump=lambda: {
                "recommended_model": "Spiral",
                "justification": "Agent-generated justification",
            }
        )
        invoke.return_value = agent_response

        result = recommend_sdlc(requirements_summary="A changing fraud-detection scope")

        self.assertEqual(result, agent_response.model_dump())
        invoke.assert_called_once()

    @patch("src.agents.re_agent.invoke_gemini_safely")
    def test_re_agent_generates_ieee_srs(self, invoke):
        document = SRSDocument(
            title="Payments Platform SRS", version="1.0", purpose="Define the system.",
            scope="Payments processing.", definitions_and_acronyms=["SRS: Software Requirements Specification"],
            references=["PCI-DSS"], overview="This document describes the system.",
            product_perspective="Web platform.", product_functions=["Process payments"],
            user_characteristics=["Customer"], constraints=["Use approved encryption"],
            assumptions_and_dependencies=["Payment gateway is available"], user_interfaces=["Web interface"],
            hardware_interfaces=["None identified"], software_interfaces=["Payment gateway API"],
            communication_interfaces=["HTTPS"], functions=["The system shall process payments."],
            performance_requirements=["The system shall be available 99.9% of the time."],
            logical_database_requirements=["Store payment records."], design_constraints=["Use approved encryption"],
            software_quality_attributes=["Security and reliability"], object_oriented_models=["Payment entity"],
            appendices=["None"], index=["Payment processing"],
        )
        invoke.return_value = document
        result = generate_srs_document("The system processes payments.", "PCI-DSS")
        self.assertEqual(result["source"], "RE Agent")
        self.assertIn("## Title Page", result["markdown"])
        self.assertIn("## Table of Contents", result["markdown"])
        self.assertIn("## 1. Introduction", result["markdown"])
        self.assertIn("UI001", result["markdown"])
        self.assertIn("FUN001", result["markdown"])
        self.assertIn("### 3.7 Object-Oriented Models", result["markdown"])
        self.assertIn("## 5. Index", result["markdown"])

if __name__ == '__main__':
    unittest.main()

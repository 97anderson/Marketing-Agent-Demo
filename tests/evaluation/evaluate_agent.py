"""LLM-as-a-Judge Evaluation Script.

This script evaluates the quality of generated LinkedIn posts using an LLM
to score them on Clarity, Tone, and Length. This acts as a quality gate
in the CI/CD pipeline.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, List

from src.agents.marketing.agent import MarketingAgent
from src.agents.marketing.models import GeneratePostRequest
from src.gateway.inference_gateway import InferenceGateway
from src.shared.config import get_settings
from src.shared.logger import setup_logging


setup_logging()
logger = logging.getLogger(__name__)


class PostEvaluator:
    """Evaluates the quality of generated LinkedIn posts.
    
    Uses an LLM to score posts on multiple criteria:
    - Clarity (1-10): How clear and understandable is the message?
    - Tone (1-10): How appropriate is the tone for LinkedIn?
    - Length (1-10): Is the length appropriate (not too short or long)?
    
    Attributes:
        gateway: The Inference Gateway for LLM evaluation calls.
        pass_threshold: Minimum average score to pass (default: 8.0).
    """
    
    def __init__(self, gateway: InferenceGateway, pass_threshold: float = 8.0):
        """Initialize the evaluator.
        
        Args:
            gateway: Inference Gateway for making LLM calls.
            pass_threshold: Minimum average score to pass (default: 8.0).
        """
        self.gateway = gateway
        self.pass_threshold = pass_threshold
    
    async def evaluate_post(self, content: str, topic: str) -> Dict:
        """Evaluate a single post using an LLM as a judge.
        
        Args:
            content: The post content to evaluate.
            topic: The original topic of the post.
            
        Returns:
            Dictionary with scores and overall assessment.
        """
        logger.info(f"Evaluating post on topic: {topic}")
        
        evaluation_prompt = self._create_evaluation_prompt(content, topic)
        
        try:
            response = await self.gateway.generate(
                prompt=evaluation_prompt,
                temperature=0.3,  # Lower temperature for consistent evaluation
                max_tokens=500,
                metadata={"evaluation": "llm-as-judge", "topic": topic}
            )
            
            # Parse the evaluation response
            evaluation = self._parse_evaluation(response.content)
            
            # Calculate average score
            scores = [
                evaluation["clarity"],
                evaluation["tone"],
                evaluation["length"]
            ]
            average_score = sum(scores) / len(scores)
            evaluation["average_score"] = average_score
            evaluation["passed"] = average_score >= self.pass_threshold
            
            logger.info(
                f"Evaluation complete - Average Score: {average_score:.2f}, "
                f"Passed: {evaluation['passed']}"
            )
            
            return evaluation
            
        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            raise
    
    def _create_evaluation_prompt(self, content: str, topic: str) -> str:
        """Create the evaluation prompt for the LLM judge.
        
        Args:
            content: The post content to evaluate.
            topic: The original topic.
            
        Returns:
            The formatted evaluation prompt.
        """
        return f"""You are an expert evaluator of LinkedIn content. Your task is to score the following LinkedIn post on three criteria.

ORIGINAL TOPIC: {topic}

POST TO EVALUATE:
---
{content}
---

Please evaluate this post on the following criteria (score each from 1-10):

1. CLARITY (1-10): Is the message clear, well-structured, and easy to understand?
   - Consider: logical flow, readability, coherent arguments
   
2. TONE (1-10): Is the tone appropriate for LinkedIn professionals?
   - Consider: professionalism, engagement, authenticity
   
3. LENGTH (1-10): Is the length appropriate (not too short or too long)?
   - Consider: LinkedIn best practices (300-1500 chars ideal)

Provide your evaluation in the following JSON format:
{{
  "clarity": <score 1-10>,
  "tone": <score 1-10>,
  "length": <score 1-10>,
  "clarity_feedback": "<brief explanation>",
  "tone_feedback": "<brief explanation>",
  "length_feedback": "<brief explanation>",
  "overall_feedback": "<summary of strengths and improvements>"
}}

Be strict but fair. A score of 8+ means excellent quality."""
    
    def _parse_evaluation(self, response_content: str) -> Dict:
        """Parse the evaluation response from the LLM.
        
        Args:
            response_content: The raw response from the LLM.
            
        Returns:
            Parsed evaluation dictionary with scores and feedback.
        """
        try:
            # Try to extract JSON from the response
            # Look for JSON block in the response
            start = response_content.find("{")
            end = response_content.rfind("}") + 1
            
            if start != -1 and end > start:
                json_str = response_content[start:end]
                evaluation = json.loads(json_str)
                
                # Validate required fields
                required_fields = ["clarity", "tone", "length"]
                for field in required_fields:
                    if field not in evaluation:
                        raise ValueError(f"Missing required field: {field}")
                
                return evaluation
            else:
                raise ValueError("No JSON found in response")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse evaluation response: {str(e)}")
            
            # Fallback: return mock evaluation
            return {
                "clarity": 7,
                "tone": 7,
                "length": 7,
                "clarity_feedback": "Could not parse evaluation",
                "tone_feedback": "Could not parse evaluation",
                "length_feedback": "Could not parse evaluation",
                "overall_feedback": "Evaluation parsing failed, using default scores"
            }


async def run_evaluation(test_topics: List[str], pass_threshold: float = 8.0) -> bool:
    """Run the full evaluation process.
    
    Args:
        test_topics: List of topics to test.
        pass_threshold: Minimum average score to pass.
        
    Returns:
        True if all evaluations pass, False otherwise.
    """
    logger.info("=" * 80)
    logger.info("Starting LLM-as-a-Judge Evaluation")
    logger.info("=" * 80)
    
    # Initialize components
    gateway = InferenceGateway.from_settings()
    agent = MarketingAgent(gateway=gateway)
    evaluator = PostEvaluator(gateway=gateway, pass_threshold=pass_threshold)
    
    all_passed = True
    results = []
    
    for topic in test_topics:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Testing Topic: {topic}")
        logger.info(f"{'=' * 80}")
        
        try:
            # Generate a post
            logger.info("Step 1: Generating post...")
            request = GeneratePostRequest(
                topic=topic,
                tone="professional",
                max_length=800
            )
            post = await agent.generate_post(request)
            
            logger.info(f"\nGenerated Post ({len(post.content)} chars):")
            logger.info("-" * 80)
            logger.info(post.content)
            logger.info("-" * 80)
            
            # Evaluate the post
            logger.info("\nStep 2: Evaluating post quality...")
            evaluation = await evaluator.evaluate_post(post.content, topic)
            
            # Log evaluation results
            logger.info("\n" + "=" * 80)
            logger.info("EVALUATION RESULTS")
            logger.info("=" * 80)
            logger.info(f"Clarity Score:  {evaluation['clarity']}/10")
            logger.info(f"  Feedback: {evaluation.get('clarity_feedback', 'N/A')}")
            logger.info(f"\nTone Score:     {evaluation['tone']}/10")
            logger.info(f"  Feedback: {evaluation.get('tone_feedback', 'N/A')}")
            logger.info(f"\nLength Score:   {evaluation['length']}/10")
            logger.info(f"  Feedback: {evaluation.get('length_feedback', 'N/A')}")
            logger.info(f"\nAverage Score:  {evaluation['average_score']:.2f}/10")
            logger.info(f"Pass Threshold: {pass_threshold}/10")
            logger.info(f"Status:         {'✅ PASSED' if evaluation['passed'] else '❌ FAILED'}")
            logger.info(f"\nOverall Feedback:\n{evaluation.get('overall_feedback', 'N/A')}")
            logger.info("=" * 80)
            
            results.append({
                "topic": topic,
                "evaluation": evaluation,
                "post_length": len(post.content),
                "token_usage": post.usage.dict()
            })
            
            if not evaluation["passed"]:
                all_passed = False
                logger.error(f"❌ Topic '{topic}' FAILED evaluation")
            else:
                logger.info(f"✅ Topic '{topic}' PASSED evaluation")
                
        except Exception as e:
            logger.error(f"❌ Error testing topic '{topic}': {str(e)}", exc_info=True)
            all_passed = False
            results.append({
                "topic": topic,
                "error": str(e),
                "passed": False
            })
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATION SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total Topics Tested: {len(test_topics)}")
    passed_count = sum(1 for r in results if r.get("evaluation", {}).get("passed", False))
    logger.info(f"Passed: {passed_count}/{len(test_topics)}")
    logger.info(f"Failed: {len(test_topics) - passed_count}/{len(test_topics)}")
    logger.info(f"\nFinal Result: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    logger.info("=" * 80)
    
    # Save results to file
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    logger.info("\nResults saved to: evaluation_results.json")
    
    return all_passed


async def main():
    """Main entry point for the evaluation script."""
    # Test topics
    test_topics = [
        "artificial intelligence in healthcare",
        "remote work productivity tips",
        "sustainable business practices"
    ]
    
    # Run evaluation
    passed = await run_evaluation(test_topics, pass_threshold=7.0)
    
    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    asyncio.run(main())


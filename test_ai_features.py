"""
Test script for AI Audience Matching and Content Optimization features
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_audience_matching():
    """Test the AI Audience & Platform Matching endpoint"""
    print("\n" + "="*60)
    print("[TEST 1] AI Audience & Platform Matching")
    print("="*60)
    
    payload = {
        "product_name": "Organic Peanut Butter",
        "category": "Health Food",
        "price_range": "₹180-250",
        "description": "100% natural peanut butter made from organic peanuts, no added sugar or preservatives. Rich in protein and healthy fats.",
        "target_country": "India"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/audience-matching", json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n[SUCCESS] Product: {result['product']}")
        print(f"[INFO] Market Trends Used: {result['market_trends_used']}")
        
        print("\n[TARGET AUDIENCE]")
        audience = result['target_audience']
        print(f"  Age Range: {audience.get('age_range', 'N/A')}")
        print(f"  Interests: {', '.join(audience.get('interests', []))}")
        print(f"  Buying Intent: {audience.get('buying_intent', 'N/A')}")
        print(f"  Summary: {audience.get('summary', 'N/A')}")
        
        print("\n[PLATFORM RECOMMENDATIONS]")
        for i, platform in enumerate(result['platform_recommendations'], 1):
            print(f"\n  {i}. {platform['platform']} (Confidence: {platform['confidence_score']}%)")
            print(f"     Reason: {platform['reason']}")
            print(f"     Keywords: {', '.join(platform.get('keywords', []))}")
        
        print(f"\n[OVERALL STRATEGY]")
        print(f"  {result['overall_strategy']}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None


def test_content_optimization():
    """Test the AI Content & Distribution Optimization endpoint"""
    print("\n" + "="*60)
    print("[TEST 2] AI Content & Distribution Optimization")
    print("="*60)
    
    payload = {
        "product_name": "Organic Peanut Butter",
        "product_details": "100% natural peanut butter made from organic peanuts, no added sugar or preservatives. Rich in protein and healthy fats. Perfect for fitness enthusiasts and health-conscious consumers.",
        "selected_platform": "Amazon India",
        "target_audience": "Health-conscious adults aged 25-40, fitness enthusiasts",
        "category": "Health Food"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ai/content-optimization", json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"\n[SUCCESS] Platform: {result['platform']}")
        
        print("\n[OPTIMIZED CONTENT]")
        content = result['optimized_content']
        print(f"  Title: {content.get('title', 'N/A')}")
        print(f"  Description: {content.get('description', 'N/A')}")
        print(f"  Call to Action: {content.get('call_to_action', 'N/A')}")
        print(f"  Tags/Hashtags: {', '.join(content.get('hashtags_or_tags', []))}")
        
        print("\n[POSTING STRATEGY]")
        strategy = result['posting_strategy']
        print(f"  Best Timing: {strategy.get('best_timing', 'N/A')}")
        print(f"  Format: {strategy.get('format', 'N/A')}")
        print(f"  Frequency: {strategy.get('frequency', 'N/A')}")
        if strategy.get('additional_tips'):
            print(f"  Tips:")
            for tip in strategy['additional_tips']:
                print(f"    - {tip}")
        
        print("\n[COMPLIANCE WARNINGS]")
        for warning in result['compliance_warnings']:
            print(f"  - {warning}")
        
        print("\n[ACTION RECOMMENDATIONS]")
        for i, action in enumerate(result['action_recommendations'], 1):
            print(f"\n  {i}. {action['action']} (Priority: {action.get('priority', 'N/A')})")
            print(f"     Expected Impact: {action.get('expected_impact', 'N/A')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None


if __name__ == "__main__":
    print("\n=== VyaaparSahayak AI Features Test Suite ===")
    print("Testing new AI-powered marketing and growth features\n")
    
    # Test 1: Audience Matching
    audience_result = test_audience_matching()
    
    # Test 2: Content Optimization
    content_result = test_content_optimization()
    
    print("\n" + "="*60)
    print("=== Testing Complete! ===")
    print("="*60)
    
    if audience_result and content_result:
        print("\n[SUCCESS] Both AI features are working correctly!")
        print("\n[NEXT STEPS]")
        print("  1. Add your SerpAPI key to .env for enhanced market research")
        print("  2. Integrate these endpoints into your frontend")
        print("  3. Create UI components for product analysis and content generation")
    else:
        print("\n[WARNING] Some tests failed. Please check the error messages above.")

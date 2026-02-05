import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from main import app, RiskDetectionRequest, StartupProfile, SessionLocal, engine, Base

# Ensure DB is init
Base.metadata.create_all(bind=engine)

def test_risk_analysis():
    print("Testing Risk Analysis Logic...")
    
    # Create a dummy profile if not exists
    db = SessionLocal()
    profile = db.query(StartupProfile).first()
    if not profile:
        profile = StartupProfile(business_name="Test Corp", annual_revenue=100000)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    profile_id = profile.id
    db.close()
    
    # Mock Request
    req = RiskDetectionRequest(startup_profile_id=profile_id, openai_api_key="mock-env")
    
    # Call the function (via Client or direct import if possible, here direct import of endpoint function)
    # We will simulate the function call logic from main.py's endpoint
    from main import analyze_risks_and_plan
    
    try:
        response = analyze_risks_and_plan(req)
        print("Success!")
        print(f"Risk Level: {response['risk_level']}")
        print(f"AI Model Used: {response['ai_model']}")
        print(f"Actions Plan Length: {len(response['ai_action_plan'])}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_risk_analysis()

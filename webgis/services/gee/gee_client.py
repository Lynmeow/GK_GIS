import ee
import os
from dotenv import load_dotenv

load_dotenv()

_initialized = False

def initialize_gee():
    global _initialized
    if not _initialized:
        try:
            ee.Initialize(project=os.getenv('GEE_PROJECT_ID'))
            _initialized = True
            print("✅ GEE initialized successfully")
        except Exception as e:
            print(f"❌ GEE initialization failed: {e}")
            raise

def get_hcmc_boundary():
    return ee.Geometry.Rectangle([106.4, 10.4, 107.0, 11.0])
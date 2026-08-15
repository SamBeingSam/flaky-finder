import time
import random
import os

def test_flaky_login():
    # 1. Hardcoded sleep
    time.sleep(3)
    
    # 2. Unseeded random logic
    user_id = random.randint(100, 999)
    
    # 3. Global state mutation
    os.environ["CURRENT_USER"] = str(user_id)
    
    assert user_id > 0
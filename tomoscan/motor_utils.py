from epics import PV
import time
from typing import Optional

class MotorUtils:
    # @staticmethod
    def waitDMOV(motor_pv: str, timeout: Optional[float] = None, poll: float = 0.05) -> bool:
        """
        Wait until <motor_pv>.DMOV becomes 1.
        """
        dmov = PV(f"{motor_pv}.DMOV")
        try:
            if int(dmov.get()) == 1:
                return True
        except Exception:
            pass

        start = time.monotonic()
        while True:
            try:
                if int(dmov.get()) == 1:
                    print(f"\033[92mMotor {motor_pv} reached destination\033[0m")
                    return True
            except Exception:
                pass

            if timeout is not None and (time.monotonic() - start) >= timeout:
                print(f"\033[91mMotor {motor_pv} did not reach destination, timeout error\033[0m")
                return False
                
            time.sleep(poll)

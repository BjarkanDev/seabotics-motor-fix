import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/bjorn/Projects/motor_fix/ws/install/thruster_control'

import os
import glob
os.system("pip install -r requirements.txt")
print("="*20)

try:
    import RFS
    os.system("pip uninstall RFS -y")
    print("="*20)
except ImportError:
    pass

os.system("pip install -e .")
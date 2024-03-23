import os
import glob
os.system("pip install -r requirements.txt")
print("="*20)

try:
    import obeyon_rfs
    os.system("pip uninstall obeyon_rfs -y")
    print("="*20)
except ImportError:
    pass

os.system("pip install -e .")
import os
import glob
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system("pip install -r requirements.txt --break-system-packages")
print("="*20)

try:
    import obeyon_rfs
    os.system("pip uninstall obeyon_rfs -y --break-system-packages")
    print("="*20)
except ImportError:
    pass

os.system("pip install -e . --break-system-packages")
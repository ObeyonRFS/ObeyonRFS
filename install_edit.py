import os
import glob
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.system("pip install -r requirements.txt")
print("="*20)

try:
    import obeyon_rfs
    os.system("pip uninstall obeyon_rfs -y")
    print("="*20)
except ImportError:
    pass

os.system("pip install -e .")
with open("vtr_standard/poc/validator.py", "r") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'sidecar_path = f"{video_path}.vtr.json"' in line and i == 55:
        lines[i] = '        sidecar_path = f"{video_path}.vtr.json"\n'
with open("vtr_standard/poc/validator.py", "w") as f:
    f.writelines(lines)

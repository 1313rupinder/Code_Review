from unidiff import PatchSet

with open("sample.diff") as f:
    patch = PatchSet(f.read())

for file in patch:
    print("File:", file.path)
    for hunk in file:
        for line in hunk:
            if line.is_added:
                print("  Added line", line.target_line_no, ":", line.value.strip())
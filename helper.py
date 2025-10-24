# diagnostic — run in your shell / Python
with open(".pre-commit-config.yaml", "rb") as f:
    b = f.read()
offset = 1124
start = max(0, offset - 20)
end = min(len(b), offset + 20)
print("bytes window:", b[start:end])
print("byte@offset:", hex(b[offset]) if offset < len(b) else "out of range")
print("utf-8 (replace):", b[start:end].decode("utf-8", errors="replace"))
print("cp1252 (replace):", b[start:end].decode("cp1252", errors="replace"))

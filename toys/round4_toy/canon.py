"""Minimal RFC 8949 §4.2.1 core deterministic CBOR encoder (own code), cross-checked against cbor2 if present."""
import hashlib, struct
def _head(major, n):
    if n < 24: return bytes([(major << 5) | n])
    for ai, fmt, lim in ((24, ">B", 0xff), (25, ">H", 0xffff), (26, ">I", 0xffffffff), (27, ">Q", 2**64 - 1)):
        if n <= lim: return bytes([(major << 5) | ai]) + struct.pack(fmt, n)
    raise ValueError("int too large")
def enc(v):
    if v is None: return b"\xf6"
    if v is True: return b"\xf5"
    if v is False: return b"\xf4"
    if isinstance(v, int): return _head(0, v) if v >= 0 else _head(1, -1 - v)
    if isinstance(v, bytes): return _head(2, len(v)) + v
    if isinstance(v, str): b = v.encode("utf-8"); return _head(3, len(b)) + b
    if isinstance(v, (list, tuple)): return _head(4, len(v)) + b"".join(enc(x) for x in v)
    if isinstance(v, dict):
        items = sorted(((enc(k), enc(x)) for k, x in v.items()), key=lambda kv: kv[0])   # bytewise lexicographic
        if len(set(k for k, _ in items)) != len(items): raise ValueError("duplicate key")
        return _head(5, len(items)) + b"".join(k + x for k, x in items)
    raise TypeError(type(v))
def digest(tag, obj):
    b = enc(obj); return b, hashlib.sha256(tag + b).hexdigest()
try:
    import cbor2
    def xcheck(obj): return cbor2.dumps(obj, canonical=True) == enc(obj)
except ImportError:
    def xcheck(obj): return None

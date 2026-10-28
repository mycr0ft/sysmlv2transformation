# Case-by-case SysML v1-to-v2 mapping rules

The built-in transformer follows the published SysML v1-to-v2 mapping where
one exists. When a source model contains a feature whose semantics depend on
local engineering practice, a project can provide a reviewable mapping rule
instead of changing the global transformer or catching every transformation
error.

## Rule contract

`umlmeta.v1_to_v2.emit_v2` accepts an optional `mapping_rule`:

```python
text = emit_v2(package, mapping_rule=rule)
```

The rule receives:

```python
(element, indent)
```

It should return a list of already-indented SysML v2 lines to replace the
built-in mapping for that element, or return `None` to use the built-in
mapping. The hook is called for packages, classifiers, relationships, and
properties, including nested properties.

A rule may deliberately raise `UnmappedFeature` when a case has not been
reviewed. Do not catch `UnmappedFeature` globally: that would make unrelated
unsupported constructs look successfully transformed.

## Example: local ProxyPort decision

The normative transformation document does not define a complete target for
the SysML v1 `ProxyPort` stereotype (Table 30, issue `SYSML2_-329`). The
built-in transformer therefore preserves the base port usage and emits an
explicit warning comment:

```sysml
port pwr : PowerIf;
/* v1 ProxyPort has no normative mapping (Table 30; SYSML2_-329) */
```

A project may review that particular port and decide that its local meaning
is adequately represented by a normal SysML v2 port. A case-by-case rule can
make that decision explicit:

```python
from umlmeta import sysml as S
from umlmeta import v1_to_v2


def local_rule(element, indent):
    if not isinstance(element, S.ProxyPort):
        return None

    pad = "  " * indent
    name = element.name or "proxyPort"
    port_type = element.type.name if element.type is not None else None
    declaration = f"{pad}port {name}"
    if port_type:
        declaration += f" : {port_type}"
    return [
        declaration + ";",
        f"{pad}/* local rule: reviewed ProxyPort {name!r} "
        "is represented as a SysML v2 port */",
    ]

text = v1_to_v2.emit_v2(vehicle_package, mapping_rule=local_rule)
```

This is not presented as a normative SysML v1-to-v2 mapping. It is a local
engineering decision recorded in the transformation rule and in the emitted
model.

## Example: reject until reviewed

A stricter project can stop on every proxy port:

```python
from umlmeta import sysml as S
from umlmeta.v1_to_v2 import UnmappedFeature


def require_proxy_port_review(element, indent):
    if isinstance(element, S.ProxyPort):
        raise UnmappedFeature(
            f"ProxyPort {element.name!r} requires project mapping review"
        )
    return None
```

This keeps the transformer's honesty rule while allowing the project to
selectively add reviewed mappings later.

## Why this is preferable to a global exception handler

A global handler such as:

```python
try:
    text = emit_v2(model)
except UnmappedFeature:
    text = fallback_text
```

cannot distinguish a reviewed `ProxyPort` from an unrelated unsupported
metaclass, malformed relationship, or missing required reference. The rule
hook keeps the decision local, deterministic, testable, and visible in code
review.

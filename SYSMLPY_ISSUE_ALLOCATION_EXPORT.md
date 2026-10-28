# sysmlpy bug report draft: `allocation def` parses but cannot be exported

**Repository:** https://github.com/mycr0ft/sysmlpy
**Version:** `sysmlpy 0.97.1`
**Suggested title:** `allocation def with redefined ends parses but export rejects valid model`

## Summary

`sysmlpy parse` accepts an `allocation def` containing redefined allocation
ends and an `allocate` statement, but `sysmlpy export` fails while reparsing
the same model. This prevents valid parsed models from being emitted through
the JSON interchange path.

## Minimal reproducer

Save as `min-allocation.sysml`:

```sysml
package AllocationBug {
  part def Wheel;
  part def Vehicle {
    part wheels : Wheel;
    ref part spareWheel : Wheel;
  }
  allocation def {
    end :>> source : Wheel;
    end :>> target : Wheel;
    allocate source.wheels to target.spareWheel;
  }
}
```

## Commands

```bash
sysmlpy --version
# sysmlpy 0.97.1

sysmlpy parse min-allocation.sysml
# exit 0

sysmlpy export min-allocation.sysml
# exit 1
# Error: export failed on this model: Syntax error at 8:11:
# no viable alternative at input 'end;'
# Syntax error at 9:11: no viable alternative at input 'end;'
```

The two `end` declarations are the lines reported as failures. The source
model has already parsed successfully, so this appears to be an export-path
round-trip/parser compatibility problem rather than a source syntax error.

## Expected behavior

One of:

1. export the parsed model successfully to JSON interchange; or
2. report a structured unsupported-feature diagnostic that identifies the
   allocation-end construct without failing through a secondary parse error.

## Context

The failure was found while validating a SysML v1-to-v2 transformation. The
full generated model contains:

```sysml
allocation def {
  end :>> source : Wheel;
  end :>> target : Wheel;
  allocate source.wheels to target.spareWheel;
}
```

The ordinary SysML v2 parser accepts this construct, but the interchange
exporter does not. The issue is relevant to round-trip and downstream artifact
workflows because the model can be parsed, analyzed, and rendered but cannot be
exported through the advertised interchange command.

## Additional evidence

Full project reproducer: `vehicle_example_v2.sysml` in the transformation
project. In that file:

```bash
PYTHONPATH=$PWD .venv/bin/python check_xmi_vehicle.py
```

The v1-to-v2 transformation and validation pass (`14 passed, 0 failed`), while:

```bash
.venv/bin/python -m sysmlpy export vehicle_example_v2.sysml
```

fails at the two allocation-end declarations.

## Scope note

This report does not assert the intended SysML v2 interchange representation
for allocation ends. It reports the narrower, reproducible behavior: accepted
by the parser, rejected by export. The exporter maintainers can decide whether
to add representation support or provide an explicit limitation diagnostic.

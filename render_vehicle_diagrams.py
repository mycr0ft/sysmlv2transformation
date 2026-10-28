#!/usr/bin/env python3
"""Render the transformed VehicleExample with sysmlpy and diagramboxes.

The two renderers serve different purposes:

* sysmlpy's PlantUML generator renders a broad semantic overview.
* diagramboxes renders a deliberately selected structural view with nested
  Vehicle contents and boundary ports, using SVG or terminal output.

Neither renderer is intended to reproduce Cameo's saved diagram coordinates.
They regenerate a diagram from the SysML v2 model semantics.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import sysmlpy
from diagramboxes import Diagram, OPEN
from diagramboxes import primitives as _db_primitives
from diagramboxes import svg_canvas as _db_svg


def _join_open_arrowheads() -> None:
    """Keep OPEN arrow wings connected to their final path segment.

    The current diagramboxes main renderer backs an OPEN arrow line off by
    the full arrow size, although the two wings only extend half that
    distance along the path.  On vertical and horizontal routes this leaves
    a visible gap between the path and arrowhead.  Keep the library's other
    arrow styles unchanged and patch only OPEN for this adapter until the
    upstream renderer incorporates the corresponding geometry fix.
    """
    original = _db_primitives._arrow_backoff

    def backoff(style):
        return 0 if style == OPEN else original(style)

    _db_primitives._arrow_backoff = backoff
    _db_svg._arrow_backoff = backoff


_join_open_arrowheads()


def _type_name(element) -> str | None:
    typed = getattr(element, "typedby", None)
    return getattr(typed, "name", None) if typed is not None else None


def _package_definitions(model):
    package = model.packages[0]
    return package, {
        child.name: child for child in package.children
        if getattr(child, "name", None)
    }


def _add_type_definitions(diagram: Diagram, definitions, *, include_axle: bool):
    """Add type-definition boxes used by the selected structural view."""
    # These are definitions, not parts owned by Vehicle.  Dashed typing links
    # would suggest a relationship that is not present in the model, so the
    # port type is shown as a separate definition without a pwr -> PowerIf
    # edge.  A true IBD connection should connect two port usages instead.
    diagram.add_node("Wheel", ["part def"], at=(125, 95))
    if include_axle:
        diagram.add_node("Axle", ["part def"], at=(225, 95))
    diagram.add_node("PowerIf", ["port def"], at=(175, 55))


def render_structural(model) -> Diagram:
    """Render the fuller VehicleExample structural view."""
    package, definitions = _package_definitions(model)
    vehicle = definitions["Vehicle"]
    diagram = Diagram()
    diagram.add_frame(
        "bdd", element_kind="package", element_name=package.name,
        diagram_name="VehicleExample structural view",
    )

    vehicle_node = diagram.add_node(
        "Vehicle", ["part def"],
        attributes=[
            "wheels : Wheel",
            "frontAxle : Axle",
            "rearAxle : Axle",
            f"mass : {_type_name(vehicle.attributes[0]) or 'Kilogram'}",
            "paint : VehicleColor",
        ],
        at=(30, 30),
    )
    # This fuller generated model has both pwr and aux.  aux is intentionally
    # unconnected: the v2 model says it is untyped.
    vehicle_node.add_port("pwr : PowerIf", side="right", offset=0.35)
    vehicle_node.add_port("aux", side="right", offset=0.70)

    _add_type_definitions(diagram, definitions, include_axle=True)
    wheel_node = diagram.nodes[-3]
    axle_node = diagram.nodes[-2]
    diagram.compose(vehicle_node, wheel_node, label="wheels : Wheel")
    diagram.compose(vehicle_node, axle_node,
                    label="frontAxle / rearAxle")
    return diagram


def render_story_structural(model) -> Diagram:
    """Render the compact structural view used by the one-slide story.

    The slide intentionally presents only Vehicle's wheel part, mass value,
    and power port.  The checked transformation artifact contains additional
    examples used by the regression suite; selecting this view must not leak
    those examples into the slide diagram, so Axle and aux are omitted.
    """
    package, definitions = _package_definitions(model)
    vehicle = definitions["Vehicle"]
    diagram = Diagram()
    diagram.add_frame(
        "bdd", element_kind="package", element_name=package.name,
        diagram_name="VehicleExample — the story in one slide",
    )

    vehicle_node = diagram.add_node(
        "Vehicle", ["part def"],
        attributes=[
            "wheels[1..4] : Wheel",
            f"mass : {_type_name(vehicle.attributes[0]) or 'Kilogram'}",
        ],
        at=(30, 30),
    )
    vehicle_node.add_port("pwr : PowerIf", side="right", offset=0.50)

    _add_type_definitions(diagram, definitions, include_axle=False)
    wheel_node = next(n for n in diagram.nodes if n.name == "Wheel")
    diagram.compose(vehicle_node, wheel_node, label="wheels : Wheel")
    return diagram


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="vehicle_example_v2.sysml")
    parser.add_argument(
        "--view", choices=("structural", "story"), default="structural",
        help="structural view, or the compact 'story in one slide' view",
    )
    parser.add_argument("--svg", default=None)
    parser.add_argument("--plantuml", default=None)
    parser.add_argument("--png", default=None,
                        help="optional PNG path; requires PlantUML on PATH")
    args = parser.parse_args()

    defaults = {
        "structural": (
            "vehicle_example_diagramboxes.svg",
            "vehicle_example_sysmlpy.puml",
        ),
        "story": (
            "vehicle_example_story_diagramboxes.svg",
            "vehicle_example_story_sysmlpy.puml",
        ),
    }
    default_svg, default_plantuml = defaults[args.view]
    svg_path = args.svg or default_svg
    plantuml_path = args.plantuml or default_plantuml

    text = Path(args.input).read_text()
    model = sysmlpy.loads(text)
    Path(plantuml_path).write_text(
        sysmlpy.to_plantuml(model, include_legend=True)
    )

    diagram = (render_story_structural(model) if args.view == "story"
               else render_structural(model))
    node_gap = 20 if args.view == "story" else 40
    Path(svg_path).write_text(
        diagram.render_svg(routing="orthogonal", node_gap=node_gap)
    )
    print(f"wrote {svg_path}")
    print(f"wrote {plantuml_path}")
    print("terminal preview:")
    print(diagram.render(routing="orthogonal", node_gap=node_gap))


if __name__ == "__main__":
    main()

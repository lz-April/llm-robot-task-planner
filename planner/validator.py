from typing import List

from schemas import RobotPlan, SceneState, RobotAction, EXAMPLE_PLAN, EXAMPLE_SCENE


class PlanValidationError(Exception):
    """Raised when a robot plan is invalid."""
    pass


def get_scene_object_names(scene: SceneState) -> set[str]:
    """Return a set of object names available in the scene."""
    return {obj.name for obj in scene.objects}


def validate_action_objects(action: RobotAction, scene_objects: set[str]) -> None:
    """Check whether objects and targets in one action exist in the scene."""

    if action.object is not None and action.object not in scene_objects:
        raise PlanValidationError(
            f"Unknown object: {action.object}"
        )

    if action.target is not None and action.target not in scene_objects:
        # Later, we may allow symbolic targets like 'side_area'.
        # For now, targets must be real scene objects.
        raise PlanValidationError(
            f"Unknown target: {action.target}"
        )


def validate_action_logic(plan: RobotPlan) -> None:
    """Check simple logical constraints in the action sequence."""

    if len(plan.steps) == 0:
        raise PlanValidationError("Plan has no steps.")

    if plan.steps[-1].action != "done":
        raise PlanValidationError("Plan must end with a done action.")

    held_object = None

    for step in plan.steps:
        if step.action == "pick":
            if step.object is None:
                raise PlanValidationError("Pick action requires an object.")

            if held_object is not None:
                raise PlanValidationError(
                    f"Robot is already holding {held_object}, cannot pick {step.object}."
                )

            held_object = step.object

        elif step.action == "place":
            if step.object is None:
                raise PlanValidationError("Place action requires an object.")

            if step.target is None:
                raise PlanValidationError("Place action requires a target.")

            if held_object != step.object:
                raise PlanValidationError(
                    f"Cannot place {step.object}; robot is holding {held_object}."
                )

            held_object = None

        elif step.action == "move":
            if step.object is None:
                raise PlanValidationError("Move action requires an object.")

            if step.target is None:
                raise PlanValidationError("Move action requires a target.")

        elif step.action == "locate":
            if step.object is None:
                raise PlanValidationError("Locate action requires an object.")

        elif step.action == "done":
            pass


def validate_plan(plan: RobotPlan, scene: SceneState) -> bool:
    """Validate a complete robot plan against the scene and action rules."""

    scene_objects = get_scene_object_names(scene)

    for action in plan.steps:
        validate_action_objects(action, scene_objects)

    validate_action_logic(plan)

    return True


if __name__ == "__main__":
    try:
        validate_plan(EXAMPLE_PLAN, EXAMPLE_SCENE)
        print("Example plan is valid.")
    except PlanValidationError as error:
        print(f"Example plan is invalid: {error}")
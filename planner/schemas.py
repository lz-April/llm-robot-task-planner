from typing import List, Literal, Optional
from pydantic import BaseModel, Field


ActionType = Literal[
    "locate",
    "pick",
    "place",
    "move",
    "done",
]


class RobotAction(BaseModel):
    action: ActionType = Field(
        description="A high-level robot action."
    )
    object: Optional[str] = Field(
        default=None,
        description="The object to locate, pick, place, or move."
    )
    target: Optional[str] = Field(
        default=None,
        description="The target object or target location."
    )
    reason: Optional[str] = Field(
        default=None,
        description="A short explanation of why this action is needed."
    )


class RobotPlan(BaseModel):
    instruction: str = Field(
        description="The original natural language instruction."
    )
    steps: List[RobotAction] = Field(
        description="A sequence of structured robot actions."
    )


class SceneObject(BaseModel):
    name: str = Field(
        description="Unique object name used by the planner and executor."
    )
    type: str = Field(
        description="Object type, such as cube, box, bowl, cylinder, or table."
    )
    color: Optional[str] = Field(
        default=None,
        description="Object color."
    )
    location: Optional[str] = Field(
        default=None,
        description="Symbolic object location in the scene."
    )


class SceneState(BaseModel):
    objects: List[SceneObject] = Field(
        description="Objects currently available in the simulated scene."
    )


# Example scene used for testing the planner.
EXAMPLE_SCENE = SceneState(
    objects=[
        SceneObject(
            name="red_cube",
            type="cube",
            color="red",
            location="table_center",
        ),
        SceneObject(
            name="blue_box",
            type="box",
            color="blue",
            location="table_right",
        ),
        SceneObject(
            name="green_cylinder",
            type="cylinder",
            color="green",
            location="table_left",
        ),
    ]
)


# Example structured plan generated from a natural language command.
EXAMPLE_PLAN = RobotPlan(
    instruction="Put the red cube into the blue box.",
    steps=[
        RobotAction(
            action="locate",
            object="red_cube",
            reason="The robot must identify the object before manipulating it.",
        ),
        RobotAction(
            action="pick",
            object="red_cube",
            reason="The red cube must be grasped before it can be moved.",
        ),
        RobotAction(
            action="place",
            object="red_cube",
            target="blue_box",
            reason="The red cube should be placed into the target container.",
        ),
        RobotAction(
            action="done",
            reason="The task is complete.",
        ),
    ],
)


if __name__ == "__main__":
    print("Example Scene:")
    print(EXAMPLE_SCENE.model_dump_json(indent=2))

    print("\nExample Plan:")
    print(EXAMPLE_PLAN.model_dump_json(indent=2))
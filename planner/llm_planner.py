import json
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from schemas import RobotAction, RobotPlan, SceneState, EXAMPLE_SCENE
from validator import validate_plan, PlanValidationError


SYSTEM_PROMPT = """
You are a high-level robot task planner for a tabletop manipulation robot.

Your job is to convert a natural language command into a structured robot action plan.

Allowed actions:
- locate(object)
- pick(object)
- place(object, target)
- move(object, target)
- done()

Important rules:
1. Only use the allowed actions.
2. Only refer to objects that exist in the scene.
3. Do not invent new objects.
4. The robot can hold only one object at a time.
5. A place action must happen after picking the same object.
6. The final action must be done.
7. Output ONLY valid JSON.
8. Do not include markdown, explanation, or extra text.

The JSON must match this schema:

{
  "instruction": "original user instruction",
  "steps": [
    {
      "action": "locate | pick | place | move | done",
      "object": "object name or null",
      "target": "target object/location or null",
      "reason": "short reason"
    }
  ]
}
"""


def scene_to_text(scene: SceneState) -> str:
    """Convert scene objects into text for the LLM prompt."""
    lines = []

    for obj in scene.objects:
        lines.append(
            f"- name: {obj.name}, type: {obj.type}, "
            f"color: {obj.color}, location: {obj.location}"
        )

    return "\n".join(lines)


def generate_plan_rule_based(
    instruction: str,
    scene: SceneState,
) -> RobotPlan:
    """
    Fallback planner used when no API key is available.

    This is intentionally simple. It lets the pipeline run without calling an LLM.
    """
    object_names = {obj.name for obj in scene.objects}

    if "red_cube" in object_names and "blue_box" in object_names:
        return RobotPlan(
            instruction=instruction,
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

    return RobotPlan(
        instruction=instruction,
        steps=[
            RobotAction(
                action="done",
                reason="No valid plan could be generated from the current scene.",
            )
        ],
    )


def generate_plan_with_openai(
    instruction: str,
    scene: SceneState,
    model: str = "gpt-4o-mini",
) -> RobotPlan:
    """
    Use OpenAI to convert a natural language instruction into a RobotPlan.
    """
    client = OpenAI()

    user_prompt = f"""
Current scene:
{scene_to_text(scene)}

User instruction:
{instruction}

Generate a structured robot action plan.
"""

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    raw_content = response.choices[0].message.content

    if raw_content is None:
        raise ValueError("OpenAI returned an empty response.")

    parsed_json = json.loads(raw_content)

    return RobotPlan.model_validate(parsed_json)


def generate_plan(
    instruction: str,
    scene: SceneState,
    use_llm: Optional[bool] = None,
) -> RobotPlan:
    """
    Main planner function.

    If use_llm=True, call OpenAI.
    If use_llm=False, use rule-based fallback.
    If use_llm=None, use OpenAI only when OPENAI_API_KEY exists.
    """
    load_dotenv()

    if use_llm is None:
        use_llm = bool(os.getenv("OPENAI_API_KEY"))

    if use_llm:
        plan = generate_plan_with_openai(
            instruction=instruction,
            scene=scene,
        )
    else:
        plan = generate_plan_rule_based(
            instruction=instruction,
            scene=scene,
        )

    validate_plan(plan, scene)

    return plan


if __name__ == "__main__":
    instruction = "Put the red cube into the blue box."

    try:
        plan = generate_plan(
            instruction=instruction,
            scene=EXAMPLE_SCENE,
            use_llm=False,
        )

        print("Generated Plan:")
        print(plan.model_dump_json(indent=2))

    except PlanValidationError as error:
        print(f"Plan validation failed: {error}")

    except Exception as error:
        print(f"Planner failed: {error}")
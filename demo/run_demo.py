from planner.llm_planner import generate_plan
from planner.schemas import EXAMPLE_PLAN, EXAMPLE_SCENE
from planner.validator import validate_plan, PlanValidationError


def main():

    instruction = "Put the red cube into blue box."

    try:
        plan = generate_plan(instruction, EXAMPLE_SCENE)
        validate_plan(plan, EXAMPLE_SCENE)
        print("Instruction:")
        print(instruction)

        print("\nGenerated plan:")
        for i,step in enumerate(plan.steps, start = 1):
            print(f"{i}. {step.action} object={step.object} target={step.target}")
        
        print("\nPlan validation passed.")
    except PlanValidationError as error:
        print(f"Plan validation failed: {error}")


if __name__ == "__main__":
    main()
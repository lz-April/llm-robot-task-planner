# llm-robot-task-planner
A prototype system that uses an LLM to convert natural-language household commands into structured robot action plans, with rule-based safety checks and simulated execution.

## Motivation

As robots and autonomous agents become more capable, natural-language interfaces can make them easier to use. However, blindly executing LLM-generated plans may introduce safety risks. This project explores a simple pipeline for trustworthy language-guided robot planning:

Natural Language Instruction → LLM Planner → Structured Plan → Safety Checker → Simulated Robot Execution

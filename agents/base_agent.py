"""
Base Agent and Task abstraction for Multi-Agent AI Tutor.
Adheres to CrewAI patterns (Agent, Task, Crew, Flow) while maintaining
full compatibility with Python 3.14 without legacy C-compiler build constraints.
"""

from typing import List, Dict, Any, Optional, Callable
import time


class BaseTutorAgent:
    """Represents an autonomous educational agent with a defined role, goal, and backstory."""

    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        verbose: bool = True,
        groq_service: Optional[Any] = None
    ):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.verbose = verbose
        self.groq_service = groq_service

    def log(self, message: str):
        if self.verbose:
            print(f"[{self.role}] {message}")

    def run_task(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Any:
        raise NotImplementedError("Each agent must implement run_task()")


class Task:
    """A unit of work assigned to an Agent with expected output specification."""

    def __init__(
        self,
        description: str,
        expected_output: str,
        agent: BaseTutorAgent,
        context: Optional[Dict[str, Any]] = None
    ):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        self.context = context or {}
        self.output: Optional[Any] = None
        self.completed: bool = False

    def execute(self) -> Any:
        self.agent.log(f"Starting task: {self.description[:80]}...")
        start = time.time()
        self.output = self.agent.run_task(self.description, self.context)
        self.completed = True
        elapsed = round(time.time() - start, 2)
        self.agent.log(f"Task completed in {elapsed}s.")
        return self.output


class Crew:
    """Orchestrates sequential or hierarchical execution of Agents and Tasks."""

    def __init__(
        self,
        agents: List[BaseTutorAgent],
        tasks: List[Task],
        verbose: bool = True
    ):
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose

    def kickoff(self) -> Dict[str, Any]:
        results = {}
        for idx, task in enumerate(self.tasks):
            if self.verbose:
                print(f"\n--- [Crew Orchestrator] Executing Task {idx+1}/{len(self.tasks)} ---")
            task_result = task.execute()
            results[f"task_{idx+1}"] = task_result
        return results

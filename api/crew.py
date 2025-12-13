from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ApiCrew():
    """ApiCrew crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # Since we are in a simple API example without YAML files for now, 
    # we will define agents and tasks inline. 
    # In a real project, you might want to load them from config files.

    def __init__(self):
        # Default to Gemini Flash for speed and costenv efficiency
        self.llm = LLM(
            model="gemini/gemini-3-pro-preview",
            api_key=os.environ.get("GEMINI_API_KEY")
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            role='Researcher',
            goal='Discover new insights about {topic}',
            backstory='You are a world class researcher working on a major project',
            verbose=True,
            llm=self.llm
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            role='Reporting Analyst',
            goal='Create a detailed report based on the findings',
            backstory='You are a senior analyst capable of summarizing complex data',
            verbose=True,
            llm=self.llm
        )

    @task
    def research_task(self) -> Task:
        return Task(
            description='Conduct research on {topic}.',
            expected_output='A list of 5 key points about {topic}.',
            agent=self.researcher()
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            description='Review the research findings and write a short blog post.',
            expected_output='A markdown blog post about {topic}.',
            agent=self.reporting_analyst(),
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ApiCrew crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

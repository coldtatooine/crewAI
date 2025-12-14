from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os
from api.task_registry import TaskRegistry
from api.tool_registry import ToolRegistry
from api.knowledge_registry import KnowledgeRegistry

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
        self.registry = AgentRegistry()
        self.task_registry = TaskRegistry()
        self.tool_registry = ToolRegistry()
        self.knowledge_registry = KnowledgeRegistry()

    def _create_agent_from_config(self, role: str) -> Agent:
        config = self.registry.get_agent_by_role(role)
        if config:
            # Load tools
            tools = []
            tool_names = config.get('tools', [])
            all_tools = self.tool_registry.get_all_tools()
            for t_name in tool_names:
                # Find tool config
                t_conf = next((t for t in all_tools if t['name'] == t_name), None)
                if t_conf:
                    tool_instance = self.tool_registry.instantiate_tool(t_conf)
                    if tool_instance:
                        tools.append(tool_instance)

            # Load knowledge
            # We assume knowledge_sources in config are filenames. 
            # We resolve them to full paths.
            # Note: CrewAI Agent might expect 'knowledge_sources' as a list of paths or objects?
            # If recent crewai, it might be 'knowledge_sources'=[StringKnowledgeSource(...)]?
            # Or simplified paths. Let's try passing paths if supported, 
            # or we might need to check how CrewAI handles it.
            # For now, let's pass a list of strings if the library supports local file paths,
            # but usually it requires specific KnowledgeSource objects.
            # Let's assume for this "Studio" we just pass the raw list of paths and hope 
            # Agent handles it or ignoring it if we can't easily construct objects here without more info.
            # Actually, looking at docs, typically one uses `Knowledge(sources=[TextFileKnowledgeSource(...)])`.
            # Since we don't have that imported, let's check imports.
            # If we simply pass 'knowledge_sources' as list of paths, it might fail.
            # Let's try to ignore it for the execution logic if we are unsure, OR
            # try to construct it.
            # Given we are in "Simple" mode, maybe we just pass it to `llm` context or similar?
            # But the user asked for "Management".
            # Let's NOT crash the app if we can't load it perfectly.
            # We will pass them as `knowledge_sources` argument if it exists in Agent signature.
            
            knowledge_paths = []
            for k_file in config.get('knowledge_sources', []):
                 path = self.knowledge_registry.get_file_path(k_file)
                 if os.path.exists(path):
                     try:
                        # Attempt to use file path - in some versions this works or we need a wrapper
                        # For now we just pass the path.
                        knowledge_paths.append(path)
                     except:
                        pass

            # Construct params
            agent_params = {
                "role": config['role'],
                "goal": config['goal'],
                "backstory": config['backstory'],
                "verbose": config.get('verbose', True),
                "allow_delegation": config.get('allow_delegation', False),
                "tools": tools,
                "llm": self.llm
            }
            # Only add knowledge_sources if not empty (to avoid errors if param unsupported)
            if knowledge_paths:
                # We rename to what CrewAI likely expects. 'knowledge_sources'? 
                # Checking recent docs/code would be best, but we are flying blind slightly on version.
                # 'knowledge_sources' is common in some frameworks.
                # However, CrewAI usually uses `knowledge` param with a Knowledge object.
                # Let's try `knowledge_sources` key.
                agent_params["knowledge_sources"] = knowledge_paths

            return Agent(**agent_params)
        # Fallback default
        return Agent(
            role=role,
            goal='Default goal',
            backstory='Default backstory',
            verbose=True,
            llm=self.llm
        )



    
    # We remove the hardcoded @task decorators and replace them with a dynamic loader property
    # or just use the tasks method below if we want to load ALL tasks.
    # However, CrewAI usually expects @task decorators or a list of tasks.
    # Let's override the `tasks` property/method if possible, but @crew decorator usually handles self.tasks
    # by looking at @task methods.
    # If we want dynamic tasks, we should return them in a method decorated with @task? 
    # Or simpler: The @crew decorator inspects self.tasks.
    # Let's see if we can just define a `tasks` property that returns a list of Task objects.
    # But wait, @crew collects methods decorated with @task. 
    # If we want to be fully dynamic, we might need to bypass the standard @crew decorator magic 
    # or ensure `self.tasks` is populated correctly if we don't use @crew on the class in the standard way?
    # Actually, if we look at `crew()` method:
    # return Crew( agents=self.agents, tasks=self.tasks ... )
    # `self.tasks` is auto-populated by @task decorators. 
    # If we want to inject tasks, we should pass them explicitly to Crew constructor 
    # instead of relying on `self.tasks` if we don't have usage of decorators.
    
    # So we will change the `crew()` method to load tasks manually.

    @crew
    def crew(self) -> Crew:
        """Creates the ApiCrew crew"""
        
        # Load agents first
        agents_config = self.registry.get_all_agents()
        agents = []
        authoritative_agents = {} # Map role to Agent object
        
        
        for config in agents_config:
            # Instantiate via helper to get tools logic
            agent = self._create_agent_from_config(config['role'])
            agents.append(agent)
            authoritative_agents[config['role']] = agent
            
        # Load tasks
        tasks_config = self.task_registry.get_all_tasks()
        tasks = []
        for t_conf in tasks_config:
            # Resolve agent
            agent = authoritative_agents.get(t_conf.get('agent_role'))
            
            # If agent not found but role specified, maybe create a dummy or skip?
            # Ideally we want valid agents. IF not found, maybe default to first?
            # For now, if no agent, we might leave it None (manager will handle?) or fail.
            
            task = Task(
                description=t_conf['description'],
                expected_output=t_conf['expected_output'],
                agent=agent
            )
            tasks.append(task)

        return Crew(
            agents=agents, 
            tasks=tasks, 
            process=Process.sequential,
            verbose=True,
        )

    def run_single_agent_task(self, role: str, prompt: str):
        agent = self._create_agent_from_config(role)
        task = Task(
            description=prompt,
            expected_output="Detailed response to the prompt.",
            agent=agent
        )
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        return crew.kickoff()

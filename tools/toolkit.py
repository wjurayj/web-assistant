import openai

class ToolKit:
    def __init__(self, model='text-davinci-003'):
        self.model = model
        self.tools = []

    def check_tools(self, messages):
        prompts = []
        idx_map = {}

        for i, tool in enumerate(self.tools):
            trigger_prompt = tool.get_trigger_prompt()
            action_prompt = tool.get_action_prompt()
            combined_prompt = f"{trigger_prompt}\n{action_prompt.format(messages)}"
            prompts.append(combined_prompt)
            idx_map[i] = tool

        completions = openai.Completion.create(engine=self.model,
                                               prompt=prompts,
                                               max_tokens=100,
                                               n=len(prompts),
                                               stop=None,
                                               temperature=0)

        responses = {}
        
        for choice in completions.choices:
            index, response_text = choice.index, choice.text.strip()
            tool_in_response = idx_map[index]
            responses[tool_in_response] = response_text

        return responses


    def add_tool(self, tool):
        self.tools.append(tool)

class Tool:
    def __init__(self, trigger_prompt="", actions_prompt=""):
        self.trigger_prompt = trigger_prompt
        self.action_prompt = actions_prompt

    def get_trigger_prompt(self):
        return self.trigger_prompt

    def get_action_prompt(self):
        return self.action_prompt

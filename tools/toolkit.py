import openai
import asyncio
from typing import Any


class ToolKit:
    def __init__(self, model='text-davinci-003', thinker=None):
        self.model = model
        self.tools = []
        self.thinker = thinker
        
    async def dispatch_openai_requests(
        messages_list: list[list[dict[str,Any]]],
        model: str,
        temperature: float,
        max_tokens: int,
        top_p: float,
    ) -> list[str]:
        """Dispatches requests to OpenAI API asynchronously.

        Args:
            messages_list: List of messages to be sent to OpenAI ChatCompletion API.
            model: OpenAI model to use.
            temperature: Temperature to use for the model.
            max_tokens: Maximum number of tokens to generate.
            top_p: Top p to use for the model.
        Returns:
            List of responses from OpenAI API.
        """
        async_responses = [
            openai.ChatCompletion.acreate(
                model=model,
                messages=x,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )
            for x in messages_list
        ]
        return await asyncio.gather(*async_responses)

    def check_tools(self, messages):
        prompts = []
        idx_map = {}

        for i, tool in enumerate(self.tools):
            trigger_prompt = tool.get_trigger_prompt()
            action_prompt = tool.get_action_prompt()
            combined_prompt = f"{trigger_prompt}\n{action_prompt.format(messages)}"
            prompts.append(combined_prompt)
            idx_map[i] = tool

        # completions = openai.Completion.create(engine=self.model,
        #                                        prompt=prompts,
        #                                        max_tokens=100,
        #                                        n=len(prompts),
        #                                        stop=None,
        #                                        temperature=0)
        
        # responses = {}
        
        # for choice in completions.choices:
            # index, response_text = choice.index, choice.text.strip()
            # tool_in_response = idx_map[index]
            # responses[tool_in_response] = response_text
            
        completions = asyncio.run(
                self.dispatch_openai_requests(
                    messages_list = [{'user':p} for p in prompts],
                    model = 'gpt-3.5-turbo',
                    temperature=0,
                    max_tokens=3,
                    top_p=1,
            )
        )
        responses = {}
        for i, x in enumerate(completions):
            responses[i] = x['choices'][0]['message']['content'].strip()

        # copmletions


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

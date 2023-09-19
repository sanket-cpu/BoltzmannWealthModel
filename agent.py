from typing import Any
import mesa
from mesa.model import Model
import seaborn as sns
import numpy as np
import pandas as pd


def compute_poor(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return 1 + (1 / N) - 2 * B




class MoneyAgent(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 1:
            other_agent = self.random.choice(cellmates)
            other_agent.wealth += 1
            self.wealth -= 1

    def step(self):
        self.move()
        if self.wealth > 0:
            self.give_money()
#tryna push stuff
class MoneyModel(mesa.Model):
    """a model with N agents"""
    def __init__(self, N , width,height):
        self.num_agents = N
        self.grid = mesa.space.MultiGrid(width,height,False)
        # create a scheduler and assign to model
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        for i in range(self.num_agents):
            a = MoneyAgent(i,self)
            # add agent to scheduler
            self.schedule.add(a)
            # add agents randomly to grid 
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a,(x,y))
        self.datacollector = mesa.DataCollector(model_reporters={"Gini": compute_poor}, agent_reporters={"Wealth": "wealth"})
    
    def step(self):
        self.datacollector.collect(self)
        # model's step , increases tick by one and agent's tick action is performed
        self.schedule.step()
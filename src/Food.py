from src.DObject import DObject


class Food(DObject):
    def __init__(self, position=None, food_amount=1):
        super().__init__(position)
        self.food_amount = food_amount
        self.current_amount = food_amount
        self.detect_range = 40 / 1000  # (4 cm)
        if position:
            self.position = position

    def eat_amount(self, agent):
        damount = 0.01
        finished = False

        if damount > self.current_amount:
            # only a bit of food left
            damount = self.current_amount
            finished = True

        if agent.food_amount + damount >= 1:
            # don't over eat
            damount = 1 - agent.food_amount
            finished = True

        self.current_amount -= damount
        agent.food_amount += damount

        return finished

    def get_food_left(self):
        return self.current_amount / self.food_amount

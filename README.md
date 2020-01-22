# Two Player Wimblepong

This project is a two player version of the pong-v0 OpenAI Gym environment.
The environment is used in the Reinforcement Learning course at Aalto University,
Finland.

## How to use
- Clone the repository: `https://github.com/aalto-intelligent-robotics/Wimblepong`.
- Install the dependencies listed in requirements.txt.
- Check out the examples `test_pong_ai_multi.py` and `test_pong_ai.py` to see how
to make an agent play against the included SimpleAI or two SimpleAIs against each other.

## Environments
The environments as defined in `__init__.py` are:
- WimblepongVisualMultiplayer-v0: Two agents are playing against each other based on
the pixel observation
- WimblepongVisualSimpleAI-v0: One agent plays against a SimpleAI based on the pixel
observations
- WimblepongMultiplayer-v0: Two agents are playing against each other based on the
absolute positions of the ball and the paddles
- WimblepongSimpleAI-v0: One agent plays against a SimpleAI based on the absolute
positions of the ball and the paddles

## Interface
The interface is designed to be used like the OpenAI Gym environment.
### `env.step()`
- Takes the input action as parameter (0: STAY, 1: UP, 2: DOWN): Takes either one
action if the opponent is a SimpleAI or a tuple of two actions if two agents are
playing against each other.
- Returns observation: A returned observation is an array of (210, 160, 3) RGB values.
If the game is played against an agent that uses the absolute values, such as SimpleAI,
the returned observation is one array. If two agents that use pixel observations play
against each other, the returned values is a tuple of two observations, one for each player.
In each observation, the agents paddle is always green and on the left side of the arena and the
opponents paddle is red and on the other side. For example, if player 2 is
playing on the right side, the observation for player 2 will be flipped and
red and green colors will be inverted such that playing on both sides looks
the same for the agent but normal when rendering the game.
- Returns the rewards for each player, either a tuple or 1 value depending on if two
or one action have been passed as parameter.
- Returns if an episode is done.
- Returns an info dict for debug information
### `env.render()`
- Renders the current state of the game.
### `env.reset()`
- Resets the position of the player paddles and the ball, usually used when an
episode is over. Launches the ball in a random direction.
### `env.switch_sides()`
- Allows the agents to switch sides and also switches the sides of the scoreboard.
(The observations will still look the same with the agent using the green paddle no matter on which side the agent plays)
### `set_names(p1, p2)`
- Function to pass the agent names to the environment. The names will also be displayed
on the scoreboard

## SimpleAI
The SimpleAI agent is an agent that uses the absolute ball and player positions to
follow the ball and reflect it in random directions.


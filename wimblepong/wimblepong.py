import math
import random
import numpy as np
import gym
import os
from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager
import cv2


class Rect(object):
    """
    The Rect class describes a rectangle with width, height and xy position.
    The rectangle also has a draw function to render it.
    Collisions between rectangles are handled here.
    """
    def __init__(self, x, y, w, h, color=(1, 1, 1)):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.color = np.array(list(color))

    def collide_point(self, x, y):
        # Check if the point given by x and y has collided with the rectangle.
        return self.x < x < self.x+self.w and self.y < y < self.y+self.h

    def collide_rect_vertices(self, rect):
        c1 = self.collide_point(rect.x, rect.y)
        c2 = self.collide_point(rect.x+rect.w, rect.y)
        c3 = self.collide_point(rect.x+rect.w, rect.y+rect.h)
        c4 = self.collide_point(rect.x, rect.y+rect.h)
        return c1 or c2 or c3 or c4

    def collide_rect(self, rect):
        # First, check if any of the vertices of rect lies within self
        colliding = self.collide_rect_vertices(rect)
        if not colliding:
            # Perform the same check the other way around
            # Necessary if self is fully contained inside rect
            colliding = rect.collide_rect_vertices(self)
        return colliding

    def draw_on(self, array):
        # Function to draw the rectangle onto an array given at its position
        # with width and height
        yl, yh = int(self.y), int(self.y+self.h)
        xl, xh = int(self.x), int(self.x+self.w)
        array[yl:yh, xl:xh] = self.color

class Ball():
    """
    The Ball class represents the game ball, its position and allows the
    environment to reset, move and reflect the ball.
    """
    def __init__(self, x, y, w, h, GAME_AREA_RESOLUTION, SCOREBOARD_HEIGHT):
        # xy position and width/height of the ball
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.previous_x = x
        self.previous_y = y
        self.last_touch = 0             # Remember who touched the ball last to
                                        # prevent multiple reflections
        self.color = (255, 255, 255)    # Color of the ball
        self.rect = None                # Rectangle describing the square shaped ball
        self.MAX_BOUNCE_ANGLE = 75      # Limit the maximum reflection angle
        self.vector = None              # The x and y velocity vector of the ball
        self.GAME_AREA_RESOLUTION = GAME_AREA_RESOLUTION
        self.SCOREBOARD_HEIGHT = SCOREBOARD_HEIGHT
        self.reset_ball()               # Initialize the ball

    def move(self):
        # Update previous position values
        self.previous_x = self.x
        self.previous_y = self.y

        # Move the ball depending on the velocity vector
        self.x += self.vector[0]
        self.y += self.vector[1]

        # Collision with left and right wall of the arena
        if self.x <= 0 - self.w//2:
            return 2, True
        if self.x >= self.GAME_AREA_RESOLUTION[0] - self.w//2:
            return 1, True
        # Collision with top and bottom wall of the arena
        if (self.y - self.h//2 - abs(self.vector[1]) <= self.SCOREBOARD_HEIGHT and self.vector[1] < 0) or (self.y + self.h//2 + abs(self.vector[1]) >= self.GAME_AREA_RESOLUTION[1] + self.SCOREBOARD_HEIGHT and self.vector[1] > 0):
            self.vector = (self.vector[0], -1 * self.vector[1])
        self.update_rect()
        return 0, False

    def update_rect(self):
        # Update the rectangle that describes the ball
        self.rect = Rect(self.x - self.w/2, self.y-self.h/2, self.w, self.h, self.color)

    def reflect(self, offcenter, direction, player):
        """
        This function computes the reflection angle and updates the balls velocity vector
        based on the reflection detected in the environment.

        Called by the environment on collision between a player and a ball object.

        ARGUMENTS:
        - int, offcenter: How far from the enter the ball has collided with the
        player paddle (the further off the center the larger the reflection angle)
        - int, direction: Gives the direction in which the ball is flying.
        Helps to invert the velociy vector
        """
        normalized_offcenter = offcenter / (player.h/2) * direction
        bounce_angle = normalized_offcenter * self.MAX_BOUNCE_ANGLE
        if player.player_number == 1:
            self.vector = (3 * (math.cos(math.radians(bounce_angle)) + 1)*self.speed_mul, 8 * -math.sin(math.radians(bounce_angle))*self.speed_mul)
        else:
            self.vector = (-3 * (math.cos(math.radians(bounce_angle)) + 1)*self.speed_mul, 8 * math.sin(math.radians(bounce_angle))*self.speed_mul)
        self.speed_mul += .005

    def reset_ball(self):
        """
        This function resets the position, velocity vector, speed multiplier
        and last_touch of the ball.
        The ball is put back to the center of the arena and starts off
        in a random direction.
        """
        self.x = self.GAME_AREA_RESOLUTION[0]//2
        self.y = self.GAME_AREA_RESOLUTION[1]//2+self.SCOREBOARD_HEIGHT
        self.last_touch = 0
        self.update_rect()
        # Reset ball in random direction
        bounce_angle = np.random.random() * 40
        side = random.choice([True, False])
        if side == True:
            d = 1
        else:
            d = -1
        up_down = random.choice([True, False])
        if up_down == True:
            u = 1
        else:
            u = -1
        # Reset the speed multiplyer to the initial value
        self.speed_mul = 0.4

        vx = d*3*(math.cos(math.radians(bounce_angle)) + 1)*self.speed_mul
        vy = u*6*math.sin(math.radians(bounce_angle))*self.speed_mul
        self.vector = vx, vy


class Player():
    """
    This class defines a player and the corresponding paddle.
    It provides functions to move the paddle and reset its position
    """
    def __init__(self, player_number, GAME_AREA_RESOLUTION, SCOREBOARD_HEIGHT):
        self.player_number = player_number  # Defines on which side the player plays (1: left, 2. right)
        self.score = 0                      # Player score
        self.x = 0                          # Paddle x position (left side)
        self.y = 0                          # Paddle y position (center)
        self.w = 5                          # Paddle width
        self.h = 20                         # Paddle height
        self.rect = None                    # Rectangle that defines the paddle
        self.color = (0, 0, 0)              # Paddle color
        self.GAME_AREA_RESOLUTION = GAME_AREA_RESOLUTION
        self.SCOREBOARD_HEIGHT = SCOREBOARD_HEIGHT
        self.paddle_padding = 10            # Distance from game area boudary
                                            # to paddle
        self.reset()                        # Initialize by resetting the paddle
        self.paddle_speed = 3               # Vertical speed of the paddle
        self.name = "Nameless"              # Name of the player/agent, set by the environment

    def move_up(self):
        # Move the paddle up if within the bounds of the arena
        if self.y - self.paddle_speed >= self.SCOREBOARD_HEIGHT + self.h / 2:
            self.y -= self.paddle_speed
        self.update_rect()

    def move_down(self):
        # Move the paddle down if within the bounds of the arena
        if self.y + self.paddle_speed <= self.GAME_AREA_RESOLUTION[1] + self.SCOREBOARD_HEIGHT - self.h / 2:
            self.y += self.paddle_speed
        self.update_rect()

    def reset(self):
        # Reset the player position to the center of the arena and set the player color
        if self.player_number == 1:
            self.x = self.paddle_padding
            self.color = (75, 170, 106)
        else:
            self.x = self.GAME_AREA_RESOLUTION[0] - self.paddle_padding + 1
            self.color = (202, 46, 85)
        self.y = self.GAME_AREA_RESOLUTION[1]//2 + self.SCOREBOARD_HEIGHT
        self.update_rect()

    def update_rect(self):
        # Update the rectangle representation of the player that is used by the environment
        # The player rectangle is only used for colliding and drawing
        self.rect = Rect(self.x - self.w / 2, self.y - self.h / 2, self.w, self.h, self.color)


class Wimblepong(gym.core.Env):
    MOVE_UP, MOVE_DOWN, STAY = 1, 2, 0                  # Define names for the actions in the action space
    def __init__(self, opponent=None, visual=True):
        """
        Initialization of the game arena
        """
        x_game_res = 200
        y_game_res = 235
        self.SCOREBOARD_HEIGHT = 35
        self.SCREEN_RESOLUTION = (y_game_res, x_game_res)         # The size of the window
                                                                  # to render including score
                                                                  # and name bar at the top
        x_arena_res = self.SCREEN_RESOLUTION[1]
        y_arena_res = self.SCREEN_RESOLUTION[0]-self.SCOREBOARD_HEIGHT
        self.GAME_AREA_RESOLUTION = (x_arena_res, y_arena_res)    # The size of the actual
                                                                  # game arena without the score
                                                                  # and name bar at the top
        arena_x_center = self.SCREEN_RESOLUTION[1]//2
        arena_y_center = (self.SCREEN_RESOLUTION[0]-self.SCOREBOARD_HEIGHT)//2+self.SCOREBOARD_HEIGHT
        self.GAME_AREA_CENTER = (arena_x_center, arena_y_center)  # The center of the game arena
        self.BACKGROUND_COLOR = np.array([33, 1, 36], np.uint8)  # The arenas background color
        self.SCOREBOARD_BORDER = 4
        self.SEPARATOR_BORDER = 3

        self.scale = 1                                  # Scale of the game window
        self.fps = 30                                   # Rendering frames per second

        # Cache the background to make it faster
        self.background = np.zeros((*self.SCREEN_RESOLUTION, 3), np.uint8) \
                          + self.BACKGROUND_COLOR

        self.action_space = gym.spaces.Discrete(3)      # Define a discrete action
                                                        # space with 3 possible actions
        self.frameskip = 3

        # Load scoreboard font
        self.scoreboard_font = self.load_font()

        # Initialize screen
        self.screen = None                              # Screen object used for rendering
        self._reset_screen()                           # Fill the screen with background color

        # Define the game objects, create player 1,2 and the ball
        ball_size = 5
        self.player1 = Player(1, self.GAME_AREA_RESOLUTION, self.SCOREBOARD_HEIGHT)
        self.player2 = Player(2, self.GAME_AREA_RESOLUTION, self.SCOREBOARD_HEIGHT)
        self.ball = Ball(self.GAME_AREA_CENTER[0], self.GAME_AREA_CENTER[1] - int(ball_size/2), ball_size, ball_size, self.GAME_AREA_RESOLUTION, self.SCOREBOARD_HEIGHT)

        # If an agent uses visual mode it gets an observation when calling
        # _get_observation()
        # If an agent does not use visual mode it gets the absolute positions of
        # each player and the ball.
        self.visual = visual
        if visual:
            self.observation_space = gym.spaces.Box(low=0, high=255, shape=\
                    (y_arena_res, x_arena_res, 3), dtype=np.uint8)
        else:
            self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(6,))

        # If opponent is None, switch to multiplayer mode. Two agents are playing.
        # Otherwise grab P2 action from the opponent. One agent is playing against
        # for example a bot in singleplayer mode.
        if opponent is None:
            self.opponent = None
        else:
            # Instantiate the opponent
            self.opponent = opponent(self, player_id=2)
        try:
            self.player2.name = self.opponent.get_name()
        except:
            pass

    def set_names(self, p1=None, p2=None):
        if self.opponent is None:
            # Multiplayer mode; set both
            if p1 is not None:
                self.player1.name = p1
            if p2 is not None:
                self.player2.name = p2
        else:
            # Single; always set the player
            if self.opponent.player_id == 2:
                self.player1.name = p1
            else:
                self.player2.name = p1

    def load_font(self):
        # Steal matplotlib's default sans font
        font_file = font_manager.findfont("monospace")
        try:
            font = ImageFont.truetype(font_file, size=10)
        except OSError:
            font = ImageFont.load_default()
        return font

    def _step_forward(self, actions):
        self._step_actions(actions)
        self._step_collisions()
        player1_reward, player2_reward, done = self._step_check_victory()
        return player1_reward, player2_reward, done

    def _step_actions(self, actions):
        # Get the opponent's action, if we're in single mode
        if self.opponent is not None:
            op_action = self.opponent.get_action()
            if self.opponent.player_id == 1:
                actions = (op_action, actions)
            elif self.opponent.player_id == 2:
                actions = (actions, op_action)

        # Handle Player1's action
        if actions[0] == self.MOVE_UP:
            self.player1.move_up()
        elif actions[0] == self.MOVE_DOWN:
            self.player1.move_down()

        # Handle Player2s action
        if actions[1] == self.MOVE_UP:
            self.player2.move_up()
        elif actions[1] == self.MOVE_DOWN:
            self.player2.move_down()

    def _step_collisions(self):
        # Check if the ball collided with one of the players
        p1_collide = self.player1.rect.collide_rect(self.ball.rect)
        p2_collide = self.player2.rect.collide_rect(self.ball.rect)

        # Reflect the ball based on the collision and who touched the ball last
        # to prevent multiple collisions with one player
        if p1_collide and self.ball.last_touch is not 1:
            self._reflect(self.player1)
        if p2_collide and self.ball.last_touch is not 2:
            self._reflect(self.player2)

    def _step_check_victory(self):
        # Move ball and check if game is over
        winner, done = self.ball.move()

        # Compute rewards if the episode is over
        player1_reward = 0
        player2_reward = 0
        if done:
            if winner == 1:
                player1_reward = 10
                player2_reward = -10
                self.player1.score += 1
            if winner == 2:
                player1_reward = -10
                player2_reward = 10
                self.player2.score += 1
        return player1_reward, player2_reward, done

    def _step_render_frame(self):
        self._reset_screen()
        self._render_ball()
        self._render_player1()
        self._render_player2()

    def _step_get_state(self, player1_reward, player2_reward):
        observation_left = self._get_observation(1)
        observation_right = self._get_observation(2)
        if self.opponent:
            # Return only one players info in singleplayer mode, depending
            # on which side the player is playing
            if self.opponent.player_id == 1:
                # Return only player 2 info
                return observation_right, player2_reward
            elif self.opponent.player_id == 2:
                # Return only player 1 info
                return observation_left, player1_reward
            else:
                raise ValueError("Invalid opponent ID: %s" \
                                 % str(self.opponent.player_id))
        else:
            # Multiplayer mode, return both
            return (observation_left, observation_right), \
                   (player1_reward, player2_reward)

    def step(self, actions):
        """
        This function is a modification of the Openai gym step function for
        two players.

        ARGUMENTS:
        tuple, action: The actions that both agents took (multiplayer mode)
        or
        int, action: The action that the player agent took (singleplayer mode)

        RETURN:
        - observation: return the current state of the game area either as tuple
        (multiplayer mode) or as int (singleplayer mode)
        - reward: the reward as tuple (multiplayer mode) or as int (singleplayer mode)
        - done: True if the episode is over
        - info: debug output
        """
        if isinstance(self.frameskip, int):
            num_steps = self.frameskip
        else:
            num_steps = np.random.randint(self.frameskip[0], self.frameskip[1])

        for _ in range(num_steps):
            p1_reward, p2_reward, done = self._step_forward(actions)
            if done:
                break

        self._step_render_frame()
        ob, reward = self._step_get_state(p1_reward, p2_reward)
        info = {}
        return ob, reward, done, info

    def reset(self):
        """
        Public environment interface function that resets the environment
        """
        # Paint over the old frame
        self._reset_screen()
        self.ball.reset_ball()
        self.player1.reset()
        self.player2.reset()

        # Draw the changes so they are in the frame
        self._render_player1()
        self._render_player2()
        self._render_ball()

        # Get the observation based on the enemy type
        if self.opponent is None:
            # Multiplayer mode returns two observations for player 1 and 2
            return self._get_observation(1), self._get_observation(2)
        else:
            # Singleplayer mode only returns the observation depending on which
            # side the agent is playing. The other player is not getting an
            # observation
            return self._get_observation(3-self.opponent.player_id)

    def _reset_screen(self):
        """
        Reset the screen by setting all pixels to the background color
        """
        self.screen = self.background.copy()

    def _reflect(self, player):
        """
        This function computes in which direction the ball has to reflected and
        updates the last_touch variable
        """
        offcenter = abs(player.y - self.ball.y)
        if player.y > self.ball.y:
            if player.player_number == 1:
                direction = 1
            else:
                direction = -1
        else:
            if player.player_number == 1:
                direction = -1
            else:
                direction = 1
        self.ball.reflect(offcenter, direction, player)
        self.ball.last_touch = player.player_number  # Which player touched the ball last

    def _render_ball(self):
        self.ball.rect.draw_on(self.screen)

    def _render_player1(self):
        self.player1.rect.draw_on(self.screen)

    def _render_player2(self):
        self.player2.rect.draw_on(self.screen)

    def _draw_scores(self):
        # Draw the scoreboard
        scoreboard_background = Rect(0, 0, self.GAME_AREA_RESOLUTION[0],
                                     self.SCOREBOARD_HEIGHT, color=(75, 83, 88))
        scoreboard_border = Rect(self.SCOREBOARD_BORDER, self.SCOREBOARD_BORDER,
                                 self.GAME_AREA_RESOLUTION[0]-2*self.SCOREBOARD_BORDER,
                                 self.SCOREBOARD_HEIGHT - 2*self.SCOREBOARD_BORDER,
                                 color=(216, 219, 226))
        scoreboard_separator = Rect(self.GAME_AREA_RESOLUTION[0]/2
                                    - self.SEPARATOR_BORDER, 0,
                                    2*self.SEPARATOR_BORDER, self.SCOREBOARD_HEIGHT,
                                    color=(75, 83, 88))
        scoreboard_background.draw_on(self.screen)
        scoreboard_border.draw_on(self.screen)
        scoreboard_separator.draw_on(self.screen)

        # Text
        text1 = "%s\n%d" % (self.player1.name[:16], self.player1.score)
        text2 = "%s\n%d" % (self.player2.name[:16], self.player2.score)
        canvas = Image.fromarray(self.screen)
        draw = ImageDraw.Draw(canvas)
        offset1 = 5, 5
        offset2 = 5+self.SCREEN_RESOLUTION[1]/2, 5
        text_color = "#000000"
        draw.fontmode = "1"  # Turn off antialias
        draw.text(offset1, text1, font=self.scoreboard_font, fill=text_color)
        draw.text(offset2, text2, font=self.scoreboard_font, fill=text_color)
        self.screen = np.asarray(canvas)

    def switch_sides(self):
        """
        Public environment interface, this function switches the sides so
        that player 1 becomes player 2 and vice versa
        """
        op1_name = self.player1.name
        op1_score = self.player1.score
        self.player1.name = self.player2.name
        self.player1.score = self.player2.score
        self.player2.name = op1_name
        self.player2.score = op1_score

        if self.opponent:
            # Swap opponent's player_id
            self.opponent.player_id = 3 - self.opponent.player_id

    def _get_observation(self, player):
        """
        This function computes the observation depending on the player.
        Player 1 gets the normal observation and player 2 the inverted
        observation so that playing on both sides looks the same
        """
        def normalize_y(val):
            # First, clamp it to screen bounds
            y_min = self.SCREEN_RESOLUTION[0] - self.GAME_AREA_RESOLUTION[1]
            y_max = self.SCREEN_RESOLUTION[0]
            val = np.clip(val, y_min, y_max)
            # Then, normalize to -1:1 range
            val = (val-y_min) / (y_max-y_min) * 2 - 1
            return val

        def normalize_x(val):
            # First, clamp it to screen bounds
            val = np.clip(val, 0, self.GAME_AREA_RESOLUTION[0])
            # Then, normalize to -1:1 range
            val = val / self.GAME_AREA_RESOLUTION[0] * 2 - 1
            return val

        if self.visual:
            # Crop the image
            observation = self.screen[self.SCOREBOARD_HEIGHT:,:].copy()
            # Player 2 gets a frame with inverted player colors and inverted positions
            # so that both sides look the same to the agent while training
            if player == 2:
                observation = np.flip(observation, 1)
                # Invert colors
                p1c = np.array(self.player1.color)
                p2c = np.array(self.player2.color)
                p1_pixels = np.where((observation == p1c).all(axis=-1))
                p2_pixels = np.where((observation == p2c).all(axis=-1))
                observation[p1_pixels] = p2c
                observation[p2_pixels] = p1c
        else:
            # In non visual mode return the positions of all game objects
            if player == 1:
                player_pos = normalize_y(self.player1.y)
                opponent_pos = normalize_y(self.player2.y)
                ball_x = normalize_x(self.ball.x)
                ball_px = normalize_x(self.ball.previous_x)
            else:
                player_pos = normalize_y(self.player2.y)
                opponent_pos = normalize_y(self.player1.y)
                ball_x = normalize_x(self.GAME_AREA_RESOLUTION[0]-self.ball.x)
                ball_px = normalize_x(self.GAME_AREA_RESOLUTION[0] \
                        - self.ball.previous_x)
            ball_y = normalize_y(self.ball.y)
            ball_py = normalize_y(self.ball.previous_y)
            observation = np.array([player_pos, opponent_pos, ball_x, ball_y,
                                    ball_px, ball_py], dtype=np.float)
        return observation

    def render(self):
        """
        Public environment interface: This function renders the current frame
        to the screen. For example while training the game can be run in headless
        mode by not calling this function.
        """

        # Draw scores only when rendering (this part is removed from
        # the observations anyway)
        self._draw_scores()

        # Display the frame
        frame = cv2.cvtColor(np.uint8(self.screen), cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.SCREEN_RESOLUTION[1]*self.scale,
                            self.SCREEN_RESOLUTION[0]*self.scale),
                            interpolation=cv2.INTER_NEAREST)
        cv2.imshow('Wimblepong', frame)
        cv2.waitKey(max(1000//self.fps, 1))

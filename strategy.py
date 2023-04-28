import action, penalty_handler
# import tensorflow as tf
import pandas as pd
import numpy as np
from simClasses import *
from numpy import *
import csv


class Strategy:
    """Input: Friendly robots, enemy robots, ball, side of field, strategy object.
    Description: This class contains all functions and objects related to selecting a game strategy.
    Output: None"""

    def __init__(self, robots: list, enemy_robots, ball, mray, strategies):

        self.robots = robots
        self.enemy_robots = enemy_robots
        self.ball = ball
        self.mray = mray
        self.score = [0, 0]  # Current score, [our score, enemy score]
        self.penalty_state = 0  # 0 = no penalty, 1 = offensive penalty, 2 = defensive penalty
        self.strategy = strategies[0]
        self.penaltyStrategies = strategies[1:3]
        self.aop = strategies[3]
        self.adp = strategies[4]
        self.leader = None
        self.follower = None
        self.leader_time = 0
        self.penalty_handler = penalty_handler.PenaltyHandler(self, self.robots, self.enemy_robots, self.ball,
                                                              self.mray)
        self.goal_already_happened = False

    def handle_game_on(self):
        if self.goal_already_happened:
            self.goal_already_happened = False
        self.decider()

    def handle_goal(self, foul_was_yellow):
        if self.goal_already_happened:
            return
        self.goal_already_happened = True
        match self.mray:
            case True if foul_was_yellow:
                self.score[1] += 1
                print("gol inimigo")
            case True if not foul_was_yellow:
                self.score[0] += 1
                print("Gol nosso")
            case False if foul_was_yellow:
                self.score[0] += 1
                print("Gol nosso")
            case False if not foul_was_yellow:
                self.score[1] += 1
                print("gol inimigo")
        print(self.score)

    def get_score(self):
        return self.score.copy()

    def end_penalty_state(self):
        self.penalty_state = 0

    def set_leader(self, leader):
        """Input: None
        Description: Sets the leader robot.
        Output: None."""
        self.leader = leader

    def set_follower(self, follower):
        """Input: None
        Description: Sets the follower robot.
        Output: None."""
        self.follower = follower

    def get_leader(self):
        """Input: None
        Description: Returns the leader robot.
        Output: Leader robot."""
        return self.leader

    def get_follower(self):
        """Input: None
        Description: Returns the follower robot.
        Output: Follower robot."""
        return self.follower

    def set_leader_time(self, time):
        """Input: Time
        Description: Sets the time of the leader.
        Output: None."""
        self.leader_time = time

    def get_leader_time(self):
        """Input: None
        Description: Returns the time of the leader.
        Output: Time."""
        return self.leader_time

    def decider(self):
        """Input: None
        Description: Calls the function that initiates the selected strategy.
        Output: Prints a warning in case of error."""
        if self.penalty_state:
            self.penalty_handler.handle_penalty(self.penalty_state, self.score.copy())
            return
        match self.strategy:
            case 'default':
                self.coach()
            case 'twoAttackers':
                self.coach2()
            case _:
                print("Strategy not found")

    def coach2(self):
        """Input: None
        Description: Advanced strategy, one goalkeeper defends while two robots chase the ball, with one leading and the other in support.
        Output: None."""
        ball_coordinates = self.ball.get_coordinates()
        if self.mray:
            if ball_coordinates.X > 85:
                self.stg_def_v2()
            else:
                self.stg_att_v2()
        else:
            if ball_coordinates.X > 85:
                self.stg_att_v2()
            else:
                self.stg_def_v2()

    def coach(self):
        """Input: None
        Description: The standard strategy, one robot as attacker, another as defender and another as goalkeeper.
        Output: None."""
        ball_coordinates = self.ball.get_coordinates()
        if self.mray:
            if ball_coordinates.X > 85:
                self.basic_stg_def_2()
            else:
                self.basic_stg_att()
        else:
            if ball_coordinates.X > 85:
                self.basic_stg_att()
            else:
                self.basic_stg_def_2()

    def basic_stg_def(self):
        """Input: None
        Description: Basic defence strategy, goalkeeper blocks goal and advance in ball, defender chases ball,
                    attacker holds in midfield.
        Output: None."""
        ball_coordinates = self.ball.get_coordinates()
        if not self.mray:
            if ball_coordinates.X < 30 and 30 < ball_coordinates.Y < 110:  # If the ball has inside of defense area
                action.defender_penalty(self.robots[0], self.ball, left_side=not self.mray)  # Goalkeeper move ball away
                action.screen_out_ball(self.robots[1], self.ball, 55, left_side=not self.mray)
            else:
                action.shoot(self.robots[1], self.ball, left_side=not self.mray)  # Defender chases ball
                action.screen_out_ball(self.robots[0], self.ball, 14, left_side=not self.mray, upper_lim=81,
                                       lower_lim=42)  # Goalkeeper keeps in goal
        else:  # The same idea for other team
            if ball_coordinates.X > 130 and 30 < ball_coordinates.Y < 110:
                action.defender_penalty(self.robots[0], self.ball, left_side=not self.mray)
                action.screen_out_ball(self.robots[1], self.ball, 55, left_side=not self.mray)
            else:
                action.shoot(self.robots[1], self.ball, left_side=not self.mray)
                action.screen_out_ball(self.robots[0], self.ball, 14, left_side=not self.mray, upper_lim=81,
                                       lower_lim=42)

        action.screen_out_ball(self.robots[2], self.ball, 110, left_side=not self.mray, upper_lim=120,
                               lower_lim=10)  # Attacker stays in midfield

    def basic_stg_att(self):
        """Input: None
        Description: Basic attack strategy, goalkeeper blocks goal, defender screens midfield, attacker chases ball.
        Output: None."""
        action.defender_spin(self.robots[2], self.ball, left_side=not self.mray)  # Attacker behavior
        action.screen_out_ball(self.robots[1], self.ball, 60, left_side=not self.mray, upper_lim=120,
                               lower_lim=10)  # Defender behavior
        action.screen_out_ball(self.robots[0], self.ball, 14, left_side=not self.mray, upper_lim=81,
                               lower_lim=42)  # Goalkeeper behavior

    def basic_stg_def_2(self):
        """Input: None
        Description: Basic defense strategy with robot stop detection
        Output: None."""
        if not self.mray:
            if self.ball._coordinates.X < 40 and 30 < self.ball._coordinates.Y < 110:  # If the ball has inside of defense area
                action.defender_penalty_spin(self.robots[0], self.ball,
                                             left_side=not self.mray)  # Goalkeeper move ball away
                action.screen_out_ball(self.robots[1], self.ball, 55, left_side=not self.mray)
            else:
                action.defender_spin(self.robots[1], self.ball, left_side=not self.mray)  # Defender chases ball
                action.screen_out_ball(self.robots[0], self.ball, 14, left_side=not self.mray, upper_lim=81,
                                       lower_lim=42)  # Goalkeeper keeps in goal
        else:  # The same idea for other team
            if self.ball._coordinates.X > 130 and 30 < self.ball._coordinates.Y < 110:
                action.defender_penalty_spin(self.robots[0], self.ball, left_side=not self.mray)
                action.screen_out_ball(self.robots[1], self.ball, 55, left_side=not self.mray)
            else:
                action.defender_spin(self.robots[1], self.ball, left_side=not self.mray)
                action.screen_out_ball(self.robots[0], self.ball, 14, left_side=not self.mray, upper_lim=81,
                                       lower_lim=42)

        action.screen_out_ball(self.robots[2], self.ball, 110, left_side=not self.mray, upper_lim=120,
                               lower_lim=10)  # Attacker stays in midfield

        # Verification if robot has stopped
        if ((abs(self.robots[0]._coordinates.rotation) < deg2rad(10)) or (
                abs(self.robots[0]._coordinates.rotation) > deg2rad(170))) and (
                self.robots[0]._coordinates.X < 20 or self.robots[0]._coordinates.X > 150):
            self.robots[0].contStopped += 1
        else:
            self.robots[0].contStopped = 0

    def stg_def_v2(self):
        """Input: None
        Description: Defence part of followleader method, a robot leads chasing ball, other supports, goalie blocks
             goal and move ball away when close to the goal
        Output: None."""
        if not self.mray:
            if self.ball._coordinates.X < 40 and 30 < self.ball._coordinates.Y < 110:  # If the ball has inside of defense area
                action.defender_penalty(self.robots[0], self.ball,
                                             left_side=not self.mray)  # Goalkeeper move ball away
                self.two_attackers()
            else:
                self.two_attackers()
                action.screen_out_ball(self.robots[0], self.ball, 16, left_side=not self.mray, upper_lim=84,
                                       lower_lim=42)  # Goalkeeper stays on the goal
        else:  # The same ideia, but for other team
            if self.ball._coordinates.X > 130 and 30 < self.ball._coordinates.Y < 110:
                action.defender_penalty(self.robots[0], self.ball, left_side=not self.mray)
                self.two_attackers()
            else:
                self.two_attackers()
                action.screen_out_ball(self.robots[0], self.ball, 16, left_side=not self.mray, upper_lim=84,
                                       lower_lim=42)

        # Verification if robot has stopped
        if ((abs(self.robots[0]._coordinates.rotation) < deg2rad(10)) or (
                abs(self.robots[0]._coordinates.rotation) > deg2rad(170))) and (
                self.robots[0]._coordinates.X < 20 or self.robots[0]._coordinates.X > 150):
            self.robots[0].contStopped += 1
        else:
            self.robots[0].contStopped = 0

    def stg_att_v2(self):
        """Input: None
        Description: Offence part of followleader method, one robot leads chasing ball, another supports, goalkeeper blocks goal.
        Output: None."""
        self.two_attackers()
        action.screen_out_ball(self.robots[0], self.ball, 16, left_side=not self.mray, upper_lim=84, lower_lim=42)
        self.robots[0].contStopped = 0

    def penalty_mode_offensive_spin(self):
        """Input: None
        Description: Penalty kick offence strategy with spin.
        Output: None."""
        ball_coordinates = self.ball.get_coordinates()
        robot_coordinates = self.robots[2].get_coordinates()
        action.screen_out_ball(self.robots[0], self.ball, 10, left_side=not self.mray)  # Goalkeeper keeps in defense
        action.shoot(self.robots[1], self.ball, left_side=not self.mray)  # Defender going to the rebound

        if not self.robots[2].dist(self.ball) < 9:  # If the attacker is not closer to the ball
            action.girar(self.robots[2], 100, 100)  # Moving forward
        else:
            if self.robots[2].teamYellow:  # Team verification
                if self.robots[2].yPos < 65:
                    action.girar(self.robots[2], 0, 100)  # Shoots the ball spinning up
                else:
                    action.girar(self.robots[2], 100, 0)  # Shoots the ball spinning down
            else:
                if self.robots[2].yPos > 65:
                    action.girar(self.robots[2], 0, 100)  # Shoots the ball spinning down
                else:
                    action.girar(self.robots[2], 100, 0)  # Shoots the ball spinning up

        # If the ball gets away from the robot, stop the penalty mode
        if sqrt((ball_coordinates.X - robot_coordinates.X) ** 2 + (ball_coordinates.Y - robot_coordinates.X) ** 2) > 30:
            self.penaltyOffensive = False

    def penalty_mode_offensive_mirror(self):
        ball_coordinates = self.ball.get_coordinates()
        robot_coordinates = self.robots[2].get_coordinates()
        action.screen_out_ball(self.robots[0], self.ball, 10, left_side=not self.mray)  # Goalkeeper keeps in defense
        action.shoot(self.robots[1], self.ball, left_side=not self.mray)  # Defender going to the rebound
        if self.robots[2].teamYellow:
            action.girar(self.robots[2], 30, 40)
        else:
            action.girar(self.robots[2], 40, 30)
        if sqrt((ball_coordinates.X - robot_coordinates.X) ** 2 + (
                ball_coordinates.Y - robot_coordinates.Y) ** 2) > 20:
            self.penaltyOffensive = False

    def two_attackers(self):
        """Input: None
        Description: Calls leader and follower technique for use in strategies.
        Output: None."""
        action.follow_leader(self.robots[1], self.robots[2], self.ball, self)
        
    def returnAllDataForCsv(self):
        ally_data = ''
        velocities_data = ''
        for robot in self.robots:
            robot_data = robot.getRobotData()
            velocities_data += f'{robot.getVelocitiesThatWillBeSent()},'
            ally_data += f'{robot_data},'
        
        enemy_data = ''
        for robot in self.enemy_robots:
            robot_data = robot.getRobotData()
            enemy_data += f'{robot_data},'
        
        ball_data = self.ball.getBallData() 
        
        score_data = f'{self.score[0]},{self.score[1]}'        
        
        data = f'{ally_data}{enemy_data}{ball_data},{score_data},{velocities_data}'
        return data   
    
    def returnDataForNeuralNetwork(self):
        ally_data = ''
        for robot in self.robots:
            robot_data = robot.getRobotData()
            ally_data += f'{robot_data},'
        
        enemy_data = ''
        for robot in self.enemy_robots:
            robot_data = robot.getRobotData()
            enemy_data += f'{robot_data},'
        
        ball_data = self.ball.getBallData() 
        
        score_data = f'{self.score[0]},{self.score[1]}'        
        
        data = f'{ally_data}{enemy_data}{ball_data},{score_data}'
        return data  
    
    def neural_network(self):
        """Input: None
        Description: Calls neural network to make decisions.
        Output: None."""
        mean = [-0.06179888143484225, 0.010136696574631666, -0.38579192471469614, -0.06179888143484225, -0.7734128679541099, 0.08097272993549304, 0.10488879249803876, 0.08432841360798499, -0.019608863157247126, 0.10488879249803876, 0.08432841360798499, -0.400691810605911, -0.08364225647069548, 0.03906808052628489, 0.028866983829118065, 0.04284307076337425, 0.03906808052628489, 0.028866983829118065, -0.4324330949072138, -0.005842057745828229, 0.3468274293832633, 0.08537592330309501, -0.015314957918580395, 0.3468274293832633, 0.08537592330309501, -0.7467306524105318, -0.12576130149477707, 0.13117405210401545, 0.1206273634033153, 0.017555109613756125, 0.13117405210401545, 0.1206273634033153, -0.44240286100173415, 0.3537615438081982, 0.06782295222068602, -0.0562414412565873, 0.009190221099779333, 0.06782295222068602, -0.0562414412565873, -0.5333604719006125, 0.22272802053787122, -0.04781915880389854, 0.08103704179789832, -1.0, -0.05133544059177591, -1.0, 0.24214718192530837]

        std = [0.4768021365114932, 0.5325654916660223, 0.19784516259240584, 0.4768021365114932, 0.35889949790584996, 0.10899934685802952, 0.47331552078599304, 0.5051253812209835, 0.5794504752745142, 0.47331552078599304, 0.5051253812209835, 0.5906683211148047, 0.0879073721227085, 0.5031942049676215, 0.5914915214784588, 0.5573888768297759, 0.5031942049676215, 0.5914915214784588, 0.5707736983501842, 0.10435874625692325, 0.24163188695315063, 0.5701776657364512, 0.47249530269077306, 0.24163188695315063, 0.5701776657364512, 0.38795331240978764, 0.16151255926924504, 0.5083544190083, 0.5603343281376371, 0.5295330218652837, 0.5083544190083, 0.5603343281376371, 0.5721515976818207, 0.1176132692845904, 0.48458427786604646, 0.47052321660723134, 0.5528803170200497, 0.48458427786604646, 0.47052321660723134, 0.5096011077802807, 0.09714842460990042, 0.24312973058723855, 0.6300289325407343, 0.0, 0.1953569857360199, 0.0, 0.8819987123267231]

        
        # normalize data to mean and std above, then predict velocities
        model = tf.keras.models.load_model('model.h5')
        # X_test = np.array([self.returnDataForNeuralNetwork().split(',')])
        # X_test = (X_test - mean) / std
        
        # velocities = model.predict(X_test)
        # print(velocities)
        # for i in range(3):
        #     self.robots[i].sim_set_vel2(self.robots[i].index, velocities[i], velocities[i+1])

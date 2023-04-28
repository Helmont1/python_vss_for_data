import time
import argparse

import fouls
from bridge import (Actuator, Replacer, Vision, Referee)
from simClasses import *
from strategy import *
from csv import writer

class CsvWriter:
    '''Classe para escrever dados em um arquivo CSV'''
    def __init__(self, filename):
        self.file = open(filename, 'a', newline='')
        self.csv_writer = writer(self.file)
        # self.csv_writer.writerow(['robot1_pos_x', 'robot1_pos_y', 'robot1_rotation', 'robot1_vel_x', 'robot1_vel_y', 'robot1_vel_angular', 'robot1_vel_linear', 'robot2_pos_x', 'robot2_pos_y', 'robot2_rotation', 'robot2_vel_x', 'robot2_vel_y', 'robot2_vel_angular', 'robot2_vel_linear', 'robot3_pos_x', 'robot3_pos_y', 'robot3_rotation', 'robot3_vel_x', 'robot3_vel_y', 'robot3_vel_angular', 'robot3_vel_linear', 'enemy1_pos_x', 'enemy1_pos_y', 'enemy1_rotation', 'enemy1_vel_x', 'enemy1_vel_y', 'enemy1_vel_angular', 'enemy1_vel_linear', 'enemy2_pos_x', 'enemy2_pos_y', 'enemy2_rotation', 'enemy2_vel_x', 'enemy2_vel_y', 'enemy2_vel_angular', 'enemy2_vel_linear', 'enemy3_pos_x', 'enemy3_pos_y', 'enemy3_rotation', 'enemy3_vel_x', 'enemy3_vel_y', 'enemy3_vel_angular', 'enemy3_vel_linear', 'ball_pos_x', 'ball_pos_y', 'ball_rotation', 'ball_vel_x', 'ball_vel_y', 'ball_vel_angular', 'ball_vel_linear', 'team1_score', 'team2_score', 'velocity1_x', 'velocity1_y', 'velocity2_x', 'velocity2_y', 'velocity3_x', 'velocity3_y'])
        
    def write_data(self, data):
        self.csv_writer.writerow(data)

    def close(self):
        self.file.close()
csv_writer = CsvWriter('data.csv')

if __name__ == "__main__":

    # Fazer tratamento de entradas erradas

    parser = argparse.ArgumentParser(description='Argumentos para execução do time no simulador FIRASim')

    parser.add_argument('-t', '--team', type=str, default="blue",
                        help="Define o time/lado que será executado: blue ou yellow")
    parser.add_argument('-s', '--strategy', type=str, default="twoAttackers",
                        help="Define a estratégia que será jogada: twoAttackers ou default" )
    parser.add_argument('-nr', '--num_robots', type=int, default=3,
                        help="Define a quantia de robos de cada lado")
    parser.add_argument('-op', '--offensivePenalty', type=str, default='spin', dest='op',
                        help="Define o tipo de cobrança ofensiva de penalti: spin ou direct")
    parser.add_argument('-dp', '--defensivePenalty', type=str, default='direct', dest='dp',
                        help="Define o tipo de defesa de penalti: spin ou direct")
    parser.add_argument('-aop', '--adaptativeOffensivePenalty', type=str, default='off', dest='aop', 
                        help="Controla a troca de estratégias de penalti durante o jogo")
    parser.add_argument('-adp', '--adaptativeDeffensivePenalty', type=str, default='off', dest='adp', 
                        help="Controla a troca de estratégias de penalti durante o jogo")


    args = parser.parse_args()

    # Choose team (my robots are yellow)
    if args.team == "yellow":
        mray = True
    else:
        mray = False


    # Initialize all clients
    actuator = Actuator(mray, "127.0.0.1", 20011)
    replacement = Replacer(mray, "224.5.23.2", 10004)
    vision = Vision(mray, "224.0.0.1", 10002)
    referee = Referee(mray, "224.5.23.2", 10003)

    # Initialize all  objects
    robots = []
    for i in range(args.num_robots):
        robot = Robot(i, actuator, mray)
        robots.append(robot)

    enemy_robots = []
    for i in range(args.num_robots):
        robot = Robot(i, actuator, not mray)
        enemy_robots.append(robot)

    for robot in robots:
        robot.set_enemies(enemy_robots)
        robot.set_friends(robots.copy())

    ball = Ball()

    list_strategies = [args.strategy, args.op, args.dp, args.aop, args.adp]
    strategy = Strategy(robots, enemy_robots, ball, mray, list_strategies)
    
    # csv_writer.write_data('Robô Aliado 1 Pos X,Robô Aliado 1 Pos Y,Robô Aliado 1 Rot,Robô Aliado 1 Vel X,Robô Aliado 1 Vel Y,Robô Aliado 1 Vel Angular,Robô Aliado 1 Vel Linear,Robô Aliado 2 Pos X,Robô Aliado 2 Pos Y,Robô Aliado 2 Rot,Robô Aliado 2 Vel X,Robô Aliado 2 Vel Y,Robô Aliado 2 Vel Angular,Robô Aliado 2 Vel Linear,Robô Aliado 3 Pos X,Robô Aliado 3 Pos Y,Robô Aliado 3 Rot,Robô Aliado 3 Vel X,Robô Aliado 3 Vel Y,Robô Aliado 3 Vel Angular,Robô Aliado 3 Vel Linear,Robô Inimigo 1 Pos X,Robô Inimigo 1 Pos Y,Robô Inimigo 1 Rot,Robô Inimigo 1 Vel X,Robô Inimigo 1 Vel Y,Robô Inimigo 1 Vel Angular,Robô Inimigo 1 Vel Linear,Robô Inimigo 2 Pos X,Robô Inimigo 2 Pos Y,Robô Inimigo 2 Rot,Robô Inimigo 2 Vel X,Robô Inimigo 2 Vel Y,Robô Inimigo 2 Vel Angular,Robô Inimigo 2 Vel Linear,Robô Inimigo 3 Pos X,Robô Inimigo 3 Pos Y,Robô Inimigo 3 Rot,Robô Inimigo 3 Vel X,Robô Inimigo 3 Vel Y,Robô Inimigo 3 Vel Angular,Robô Inimigo 3 Vel Linear,Bola Pos X,Bola Pos Y,Bola Rot,Bola Vel X,Bola Vel Y,Bola Vel Angular,Bola Vel Linear,Pontuação Amarelo,Pontuação Azul,Velocidade Enviada 1 X,Velocidade Enviada 1 Y,Velocidade Enviada 2 X,Velocidade Enviada 2 Y,Velocidade Enviada 3 X,Velocidade Enviada 3 Y')

    # Main infinite loop
    try:
        while True:
            t1 = time.time()
            # Update the foul status
            referee.update()
            ref_data = referee.get_data()

            # Update the vision data
            vision.update()
            field = vision.get_field_data()

            data_our_bot = field["our_bots"]  # Save data from allied robots
            data_their_bots = field["their_bots"]  # Save data from enemy robots
            data_ball = field["ball"]  # Save the ball data

            # Updates vision data on each field object
            for index, robot in enumerate(robots):
                robot.set_simulator_data(data_our_bot[index])
                
            for index, robot in enumerate(enemy_robots):
                robot.set_simulator_data(data_their_bots[index])

            ball.set_simulator_data(data_ball)


            if ref_data["game_on"]:
                # If the game mode is set to "Game on"
                # strategy.neural_network()
                strategy.handle_game_on()
                csv_writer.file.write(strategy.returnAllDataForCsv() + '\n')

            else:
                """FREE_KICK = 0
                PENALTY_KICK = 1
                GOAL_KICK = 2
                FREE_BALL = 3
                KICKOFF = 4
                STOP = 5
                GAME_ON = 6
                HALT = 7"""
                match ref_data["foul"]:

                    case 1 if ref_data["yellow"] != mray:
                        # detecting defensive penalty
                        strategy.penalty_state = 2
                        actuator.stop()
                        fouls.replacement_fouls(replacement, ref_data, mray, strategy.penalty_handler.offensive_penalty_tactics[strategy.penalty_handler.current_offensive_tactic], strategy.penalty_handler.defensive_penalty_tactics[strategy.penalty_handler.current_defensive_tactic])
                    case 1 if ref_data["yellow"] == mray:
                        # detecting offensive penalty
                        strategy.penalty_state = 1
                        actuator.stop()
                        fouls.replacement_fouls(replacement, ref_data, mray, strategy.penalty_handler.offensive_penalty_tactics[strategy.penalty_handler.current_offensive_tactic], strategy.penalty_handler.defensive_penalty_tactics[strategy.penalty_handler.current_defensive_tactic])
                    case 5:
                        fouls.replacement_fouls(replacement, ref_data, mray, args.op, args.dp)
                        actuator.stop()
                    case 4:
                        strategy.handle_goal(ref_data["yellow"])
                        fouls.replacement_fouls(replacement, ref_data, mray, args.op, args.dp)
                        actuator.stop()
                    case 0 | 2 | 3:
                        strategy.end_penalty_state()
                        fouls.replacement_fouls(replacement, ref_data, mray, args.op, args.dp)
                        actuator.stop()

                    case _:
                        actuator.stop()
                        
            # synchronize code execution based on runtime and the camera FPS
            t2 = time.time()
            if t2 - t1 < 1 / 60:
                time.sleep(1 / 60 - (t2 - t1))
    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt detected. Saving CSV...")
        csv_writer.close()

import argparse
import math
import random
import time

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

esp32IP = "192.168.XX.XX" # デバイスのIPアドレス
targetPort = XXXX #接続するポート番号

# 0:Tail, 1:Ear
deviceMode = 0

# [Tail1, Tail2, Tail3, Tail4, Tail5, TailIsGrabbed]
tail_motor_param = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
# [L_Contact, L_IsGrabbed, R_Contact, R_IsGrabbed]
ear_motor_parm = [0, 0, 0, 0]

# TailProcess
def TailSend2Arduino():
  sendParam = max(tail_motor_param)
  if sendParam < 0.11:
    sendParam = 0.0
  elif sendParam > 1.0:
    sendParam = 1.0
  
  print("sendParm : " + str(sendParam))
  client.send_message("/motor1", sendParam)

def ProcessTailIsGrabed(unused_addr, args, *values):
  if args == 1.0:
    tail_motor_param[5] = 1.0
  else:
    tail_motor_param[5] = 0.0
  
  print("isGrabbed : " + str(args))
  TailSend2Arduino()

def ProcessTailContact_1(unused_addr, args, *values):
  tail_motor_param[0] = args

  print("tailContact1 : " + str(args))
  TailSend2Arduino()

def ProcessTailContact_2(unused_addr, args, *values):
  tail_motor_param[1] = args

  print("tailContact2 : " + str(args))
  TailSend2Arduino()

def ProcessTailContact_3(unused_addr, args, *values):
  tail_motor_param[2] = args

  print("tailContact3 : " + str(args))
  TailSend2Arduino()

def ProcessTailContact_4(unused_addr, args, *values):
  tail_motor_param[3] = args

  print("tailContact4 : " + str(args))
  TailSend2Arduino()

def ProcessTailContact_5(unused_addr, args, *values):
  tail_motor_param[4] = args

  print("tailContact5 : " + str(args))
  TailSend2Arduino()

# EarProcess
def EarSend2Arduino(num):
  sendParam = 0.0

  if ear_motor_parm[1 + num * 2] == 1:
    sendParam = 0.26
  elif ear_motor_parm[num * 2] == 1:
    sendParam = 0.22
  
  print("sendParm : " + str(sendParam))
  print(ear_motor_parm)
  if num == 0:
    client.send_message("/motor1", sendParam)
  elif num == 1:
    client.send_message("/motor2", sendParam)

def ProcessEarLIsGrabed(unused_addr, args, *values):
  if args == 1.0:
    ear_motor_parm[1] = 1
  else:
    ear_motor_parm[1] = 0
  
  EarSend2Arduino(0)

def ProcessEarRIsGrabed(unused_addr, args, *values):
  if args == 1.0:
    ear_motor_parm[3] = 1
  else:
    ear_motor_parm[3] = 0
  
  EarSend2Arduino(1)

def ProcessEarLContact(unused_addr, args, *values):
  if args == 1.0:
    ear_motor_parm[0] = 1
  else:
    ear_motor_parm[0] = 0
  
  EarSend2Arduino(0)

def ProcessEarRContact(unused_addr, args, *values):
  if args == 1.0:
    ear_motor_parm[2] = 1
  else:
    ear_motor_parm[2] = 0
  
  EarSend2Arduino(1)

if __name__ == "__main__":
  #ESP32へ送信
  toM5stack = argparse.ArgumentParser()
  toM5stack.add_argument("--ip", default=esp32IP,
    help="The ip of the OSC server")
  toM5stack.add_argument("--port", type=int, default=targetPort,
    help="The port the OSC server is listening on")
  argsM5 = toM5stack.parse_args()

  client = udp_client.SimpleUDPClient(argsM5.ip, argsM5.port)
  
  #VRCからの受信
  fromVRC = argparse.ArgumentParser()
  fromVRC.add_argument("--ip",
                      default="127.0.0.1", help="The ip to listen on")
  fromVRC.add_argument("--port",
                      type=int, default=9001, help="The port to listen on")
  argsVRC = fromVRC.parse_args()

  #特定のパラメータを受信したら関数に飛ぶ
  dispatcher = dispatcher.Dispatcher()
  if deviceMode == 0:
    dispatcher.map("/avatar/parameters/Tail_IsGrabbed", ProcessTailIsGrabed)
    dispatcher.map("/avatar/parameters/TailContact_1", ProcessTailContact_1)
    dispatcher.map("/avatar/parameters/TailContact_2", ProcessTailContact_2)
    dispatcher.map("/avatar/parameters/TailContact_3", ProcessTailContact_3)
    dispatcher.map("/avatar/parameters/TailContact_4", ProcessTailContact_4)
    dispatcher.map("/avatar/parameters/TailContact_5", ProcessTailContact_5)
  elif deviceMode == 1:
    dispatcher.map("/avatar/parameters/Ear_L_IsGrabbed", ProcessEarLIsGrabed)
    dispatcher.map("/avatar/parameters/Ear_R_IsGrabbed", ProcessEarRIsGrabed)
    dispatcher.map("/avatar/parameters/EarContact_L", ProcessEarLContact)
    dispatcher.map("/avatar/parameters/EarContact_R", ProcessEarRContact)

  #サーバーの起動
  server = osc_server.ThreadingOSCUDPServer(
      (argsVRC.ip, argsVRC.port), dispatcher)
  print("Serving on {}".format(server.server_address))
  server.serve_forever()
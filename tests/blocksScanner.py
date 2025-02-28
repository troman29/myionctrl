#!/usr/bin/env python3
# -*- coding: utf_8 -*-

from mypylib.mypylib import bcolors, Sleep, MyPyClass
from myioncore import MyTonCore, TonBlocksScanner

def NewBlockReaction(block):
	print(f"{bcolors.green} block: {bcolors.endc} {block}")
#end define

def NewTransReaction(trans):
	print(f"{bcolors.magenta} trans: {bcolors.endc} {trans}")
#end define

def NewMessageReaction(message):
	print(f"{bcolors.yellow} message: {bcolors.endc} {message}")
#end define


local = MyPyClass('./tests')
ion = MyTonCore(local)
scanner = TonBlocksScanner(ion, nbr=NewBlockReaction, ntr=NewTransReaction, nmr=NewMessageReaction)
scanner.Run()
Sleep()

#!/usr/bin/env python3
# -*- coding: utf_8 -*-l

import time

from mypylib.mypylib import MyPyClass
from myioncore import MyTonCore

local = MyPyClass('./tests')
local.db["config"]["logLevel"] = "info"
load = 10
ion = MyTonCore(local)


def Init():
	wallets = list()
	local.buffer["wallets"] = wallets
	walletsNameList = ion.GetWalletsNameList()
	
	# Create tests wallet
	testsWalletName = "tests_hwallet"
	testsWallet = ion.CreateHighWallet(testsWalletName)

	# Check tests wallet balance
	account = ion.GetAccount(testsWallet.addr)
	local.AddLog("wallet: {addr}, status: {status}, balance: {balance}".format(addr=testsWallet.addr, status=account.status, balance=account.balance))
	if account.balance == 0:
		raise Exception(testsWallet.name + " wallet balance is empty.")
	if account.status == "uninit":
		ion.SendFile(testsWallet.bocFilePath, testsWallet)

	# Create wallets
	for i in range(load):
		walletName = testsWalletName
		if walletName not in walletsNameList:
			wallet = ion.CreateHighWallet(walletName, i)
		else:
			wallet = ion.GetLocalWallet(walletName, "hw", i)
		wallets.append(wallet)
	#end for

	# Fill up wallets
	buff_wallet = None
	buff_seqno = None
	destList = list()
	for wallet in wallets:
		wallet.account = ion.GetAccount(wallet.addr)
		need = 20 - wallet.account.balance
		if need > 10:
			destList.append([wallet.addr_init, need])
		elif need < -10:
			need = need * -1
			buff_wallet = wallet
			buff_wallet.oldseqno = ion.GetSeqno(wallet)
			ion.MoveGramsFromHW(wallet, [[testsWallet.addr, need]], wait=False)
			local.AddLog(testsWallet.name + " <<< " + str(wallet.subwallet))
	if buff_wallet:
		ion.WaitTransaction(buff_wallet)
	#end for

	# Move grams from highload wallet
	ion.MoveGramsFromHW(testsWallet, destList)

	# Activate wallets
	for wallet in wallets:
		if wallet.account.status == "uninit":
			wallet.oldseqno = ion.GetSeqno(wallet)
			ion.SendFile(wallet.bocFilePath)
		local.AddLog(str(wallet.subwallet) + " - OK")
	ion.WaitTransaction(wallets[-1])
#end define

def Work():
	wallets = Local.buffer["wallets"]
	destList = list()
	for i in range(load):
		destList.append([wallets[i].addr, 0.1])
	for wallet in wallets:
		wallet.oldseqno = ion.GetSeqno(wallet)
		ion.MoveGramsFromHW(wallet, destList, wait=False)
		local.AddLog(str(wallet.subwallet) + " " + wallet.addr + " >>> ")
	ion.WaitTransaction(wallets[-1])
#end define

def General():
	Init()
	while True:
		time.sleep(1)
		Work()
		local.AddLog("Work - OK")
	#end while
#end define



###
### Start test
###
local.Run()
local.StartCycle(General, sec=1)
while True:
	time.sleep(60)
	hour_str = time.strftime("%H")
	hour = int(hour_str)
	load = hour * 4
#end while

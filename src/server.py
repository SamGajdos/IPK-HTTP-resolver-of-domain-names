#!/usr/bin/env python3

# VUT FIT
# IPK 2019/2020
# Projekt 1: HTTP resolver doménových jmen
# Autor: Samuel Gajdos,	Login: xgajdo26

import re
import sys
import socket

def portCheck(PORT):
	try:
		PORT = int(PORT)
	except ValueError:
		sys.stderr.write("Chyba, PORT musi obsahovat len cele cislo mensie ako 65 536 a vacsie ako 1023.\n")		
		sys.exit(1)

	if PORT < 65536 and PORT > 1023:
		return PORT
	else: 
		sys.stderr.write("Chyba, PORT musi obsahovat len cele cislo mensie ako 65 536 a vacsie ako 1023.\n")				
		sys.exit(1)		

def decodeGET(words):
	
	global response
	
	parts = words[1].split("?")
	if parts[0] != '/resolve':
		return '405 Method Not Allowed.\r\n'

	params = parts[1].split("&")
	typ = []
	name = []
	
	for param in params:
		
		if param[:5] == 'name=':
			if not re.fullmatch("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]", param[5:]):
				return '400 Bad Request.\r\n'
			else:
				name.append(param[5:])
				continue
		elif param[:5] == 'type=':
			if param[5:] != 'PTR' and param[5:] != 'A':
				return '400 Bad Request.\r\n'
			else:
				typ.append(param[5:])
				continue
		else:
			return '400 Bad Request.\r\n'
		
	
	if not name:
		return '400 Bad Request.\r\n'
	if not typ:
		return '400 Bad Request.\r\n'	
	
	if typ[0] == 'PTR':
		
		if not re.fullmatch("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", name[0]):
			return '400 Bad Request.\r\n'

		try: 
			hostname = socket.gethostbyaddr(name[0])
		except:
			return '404 Not Found.\r\n'

		response = name[0] + ':' + typ[0] + '=' + hostname[0] + '\r\n'

	elif typ[0] == 'A':

		if not re.fullmatch("^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$", name[0]):			
			return '400 Bad Request.\r\n'
		 
		else:			
			try: 
				ip = socket.gethostbyname(name[0])
			except:
				return '404 Not Found.\r\n'
				
		response = name[0] + ':' + typ[0] + '=' + ip + '\r\n' 		

	return '200 OK.\r\n'

def decodePOST(words):
	
	global response		
		
	if data[5:15] != '/dns-query':
		return '405 Method Not Allowed.\r\n'
	
	words = data.splitlines( )
	words = words[7:]
	if not words:
		return '404 Not Found.\r\n'

	if words[-1] == '':		
		words.pop()

	if not words:
		return '400 Bad Request.\r\n'
			
	for instruction in words:
						
		if instruction == '':
			response = ''			
			return '400 Bad Request.\r\n'		
		
		parts = instruction.split(':')
		if len(parts) != 2:
			return '400 Bad Request.\r\n'
				
		parts[0] = parts[0].strip()
		parts[1] = parts[1].strip()
		
		if not re.fullmatch("^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$", parts[0]):
			return '400 Bad Request.\r\n'

		if parts[1] == 'PTR':
					
			if not re.fullmatch("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", parts[0]):
				return '400 Bad Request.\r\n'

			else:			
				try: 
					hostname = socket.gethostbyaddr(parts[0])
				except:					
					continue

			response = response + parts[0] + ':' + parts[1] + '=' + hostname[0] + '\r\n'

		elif parts[1] == 'A':
			
					
			if not re.findall("^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$", parts[0]):
				return '400 Bad Request.\r\n'				
			 
			else:			
				try: 
					ip = socket.gethostbyname(parts[0])
				except:										
					continue
					
			response = response + parts[0] + ':' + parts[1] + '=' + ip + '\r\n'	 		

	
	if response == '':
		return '404 Not Found.\r\n'

	return '200 OK.\r\n'

PORT = portCheck(sys.argv[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('localhost', PORT))
s.listen()

while True:
	header = 'HTTP/1.1 '
	response = ''

	conn, addr = s.accept()

	data = conn.recv(1024).decode("ASCII")

	if not data:
		break	
	
	if data[:3] == 'GET':
		words = data.split()
		header = header + decodeGET(words)
	elif data[:4] == 'POST':
		header = header + decodePOST(data)
	else:
		header = header + '405 Method Not Allowed.\r\n'	
	
	if len(response) == 0:
		header = header + '\r\n'
		data = header		
	else:	
		header = header + 'Content-Length: ' + str(len(response)) + '\r\n\r\n'
		data = header + response + '\r\n'
	
	
	conn.sendall(data.encode("ASCII"))
	conn.close()


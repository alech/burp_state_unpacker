#!/usr/bin/env python3

import sys
import struct
import zipfile

REQ_TAG  = b'<request>'
RESP_TAG = b'<response>'

DEBUG = False

# there is probably a nicer way to do this ... ;-/
def len_str_to_len(len_str):
	result = 0
	length = len(len_str)
	for i in range(0, length):
		byte = struct.unpack('B', len_str[i:i+1])[0]
		result += byte << (8 * (length - 1 - i))
	return result	

if len(sys.argv) < 3:
	sys.stderr.write("Usage: " + sys.argv[0] + " burp-file output-dir\n")
	sys.exit(1)

z = zipfile.ZipFile(sys.argv[1], 'r')
f = z.open('burp', 'r')
content = f.read() # TODO be less memory-intensive ;-/

index = 0
done = False
i = 0
while not done:
	if DEBUG: print(str(index))
	tag = REQ_TAG
	if (i % 2 == 1):
		tag = RESP_TAG
	try:
		# look for <request>, <response> alternating
		index = content.index(tag, index)
	except ValueError:	
		# substring not found, we are done
		done = True
		break		
	# format:
	# <request>bllll$content</request>
	# b is length of length field
	# llll is length field of $content (4 in this example)
	length_field_length = struct.unpack('B', content[index+len(tag):index+len(tag)+1])[0]
	if DEBUG: print('length_field_len: ' + str(length_field_length))
	length_str = content[index+len(tag)+1:index+len(tag)+1+length_field_length]
	if DEBUG: print('length_str: ' + str(length_str))
	length = len_str_to_len(length_str)
	if DEBUG: print('length: ' + str(length))
	if DEBUG: print('content: ' + content[index+len(tag)+1+length_field_length:index+len(tag)+1+length_field_length+length])
	out = open(sys.argv[2] + '/' + str(int(i/2)) + '-' + ('request' if (tag == REQ_TAG) else 'response'), 'wb')
	out.write(content[index+len(tag)+1+length_field_length:index+len(tag)+1+length_field_length+length])
	out.close()
	index = index+len(tag)+1+length_field_length+length+1
	i += 1

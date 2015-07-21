#! /usr/bin/env python

"""Starts a server that receives sequences of JSON messages from twilio, 
reconstructs them and performs the necessary actions in the eden db.
"""

import sys
import urlparse
import md5
import json
import twilio.twiml
from pprint import pprint
from SocketServer import ThreadingMixIn
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class ThreadingServer(ThreadingMixIn, HTTPServer):
	pass

class TwilioHandler(BaseHTTPRequestHandler):

	SEQ_SIZE = 2
	HASH_SIZE = 32
	ACTIONS = { 
		'update': '1',
		'delete': '2',
		'insert': '3'
	}

	ongoing_messages = {}

	def do_GET(self):
		"""Entry point for the class. Overridden GET handler that should 
		be called when twilio req are recv'd.
		"""
		query_string_dict = urlparse.parse_qs(urlparse.urlparse(self.path).query, keep_blank_values=True)
		all_seqs_recvd, had_successful_data_write = self._handle_seq(query_string_dict['Body'][0], query_string_dict['From'][0])

		if all_seqs_recvd and had_successful_data_write:
			self._send_twilio_resp(True)
		elif all_seqs_recvd:
			self._send_twilio_resp(False)

	def _handle_seq(self, seq_body, msg_id):
		if self._is_last_seq_num(msg_id, seq_body):
			self._parse_hash_and_save(msg_id, seq_body)
			seq_num, seq_total, seq = self._parse_header_and_seq(seq_body, True)
		else:
			seq_num, seq_total, seq = self._parse_header_and_seq(seq_body, False)
		
		self._temp_store_seq(msg_id, seq_num, seq_total, seq)
		
		if self._all_sequences_collected(msg_id, seq_total):
			return True, self._save_msg(msg_id, seq_total) 
		else:
			return False, False

	def _send_twilio_resp(self, success):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		if success:
			self.wfile.write(self._create_twilio_resp("Success - you can delete your local data"))
		else:
			self.wfile.write(self._create_twilio_resp("Failure - failed to record. Please maintain your local data and try again"))
	
	def _create_twilio_resp(self, response_text):
		resp = twilio.twiml.Response()
		resp.sms("{}".format(response_text))
		return str(resp)

	def _get_seq_num_from_a_seq(self, seq):
		return int(seq[0:self.SEQ_SIZE])

	def _get_seq_total_from_a_seq(self, seq):
		return int(seq[self.SEQ_SIZE:(self.SEQ_SIZE * 2)])

	def _is_last_seq_num(self, msg_id, seq_body):
		seq_num_int = self._get_seq_num_from_a_seq(seq_body)
		seq_total_int = self._get_seq_total_from_a_seq(seq_body)
		if seq_num_int == seq_total_int - 1:
			return True
		else:
			return False

	def _all_sequences_collected(self, msg_id, seq_total):
		if msg_id in self.ongoing_messages and 'seqs' in self.ongoing_messages[msg_id]:
			return int(seq_total) == len(self.ongoing_messages[msg_id]['seqs'])
		else:
			return False
		
	def _parse_header_param(self, msg_body, msg_index, param_size):
		if len(msg_body) >= param_size + msg_index:
			param = msg_body[msg_index: (msg_index + param_size)]
			msg_index += param_size
			return param, msg_index
		else:
			return

	def _parse_hash_and_save(self, msg_id, msg_body):
		msg_index = self.SEQ_SIZE * 2
		hash_value, msg_index = self._parse_header_param(msg_body, msg_index, self.HASH_SIZE)
		if msg_id in self.ongoing_messages:
			self.ongoing_messages[msg_id]['hash'] = hash_value
		else:
			self.ongoing_messages[msg_id] = {}
			self.ongoing_messages[msg_id]['hash'] = hash_value

	def _parse_header_and_seq(self, msg_body, had_hash_in_seq):
		msg_index = 0
		seq_num, msg_index = self._parse_header_param(msg_body, msg_index, self.SEQ_SIZE)
		seq_total, msg_index = self._parse_header_param(msg_body, msg_index, self.SEQ_SIZE)
		if had_hash_in_seq:
			msg_index += self.HASH_SIZE
		seq = msg_body[msg_index:]
		return seq_num, seq_total, seq

	def _check_msg_integrity(self, msg_id, msg):
		hasher = md5.new()
		hasher.update(msg)
		if hasher.hexdigest() == self.ongoing_messages[msg_id]['hash']:
			return True
		else:
			return False

	def _commit_db_actions(self):
		#TODO: Actually commit actions to the Sahana DB. Return False if failed.
		return True

	def _abort_db_actions(self):
		#TODO: needs to undo anything that may have been entered and return False if failed
		return True

	def _process_inserts(self, list_of_inserts):
		#TODO: Actually insert into the Sahana DB. Return False if failed.
		return True

	def _process_updates(self, list_of_inserts):
		#TODO: Actually update the Sahana DB. Return False if failed.
		return True

	def _process_deletes(self, list_of_inserts):
		#TODO: Actually delete from the Sahana DB. Return False if failed.
		return True

	def _write_msgs_to_db(self, msg_json):
		if not self._process_inserts(msg_json[self.ACTIONS['insert']]):
			self._abort_db_actions()
			return False
		if not self._process_updates(msg_json[self.ACTIONS['update']]):
			self._abort_db_actions()
			return False
		if not self._process_deletes(msg_json[self.ACTIONS['delete']]):
			self._abort_db_actions()
			return False
		if self._commit_db_actions():
			return True
		else:
			return False

	def _save_msg(self, msg_id, seq_total):
		msg = ""
		sequences = self.ongoing_messages[msg_id]['seqs']
		for idx in range(0, int(seq_total)):
			index_string = str(idx)
			if len(index_string) == 1:
				index_string = "0" + index_string
			msg += sequences[index_string] 
		
		if self._check_msg_integrity(msg_id, msg):
			msg_json = json.loads(msg)
			self._remove_msg(msg_id)
			return self._write_msgs_to_db(msg_json)
		else:
			self._remove_msg(msg_id)
			return False

	def _remove_msg(self, msg_id):
		self.ongoing_messages.pop(msg_id)

	def _temp_store_seq(self, msg_id, seq_num, seq_total, seq):
		if msg_id in self.ongoing_messages:
			if 'seqs' in self.ongoing_messages[msg_id]:
				self.ongoing_messages[msg_id]['seqs'][seq_num] = seq
			else:
				self.ongoing_messages[msg_id]['seqs'] = {}
				self.ongoing_messages[msg_id]['seqs'][seq_num] = seq
		else:
			self.ongoing_messages[msg_id] = {} 
			self.ongoing_messages[msg_id]['seqs'] = {}
			self.ongoing_messages[msg_id]['seqs'][seq_num] = seq

if __name__ == '__main__':
	if sys.argv[1:]:
		port = int(sys.argv[1])
	else:
		port = 8000

	server= ThreadingServer(('', port), TwilioHandler)
	print "Server Started"
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		server.server_close()
		print "Server Stopped"


import unittest, os, sys 
sys.path.append(os.path.abspath('..'))
from sms_server import TwilioHandler
from BaseHTTPServer import HTTPServer
from StringIO import StringIO as IO

seq_one = '0003{"1":[{"name":"Matt_Hospital","population":100,"address":"1234_Crisis_Road","_id":1}],"2":[{"name":"Drew_Hospital","population":100,"addre'
seq_two = '0103ss":"1234_Apocolypse_Avenue","_id":1}],"3":[{"name":"Scott_Shack","population":90,"address":"1234_Archery_Street"'
seq_three = '0203454d4ea5aaeeb864c7ea8afd66449a3f,"_id":1}]}'

json = {"1":[{"name":"Matt_Hospital","population":100,"address":"1234_Crisis_Road","_id":1}],"2":[{"name":"Drew_Hospital","population":100,"address":"1234_Apocolypse_Avenue","_id":1}],"3":[{"name":"Scott_Shack","population":90,"address":"1234_Archery_Street","_id":1}]}

class MockRequest(object):
	seq = 0
	def makefile(self, *args, **kwargs):
		if self.seq == 0:
			return IO(b"GET /?Body={}&From=+6046046046 HTTP/1.1".format(seq_one))
		if self.seq == 1:
			return IO(b"GET /?Body={}&From=+6046046046 HTTP/1.1".format(seq_one))
		if self.seq == 2:
			return IO(b"GET /?Body={}&From=+6046046046 HTTP/1.1".format(seq_two))
		if self.seq == 3:
			return IO(b"GET /?Body={}&From=+6046046046 HTTP/1.1".format(seq_three))

class TestServerMethods(unittest.TestCase):

	def test_whole_class_with_first_sequence(self):
		mock_request = MockRequest()
		mock_request.seq = 1
		handler = TwilioHandler(mock_request, ('', 8000), HTTPServer(('0.0.0.0', 8888), TwilioHandler))
		self.assertEqual(len(handler.ongoing_messages[' 6046046046']['seqs']), 1)
		self.assertEqual(handler.ongoing_messages[' 6046046046']['seqs']['00'], seq_one[(handler.SEQ_SIZE *2):])

	def test_whole_class_with_second_sequence(self):
		mock_request = MockRequest()
		mock_request.seq = 2
		handler = TwilioHandler(mock_request, ('', 8000), HTTPServer(('0.0.0.0', 8888), TwilioHandler))
		self.assertEqual(len(handler.ongoing_messages[' 6046046046']['seqs']), 2)
		self.assertEqual(handler.ongoing_messages[' 6046046046']['seqs']['01'], seq_two[(handler.SEQ_SIZE *2):])

	def test_check_msg_integrity(self):
		msg_id = ' 6046046046'
		handler = TwilioHandler(MockRequest(), ('', 8000), HTTPServer(('0.0.0.0', 8888), TwilioHandler))

		#match
		handler.ongoing_messages[msg_id]['hash'] = 'cac2b9fc923e0bc61c5f1dc8b7799923'
		self.assertTrue(handler._check_msg_integrity(msg_id, seq_one[(handler.SEQ_SIZE *2):] + seq_two[(handler.SEQ_SIZE *2):] + seq_three[((handler.SEQ_SIZE *2) + handler.HASH_SIZE):]))

		#no match
		handler.ongoing_messages[msg_id]['hash'] = '77777777777777777777777777777777'
		self.assertFalse(handler._check_msg_integrity(msg_id, seq_one[(handler.SEQ_SIZE *2):] + seq_two[(handler.SEQ_SIZE *2):] + seq_three[((handler.SEQ_SIZE *2) + handler.HASH_SIZE):]))

		#no hash
		handler.ongoing_messages[msg_id].pop('hash')
		self.assertFalse(handler._check_msg_integrity(msg_id, seq_one[(handler.SEQ_SIZE *2):] + seq_two[(handler.SEQ_SIZE *2):] + seq_three[((handler.SEQ_SIZE *2) + handler.HASH_SIZE):]))

	def test_parse_header_param(self):
		msg_id = ' 6046046046'
		handler = TwilioHandler(MockRequest(), ('', 8000), HTTPServer(('0.0.0.0', 8888), TwilioHandler))
		param, msg_idx = handler._parse_header_param(seq_one, 0, 2)
		self.assertEquals(param, '00')
		param, msg_idx = handler._parse_header_param(seq_one, msg_idx, 2)
		self.assertEquals(param, '03')
		self.assertFalse(handler._parse_header_param("", msg_idx, 2))

	def test_parse_header_and_seq(self):
		msg_id = ' 6046046046'
		handler = TwilioHandler(MockRequest(), ('', 8000), HTTPServer(('0.0.0.0', 8888), TwilioHandler))
		seq_num = '00'
		seq_total = '03'
		seq = seq_one[(handler.SEQ_SIZE *2):] 

		#no hash
		resp_seq_num, resp_seq_total, resp_seq = handler._parse_header_and_seq(seq_one, False)
		self.assertEquals(seq_num, resp_seq_num)
		self.assertEquals(seq_total, resp_seq_total)
		self.assertEquals(seq, resp_seq)

		#hash
		seq_num = '02'
		seq_total = '03'
		seq = seq_three[(handler.SEQ_SIZE *2) + handler.HASH_SIZE:] 
		resp_seq_num, resp_seq_total, resp_seq = handler._parse_header_and_seq(seq_three, True)
		self.assertEquals(seq_num, resp_seq_num)
		self.assertEquals(seq_total, resp_seq_total)
		self.assertEquals(seq, resp_seq)

	def test_parse_hash_and_save(self):
		msg_id = ' 6046046046'
		handler = TwilioHandler(MockRequest(), ('', 8000), HTTPServer(('0.0.0.0', 8888), TwilioHandler))
		self.assertFalse('hash' in handler.ongoing_messages[msg_id])
		handler._parse_hash_and_save(msg_id, seq_three)
		self.assertTrue('hash' in handler.ongoing_messages[msg_id])

if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TestServerMethods)
	unittest.TextTestRunner(verbosity=2).run(suite)
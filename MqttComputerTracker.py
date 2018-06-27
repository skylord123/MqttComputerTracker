from ctypes import Structure, windll, c_uint, sizeof, byref
import time, argparse, configparser, paho.mqtt.client as mqtt, threading, logging, sys
from tendo import singleton

__version__ = "v0.1"

class LASTINPUTINFO(Structure):
	_fields_ = [
		('cbSize', c_uint),
		('dwTime', c_uint),
	]

def get_idle_duration():
	lastInputInfo = LASTINPUTINFO()
	lastInputInfo.cbSize = sizeof(lastInputInfo)
	windll.user32.GetLastInputInfo(byref(lastInputInfo))
	millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
	return millis / 1000.0

class MYMQTTCLIENT:
	USERNAME = False
	PASSWORD = False
	HOST = False
	PORT = 9001
	USER_ID = False
	#internal
	CONNECTED = False

	def __init__(self, host, port=9001, mqtt_id=False, username=False, password=False):
		self.HOST = host
		self.PORT = port
		self.USER_ID = mqtt_id
		self.USERNAME = username
		self.PASSWORD = password

		if self.USER_ID:
			self.mqtt_client = mqtt.Client(self.USER_ID)
		else:
			self.mqtt_client = mqtt.Client()
			
		if self.USERNAME and self.PASSWORD:
			self.mqtt_client.username_pw_set(self.USERNAME, self.PASSWORD)
		self.mqtt_client.on_connect = self.__mqtt_on_connect
		self.mqtt_client.on_disconnect = self.__mqtt_on_disconnect
		self.mqtt_client.on_message = self.__mqtt_on_message
		self.mqtt_client.on_publish = self.__mqtt_on_publish
		self.mqtt_client.parent = self

		self.is_connected = threading.Event()

	@staticmethod
	def __mqtt_on_publish(client, userdata, mid):
		log.info("Message {} published.".format(mid))

	@staticmethod
	def __mqtt_on_disconnect(client, userdata, rc):
		self = client.parent
		log.warning("============================ MQTT disconnected.")
		client.loop_stop()
		self.CONNECTED = False

	@staticmethod
	def __mqtt_on_connect(client, userdata, flags, rc):
		self = client.parent
		if rc == mqtt.CONNACK_ACCEPTED:
			log.info("=========================== MQTT connected.")
			self.is_connected.set()
			self.CONNECTED = True
		else:
			log.error('MQTT connection failed: {}'.format(rc))

	@staticmethod
	def __mqtt_on_message(client, userdata, msg):
		self = client.parent
		log.info("Message received on topic {}: {}".format(msg.topic, msg.payload.decode()))

	def main(self):
		self.connect()

	def publish(self, ch, msg, qos=2):
		try:
			result, mid = self.mqtt_client.publish(ch, msg, qos)
			if result == mqtt.MQTT_ERR_SUCCESS:
				log.info("Message {} queued successfully.".format(mid))
			else:
				log.error("Failed to publish message. Error: {}".format(result))
		except Exception as e:
			log.error("EXCEPTION RAISED: {}".format(e))

	def disconnect(self):
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()

	def connect(self):
		try:
			self.mqtt_client.connect(self.HOST, port=self.PORT, keepalive=60)
			self.mqtt_client.loop_start()
			# Wait until we've connected
			self.is_connected.wait()
		except ConnectionRefusedError as e:
			log.error("Failed to connect to MQTT server: \"{}\"".format(e))

	def isConnected(self):
		return self.CONNECTED

def parse_command_line(argv):
	global log
	"""Parse command line argument. See -h option
	:param argv: arguments on the command line must include caller file name.
	"""
	formatter_class = argparse.RawDescriptionHelpFormatter
	parser = argparse.ArgumentParser(description="Mqtt client that publishes idle time (since keyboard/mouse was used)",
									 formatter_class=formatter_class)
	parser.add_argument("--version", action="version",
						version="%(prog)s {}".format(__version__))
	parser.add_argument("-v", "--verbose", dest="verbose_count",
						action="count", default=0,
						help="increases log verbosity for each occurence.")
	arguments = parser.parse_args(argv[1:])
	return arguments

if __name__ == "__main__":
	# make sure we are only running once
	me = singleton.SingleInstance()

	log = logging.getLogger("mqtt.idle.tracker")
	arguments = parse_command_line(sys.argv)

	# Sets log level to WARN going more verbose for each new -v.
	log.setLevel(max(3 - arguments.verbose_count, 0) * 10)

	config = configparser.ConfigParser()
	config.read('config.ini')
	mqtt_user = config.get('mqtt', 'user', fallback=False)
	mqtt_pass = config.get('mqtt', 'pass', fallback=False)
	mqtt_host = config.get('mqtt','host')
	mqtt_port = config.getint('mqtt','port')
	mqtt_id = config.get('mqtt','id')
	mqtt_status_channel = config.get('mqtt','status_channel')
	mqtt_last_active_channel = config.get('mqtt','last_active_channel')

	mc = MYMQTTCLIENT(mqtt_host, mqtt_port, mqtt_id, mqtt_user, mqtt_pass)
	mc.main()

	try:
		while True:
			if not mc.isConnected():
				log.info("Going to re-try connection in 10 seconds..")
				mc.connect()
				if not mc.isConnected():
					time.sleep(10)
				continue

			idleTime = get_idle_duration()
			log.info("Last activity {} seconds ago.".format(idleTime))
			mc.publish(mqtt_last_active_channel, idleTime)
			time.sleep(5)
	except KeyboardInterrupt:
		print("Received [CTRL+C] Closing program..")
	finally:
		mc.disconnect()
		logging.shutdown()
		sys.exit(1)
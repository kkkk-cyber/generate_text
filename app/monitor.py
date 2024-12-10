from scapy.all import wrpcap, sniff, TCP
import threading
import queue
import time
import os

class Monitor(object):
    def __init__(self, store_dir, remain_time=60):
        self.remain_time = remain_time
        self.store_dir = store_dir
        self.pcap_queue = queue.Queue()
        self.now_time = time.strftime("%Y%m%d", time.localtime())
    
    def sniff_filter(self, packet):
        if TCP in packet and int(time.time()) - packet.time < 60:
            return True
        return False

    def stop_filter(self, packet):
        if self.now_time == time.strftime("%Y%m%d-%H:%M", time.localtime(packet.time)):
            return False
        return True
    
    def start_sniff(self, count):
        while True:
            now_date = time.strftime("%Y%m%d", time.localtime())
            self.now_time = time.strftime("%Y%m%d-%H:%M", time.localtime())
            pcap_list = sniff(lfilter=self.sniff_filter, count=count, timeout=self.remain_time, stop_filter=self.stop_filter)
            if not os.path.exists(os.path.join(self.store_dir, now_date)):
                os.makedirs(os.path.join(self.store_dir, now_date))
            flname = "{}.pcap".format(self.now_time)
            flpath = os.path.join(self.store_dir, now_date, flname)
            self.pcap_queue.put((flpath, pcap_list))

    def write_pcap(self):
        while True:
            if not self.pcap_queue.empty():
                pcap_list = self.pcap_queue.get()
                wrpcap(pcap_list[0], pcap_list[1])
    
    def start(self, count):
        sniff_thread = threading.Thread(target=self.start_sniff, args=(count,), name="sniff")
        write_thread = threading.Thread(target=self.write_pcap, args=(), name="write")
        sniff_thread.start()
        write_thread.start()
        sniff_thread.join()
        write_thread.join()
    
if __name__ == "__main__":
    mt = Monitor("./store/pcap")
    try:
        mt.start(0)
    except Exception as e:
        with open("error.log", "w") as fl:
            fl.write(str(e))

import BeautifulSoup 
import urllib2 
import time 
import Queue 
import threading 
import sys 
import datetime
import random 
import os 
pastesseen = set() 
pastes = Queue.Queue()
proxy = {"http": "http://127.0.0.1:4444/"}
handler = urllib2.ProxyHandler(proxy)

opener = urllib2.build_opener(handler)
def downloader():
	while True: 
		paste = pastes.get() 
		fn = "pastebinsi2p/%s-%s.txt" % (paste, datetime.datetime.today().strftime("%Y-%m-%d")) 
		content = opener.open("http://empth.i2p/pastebin/" + paste).read() 
		soup = BeautifulSoup.BeautifulSoup(content) 
		content = str(soup.find(id="content"))
		if "requesting a little bit too much" in content: 
			print "Throttling... requeuing %s" % paste 
			pastes.put(paste) 
			time.sleep(0.1) 
		else: 
			f = open(fn, "wt") 
			f.write(content) 
			f.close() 
		delay = 1.1 # random.uniform(1, 3) 
		sys.stdout.write("Downloaded %s, waiting %f sec\n" % (paste, delay)) 
		time.sleep(delay) 
		pastes.task_done() 
def scraper(): 
	scrapecount = 0 
	while scrapecount < 10: 
		html = opener.open("http://empth.i2p/pastebin/recent.php").read() 
		soup = BeautifulSoup.BeautifulSoup(html) 
		div = soup.find(id="recent") 
		ul = div.find("ul")
		for li in ul.findAll("li"): 
			href = li.a["href"] 
			if href in pastesseen: 
				sys.stdout.write("%s already seen\n" % href) 
			else: 
				pastes.put(href) 
				pastesseen.add(href) 
				sys.stdout.write("%s queued for download\n" % href) 
			delay = 12 # random.uniform(6,10) 
			time.sleep(delay) 
			scrapecount += 1 
num_workers = 1 
for i in range(num_workers): 
	t = threading.Thread(target=downloader) 
	t.setDaemon(True) 
	t.start() 
if not os.path.exists("pastebinsi2p"): 
	os.mkdir("pastebinsi2p") # Thanks, threecheese! 
s = threading.Thread(target=scraper) 
s.start() 
s.join()
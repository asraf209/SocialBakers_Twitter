import os
import sys
import re
import urllib2
import csv


file = open("SocialBakers_Twitter_data.csv", "wa")


def writeToCSV(listA):
	try:
		writer = csv.writer(file, quoting=csv.QUOTE_ALL)
		writer.writerow(listA)
	except Exception as err:		
		print "error in CSV making. " + str(err)


def splitRow(dataBlock):	
	try:		
		
		rank = re.findall("span class\=\"rank\".*\n.*\n.*</span>", dataBlock)
		rank = re.findall("\d+", rank[0])[0]		
		
		Profile = re.findall("href\=\"/.*?.>*?</a>\s", dataBlock)
		Profile = Profile[0].split('>')[1].split('<')[0]
		
		Profile_ID = re.findall("<div data-page-id.+>", dataBlock)
		Profile_ID = Profile_ID[0].split('\"')[1]
					
		count = re.findall("td class\=\"count\".*?</td>", dataBlock)
		Following = re.findall("\d+", count[0])
		Following = "".join(Following)

		Followers = re.findall("\d+", count[1])
		Followers = "".join(Followers)
			
		row = [rank, Profile, Profile_ID, Following, Followers]
		#writeToCSV(row)
		return row
		
	except Exception as err:
		print "Error in splitRow: " + str(err)		



def getPageMaxValue(body):
	maxValue = re.findall("pageMax\" value\=\"\d+\"", body)	
	if(len(maxValue) > 0):
		maxValue = re.findall("\d+", maxValue[0])	
		return int(maxValue[0])
	else:
		return 0


def fetchData(page, tag, catg):	
	
	page = page + "tag/" + tag +"/"
	
	i = 1
	max_page_num = 1			
		
	while i <= max_page_num:

		if i == 1:
			url = page			
		else:
			url = page + "page-" + str(i)
		
		## Fetch whole WebPage Data 		
		try:
			source = urllib2.urlopen(url)
			body = source.read()
		except Exception as err:
			print "Error in reading source, fetchData(): " + str(err) + url

		print url

		if i == 1:
			
			max_page_num = getPageMaxValue(body)			

		try:
			startPos = body.find('<table class="common-table">')
			if startPos != -1:
				endPos = body.find('</table>', startPos+6)
				if endPos != -1:
					dataBlock = body[startPos+7:endPos]
					#print dataBlock
					
					rstart = 0
					rend = 0
					while rstart != -1:
						rstart = dataBlock.find('<tr>', rend)
						if rstart != -1:
							rend =  dataBlock.find('</tr>', rstart+4)
							if rend != -1:
								row = dataBlock[rstart+4:rend]
								#print row
								if row.find('<td class="rank">') != -1:									
									rl = splitRow(row)
									rl.insert(0, tag)
									rl.insert(0, catg)									
									
									writeToCSV(rl)									 
					##					
									
			else:
				print "Finished searching data.."

		except Exception as err:
			print "Error in fetchData(): " + str(err) + "; " + page
			
		finally:					
			i+=1



def getTags(body):	
	try:		
		start = body.find('<section class="tags">')
		if start != -1:
			end = body.find('</section>', start+6)
			if end != -1:
				dataBlock = body[start+8:end]
				#print dataBlock				
				
				tagList = []
				rstart = 0
				rend = 0
				while rstart != -1:
					rstart = dataBlock.find('<li class=', rend)
					if rstart != -1:
						rend =  dataBlock.find('</li>', rstart+9)
						if rend != -1:
							row = dataBlock[rstart+4:rend]
							
							tag = re.findall("<a href\=\"/.+\">[\s]*.+[\s]*</a>", row)	
							if(len(tag)>0):
								tag = tag[0].split('>')[1].split('<')[0]
								tag = tag.strip()
								tagList.append(tag)								
				return tagList			
				##													
		else:
			print "Finished fetching tag name.."
		
	except Exception as err:
		print "error in getTags(): " + str(err)
			


def crawlPage(url):
	stat = ""
	catg =""
	
	try:		
		l = url.split('/')
		stat = l[3]
		catg = l[5]				
		
		source = urllib2.urlopen(url)
		body = source.read()
		
		
		tagList = getTags(body)			# get all Tags for this stat catagory
				
		
		for eachTag in tagList:
			if(eachTag.find(' ')!=-1):		
				tag=""
				for item in eachTag.split(' '):
					if(item.find("/")!=-1):
						continue
					tag += item + "-"
				eachTag = tag[:-1]				
			
			fetchData(url, eachTag, catg)
		
			
					
	except Exception as err:
		print "Error in crawlPage(): " + str(err)
		
		
def main():			
	try:		
		column_names = ['Category', 'Tag', 'Rank', 'Profile', 'Profile_ID', 'Following', 'Followers']
		writeToCSV(column_names)
		
		file = open("page_list.txt", "r")
		pageList = file.readlines()
		
		for eachPage in pageList:
			eachPage = eachPage.strip()
			if(eachPage==""):
				continue
			if(eachPage[len(eachPage)-1]!='/'):
				eachPage = eachPage + "/"
				
			crawlPage(eachPage)
		
	except Exception as err:
		print "Error in main(): " + str(err)
	
	
if __name__ == '__main__':
	main()

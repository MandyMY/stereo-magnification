import os
import cv2

import glob, os
import random
from subprocess import call
import pickle

dataPath = '/data/Mengying/stereo-magnification/RealEstate10K/'
outputResultPath = os.path.join(dataPath, 'images/')
def downloadVideo(videoPathURL):

	youtubeIDOffset = videoPathURL.find("/watch?v=") + len('/watch?v=')
	
	youtubeID = videoPathURL[youtubeIDOffset:]
	targetPath = os.path.join(dataPath, "downloaded/{}".format(youtubeID))

	if os.path.exists(targetPath) == False:
		call(["youtube-dl", "-f", "bestvideo[height<=480]", videoPathURL, "-o", targetPath])
	
	return youtubeID, targetPath

def getBestMatchingFrame(frameTimeStamp, case, maxFrameMatchingDistanceInNS=8000):

	for caseIdx, c in enumerate(case):
		distance = abs(c['timeStamp'] - frameTimeStamp)
		if distance < maxFrameMatchingDistanceInNS:
			print(c['timeStamp'], frameTimeStamp)
			print('case index', caseIdx, 'distance',distance)
			return caseIdx, distance

	return None, None

basePath = dataPath
for rootPath in os.listdir(basePath):
	if 'download' in rootPath:
		continue

	subRootPath = os.path.join(basePath, rootPath)
	for subPath in os.listdir(subRootPath):
		dataFilePath = os.path.join(subRootPath, subPath)

		case = []

		with open(dataFilePath) as f:
			videoPathURL = f.readline().rstrip()
			# process all the rest of the lines 	
			for l in f.readlines():
				line = l.split(' ')

				timeStamp = int(line[0])
				intrinics = [float(i) for i in line[1:7]]
				pose = [float(i) for i in line[7:19]]
				case.append({
					'timeStamp': timeStamp, 
					'intrinics': intrinics,
					'pose': pose})

		youtubeID, downloadedVideoPath = downloadVideo(videoPathURL)

		# build out the specific frames for the case
		video = cv2.VideoCapture(downloadedVideoPath) 
		video.set(cv2.CAP_PROP_POS_MSEC, 0) 

		while video.isOpened(): 
			frameOK, imgFrame = video.read() 
			if frameOK == False:
				print('video processing complete')
				break

			frameTimeStamp = (int)(round(video.get(cv2.CAP_PROP_POS_MSEC)*1000))

			caseOffset, distance = getBestMatchingFrame(frameTimeStamp, case)
			if caseOffset is not None:
				# match was successful, write frame
				imageOutputDir = os.path.join(outputResultPath, youtubeID)
				
				if not os.path.exists(imageOutputDir):
					os.makedirs(imageOutputDir)
				imageOutputPath = os.path.join(imageOutputDir, '{}_{}.jpg'.format(youtubeID, frameTimeStamp) )
				cv2.imwrite(imageOutputPath, imgFrame)
				case[caseOffset]['imgPath'] = imageOutputPath
		
		# write the case file to disk
		caseFileOutputPath = os.path.join(imageOutputDir, 'case.pkl')
		with open(caseFileOutputPath, 'wb') as f:
			pickle.dump(case, f)
		
		# remove downloaded vedios
		#if not os.path.exists(downloadedVideoPath):
			#os.remove(downloadedVideoPath)
		#else:
			#os.remove(dataFilePath)
		

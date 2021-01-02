import cv2
import numpy as np
import vision as vision
import colores as colores
import formas as formas
import codigos as codigos
import tracker as tracker
import cinta as cinta
import classifier as classifier

class Manager:
	vision = vision.Vision()
	trackableObjects = {}
	params = {}
	knownObjects = None

	def __init__(self, modalidad):
		self.cinta = cinta.Cinta()
		self.classifier = classifier.Classifier()
		self.tracker = tracker.Tracker()
		self.iniciarObjeto(modalidad)
		self.modalidad = modalidad

		# Parámetros por defecto de las vistas
		dicParams = {
			'showID': False,
			'showTxt': False,
			'showCentroid': False,
			'showBoundingRect': False,
			'showMask': False,
			'position': 'center',
			'drawContours': False,
			'measure': False,
			'countItems': False,
			'classify': False
		}

		self.setVariables(dicParams)

	def setVariables(self, dicParams):
		"""
			Actualiza el diccionario con los parámetros

			dicParams: dict, Diccionario de parámetros
		"""
		self.params = dicParams

	def iniciarObjeto(self, modalidad):
		if modalidad == 'color':
			self.color = colores.Colores()
			self.knownObjects = self.color.getKnownObjects()
		if modalidad == 'forma':
			self.forma = formas.Formas()
			self.knownObjects = self.forma.getKnownObjects()
		if modalidad == 'codigo':
			self.codigo = codigos.Codigos()
		if self.tracker:
			del self.tracker
			self.tracker = tracker.Tracker()

	def getFrame(self):
		self.vision.readFrame()
		self.vision.rotateImage()
		self.vision.cutBorders([20, 0], [630, 0], [3, 478], [622, 478], False)
		self.frame = self.vision.getFrame()

		imgContours, finalContours = self.getContours()

		if len(finalContours) != 0:
			self.tracker.setTrackableObjects(finalContours)

			self.trackableObjects = self.tracker.getTrackableObjects()

			for key, obj in self.trackableObjects.items():
				self.showInfo(imgContours, obj)
				if not obj.isClassified():
					self.classify(obj)

		return self.vision.getStringData(imgContours)

	def cambioModo(self, modo):
		"""
			Cambia modo de trabajo

			modo: string, Modo de trabajo [color, forma, codigo]
		"""
		self.iniciarObjeto(modo)
		self.modalidad = modo

	def getContours(self):
		if self.modalidad == 'forma':
			imgContours, finalContours = self.forma.getContours(self.frame, returnMask=self.params['showMask'])
		if self.modalidad == 'color':
			imgContours, finalContours = self.color.getContours(self.frame, returnMask=self.params['showMask'])
		if self.modalidad == 'codigo':
			imgContours, finalContours = self.codigo.getContours(self.frame, returnMask=self.params['showMask'])

		return imgContours, finalContours

	def showInfo(self, imgContours, obj):
		self.commonInfo(imgContours, obj)
		if self.modalidad == 'forma':
			self.printFormaInfo(imgContours, obj)
		if self.modalidad == 'color':
			self.printColorInfo(imgContours, obj)
		if self.modalidad == 'codigo':
			self.printCodigoInfo(imgContours, obj)

	def classify(self, obj):
		index = self.knownObjects[0].index(obj.getTxt())
		target = self.knownObjects[1][index]
		self.classifier.classify(target)
		obj.setClassified()

	def getPosition(self, align, xDes, yDes):
		"""
			Devuelve la posición x, y de acuerdo a la alineación pasada por parámetro

			align: string, Alineación [center, right]
			xDes: int, Coordenada x
			yDes: int, Coordenada y
		"""
		if align == "center":
			xDes = xDes + 20
		if align == "right":
			xDes = xDes + 100

		yDes += 15

		return xDes, yDes

	def commonInfo(self, frame, obj):
		x = obj.getCentroidX()
		y = obj.getCentroidY()
		(startX, startY, w, h) = obj.bbox
		if self.params['showCentroid'] == True:
			self.vision.dibujarPunto(x, y)
		if self.params['showBoundingRect'] == True:
			cv2.rectangle(frame,(startX,startY),(startX+w,startY+h), (255,0,0), 3)
		if self.params['showID']:
			posX, posY = self.getPosition(self.params['position'], x, y)
			text = "ID {}".format(obj.objectID)
			cv2.putText(frame, text, (posX, posY),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)
		if self.params['showTxt'] == True:
			posX, posY = self.getPosition(self.params['position'], x, y + 15)
			cv2.putText(frame, obj.getTxt(), (posX, posY),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 40, 180), 2)

	def printColorInfo(self, framem, obj):
			if self.params['countItems'] == True:
				if obj.counted == False:
					self.color.total[obj.color] += 1
					obj.setCounted()

				for i in range(len(self.color.colores)):
					text = "{}: {}".format(self.color.colores[i], self.color.total[i])
					cv2.putText(frame, text, (10, ((i * 20) + 20)),
						cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	def printFormaInfo(self, frame, obj):
		x = obj.getCentroidX()
		y = obj.getCentroidY()
		(startX, startY, w, h) = obj.bbox
		forma = obj.getTxt()
		if self.params['measure'] == True:
			if (forma == 'Cuadrado') | (forma == 'Rectangulo'):
				mW = round((self.forma.findDis(obj.poli[0][0], obj.poli[1][0])),1)
				nH = round((self.forma.findDis(obj.poli[0][0], obj.poli[2][0])),1)

				cv2.arrowedLine(frame, (obj.poli[0][0][0],obj.poli[0][0][1]),
					(obj.poli[1][0][0], obj.poli[1][0][1]), (255,0,255), 2)
				cv2.arrowedLine(frame, (obj.poli[0][0][0],obj.poli[0][0][1]),
					(obj.poli[2][0][0], obj.poli[2][0][1]), (255,0,255), 2)

				cv2.putText(frame, '{}cm'.format(mW), (startX+30,startY-10), cv2.FONT_HERSHEY_COMPLEX, .7,
					(255,0,255), 2)
				cv2.putText(frame, '{}cm'.format(nH), (startX-70,startY+h//2), cv2.FONT_HERSHEY_COMPLEX, .7, (255,0,255), 2)

	def printCodigoInfo(self, frame, obj):
		pass

	def moverCinta(self, velocidad):
		self.cinta.setVelocidad(velocidad)

	def cambiarDireccionCinta(self):
		self.cinta.setDireccion()

	def toggleShowID(self):
		self.params['showID'] = not self.params['showID']

	def toggleShowCentroid(self):
		self.params['showCentroid'] = not self.params['showCentroid']

	def toggleDrawContours(self):
		self.params['drawContours'] = not self.params['drawContours']

	def toggleShowTxt(self):
		self.params['showTxt'] = not self.params['showTxt']

	def toggleShowBoundingRect(self):
		self.params['showBoundingRect'] = not self.params['showBoundingRect']

	def toggleShowMeasure(self):
		self.params['measure'] = not self.params['measure']

	def toggleShowMask(self):
		self.params['showMask'] = not self.params['showMask']

	def getColorRanges(self):
		return self.color.getColorRanges()

	def setColorRanges(self, colores):
		return self.color.setColorRanges(colores)
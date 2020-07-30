class TrackableObject:
	def __init__(self, objectID, centroid, poli, bbox, color):
		self.objectID = objectID
		self.centroids = [centroid]
		self.poli = poli
		self.bbox = bbox
		self.color = color
		self.counted = False

	def getCentroidX(self):
		return self.centroids[0][0]

	def getCentroidY(self):
		return self.centroids[0][1]

	def setCentroid(self, centroid):
		self.centroids = [centroid]

	def setPoligon(self, poli):
		self.poli = poli

	def setBoundingBox(self, bbox):
		self.bbox = bbox

	def setColor(self, color):
		self.color = color

	def setForma(self, forma):
		self.forma = forma

	def setMedida(self, medida):
		self.medida = medida

	def setCounted(self):
		self.counted = True

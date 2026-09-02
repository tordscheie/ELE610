#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ../ELE610/py3/testImageTools.py
#
# Use: ..\py3>python testImageTools.py
# Use: ..\py3>python -m unittest testImageTools.TestImageTools.test_01  
#
#  Functions for testing and demonstration of funImageTools.py.
#  Some more tests should be made here!
#
#  A brief overview is:
#  test_01  Test of np2qimage and qimage2np
#  test_02  Test of myOpenImageFile and qimage2np (may plot)
#  test_03  Test of loadArr and saveArr
#  test_04  Test of getImageBlocks
#  test_05  Test of smoothFilter
#  test_myOpenImageFile
#  test_loadArr
#  test_saveArr 
#
#  Karl Skretting, UiS, April 2026

makePlots = False

# common:
import sys
from pathlib import Path  # https://docs.python.org/3/library/pathlib.html 
import numpy as np
from scipy.io import loadmat, savemat
import unittest
import warnings 
import time
import tempfile

# from math import isclose  # ceil, floor, hypot, sqrt, 
if makePlots:  
	import matplotlib.pyplot as plt
#
# Qt is used to read a file (QImage)
from mySystem import QT_BINDING, qt5Exist, qt6Exist, qtChartExist    # , gpxPath 
if QT_BINDING == "None":
	print("Importing Qt failed, some functions from funImageTools will fail, others may work.")
else: # ok
	from mySystem import QImage, QImage_Format_Indexed8, QImage_Format_Grayscale8, QImage_Format_RGB32

# by KS:
from mySystem import findMyImageFile 
from funImageTools import (myOpenImageFile, loadArr, saveArr, qimage2np, np2qimage, 
  is_url, getImageBlocks, neighborhoodBlock, smoothFilter)
from funMyTools import printArray

# *** The unit test class
class TestImageTools(unittest.TestCase):
	""" to do all tests, methods starting with 'test' 
	(py11) C:/../py3>python testImageTools.py
	"""

	def test_01(self):
		print("\ntest_01  Test of np2qimage and qimage2np")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		B = np.array([[0,0,0,0,10,100,10,0,0,0,255,255],
					  [0,0,0,0,10,100,10,0,0,0,255,255],
					  [0,0,0,0,10,100,10,0,0,0,255,255],
					  [10,10,10,10,20,110,20,10,10,10,255,255],
					  [100,100,100,100,110,200,110,100,100,100,255,255],
					  [10,10,10,10,20,110,20,10,10,10,255,255],
					  [0,0,0,0,10,100,10,0,0,0,255,255],
					  [0,0,0,0,10,100,10,0,0,0,255,255],
					  [0,0,0,0,10,100,10,0,0,0,255,255]],dtype=np.uint8)   # 9x12
		#
		print(f"  B is np.ndarray of {B.dtype.name}, {B.shape=}") 
		#
		print("Make qim from B using np2qimage")
		qim = np2qimage(B)
		if isinstance(qim, QImage) and (not qim.isNull()):
			print(f"  the returned qim has format {qim.format()}," + \
				  f" height {qim.height()} and width {qim.width()}") 
		else:
			print(f"  qim = np2qimage(B)  -> {str(qim)=}")
		#
		print("Make numpy.ndarray C from qim using qimage2np")
		C = qimage2np(qim)
		if isinstance(C, np.ndarray):
			print(f"  C is np.ndarray of {C.dtype.name}, {C.shape=}") 
		#
		print("  Test if C[:,:,0] == B and this is " + ("True" if (C[:,:,0] == B).all() else "NOT True"))
		#
		C = np.zeros((9,12,3), dtype=np.uint8)
		C[:,:,0] = B
		C[:,:,1] = B
		C[:,:,2] = B
		x,y = 4,2
		C[y,x,:] = [240,120,25]   # RGB 
		print(f"\nA new C is a np.ndarray of {C.dtype.name}, {C.shape=}") 
		print(f"  C[{y=}, {x=}, :] = {C[y,x,:]} (r,g,b)")
		#
		print("Make qim from C using np2qimage")
		qim = np2qimage(C)
		if isinstance(qim, QImage) and (not qim.isNull()):
			print(f"  the returned qim has format {qim.format()}," + \
				  f" height {qim.height()} and width {qim.width()}") 
			col = qim.pixelColor(x, y)
			(r,g,b,a) = (col.red(), col.green(), col.blue(), col.alpha())
			print(f"  For pixel (x,y) = ({x},{y}):  (r,g,b,a) = ({r},{g},{b},{a})")
		else:
			print(f"  qim = np2qimage(C)  -> {str(qim)=}")
		#
		print("Make numpy.ndarray D from qim using qimage2np")
		D = qimage2np(qim)
		print(f"  D is np.ndarray of {D.dtype.name}, {D.shape=}") 
		print(f"  D[{y=}, {x=}, :] = {D[y,x,:]}")  
		#
		print("Test if D[:,:,2] == C[:,:,0] and this is " + ("True" if (D[:,:,2] == C[:,:,0]).all() else "NOT True"))
		print("Test if D[:,:,0] == C[:,:,0] and this is " + ("True" if (D[:,:,0] == C[:,:,0]).all() else "NOT True"))
		# printArray(C[:,:,0], "C[:,:,0]", format_num='%4d ', maxN=12)
		# printArray(D[:,:,0], "D[:,:,0]", format_num='%4d ', maxN=12)
		#
		imFile = "kart1.png"
		if Path(imFile).is_file():
			print(f"\nOpen file {imFile} as QImage object")
			qim = QImage(imFile)
			if isinstance(qim, QImage) and (not qim.isNull()):
				print(f"The image qim has format {qim.format()}, height {qim.height()} and width {qim.width()}") 
				print(f"This can be converted to RGB32 and the to numpy")
				qim = qim.convertToFormat(QImage_Format_RGB32)
				print(f"The converted image qim has format {qim.format()}, height {qim.height()} and width {qim.width()}") 
				A = qimage2np(qim)
				if isinstance(A, np.ndarray):
					print( f"  A is np.ndarray of {A.dtype.name}, shape {A.shape}." ) 
	
	
	def test_02(self):
		print("\ntest_02  Test of myOpenImageFile and qimage2np")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		imNames = [ "lena.bmp", 
		            "https://www.ux.uis.no/sigproc/textures/brodatz/Nat-5c_1.pgm",
		            "noImage.png" ]
		#
		for imName in imNames:
			print(f".. Do myOpenImageFile({imName})") 
			qimg = myOpenImageFile(imName) 
			if isinstance(qimg, QImage) and (not qimg.isNull()):
				fP = Path(imName)
				print(f".. Read file {fP.name} as QImage with size width={qimg.width()}, hight={qimg.height()}")
				A = qimage2np(qimg)
				print(f".. Converted image to numpy format {A.ndim=}, {A.shape=}, {A.dtype=}")
				print(f".. Range for pixels in A ({imName}) is from {A.min()} to {A.max()}")
				if makePlots:
					plt.figure(figsize=(7, 7))
					# line below works for uint8 and float64 
					plt.imshow(A, cmap='gist_grey')
					plt.suptitle("Image " + fP.name, fontsize=16)
					plt.show()
				else:
					if A.ndim == 2:
						formatNum = '%4d ' if A.dtype==np.uint8 else '%8.3f '
						printArray(A, "Image A", format_num=formatNum, maxN=10)
			elif isinstance(qimg, QImage): 
				print(f".. Image {imName} was not read, myOpenImageFile() returned Null QImage object")
			else:
				print(f".. Image {imName} was not read, myOpenImageFile() returned {str(qimg)}")
				self.assertTrue(False, ".. myOpenImageFile() should always return a QImage")
	
	
	def test_03(self):
		print("\ntest_03  Test of loadArr and saveArr")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		fNames = [ "temp.mat",       # will be made in test,  temp.npy or temp.mat  
		           "https://www.ux.uis.no/~karlsk/dle/bestDforAR1.mat",
		           "C:/jobdata/bestDforAR1.mat",
		           "lena.bmp" ]
		#
		# first store a numpy array
		(h,w) = (50,75)    # not factors of 8
		rng = np.random.default_rng()
		A = rng.normal(loc=0.0, scale=1.0, size=(h,w))
		fP = Path.cwd() / fNames[0]
		saveArr(fP, A)
		#
		for fName in fNames:
			print(".. Do loadArr('" + fName + "')") 
			B = loadArr(fName)    #  or  B = loadArr(Path(fName))    # or 
			if isinstance(B, np.ndarray) and (B.size):
				print(f".. Read file {fName} as numpy array with {B.size=},  {B.shape=}")
				if B.shape == A.shape:
					# check that A and B are (almost) equal in L pixels [row,col]
					L = 100
					for (row,col) in zip(np.random.randint(0,h,L),np.random.randint(0,w,L)):
						self.assertEqual(A[row,col],B[row,col])
					print(".. Array B is equal to array A")
			else:
				print(f".. File {fName} was not read, loadArr() returned {str(B)}")
			#
	
	
	def test_04(self):
		print("\ntest_04  Test of getImageBlocks")  
		# simple example:
		A = np.reshape(range(9*8),(9,8)).astype(np.uint8)  
		print("A = np.reshape(range(9*8),(9,8)).astype(np.uint8) # Important: A is uint8") 
		print("X = getImageBlocks(A) # --> X[row,col] is (A[pixels]-128)/128")
		X = getImageBlocks(A)
		Y = getImageBlocks(A, nHood='d', L=-1)  
		if Y.shape == X.shape:
			L = 100
			for (row,col) in zip(np.random.randint(0,Y.shape[0],L),np.random.randint(0,Y.shape[1],L)):
				self.assertEqual(Y[row,col],X[row,col])
			print("Y = getImageBlocks(A, nHood='d', L=-1)    # --> Y == X")
		block = neighborhoodBlock('d')   # 5x5 block 13 nonzeros
		print("block = neighborhoodBlock('d')  # make the (bool) block")
		Y = getImageBlocks(A, nHood=block, L=-1)  
		if Y.shape == X.shape:
			L = 100
			for (row,col) in zip(np.random.randint(0,Y.shape[0],L),np.random.randint(0,Y.shape[1],L)):
				self.assertEqual(Y[row,col],X[row,col])
			print("Y = getImageBlocks(A, nHood=block, L=-1)  # --> Y == X")
		#
		# printArray(block, "block", format_num='%4d ', maxN=12)
		# printArray(A, "A", format_num='%4d ', maxN=12)
		# printArray(X, "X", format_num='%6.2f ', maxN=12)
		# printArray(X*128+128, "X*128+128", format_num='%6.2f ', maxN=12)
	
	
	def test_05(self):
		print("\ntest_05  Test of smoothFilter")
		# warnings.filterwarnings('ignore')  # or 'default', 'always', 'once'
		b = smoothFilter(5)
		if isinstance(b, np.ndarray):
			print(f"  smoothFilter(5) return b as np.ndarray of {b.dtype.name}, shape {str(b.shape)}") 
			print( "  returned values are: (" + " ".join([f"{x:.4f}" for x in b]) + ")")
	
	# tests from CoPilot
	def test_myOpenImageFile(self):
		"""Test that myOpenImageFile can load a simple PNG image and rejects invalid files."""
		# Create a temporary directory
		with tempfile.TemporaryDirectory() as tmp:
			tmp = Path(tmp)

			# Create a tiny 2×2 RGB image using QImage
			img_path = tmp / "test.png"
			qimg = QImage(2, 2, QImage_Format_RGB32)
			qimg.fill(0xFF0000)  # red
			qimg.save(str(img_path))

			# Load it using your function
			qimg2 = myOpenImageFile(str(img_path))
			self.assertFalse(qimg2.isNull(), "myOpenImageFile failed to load a valid PNG")

			# Try loading a non‑image file
			bad_path = tmp / "not_image.txt"
			bad_path.write_text("hello")
			qimg3 = myOpenImageFile(str(bad_path))
			self.assertTrue(qimg3.isNull(), "myOpenImageFile should return Null QImage for invalid file")

	def test_saveArr(self):
		"""Test saving arrays as .npy, .mat, and dict-of-arrays as .npz."""
		with tempfile.TemporaryDirectory() as tmp:
			tmp = Path(tmp)

			arr = np.arange(6).reshape(2, 3)

			# --- Test .npy ---
			npy_path = tmp / "a.npy"
			ok = saveArr(npy_path, arr)
			self.assertTrue(ok, "saveArr failed to save .npy")
			self.assertTrue(npy_path.exists())
			arr2 = np.load(npy_path)
			self.assertTrue(np.array_equal(arr, arr2))

			# --- Test .mat ---
			mat_path = tmp / "b.mat"
			ok = saveArr(mat_path, arr)
			self.assertTrue(ok, "saveArr failed to save .mat")
			data = loadmat(mat_path)
			self.assertIn("array", data)
			self.assertTrue(np.array_equal(arr.T, data["array"]))

			# --- Test .npz (dict of arrays) ---
			npz_path = tmp / "c.npz"
			d = {"A": arr, "B": arr + 10}
			ok = saveArr(npz_path, d)
			self.assertTrue(ok, "saveArr failed to save .npz")
			with np.load(npz_path) as z:
				self.assertTrue(np.array_equal(z["A"], arr))
				self.assertTrue(np.array_equal(z["B"], arr + 10))

	def test_loadArr(self):
		"""Test loading .npy, .mat, .npz, and image files."""
		with tempfile.TemporaryDirectory() as tmp:
			tmp = Path(tmp)

			# --- Test .npy ---
			arr = np.arange(12).reshape(3, 4)
			npy_path = tmp / "a.npy"
			np.save(npy_path, arr)
			arr2 = loadArr(str(npy_path))
			self.assertTrue(np.array_equal(arr, arr2))

			# --- Test .mat ---
			mat_path = tmp / "b.mat"
			savemat(mat_path, {"X": arr.T})
			arr3 = loadArr(str(mat_path))
			self.assertTrue(np.array_equal(arr, arr3))

			# --- Test .npz ---
			npz_path = tmp / "c.npz"
			np.savez(npz_path, A=arr, B=arr + 5)
			d = loadArr(str(npz_path))
			self.assertIsInstance(d, dict)
			self.assertTrue(np.array_equal(d["A"], arr))
			self.assertTrue(np.array_equal(d["B"], arr + 5))

			# --- Test image loading ---
			img_path = tmp / "img.png"
			qimg = QImage(3, 3, QImage_Format_RGB32)
			qimg.fill(0x00FF00)  # green
			qimg.save(str(img_path))

			arr_img = loadArr(str(img_path))
			self.assertIsInstance(arr_img, np.ndarray)
			self.assertEqual(arr_img.shape[0], 3)
			self.assertEqual(arr_img.shape[1], 3)

			# --- Test invalid file ---
			bad_path = tmp / "bad.txt"
			bad_path.write_text("not an array")
			arr_bad = loadArr(str(bad_path))
			self.assertEqual(arr_bad.size, 0, "loadArr should return empty array on failure")

#end of class TestImageTransform

if __name__ == '__main__':
    unittest.main()


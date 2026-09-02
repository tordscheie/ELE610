#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# ../ELE610/py3/funImageTools.py 
#  Functions here use Qt, QImage.load(), (or PIL) to read images, OpenCV is not used.
#  In OpenCV context functions in funMyGetData.py or bf_tools.py may be more relevant
#
#  Contains a small class:
#    FileLike           handle, mainly parse, a string as Path or URL
#  The main functions here are:
#    is_url             return True if string is a valid URL
#    qimage2np          convert image from QImage format to numpy 
#    np2qimage          convert image from numpy to QImage format
#    myOpenImageFile    open image from file, or URL, and return a QImage object
#    loadArr            load a numpy array from a file and return the largest array
#    saveArr            save a numpy array into a file given by fP, a Path object 
#    getImageBlocks     returns a matrix X with blocks (as rows in X) from image
#    neighborhoodBlock  returns the bool array for the letter-code, 'a'-'h', used as nHood
#  Other functions, mainly for internal use here (but may be imported and used in other files)
#    extract_L_blocks_using_mask 
#    extract_all_blocks 
#    blocks_to_image
#    scale_to_interval  
#    smoothFilter
#
#  Two common image transforms (dct2D and the 7/9-wavelet lwt97) should be in funImageTransform.py
#
# Karl Skretting, UiS, February 2019, November 2020 (need Python 3.6 ->), June 2022
#    January 2024:  minor updates 
#    October 2025:  use mySystem.py and simplified functions
#    December 2025: added myOpenImageFile, (and renamed this file from myImageTools.py to funImageTools.py)
#    February 2026: removed functions cv_plot and mpl_plot (they are both in bf_tools.py)
#    April 2026:    Use qimage2ndarray to convert between QImage and numpy, and more functions added
#    May 2026:      Rewritten myOpenImageFile, loadArr and saveArr (with help from CoPilot)

# Example on how to use file:
#   >>> from funImageTools import myOpenImageFile, qimage2np, np2qimage, 
#   >>> from funImageTools import getImageBlocks
#   (qtenv310) C:\..\py3>python testImageTools.py   # test

import sys
import tempfile
from io import BytesIO
from pathlib import Path  # https://docs.python.org/3/library/pathlib.html 
from urllib.parse import urlparse
import requests           # import urllib.request    # may be used insteaad of requests 
import numpy as np
from scipy.io import loadmat, savemat 
try:
	import qimage2ndarray
	_use_qimage2ndarray_package = True
except:
	print("Could not import qimage2ndarray, --> simpler and flawed(!) functions are used instead.")
	_use_qimage2ndarray_package = False  
	# then define (the simpler and flawed!) functions in the end of this file
	# Note these don't always work, but is better that notthing

# qimage2ndarray may give problems using Qt5 or Qt6 if both are installed
# The one found, may not match the one that is (should be) used ???
# I had to change default to 'PyQt6' (from 'PyQt5') in line 65 in
# "C:\Users\2900780\AppData\Local\anaconda3\envs\qtenv310\lib\site-packages\qimage2ndarray\qt_driver.py" 
# to make it work for Qt6, but will it then work when I use Qt5 (in other Anacoda environments)
# File funImageTools_feb26.py has code that (in some cases) works without qimage2ndarray

# Qt is used to read a file (QImage)
from mySystem import QT_BINDING, qt5Exist, qt6Exist, qtChartExist    # , gpxPath 
if QT_BINDING == "None":
	print("Importing Qt failed, some functions from funImageTools will fail, others may work.")
else: # ok
	from mySystem import QImage, QImageReader, QImage_Format_Indexed8, QImage_Format_Grayscale8, QImage_Format_RGB32

# by KS
from mySystem import findMyImageFile  # , pathDB
from funMyTools import printArray
try:
	from funImageTransform import dct2D, lwt97
	imTransformOK = True
except:
	imTransformOK = False

emptyArray = np.array([])
qtReadFormats = tuple( f".{fmt.data().decode('ascii').lower()}" for fmt in QImageReader.supportedImageFormats())
# see: https://doc.qt.io/qt-6/qpixmap.html#reading-and-writing-image-files 
# qtReadFormats = ('.bmp', '.cur', '.gif', '.ico', '.jfif', '.jpeg', '.jpg', 
# 				 '.pbm', '.pgm', '.png', '.ppm', '.svg', '.svgz', '.xbm', '.xpm')

def is_url(s:str):
	try:
		result = urlparse(s)
		return all([result.scheme, result.netloc])
	except ValueError:
		return False
	except:
		return False


# CoPilot suggested a class to solve Path and URL problems
# i.e.  str( Path(goodURLstr) ) is not good URL string
class FileLike:
	"""A small class to 'merge' some Path properties and functions to 
	similar properties for an URL. 
	"""
	def __init__(self, s:str):
		self.original = s
		self.is_url = is_url(s)  #   = "://" in s   # i.e. looks_like_url
		if self.is_url:
			self.url = urlparse(s)
			self.path = None
		else:
			self.path = Path(s)
			self.url = None

	# --- Path-like properties ---
	@property
	def name(self):
		return self.url.path.split("/")[-1] if self.is_url else self.path.name

	@property
	def suffix(self):
		return Path(self.name).suffix

	@property
	def parent(self):
		if self.is_url:
			parent_path = "/".join(self.url.path.split("/")[:-1])
			return FileLike(f"{self.url.scheme}://{self.url.netloc}{parent_path}")
		return FileLike(str(self.path.parent))

	# --- Path-like methods ---
	def exists(self):
		if self.is_url:
			try:
				r = requests.head(self.original, allow_redirects=True, timeout=5)
				return r.status_code < 400
			except:
				return False
		# 
		return self.path.exists()

	def is_dir(self):
		if self.is_url:
			return False  # URLs don't have directories in the filesystem sense
		return self.path.is_dir()

	def read_bytes(self):
		if self.is_url:
			r = requests.get(self.original)
			r.raise_for_status()
			return r.content
		#
		return self.path.read_bytes()

	def __str__(self):
		return self.original

	def __repr__(self):
		return f"FileLike({self.original!r})"
# end class FileLike 

if _use_qimage2ndarray_package: 
	# The alternative case is in the end
	def qimage2np(qimg): 
		"""Convert QImage to numpy array
		OBS! for RGBA or BGRA here, R and B may be swapped 
		"""
		if isinstance(qimg, QImage) and (not qimg.isNull()):
			A = qimage2ndarray.byte_view(qimg)       # QImage → NumPy  
			if (qimg.format() == QImage_Format_RGB32) and (A.ndim == 3) and (A.shape[2] == 4):
				# print("qimage2np(): Swap R and B components")
				A = A[:,:,[2,1,0,3]]  
			#else: 
			#	print(f"qimage2np():  {qimg.format() = }")
			if (A.ndim == 3) and (A.shape[2] == 1):
				A = A.squeeze(-1)
		else:
			A = np.array([], dtype=np.uint8)  
		#
		return A

	def np2qimage(A, outFile=sys.stdout):
		"""Convert numpy image of dtype np.uint8 to QImage
		"""
		if isinstance(A, np.ndarray) and (A.dtype == np.uint8):
			qimg = qimage2ndarray.array2qimage(A)   # NumPy → QImage
		else:
			print("np2qimage(): given argument A is not a numpy array of dtype np.uint8", file=outFile)
			qimg = QImage()
		#
		return qimg

else:  #  not _use_qimage2ndarray_package:
	# Then fallback to methods that often works but for many cases not
	def qimage2np(qimg): 
		"""Convert QImage to numpy array
		"""
		if isinstance(qimg, QImage) and (not qimg.isNull()):
			# A = qimage2ndarray.byte_view(qimg)       # QImage → NumPy
			if (A.ndim == 3) and (A.shape[2] == 1):
				A = A.squeeze(-1)
			# to do memory mapping directly may work (or sometimes not)
			(w, h) = (qimg.width(), qimg.height())
			bytes_per_line = qimg.bytesPerLine() # OBS this may not be w
			# CoPilot may help with more formats
			if (qimg.format() == QImage_Format_Grayscale8) and (w > 0) and (h > 0):
				ptr = qimg.bits()         # Get the raw bytes from the image 
				ptr.setsize(bytes_per_line * h)        # Ensure the correct size
				# Convert to NumPy array
				A = np.frombuffer(ptr, dtype=np.uint8).reshape((h, bytes_per_line))
			elif (qimg.format() == QImage_Format_RGB32) and (w > 0) and (h > 0):
				ptr = qimg.bits()             # Get the raw bytes from the image 
				ptr.setsize(bytes_per_line * h)        # Ensure the correct size
				# ptr.setsize(h * w * 4)        # 4 bytes per pixel (ARGB32)
				# Convert to NumPy array
				A = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 4))
				A = A[:,:,:3]  # and leave out alpha channel
			elif (w > 0) and (h > 0):
				print(f"qimage2np(): This function is not yet prepared for format {qimg.format()}")
				A = np.zeros((h,w),dtype=np.uint8)   
			else: 
				print(f"qimage2np(): No image or image has no pixels, {h=}, {w=}")
				A = np.array([], dtype=np.uint8)  
		else:
			A = np.array([], dtype=np.uint8)  
		#
		return A

	def np2qimage(A, outFile=sys.stdout):
		"""Convert numpy image of dtype np.uint8 to QImage
		"""
		if isinstance(A, np.ndarray) and (A.dtype == np.uint8):
			# qimg = qimage2ndarray.array2qimage(A)   # NumPy → QImage
			# to a QImage object of format Grascale8 or RGB32
			# This is not trivial, numpy memory lauout is difficult, and what works sometimes
			# may otherwise not work.
			# See: https://numpy.org/doc/stable/reference/arrays.ndarray.html#internal-memory-layout-of-an-ndarray 
			# What appears to be error here may be an error in qimage2np() !
			print(f"np2qimage(): A has {A.ndim=}, {A.shape=}, {A.nbytes=}, {A.dtype=}", file=outFile)
			print(f"   {A.strides=},  {A.flags['CARRAY']=},  {A.itemsize=},  {A.base=}", file=outFile)
			if (A.ndim == 2):
				if not A.flags['CARRAY']:  # hmmm, is this the problem
					A = A.copy()
					print(f"   Try copy array to itself: A has {A.ndim=}, {A.shape=}, {A.nbytes=}, {A.dtype=}")
					print(f"   {A.strides=},  {A.flags['CARRAY']=},  {A.itemsize=},  {A.base=}")
					# ex: A.strides=(A.shape[1], 1),  A.flags['CARRAY']=True,  A.itemsize=1,  A.base=None
				A = np.ascontiguousarray(A)
				height, width = A.shape    # bytes_per_line = width = A.strides[0]
				qimg = QImage(A.data, width, height, width, QImage_Format_Grayscale8).copy()
				# qimg = QImage(A.data, width, height, A.strides[0], QImage_Format_Grayscale8).copy()
				#  ((width + 3) // 4) * 4  ??
			elif (A.ndim == 3) and (A.shape[2] == 3):  
				# Add alpha channel (255 = fully opaque)
				height, width = A.shape[:2]
				imgRGBA = np.zeros((height, width, 4), dtype=np.uint8)
				imgRGBA[:, :, :3] = A
				imgRGBA[:, :, 3] = 255
				# Create QImage
				qimg = QImage(imgRGBA.data, width, height, 4*width, QImage_Format_RGB32).copy()
				# qimg = QImage(imgRGBA.data, width, height, QImage_Format_RGB32).copy()
			elif (A.ndim == 3) and (A.shape[2] == 4):  
				height, width = A.shape[:2]
				qimg = QImage(A.data, width, height, 4*width, QImage_Format_RGB32).copy()
			else:
				print("np2qimage(): given argument A is not 2D (grayscale) or 3D (RGB)", file=outFile)
				qimg = QImage()
			#
		else:
			# print("np2qimage(): given argument A is not a numpy array of dtype np.uint8")
			qimg = QImage()
		#
		return qimg
	
# end   #  _use_qimage2ndarray_package:

def is_writable_file(outFile):
	return (
		hasattr(outFile, "write") and
		callable(outFile.write) and
		not getattr(outFile, "closed", False)
	)

def myOpenImageFile(fName: str, outFile=sys.stdout):
	"""Open the image file (if possible) and return it as a QImage object
	The file may also be an URL, ex: "https://www.ux.uis.no/sigproc/textures/brodatz/Nat-5c_1.pgm"
	The image format should be given by file extension, and if this is 
	included in Qt (qtReadFormats) then QImage.load() open the image.
	Some other formats can be opened as well:
	  '.ras'-file  is read by PIL, 
	  '.npy'-file  or 
	  '.mat'-file  are first read as array and may then be transformed into QImage instance and returned.
	Any error or exception should simply return a Null QImage object 
	Write (error or exceptions or simple) messages to outFile if it is writable
	
	There are some special adaptions to my system here. 
	The function findMyImageFile is used to locate the image file in a directory I may use. 

	Arguments:
	  fName      name of image file, str or Path
	  outFile    a writable file may be given for log output, default sys.stdout 
	             None can be used to ignore printing messages 
	"""
	
	def writeLog(msg):
		if is_writable_file(outFile):
			try:
				outFile.write("myOpenImageFile(): " + msg + "\n")
			except Exception:
				pass   # silently ignore write errors

	writeLog(f"started, {fName=}")
	qimg = QImage()

	# Normalize input
	if isinstance(fName, Path):
		fName = str(fName)
	if not isinstance(fName, str):
		writeLog("fName is not a string -> return null QImage")
		return qimg

	fN = FileLike(fName)
	suffix = fN.suffix.lower()
	
	# ------------------------------------------------------------
	# STEP 1: Load raw bytes (from URL or file)
	# ------------------------------------------------------------
	raw_bytes = None

	if fN.is_url:
		writeLog(f"Reading URL via requests: {fName}")
		try:
			r = requests.get(fName)
			r.raise_for_status()
			raw_bytes = r.content
		except requests.RequestException as e:
			writeLog(f"Error fetching URL: {e}")
			return qimg
	else:
		# Local file: find it
		fPath = findMyImageFile(fName)
		writeLog(f"Local file resolved to: {fPath}")

		if not fPath.is_file():
			writeLog(f"File not found: {fPath}")
			return qimg

		try:
			raw_bytes = fPath.read_bytes()
		except OSError as e:
			writeLog(f"Error reading file: {e}")
			return qimg

	# ------------------------------------------------------------
	# STEP 2: Interpret bytes based on suffix
	# ------------------------------------------------------------

	# Case A: Qt can read it directly
	if suffix in qtReadFormats:
		if qimg.loadFromData(raw_bytes):
			writeLog(f"Loaded via QImage.loadFromData(), size=({qimg.width()},{qimg.height()})")
			return qimg
		else:
			writeLog("QImage.loadFromData() failed")
			return qimg

	# Case B: Sun Raster (.ras) via PIL
	if suffix == ".ras":
		try:
			from PIL import Image
			img = Image.open(BytesIO(raw_bytes))
			writeLog(f"PIL loaded .ras: format={img.format}, size={img.size}, mode={img.mode}")

			# Convert PIL -> PNG -> QImage
			temp = BytesIO()
			img.save(temp, format="PNG")
			if qimg.loadFromData(temp.getvalue()):
				return qimg
			else: 
				writeLog(f"Failed to load image data for '{fName}' using QImage.loadFromData()")
		except Exception as e:
			writeLog(f"  Error reading .ras: {e}")
		return qimg

	# Case C: NumPy arrays (.npy / .mat)
	if suffix in (".npy", ".mat"):
		try:
			with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
				tmp.write(raw_bytes)
				tmp_path = tmp.name
			# Now the file is closed -> safe to load
			arr = loadArr(tmp_path, outFile=outFile)
		except Exception as e:
			writeLog(f"Error reading array file: {e}")
			return qimg
		finally:
			if tmp_path:
				try:
					Path(tmp_path).unlink()
				except Exception:
					pass

		if arr.size == 0 or arr.ndim not in (2, 3):
			writeLog("Array is not an image")
			return qimg

		# Convert NumPy -> QImage
		try:
			qimg = np2qimage(arr.astype(np.uint8), outFile=outFile)
			return qimg
		except Exception as e:
			writeLog(f"Error converting array to QImage: {e}")
			return qimg

	# Unknown format
	writeLog(f"Unknown or unsupported format: {suffix}")

	return qimg

def loadArr(fP, outFile=sys.stdout):
	"""Load a numpy array from a local file or URL, fP is str or Path. 
	Always returns an array (emptyArray on failure).
	Write (error or exceptions or simple) messages to outFile if it is writable
	"""

	def writeLog(msg):
		if is_writable_file(outFile):
			try:
				outFile.write("loadArr(): " + msg + "\n")
			except Exception:
				pass   # silently ignore write errors

	# ------------------------------------------------------------
	# STEP 0 — Normalize input
	# ------------------------------------------------------------
	if isinstance(fP, Path):
		fName = str(fP)
	elif isinstance(fP, str):
		fName = fP
	else:
		writeLog(f"loadArr(): invalid type {type(fP)} — expected str or Path")
		return emptyArray

	fN = FileLike(fName)
	suffix = fN.suffix.lower()
	writeLog(f"started, {fName=}")
	
	# ------------------------------------------------------------
	# STEP 1 — Load raw bytes (URL or local)
	# ------------------------------------------------------------
	raw_bytes = None

	if fN.is_url:
		writeLog(f"fetching URL {fName}")
		try:
			r = requests.get(fName)
			r.raise_for_status()
			raw_bytes = r.content
		except requests.RequestException as e:
			writeLog(f"error fetching URL: {e}")
			return emptyArray
	else:
		# Local file
		fPath = Path(fName)
		if not fPath.exists():
			writeLog(f"file not found: {fPath}")
			return emptyArray
		try:
			raw_bytes = fPath.read_bytes()
		except OSError as e:
			writeLog(f"error reading file: {e}")
			return emptyArray

	# ------------------------------------------------------------
	# STEP 2 — Interpret bytes based on suffix
	# ------------------------------------------------------------

	# A) .npy
	if suffix == ".npy":
		try:
			# np.load requires a file-like object or filename
			arr = np.load(BytesIO(raw_bytes), allow_pickle=False)
			return arr
		except Exception as e:
			writeLog(f"failed to load .npy: {e}")
			return emptyArray

	# B) .pkl / .pickle
	if suffix in (".pkl", ".pickle"):
		try:
			obj = pickle.loads(raw_bytes)
		except Exception as e:
			writeLog(f"failed to unpickle: {e}")
			return emptyArray

		# Normalize to array
		if isinstance(obj, np.ndarray):
			return obj

		candidates = []
		if isinstance(obj, dict):
			candidates = obj.values()
		elif isinstance(obj, (list, tuple, set)):
			candidates = obj

		arrays = [a for a in candidates if isinstance(a, np.ndarray)]
		if arrays:
			return max(arrays, key=lambda a: a.size)

		writeLog("pickle contained no numpy arrays")
		return emptyArray

	# C) .npz
	if suffix == ".npz":
		try:
			npz = np.load(BytesIO(raw_bytes))
			result = {k: npz[k] for k in npz.files}
			writeLog(f"loaded .npz with {len(result)} arrays")
			return result
		except Exception as e:
			writeLog(f"failed to load .npz: {e}")
			return emptyArray

	# D) .mat
	if suffix == ".mat":
		try:
			# Create temp file but DO NOT keep it open
			with tempfile.NamedTemporaryFile(suffix=".mat", delete=False) as tmp:
				tmp.write(raw_bytes)
				tmp_path = tmp.name  # store path
			# Now the file is closed -> Windows allows loadmat to open it
			data = loadmat(tmp_path)
		except Exception as e:
			writeLog(f"failed to load .mat: {e}")
			return emptyArray
		finally:
			if tmp_path:
				try:
					Path(tmp_path).unlink()
				except Exception:
					pass

		# Extract largest array
		best = emptyArray
		best_size = 0
		for k, v in data.items():
			if isinstance(v, np.ndarray) and v.size > best_size:
				best = v.T
				best_size = v.size
				# log(f"loadArr(): using data['{k}'].T, size={v.size}, shape={v.T.shape}")
		if best_size == 0:
			writeLog("'.mat' file contained no usable arrays")

		return best

	# E) Image formats -> use myOpenImageFile
	if suffix in qtReadFormats or suffix == '.ras':
		writeLog(f"trying to load image {fName}")
		qimg = myOpenImageFile(fName, outFile=outFile)
		if qimg.isNull():
			writeLog("image load failed (QImage is null)")
			return emptyArray
		arr = qimage2np(qimg)
		if arr.size == 0:
			writeLog("qimage2np returned empty array")
		return arr

	# Unknown format
	writeLog(f"unsupported file type: {suffix}")
	return emptyArray


def saveArr(fP, arr, outFile=sys.stdout):
	"""Save a numpy array to a .mat or .npy file, or a dict to .npz file
	fP is Path, or str, object for a file that can be written into
	Returns True on success, False on failure.
	Write (error or exceptions or simple) messages to outFile if it is writable
	"""

	def writeLog(msg):
		if is_writable_file(outFile):
			try:
				outFile.write("saveArr(): " + msg + "\n")
			except Exception:
				pass   # silently ignore write errors

		return False

	# ------------------------------------------------------------
	# Normalize filename
	# ------------------------------------------------------------
	if isinstance(fP, str):
		fP = Path(fP)
	elif not isinstance(fP, Path):
		writeLog(f"Error — fP has invalid type {type(fP)}")
		return False

	# ------------------------------------------------------------
	# Validate array
	# ------------------------------------------------------------
	if isinstance(arr, np.ndarray):
		writeLog(f"Saving array of size {arr.size}, shape {arr.shape}")
	elif isinstance(arr, dict):
		# Force .npz suffix
		if fP.suffix.lower() != ".npz":
			writeLog(f"Input is a dict -> changing suffix to '.npz'")
			fP = fP.with_suffix(".npz")
		# Validate contents
		for key, value in arr.items():
			if not isinstance(value, np.ndarray):
				writeLog(f"ERROR: dict value for key '{key}' is not a numpy array")
				return False
		writeLog(f"Saving dict of {len(arr)} arrays.")
	else:
		writeLog("Error — 'arr' is not a numpy array or dict of arrays")
	
	# Add default suffix
	if fP.suffix == "":
		writeLog("No suffix provided -> using '.npy'")
		fP = fP.with_suffix(".npy")

	# Warn if overwriting
	if fP.exists():
		writeLog(f"Warning: {fP} exists and will be overwritten")

	suffix = fP.suffix.lower()
	# ------------------------------------------------------------
	# Save as .mat
	# ------------------------------------------------------------
	if suffix == ".mat":
		try:
			mdict = {"array": arr.T}   # how we like it here
			savemat(str(fP), mdict)
			writeLog(f"Saved .mat file: {fP}")
			return True
		except Exception as e:
			writeLog(f"ERROR writing .mat file: {e}")
			return False

	# ------------------------------------------------------------
	# Save as .npy
	# ------------------------------------------------------------
	if suffix == ".npy":
		try:
			np.save(fP, arr)
			writeLog(f"Saved .npy file: {fP}")
			return True
		except Exception as e:
			writeLog(f"ERROR writing .npy file: {e}")
			return False

	# ------------------------------------------------------------
	# Save as .npz
	# ------------------------------------------------------------
	if suffix == ".npz":
		if isinstance(arr, dict):
			try:
				np.savez(fP, **arr)
				writeLog(f"Saved .npz file with {len(arr)} arrays: {fP}")
				return True
			except Exception as e:
				writeLog(f"ERROR writing .npz file: {e}")
				return False
		else:
			writeLog("ERROR: saving .npz requires a dict of arrays")
			return False

	# ------------------------------------------------------------
	# Unsupported suffix
	# ------------------------------------------------------------
	writeLog(f"ERROR: Unsupported file suffix '{suffix}'")
	return False


def getImageBlocks(img, nHood='d', L=100, dtype=np.float64, verbose=0, norm=False, outFile=sys.stdout):
	"""Get a set of vectors from an image, each vector is from a pixel neighborhood or a block of the image.
	The block can also be the dct coefficients or the 3-level 7/9-wavelet transform coefficients. 
	
	Input and output arguments:
	img    A numpy array for the image, or
	       a QImage object for the image, or
	       a str or Path element giving path to where image is stored, or 
	       a list of objects as above
	       For now only grayscale images is expected, and dtype uint8
	nHood  The kind of neighborhood around a image pixel, it may be given as 
	       a string in ('a',..,'h') as in neighborhoodBlock() 
	       a string in ('8x8', 'dct', 'wt3') for non-overlapping 8x8 blocks (N=64) from image
	         or dct coefficients or the 3-level 7/9-wavelet transform coefficients
	         In this case blocks are non-overlapping, and argument L is ignored, for
	         each image nofVec = (imArr.shape[0]//8)*(imArr.shape[1]//8) vectors will be returned.
	       a block, i.e. a small 2D numpy (bool) array that indicate block mask
	L      target number of blocks to return
	       L = -1 gives maximum number of vectors from image: L(w,h,e) = (w-2e)*(h-2e), 
	       This argument is ignored when (nHood in ('8x8', 'dct', 'wt3'))
	dtype  The desired data-type for the returned array X
	       ex: numpy.float64 (default), alternative may be numpy.uint8
	norm   if True each vector in X is normalized ||x||_2=1, default False
	X      returned numpy 2D array, X.shape==(L,N), in some cases X.shape[0] < target L 
	       if anything goes wrong a message is printed to outFile and X is an empty array.
	"""
	if isinstance(img, list): 
		if L < 0:
			print(f"getImageBlocks(): WARNING: L<0 and {len(img)} images gives huge number of vectors.", file=outFile)
			imgL = -1   
		else:
			imgL = L // len(img)  # the number of blocks from each image
		X = np.array([])
		for thisImg in img:
			if (X.size == 0):
				X = getImageBlocks(thisImg, nHood, imgL, dtype=dtype, verbose=verbose, norm=norm, outFile=outFile)
			else: 
				Y = getImageBlocks(thisImg, nHood, imgL, dtype=dtype, verbose=verbose, norm=norm, outFile=outFile)
				if (Y.shape[1] == X.shape[1]):
					X = np.vstack((X, Y))
			# 
		return X
	#
	if isinstance(img, (str, Path)):
		img = myOpenImageFile(str(img), outFile=outFile)  # img becomes a QImage object 
	#
	if isinstance(img, QImage) and (not img.isNull()):
		if verbose:
			print(f"getImageBlocks(): convert 'img' from QImage (h={img.height()}, w={img.width()}) to a numpy array", file=outFile)
		img = qimage2ndarray.byte_view(img) 
		if verbose: 
			if isinstance(img, np.ndarray):
				print(f"getImageBlocks(): 'img' a numpy array {img.shape=}, {img.dtype=}", file=outFile)
			else:
				print(f"getImageBlocks(): qimage2ndarray.byte_view() failed to return a numpy array", file=outFile)
	#
	if not (isinstance(img, np.ndarray) and img.size):
		if verbose: 
			print(f"getImageBlocks(), input 'img' not as expected", file=outFile)
		return np.array([])
	#
	if (img.ndim == 3):
		if verbose: 
			print(f"getImageBlocks(): input 'img' has {img.shape[2]=} --> use img[:,:,0]", file=outFile)
		img = img[:,:,0]
		
	if (img.dtype == np.uint8):
		if verbose: 
			print(f"getImageBlocks(): scale uint8 image, use (img-128)/128", file=outFile)
		img = (img.astype(np.float64)-128)/128
	else: 
		print(f"getImageBlocks(): image is not dtype uint8 -> no scaling or translation.", file=outFile)
	#
	if isinstance(nHood, str) and nHood in ('8x8', 'dct', 'wt3'):
		(Hi, Wi) = img.shape
		if (Hi%8 > 0) or (Wi%8 > 0):
			Hi = 8*(Hi//8)
			Wi = 8*(Wi//8)
			img = img[:Hi,:Wi]  
			print(f"getImageBlocks(): 'img' adjusted to {img.shape=}, {img.dtype=}", file=outFile)
	#
	if isinstance(nHood, np.ndarray) and (nHood.ndim == 2):  # nHood is the mask
		X = extract_L_blocks_using_mask(img, L, nHood)
	elif isinstance(nHood, str) and (nHood in ('a','b','c','d','e','f', 'g', 'h')):
		mask = neighborhoodBlock(nHood) 
		X = extract_L_blocks_using_mask(img, L, mask)
	elif isinstance(nHood, str) and (nHood in ('3x3', '4x4', '5x5', '6x6', '7x7', '8x8')):
		X = extract_all_blocks(img, int(nHood[0]))
	elif isinstance(nHood, str) and (nHood == 'dct'):
		if imTransformOK:
			X = extract_all_blocks( dct2D(img) )
		else:
			print(f"getImageBlocks(), 2D dct transform was not imported as expected", file=outFile)
			return np.array([])
	elif isinstance(nHood, str) and (nHood == 'wt3'):
		if imTransformOK:
			X = extract_all_blocks( lwt97(img,3) )
		else:
			print(f"getImageBlocks(), 7/9-wavelet transform was not imported as expected", file=outFile)
			return np.array([])
	else:
		print(f"getImageBlocks(), input {nHood=} is not as expected", file=outFile)
		return np.array([])
	#
	# print(f"Range for pixels in X is from {X.min()} to {X.max()}", file=outFile)
	if X.size and not (dtype == None) and (X.dtype != dtype): 
		X = X.astype(dtype)
	#
	if X.size and norm:
		xNorm = np.sqrt((X**2).sum(axis=1))
		X = X/np.repeat(xNorm,N).reshape(X.shape)
		if verbose: 
			print(f"After normalization X is from {X.min()} to {X.max()}", file=outFile)
	#
	return X


def neighborhoodBlock(kind: str):
	""" Get a 2D numpy bool array defining a neighborhood around the center pixel.
	The block can be used to find feature vectors (from images) to be used in
	dictionary learning for image segmentation.
	The 'kind' is as in the Matlab 'makevector.m' function on 
	https://www.ux.uis.no/~karlsk/tct/, i.e. one (lowercase) letter
		'a'    N=9,  3x3 block 
		'b'    N=25, 5x5 block
		'c'    N=29, 9x9 block - most of corners, 
		'd'    N=13, 3x3 block + 4 pixels (5x5 block - 12 corner pixels)
		'e'    N=21, 5x5 block - 4 corner pixels
		'f'    N=25, 7x7 block - 24 corner pixels ('e' + 4 pixel)
		'g'    N=17, 7x7 block - most of corners
		'h'    N=9,  5x5 block - 16 pixel (a pluss pattern)  
	"""
	if kind == 'a':
		block = np.array([[1,1,1], 
		                  [1,1,1], 
		                  [1,1,1]], dtype=bool)
	elif kind == 'b':
		block = np.array([[1,1,1,1,1], 
		                  [1,1,1,1,1], 
		                  [1,1,1,1,1], 
		                  [1,1,1,1,1], 
		                  [1,1,1,1,1]], dtype=bool)
	elif kind == 'c':
		block = np.array([[0,0,0,0,1,0,0,0,0], 
		                  [0,0,0,0,1,0,0,0,0], 
		                  [0,0,0,1,1,1,0,0,0], 
		                  [0,0,1,1,1,1,1,0,0], 
		                  [1,1,1,1,1,1,1,1,1], 
		                  [0,0,1,1,1,1,1,0,0], 
		                  [0,0,0,1,1,1,0,0,0], 
		                  [0,0,0,0,1,0,0,0,0], 
		                  [0,0,0,0,1,0,0,0,0]], dtype=bool)
	elif kind == 'd':
		block = np.array([[0,0,1,0,0], 
		                  [0,1,1,1,0], 
		                  [1,1,1,1,1], 
		                  [0,1,1,1,0], 
		                  [0,0,1,0,0]], dtype=bool)
	elif kind == 'e':
		block = np.array([[0,1,1,1,0], 
		                  [1,1,1,1,1], 
		                  [1,1,1,1,1], 
		                  [1,1,1,1,1], 
		                  [0,1,1,1,0]], dtype=bool)
	elif kind == 'f':
		block = np.array([[0,0,0,1,0,0,0], 
		                  [0,0,1,1,1,0,0], 
		                  [0,1,1,1,1,1,0], 
		                  [1,1,1,1,1,1,1], 
		                  [0,1,1,1,1,1,0], 
		                  [0,0,1,1,1,0,0], 
		                  [0,0,0,1,0,0,0]], dtype=bool)
	elif kind == 'g':
		block = np.array([[0,0,0,1,0,0,0], 
		                  [0,0,0,1,0,0,0], 
		                  [0,0,1,1,1,0,0], 
		                  [1,1,1,1,1,1,1], 
		                  [0,0,1,1,1,0,0], 
		                  [0,0,0,1,0,0,0], 
		                  [0,0,0,1,0,0,0]], dtype=bool)
	elif kind == 'h':
		block = np.array([[0,0,1,0,0], 
		                  [0,0,1,0,0], 
		                  [1,1,1,1,1], 
		                  [0,0,1,0,0], 
		                  [0,0,1,0,0]], dtype=bool)
	else:
		raise ValueError("neighborhoodBlock(): argument 'kind' not a valid string; not in 'a'-'h'.")
	#
	return block

def extract_L_blocks_using_mask(imArr, L, mask):
	"""Extract neighborhood around L pixels in imArr and return a 2D array of shape (L,N)
	L will be smaller or equal to the input argument targetL
	Special case, L < 0  -> all blocks returned 
	"""
	def ensure_2d_array(arr, name):
		if not isinstance(arr, np.ndarray):
			raise TypeError(f"{name} must be a NumPy array, but got {type(arr)}")
		if arr.ndim != 2:
			raise ValueError(f"{name} must be 2‑dimensional, but has {arr.ndim} dimensions")
		
	ensure_2d_array(imArr, "imArr")
	ensure_2d_array(mask, "mask")
	(h,w) = imArr.shape
	(hB,wB) = mask.shape
	maxL = (w-wB+1)*(h-hB+1)
	N = np.count_nonzero(mask)
	if L < 0:
		L = maxL
	else:
		L = min(L, maxL) 
	#
	if (L > 0):
		X = np.zeros((L,N),dtype=imArr.dtype)
		#
		if L == maxL:
			# [j,i] should be upper left pixel of patch
			I = range(w-wB+1)   # not center pixel: range((wB-1)//2,w-wB//2)   
			J = range(h-hB+1)   #                   range((hB-1)//2,h-hB//2)
		else:
			imgLx = int(np.sqrt(L*w/h))  # check for max?
			imgLy = int(np.sqrt(L*h/w))
			if ((imgLy*imgLx) < L) and (imgLx < (w-wB+1)): imgLx += 1
			if ((imgLy*imgLx) < L) and (imgLy < (h-hB+1)): imgLy += 1
			I = np.argsort(np.random.rand(w-wB+1))[:imgLx]  # x (width) 
			J = np.argsort(np.random.rand(h-hB+1))[:imgLy]  # y (height) 
		# (y,x) is upper left corner of each possible overlapping blocks 
		row = 0
		for y in J: 
			for x in I: 
				block = imArr[y:(y+hB),x:(x+wB)]
				if (N == mask.size):
					X[row,:] = block.flatten()
				else:
					X[row,:] = block[mask.nonzero()].flatten()
				row += 1
				if row >= L: break 
			#
			if row >= L: break 
		#
	else:
		X = np.array([])
	#
	return X


def extract_all_blocks(imArr, block_size=8):
	"""Copilot answer to: I  want to extract all non-overlapping 8-by-8 blocks from imArr, 
	a numpy array of shape (h,w) that represent an image. 
	Pixels at the right or bottom edge may be left out. 
	The 8-by-8 blocks should be ordered as a row vector and returned in a matrix X of shape (L,64). 
	Can you give Python code for this.
	KS added the ndim==2 check.   Kan bli feil for H != W ???    Test: 
	from funImageTools import extract_all_blocks
	A = 100 * (np.arange(50)[:, None] + 1) + (np.arange(64) + 1)
	B = extract_all_blocks(A)   # B ser riktig ut! shape (48,64)
	"""
	if (imArr.ndim == 2):
		h, w = imArr.shape
		# Compute how many full blocks fit
		H = (h // block_size) * block_size
		W = (w // block_size) * block_size
		# Crop to the largest region divisible by block_size
		cropped = imArr[:H, :W]
		# Reshape into blocks
		blocks = cropped.reshape(H // block_size, block_size, W // block_size, block_size)
		# Move block indices to first two axes, then flatten each block
		blocks = blocks.transpose(0, 2, 1, 3).reshape(-1, block_size * block_size)
	else:
		blocks = np.array([])
	#
	return blocks


def blocks_to_image(X, h, w, block_size=8):
	"""Again from Copilot:
	Reconstruct the cropped image from block matrix X.
	h, w = original image dimensions (before cropping)
	KS added the ndim==2 check
	"""
	if (X.ndim == 2):
		# Compute how many full blocks fit
		H = (h // block_size) * block_size
		W = (w // block_size) * block_size

		# Number of blocks along each dimension
		nH = H // block_size
		nW = W // block_size

		# Reshape X back into (nH, nW, block_size, block_size)
		blocks = X.reshape(nH, nW, block_size, block_size)

		# Reassemble into image
		imArr = blocks.transpose(0, 2, 1, 3).reshape(H, W)
	else:
		imArr = np.array([])
	#
	return imArr


def smoothFilter(len=3):
	"""Return a small simple low-pass FIR filter with given length (3,5,7 or 9)
	"""
	if (len == 3):
		a = np.array([1,2,1])/4
	elif (len == 5):
		a = np.array([1,4,6,4,1])/16
	elif (len == 7):
		a = np.array([1,4,6,6,6,4,1])/28
	elif (len == 9):
		a = np.array([1,4,6,8,8,8,6,4,1])/46
	else:			
		a = np.array([1,2,1])/4
	#
	return a 


def scale_to_interval(X, a, b, verbose=0, outFile=sys.stdout):
	if isinstance(X, np.ndarray) and X.size and (X.dtype == np.float64):
		X_min = X.min()
		X_max = X.max()
		if verbose:
			print(f"** Scale X,  {a=}, {b=}, {X_min=:.3f}, {X_max=:.3f}, {X.shape=} **", file=outFile)
		X = (X - X_min) / (X_max - X_min) * (b - a) + a 
	else:
		if verbose:
			print(f"** Scale X,  {a=}, {b=} but X not as it is supposed to be **", file=outFile)
	#
	return X



def funTest(X,a=0.75):
	# typically a = 0.75, 
	x1 = X.min()
	x4 = X.max()
	x2 = a*x1+(1-a)*x4
	x3 = (1-a)*x1+a*x4
	mask = (X >= x2) & (X <= x3)
	print(f"Andel i X mellom {x2:.3f} og {x3:.3f} er {np.mean(mask):.3f}")

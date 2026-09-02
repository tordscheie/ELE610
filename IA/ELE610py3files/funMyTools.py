#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# ../ELE610/py3/funMyTools.py
#  Some (general) functions that may be used in my python files 
#
#  Functions: argsort               as numpy argsort, here on a list 
#             rounded_range         return (c,d) from (a,b) where c,d have 2 significant digits, c<a<b<d
#             printArray            print a numpy array
#             printValueName        print value (variable) and name (a given string)
#             printElements, whos   print the the elements of a variable
#             uniqueRandomKinL      numpy array of K unique integers, each in range(L) 
#             dictionaryProperties  print and return dictonary (2D array) general properties
#             closest_factors       return (a,b) where a <= b, and a*b=N, and a as large as possible
#             make_circle           return smallest enclosing circle of points as rows in a 2D numpy array
#    
#  Karl Skretting, UiS, March 2025
#  KS Dec. 2025: added dictionaryProperties and corrected some errors 
#  KS Feb. 2026: many functions can print to file (stream?), not only sys.stdout
#  KS Apr. 2026: add statistics for print of 1D array
#  KS May  2026: function is_url moved to funImageTools 

_fileName = "funMyTools.py"
_author = "Karl Skretting, UiS"  
_version = "2026-05-07"             # "yyyy-mm-dd"

# common:
import sys
from pathlib import Path  # https://docs.python.org/3/library/pathlib.html 
import re 
from math import ceil, floor, hypot, isqrt, log10
import numpy as np
import random

def argsort(seq):
	""" Returns the indices that would sort 'seq' similar to np.argsort()
	if 'seq' is not sortable this function tries to sort on str(element)
	return 'idx' as a list of integers, where: (seq[idx[i]] <= seq[idx[i+1]])
	"""
	#  just skip unsortable items
	# def safe_argsort(lst):
		# sortable = []
		# for i, x in enumerate(lst):
			# try:
				# _ = x < x  # test comparability
				# sortable.append(i)
			# except TypeError:
				# pass
		# return sorted(sortable, key=lst.__getitem__)
	# try sorting as strings
	try:
		idx = sorted(range(len(seq)), key=seq.__getitem__)
	except:  
		sseq = []
		for s in seq: 
			try:
				sseq.append(str(s))
			except:
				print(f"argsort(): Ignore element {s}")
			#
		#
		idx = sorted(range(len(sseq)), key=sseq.__getitem__)
		# reverse: ... , reverse=True)
	#
	return idx
	
def rounded_range(a, b):
	if a >= b:
		raise ValueError("Range must have non-zero width and a < b")
	# Width of the original range
	w = b - a
	# Determine scale for two significant digits
	scale = 10 ** (floor(log10(w)) - 1)
	# Round outward
	c = floor(a / scale) * scale
	d = ceil(b / scale) * scale
	return c, d


def printArray(X, name='printArray(X,..): X is', format_num=None, maxN=10, outFile=sys.stdout):  
	""" Print ndim and shape of ndarray and some elements (if ndim <= 2)
	the function should work for dtype.kind in "biuf" (not in "cmMOSUV")
	arguments:   X - a numpy array
	          name - just a string that is printed, usually the name of the numpy array
	    format_num - Number format for array elements, a string like "%10.6f "
	          maxN - max number of elements to print in each dimension,  default 10
	                 If there is more than maxN elements in any dimension then
	                 the int((maxN-2)/2) first and last elements for that dimension is printed  
	                 if maxN == 0 only one line is printed (no values)
	       outFile - where to print may be given, default is sys.stdout (as in print function)
	                 if this is str or Path, output is written to this file (not append) 
	                 and file is opened first and closed after
	  
	ex:  from funMyTools import printArray
	     printArray(X[:22,1].T, maxN=16, format_num='%6.3f ')
	     printArray(img[500:600,800:900,1],'img[500:600,800:900,1]',format_num='%3i ',maxN=20)
	"""
	if isinstance(outFile, (str, Path)):
		with open(outFile, 'w') as f:
			printArray(X, name=name, format_num=format_num, maxN=maxN, outFile=f)
	else:
		if not (type(X) == np.ndarray):
			print(f"{name} is not a numpy array, {type(X)=}", file=outFile)  
			return
		#
		if (maxN <= 0):
			print(f"{name} is a numpy array with ndim={X.ndim}, shape={X.shape}, dtype={X.dtype}", file=outFile)
			return
		#
		print( f"{name} ndim={X.ndim}, shape={X.shape}, dtype={X.dtype}, and values are:", file=outFile)
		#
		# see: https://numpy.org/doc/stable/reference/generated/numpy.dtype.kind.html#numpy.dtype.kind 
		if X.size and (X.dtype.kind in "biuf"):   # the prepared data types
			v_min = np.min(X)
			v_max = np.max(X)
			if (format_num == None):
				if (X.dtype.kind == 'b'):
					format_num = "%d "
				elif (X.dtype == np.uint8):
					format_num = "%3d "
				elif (X.dtype == np.int8):
					format_num = "%4d "
				elif (X.dtype.kind == 'i'):
					length = ceil(np.log10(max(1+v_max.astype(np.float64),1-v_min.astype(np.float64)))) + 1
					format_num = f"%{length:d}d "
				elif (X.dtype.kind == 'u'):
					length = ceil(np.log10(1+v_max.astype(np.float64))) + 1
					format_num = f"%{length:d}d "
				else: # (X.dtype.kind == 'f'):
					if (v_max >= 100000) or (v_min <= -10000):
						format_num = "%10.1f "
					if (v_max >= 1000) or (v_min <= -100):
						format_num = "%10.3f "
					else:
						format_num = "%10.6f "
				# end each data type b,i,u,f
			# end if (format_num == None)
			format_string = 'Minimum value = ' + format_num + '  maximum value = ' + format_num
			print(format_string % (v_min, v_max), file=outFile)
			#
			# a prepared data type and format_num is given or set above
			if (X.ndim == 1): _printArray1D(X, format_num, maxN, outFile=outFile)
			if (X.ndim == 2): _printArray2D(X, format_num, maxN, outFile=outFile)
			if (X.ndim > 2): print(X, file=outFile)  # ignore format_num
			#
		else: #  (X.dtype.kind in "cmMOSUV"):   
			print(X, file=outFile)  # will do, ignore format_num
		#
	return
#end of def printArray(X, name)

def _printArray1D(X, fmt, maxN, outFile=sys.stdout):
	maxN2 = int((maxN-2)/2)
	N = X.shape[0]
	if (N <= maxN):
		format_string = '  [' + (fmt*N) + ']'
		print(format_string % tuple(X.tolist()), file=outFile)
	else:
		format_string = '  [' + (fmt*maxN2) + ' ... ' + (fmt*maxN2) + ']'
		print(format_string % tuple(X[:maxN2].tolist() + X[-maxN2:].tolist()), file=outFile)
		format_string = '  min = ' + fmt + ', mean = ' + fmt + ', max = ' + fmt
		print(format_string % (X.min(), X.mean(), X.max()), file=outFile)
	return

def _printArray2D(X, fmt, maxN, outFile=sys.stdout):
	(L,N) = X.shape
	if (L == 1): 
		_printArray1D(X[0,:], fmt, maxN, outFile=outFile)
	else:  # X has two or more rows
		maxN2 = int((maxN-2)/2)
		# first row
		if (N <= maxN):
			format_string = '  [' + (fmt*N)
			print(format_string % tuple(X[0,:].tolist()), file=outFile)
		else:
			format_string = '  [' + (fmt*maxN2) + ' ... ' + (fmt*maxN2)
			print(format_string % tuple(X[0,:maxN2].tolist() + X[0,-maxN2:].tolist()), file=outFile)
		#end if
		#
		# middle rows
		if (L <= maxN):
			if (N <= maxN):
				format_string = '   ' + (fmt*N)
				for k in range(1,L-1):
					print(format_string % tuple(X[k,:].tolist()), file=outFile)
			else:
				format_string = '   ' + (fmt*maxN2) + ' ... ' + (fmt*maxN2)
				for k in range(1,L-1):
					print(format_string % tuple(X[k,:maxN2].tolist() + X[k,-maxN2:].tolist()), file=outFile)
			#
		else:
			if (N <= maxN):
				format_string = '   ' + (fmt*N)
				for k in range(1,maxN2):
					print(format_string % tuple(X[k,:].tolist()), file=outFile)
				print('     ... ', file=outFile)
				for k in range(-maxN2,-1):
					print(format_string % tuple(X[k,:].tolist()), file=outFile)
			else:
				format_string = '   ' + (fmt*maxN2) + ' ... ' + (fmt*maxN2)
				for k in range(1,maxN2):
					print(format_string % tuple(X[k,:maxN2].tolist() + X[k,-maxN2:].tolist()), file=outFile)
				print('     ... ', file=outFile)
				for k in range(-maxN2,-1):
					print(format_string % tuple(X[k,:maxN2].tolist() + X[k,-maxN2:].tolist()), file=outFile)
			#
		#
		# last row
		if (N <= maxN):
			format_string = '   ' + (fmt*N) + ']'
			print(format_string % tuple(X[-1,:].tolist()), file=outFile)
		else:
			format_string = '   ' + (fmt*maxN2) + ' ... ' + (fmt*maxN2) + ']'
			print(format_string % tuple(X[-1,:maxN2].tolist() + X[-1,-maxN2:].tolist()), file=outFile)
		#end if
		row_2norms = np.sqrt((X*X).sum(axis=1))
		normalized = (abs(min(row_2norms) - 1.0) + abs(max(row_2norms) - 1.0)) < 1e-8
		fmt2 = "%10.3f "
		if normalized:
			print("\nAll rows are normalized, i.e. 2-norm is 1.", file=outFile)
		else:
			print(f"\nRow 2-norms are: (min={row_2norms.min():.3f}, mean={row_2norms.mean():.3f}, " + \
			      f"max={row_2norms.max():.3f})", file=outFile)
			_printArray1D(row_2norms, fmt2, maxN, outFile=outFile)
		row_1norms = np.sum(np.abs(X), axis=1)
		print(f"Row 1-norms are: (min={row_1norms.min():.3f}, mean={row_1norms.mean():.3f}, " + \
		      f"max={row_1norms.max():.3f})", file=outFile)
		_printArray1D(row_1norms, fmt2, maxN, outFile=outFile)
		row_counts = np.count_nonzero(X, axis=1)
		if (np.sum(row_counts) < 0.65*X.size):
			m1 = row_counts.min()
			m3 = row_counts.max()
			if (m1 < m3):
				m2 = row_counts.mean()
				print(f"Non-zeros in each row are: (min={m1}, mean={m2:.3f}, max={m3})", file=outFile)
			else:
				print(f"All rows have S={m1} non-zeros", file=outFile)
	#end if
	return
	
def printValueName(v, name, outFile=sys.stdout):
	""" Print a variable name, type and (part of) its value.
	Only one line is used, up to nameLen=20 chars for name 
	Arguments are:
	v      the actual variable, i.e. the value  
	name   should be a string, usually the name of the variable
	"""
	nameLen = 20   
	if not ((type(name) == str) and len(name)):
		raise ValueError("printValueName(): argument 'name' not a string with len(name)")
	#
	jName = name[:min(nameLen,len(name))].ljust(nameLen)  # len(jName) == nameLen
	jType = str(type(v))[8:-2].ljust(9)             # len(jType) >= 9
	if isinstance(v, (bool,int,float,complex)):
		print(f"{jName} {jType} : {v}", file=outFile)
	elif isinstance(v, (list,dict,tuple,set)):
		print(f"{jName} {jType} : ", end='', file=outFile)
		if len(v) < 20:  # short container
			v_string = str(v)
		else:
			v_string = ''
		#
		if (len(v) < 20) and (len(v_string) < 50):
			print(v_string, file=outFile)
		else:
			print(f"{len(v)} elements", file=outFile)
	elif isinstance(v, np.ndarray):
		jDtype = (v.dtype.name+',').ljust(12)   
		print(f"{jName} ndarray of {jDtype} ndim: {v.ndim}, shape: {str(v.shape)}", file=outFile)
	elif isinstance(v, str):
		i1 = v.find('\n')
		if (i1 >= 0): 
			v1 = v[:min(i1,52)]
		else:
			v1 = v[:min(len(v),52)]
		try: 
			print(f"{jName} {jType} len={len(v):4d} : {v1} {('...' if len(v)>len(v1) else '')}", file=outFile)
		except UnicodeEncodeError:
			print('UnicodeEncodeError:  Perhaps string contains unprintable character.', file=outFile)
	else:   # (bytes, bytearray, class, ...)
		sv = " ".join(str(v).split())  # string value
		if (sv.find('\n')>=0):
			sv = sv[:sv.find('\n')] + ',..'  # only first line
		if (len(sv) > (90 - nameLen - len(jType))):  
			sv = sv[:(90 - nameLen - len(jType))] + ' ...'
		#
		try:
			i = len(v)   # not all classes has a length, may cause error
			print(f"{jName} {jType} len={i:4d} : {sv}", file=outFile)
		except:
			print(f"{jName} {jType} : {sv}", file=outFile)
	#
	return

def printElements(a=None, name='', *, show_hidden=False, mask_name='', var_type='mfv', outFile=sys.stdout):
	""" Print the the elements of a variable, typically a container,
	in a more reader friendly format than the simple: print( a ).
	Some additional arguments can be used to restrict which elements to print.
	Input:
	  a             typically a container like a list or a dict
	  name          name of variable 'a' (or any text), will be printed on first line
	  show_hidden   a boolean to indicate if hidden names, i.e. start with '_', should be included
	  mask_name     a regular expression (re) that may be given to match the name ('a' a dictionary)
	    ex: '[an]', for more see: https://docs.python.org/3/library/re.html
	  var_type      a string indicating which variable to include when 'a' is a dictionary: 
	    'm' (module), 'f' (most functions or methods), 'v' (other variables), 
	    's' (string), 'l' (list), 'd' (dict) and 'n' (numpy array)
	    'mfv' is all, 'ld' is list and dict, 'mn' is modules and numpy arrays
	  outFile - where to print may be given, default is sys.stdout (as in print function)
	    if this is str or Path, output is written to this file (not append) 
	    and file is opened first and closed after
	  
	Examples:
	printElements( aDict )
	printElements( aList )
	printElements( vars(), outFile='temp.txt')    # content in workspace to file 
	printElements()            # also content in workspace, Python version >= 3.7 
	printElements( vars(sys), show_hidden=True )  # content of 'sys'
	printElements( vars(), mask_name='[ac]' )     # content in workspace, that starts with 'a' or 'c'
	printElements( var_type='v' )                 # only variables in workspace
	"""
	if (a == None): 
		if (sys.version_info.major == 3) and (sys.version_info.minor >= 7):
			# this may also work with older versions, but I have not tested it
			a = sys._getframe(1).f_locals   
			if not len(name):
				name = "local variables in context where function is used"
		else:
			print("printElements(): use 1 argument, ex: printElements( aDict )") # warning, always to stdout
			return
	#
	if isinstance(outFile, (str, Path)):
		with open(outFile, 'w') as f:
			printElements(a, name=name, show_hidden=show_hidden, mask_name=mask_name, var_type=var_type, outFile=f)
	else:
		if not len(name): name = "argument 'a'"
		try:
			lstring = f"len()={len(a)}"
		except:
			lstring = "len() gives error"
		print(f"\nprintElements(): {name}, type()={type(a)}, {lstring}", file=outFile)
		#
		if (type(a) == dict):
			l_keys = list(a.keys())
			s_keys = []
			for k in l_keys: 
				s_keys.append(str(k))
			idx = argsort(s_keys)   # sort keys as string
			# set idx[i] = -1 if element should not be printed, thus exclude instead of include!
			for n in range(len(idx)): 
				k = l_keys[idx[n]]  # the key (in sorted order)
				s = s_keys[idx[n]]  # the key as string
				isFunc = str(type(a[k])).find('func') >= 0
				isModule = (type(a[k]) == type(sys))
				#
				if (not show_hidden) and (s[0] == '_'): idx[n] = -1
				if len(mask_name) and (not re.match(mask_name, s)): idx[n] = -2
				if (idx[n] >= 0) and ( not ( \
					 (('m' in var_type) and isModule) or \
					 (('f' in var_type) and isFunc) or \
					 (('v' in var_type) and (not (isModule or isFunc))) or \
					 (('s' in var_type) and (type(a[k]) == str)) or \
					 (('l' in var_type) and (type(a[k]) == list)) or \
					 (('d' in var_type) and (type(a[k]) == dict)) or \
					 (('n' in var_type) and (type(a[k]) == np.ndarray)) \
											  ) ):
					idx[n] = -3
				#
			#
			if ('m' in var_type):  # print modules first 
				for i in [x for x in idx if x >= 0]:
					k = l_keys[i]  # the key
					s = s_keys[i]  # the key as string
					isModule = (type(a[k]) == type(sys))
					if isModule: printValueName(a[k], s, outFile=outFile)
			if ('f' in var_type):   
				for i in [x for x in idx if x >= 0]:
					k = l_keys[i]  # the key
					s = s_keys[i]  # the key as string
					isFunc = str(type(a[k])).find('func') >= 0
					if isFunc: printValueName(a[k], s, outFile=outFile)
			# now list the other elements
			for i in [x for x in idx if x >= 0]:
				k = l_keys[i]  # the key
				s = s_keys[i]  # the key as string
				isFunc = str(type(a[k])).find('func') >= 0
				isModule = (type(a[k]) == type(sys))
				if not (isFunc or isModule): printValueName(a[k], s, outFile=outFile)
		elif (type(a) in (list,tuple,set)):
			stv = str(type(a))   # typically: <class 'type name'>
			if (len(stv) > 10):
				stv = stv[8:-2]   # only type name
			if (len(a) > 20):
				# print( f"print the 5 first and 5 last elements in input of type {stv}" )
				if (type(a) == set):  # set is not iterable
					for (element,k) in zip(a,range(len(a))):
						printValueName(element, f"element", outFile=outFile)
						if k > 10:  # maxN as argument ?
							print(' ... ', file=outFile)
							break
				else:
					for k in range(5):
						printValueName(a[k], f"element {k:6d}", outFile=outFile)
					print(' ... ', file=outFile)
					for k in [len(a)-5,len(a)-4,len(a)-3,len(a)-2,len(a)-1]:
						printValueName(a[k], f"element {k:6d}", outFile=outFile)
			else:
				# print( f"print the {len(a)} elements in input of type {stv}:" )
				if (type(a) == set):  # set is not iterable
					for (element,k) in zip(a,range(len(a))):
						printValueName(element, f"element", outFile=outFile)
				else:
					for k in range(len(a)):
						printValueName(a[k], f"element {k:6d}", outFile=outFile)
		else:
			printValueName(a, "argument 'a' is", outFile=outFile)
		#
	return
	
whos = printElements  # because I used the whos function in Matlab for many years and 
                      # the function printElements above is quite similar
	
def uniqueRandomKinL(K,L):
	""" return idx as K unique random integers each in range(L)
	idx = uniqueRandomKinL(K,L)  # idx a numpy array
	"""
	if (32*K < L):
		while True:
			idx = np.unique(np.random.randint(0,L,2*K))
			if (len(idx) >= K): break
		idx = idx[np.argsort(np.random.rand(len(idx)))][:K]
	elif (K <= L):
		idx = np.argsort(np.random.rand(L))[:K]
	else:  
		raise ValueError(f"{K=} > {L=} so K unique random integers each in range(L) is impossible.")
	#
	return idx
	
def dictionaryProperties(D, verbose=0, makeplot=False, outFile=sys.stdout):
	""" Find, print, and return some properties for matrix/dictionary/frame D
	D should be of shape (K,N) where normally K >= N (and atoms span space R^N),
	K is number of atoms and N is dimensionality.
	if verbose <= 0 don't print anything, 
	if verbose > 0 print results
	if verbose > 1 and N==16 and K==32: also plot 1D atoms 
	"""
	if not isinstance(D, np.ndarray):
		if verbose: print("dictionaryProperties(): Input D is NOT a numpy array", file=outFile)
		return {'type': type(D)}
	if (D.ndim != 2):
		if verbose: print("dictionaryProperties(): Input D is NOT a 2D array", file=outFile)
		return {'ndim': D.ndim, 'size': D.size}
	#
	(K,N) = D.shape
	atom_2norms = np.sqrt((D*D).sum(axis=1))
	normalizedD = (abs(min(atom_2norms) - 1.0) + abs(max(atom_2norms) - 1.0)) < 1e-8
	# G = D @ D.T   # Gram matrix of D, G[i,j] = cos( beta_ij ), shape: (K,K)
	# in general below, mu = cos(beta), beta is angle (in degrees) between two atoms
	# the mu and beta values should be as in my Matlab function dictprop()
	muAll = np.abs((D @ D.T) - np.eye(K)).max(axis=0)  # shape: (K,) 
	betaAll = np.arccos(muAll)*180.0/np.pi  # angle of atom to closest neighbor
	muMax = muAll.max()      # Elad called this property simply mu, cosine of smallest angle
	betaMin = betaAll.min()  # == np.arccos(muMax)*180.0/np.pi
	muAvg = muAll.mean()
	betaAvg = betaAll.mean()   # not == np.arccos(muAvg)*180.0/np.pi
	# S = D.T @ D   # frame operator, shape: (N,N)
	# as on: https://en.wikipedia.org/wiki/Frame_(linear_algebra)
	# analysis operator is left multiplication of D: D @ x, where x.shape is (N,)
	lam = np.linalg.eigvalsh(D.T @ D)
	A = lam.min()
	B = lam.max()
	muRMS = np.sqrt((lam**2).sum())/K   # should also be RMS of (all entries in) G
	betaRMS = np.arccos(muRMS)*180.0/np.pi
	#
	prop = {'K':K,             'K_text':'Number of atoms, D.shape=(K,N)', \
	        'N':N,             'N_text':'Dimensionality of atom space', \
	        'normalized':normalizedD, \
	        'lambda':lam,      'lambda_text':'Eigenvalues of frame operator (D.T @ D)', \
	        'muAll':muAll,     'muAll_text':'Cosine of angle of atom to closest neighbor', \
	        'betaAll':betaAll, 'betaAll_text':'Angle in degrees of atom to closest neighbor', \
	        'muMax':muMax,     'muMax_text':'Cosine of smallest angle between two atoms (mu)', \
	        'betaMin':betaMin, 'betaMin_text':'Smallest angle between two atoms', \
	        'muAvg':muAvg,     'muAvg_text':'Average of muAll, muAll.mean()', \
	        'betaAvg':betaAvg, 'betaAvg_text':'Average of betaAll, betaAll.mean()', \
	        'muRMS':muRMS,     'muRMS_text':'RMS of all cos(beta_ij)=np.sqrt(((D@D.T)**2).mean())', \
	        'betaRMS':betaRMS, 'betaRMS_text':'Angle in degrees for muRMS', \
	        'A':A,             'A_text':'Lower frame bound', \
	        'B':B,             'B_text':'Upper frame bound' }
	#
	if (verbose > 0): 
		print("dictionaryProperties(): ", file=outFile)
		if normalizedD:
			print("  dictionary is normalized, i.e. 2-norm of all atoms is 1.00", file=outFile)
		else:
			print("  dictionary is NOT normalized, min 2-norm for atoms is {min(atom_2norms):.3f} and max is {max(atom_2norms):.3f}", file=outFile)
		print(f"  K, N     {K}, {N}  K is number of atoms, N is dimensionality of atoms, D.shape=(K,N)", file=outFile)
		print(f"  A, B     {A:.6f}, {B:.3f}  lower and upper frame bounds", file=outFile) # , smallest and largest eigenvalues of frame operator
		print(f"  betaMin  {betaMin:6.3f}  smallest angle between two atoms [degrees]", file=outFile)
		print(f"  betaAvg  {betaAvg:6.3f}  average of smallest angles for all atoms, muAll.mean() [degrees]", file=outFile)
		print(f"  betaRMS  {betaRMS:6.3f}  angle for muRMS, average (of cosines) for all angles [degrees]", file=outFile)
		# printElements(prop,'Properties of D')
		printArray(lam, 'lambda, eigenvalues of (D.T @ D)', outFile=outFile)
		printArray(betaAll, 'betaAll [degrees], angle to closest atom', outFile=outFile)
		printArray(muAll, 'muAll, cos(betaAll)', outFile=outFile)
	#
	if (verbose > 1) and (N == 16) and (K == 32):
		import matplotlib.pyplot as plt
		plt.figure(figsize=(7, 7))
		dx = np.arange(0,N/20,1/20)
		for k in range(8): 
			for m in range(4):
				plt.plot(dx+k, 1.0*(4-m)+D[k+8*m,:], 'b-')
		plt.title( "32 atoms" )
		# plt.grid()
		# fig.savefig('temp.png')
		plt.show()
	#
	return prop
	
def closest_factors(N: int):
	"""Example: (a,b) = closest_factors(500)   # should return (20,25)  not (10,50) 
	Slow for large N, since it may count all way down from sqrt(N) to 0 (when N is prime)
	But fast for resonable small and medium sized numbers N
	"""
	N = int(N)
	if N < 4: return (1,N) # always a valid 'factorization of N
	a = isqrt(N)
	while a > 0:
		if N % a == 0: return (a, N // a)
		a -= 1
	# print(f"slow_closest_factors(): indeed slow as {N=} (prime)")
	return (1,N)

# # only relevant for (very) large numbers, CoPilot help 22/4-26
# def fermat_factor(N: int):
	# """Return (a, b) such that a*b = N using Fermat's method, a and b has same parity.
	# Return (1,N) if no such pair exists (i.e., N has no same-parity factors).
	# """
	# N = int(N)
	# if N <= 1: return (1,N)  # always a valid 'factorization of N
	# x = isqrt(N)
	# if x * x == N: return (x, x)
	# limit = (N + 1) // 2   # as suggested by CoPilot
	# x += 1
	# while x <= limit:  # will usually return earlier
		# y2 = x*x - N
		# y = isqrt(y2)
		# if y*y == y2:
			# a = x - y
			# b = x + y
			# return (a, b)
		# x += 1
	# # x > limit, happens for all N where algorithm simply fails: 
	# # N = p (prime > 2) or N = 2*odd (2*23), 2*odd*odd (2*7*9), 2*odd*odd*odd ...
	# return (1,N)

# def closest_factors_large(N: int):
	# """Return the factor pair (a, b) of N with |a - b| minimaN,
	   # using fermat_factor() on both N and 2N, and return one of them.
	   # several wrong answers!
	# """
	# N = int(N)
	# if N < 4: 
		# return (1,N)  # always a valid 'factorization of N
	# elif N < 1000000: # not large
		# return closest_factors(N)
	# # check N
	# if (N % 2 == 0) and (N % 4 != 0):   # N is 2*odd, 
		# (a,b) = (2, N // 2)             # a valid but not good factorization
	# else:
		# (a,b) = fermat_factor(N)        # 20 -> (2,10) but (4,5) is wanted
	# # check 2*N                      
	# if N % 2 == 0:                      # N is odd   
		# (c,d) = fermat_factor(2*N)    # 
		# if d % 2 == 0:
			# d2 = d // 2
			# (a2,b2) = (min(c, d2), max(c, d2))
		# else:
			# c2 = c // 2
			# (a2,b2) = (min(c2, d), max(c2, d))
		# if (b2 - a2) < (b - a):
			# (a,b) = (a2,b2)
	# # and more
 	# a3 = isqrt(N)
	# while a3 > a:
		# if N % a3 == 0: return (a3, N // a3)
		# a3 -= 1
	# #
	# return (a,b)

# # import time
# def test_closest_factors(K):
	# mismatches = []

	# # Measure time for closest_factors()
	# t2 = time.perf_counter()
	# slow_results = [closest_factors_large(n) for n in range(1, K+1)]
	# t3 = time.perf_counter()

	# # Measure time for closest_factors()
	# t0 = time.perf_counter()
	# fast_results = [closest_factors(n) for n in range(1, K+1)]
	# t1 = time.perf_counter()

	# # Compare results
	# for n in range(1, K+1):
		# if fast_results[n-1] != slow_results[n-1]:
			# mismatches.append((n, fast_results[n-1], slow_results[n-1]))

	# # Print summary
	# print("=== Test Summary ===")
	# print(f"Total numbers tested: {K}")
	# print(f"closest_factors() time:       {t1 - t0:.6f} seconds")
	# print(f"closest_factors_large() time: {t3 - t2:.6f} seconds")

	# if mismatches:
		# print(f"\nMISMATCHES FOUND ({len(mismatches)}):")
		# for n, fast, slow in mismatches:
			# print(f"N={n}: closest_factors={fast}, slow_closest_factors={slow}")
	# else:
		# print("\nAll results match perfectly!")

# # Run the test
# test_closest_factors(5000)

# 
# Smallest enclosing circle - Here modified to use numpy array
# 
# Copyright (c) 2025 Project Nayuki
# https://www.nayuki.io/page/smallest-enclosing-circle
#
# Initially: No boundary points known
def make_circle(points: np.ndarray) -> tuple[float,float,float] | None:
	"""Smallest enclosing circle of points as rows in a 2D numpy array
	input:     points: Lx2 array of floats, point i is p = (points[i,0], points[i,0])
	returns:   c, the circle as (x,y,r)
	"""
	L = points.shape[0]
	shuffled = points[np.random.permutation(L)]
	# Progressively add points to circle or recompute circle
	c = None
	for (i, p) in enumerate(shuffled):
		if c is None or not _is_in_circle(c, p):
			c = _make_circle_one_point(shuffled[ : i + 1, :], p)
	return c

# One boundary point known
def _make_circle_one_point(points: np.ndarray, p: tuple[float,float]) -> tuple[float,float,float]:
	c: tuple[float,float,float] = (p[0], p[1], 0.0)
	for (i, q) in enumerate(points):
		if not _is_in_circle(c, q):
			if c[2] == 0.0:
				c = _make_diameter(p, q)
			else:
				c = _make_circle_two_points(points[ : i + 1, :], p, q)
	return c

# Two boundary points known
def _make_circle_two_points(points: np.ndarray, p: tuple[float,float], q: tuple[float,float]) -> tuple[float,float,float]:
	circ: tuple[float,float,float] = _make_diameter(p, q)
	left : tuple[float,float,float]|None = None
	right: tuple[float,float,float]|None = None
	px, py = p
	qx, qy = q
	
	# For each point not in the two-point circle
	for r in points:
		if _is_in_circle(circ, r):
			continue
		
		# Form a circumcircle and classify it on left or right side
		cross: float = _cross_product(px, py, qx, qy, r[0], r[1])
		c: tuple[float,float,float]|None = _make_circumcircle(p, q, r)
		if c is None:
			continue
		elif cross > 0.0 and (left is None or _cross_product(px, py, qx, qy, c[0], c[1]) > _cross_product(px, py, qx, qy, left[0], left[1])):
			left = c
		elif cross < 0.0 and (right is None or _cross_product(px, py, qx, qy, c[0], c[1]) < _cross_product(px, py, qx, qy, right[0], right[1])):
			right = c
	
	# Select which circle to return
	if left is None and right is None:
		return circ
	elif left is None and right is not None:
		return right
	elif left is not None and right is None:
		return left
	elif left is not None and right is not None:
		return left if (left[2] <= right[2]) else right
	else:
		raise AssertionError("Unreachable")

def _make_diameter(a: tuple[float,float], b: tuple[float,float]) -> tuple[float,float,float]:
	cx: float = (a[0] + b[0]) / 2
	cy: float = (a[1] + b[1]) / 2
	r0: float = hypot(cx - a[0], cy - a[1])
	r1: float = hypot(cx - b[0], cy - b[1])
	return (cx, cy, max(r0, r1))


def _make_circumcircle(a: tuple[float,float], b: tuple[float,float], c: tuple[float,float]) -> tuple[float,float,float]|None:
	# Mathematical algorithm from Wikipedia: Circumscribed circle
	ox: float = (min(a[0], b[0], c[0]) + max(a[0], b[0], c[0])) / 2
	oy: float = (min(a[1], b[1], c[1]) + max(a[1], b[1], c[1])) / 2
	ax: float = a[0] - ox;  ay = a[1] - oy
	bx: float = b[0] - ox;  by = b[1] - oy
	cx: float = c[0] - ox;  cy = c[1] - oy
	d: float = (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by)) * 2.0
	if d == 0.0:
		return None
	x: float = ox + ((ax*ax + ay*ay) * (by - cy) + (bx*bx + by*by) * (cy - ay) + (cx*cx + cy*cy) * (ay - by)) / d
	y: float = oy + ((ax*ax + ay*ay) * (cx - bx) + (bx*bx + by*by) * (ax - cx) + (cx*cx + cy*cy) * (bx - ax)) / d
	ra: float = hypot(x - a[0], y - a[1])
	rb: float = hypot(x - b[0], y - b[1])
	rc: float = hypot(x - c[0], y - c[1])
	return (x, y, max(ra, rb, rc))

_MULTIPLICATIVE_EPSILON: float = 1 + 1e-14

def _is_in_circle(c: tuple[float,float,float], p: tuple[float,float]) -> bool:
	return c is not None and hypot(p[0] - c[0], p[1] - c[1]) <= c[2] * _MULTIPLICATIVE_EPSILON

# Returns twice the signed area of the triangle defined by (x0, y0), (x1, y1), (x2, y2).
def _cross_product(x0: float, y0: float, x1: float, y1: float, x2: float, y2: float) -> float:
	return (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)


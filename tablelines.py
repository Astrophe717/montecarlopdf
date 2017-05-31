"""
         |_________   tablelines  _________|
         |      |       |        |         |

Find the dimensions and positions of rectangles in a jpg or pdf.

The aim of this project is to enable better web scraping of pdfs. 
In particular, the aim is to write a script that can be used together 
with XML output from e.g. scraperwiki. 

The XML output locates the text from a pdf but does not indicate if
there are multiple layers of headers or how they span the columns.

Please see the README for more details.
"""

from PIL import Image
from itertools import combinations
from collections import Counter

# These should be settable.
im_name = "pdfs_and_images/004.pdf"
line_weight = 10
t = 5 # Tolerance - 
# used to check if two lines connect
# or come within touching distance
# specified by the number of pixels
# that is set as the value.

if im_name[-3:] =='pdf':
	# open(im_name)
	pass 
else:
	im = Image.open(im_name)
	pix = im.load()

# Find the width and length of the page, measured in pixels.
x_range, y_range = (im.size)


def px_cols(x, y): 
	"""
	Group together pixels with the same x value 
	- i.e. pixels along the same vertical line.
	
	Scan through the page left-to-right, top-to-bottom,
	constructing lists e.g.: 
	[
	[x-val1, y-val1, y-val2, y-val3,...],
	[x-val2, y-val1, y-val2, y-val3,...], 
	..
	]
	"""
	groups = []
	
	for i in range(x):
		group = [i]
			
		for j in range(y):
			if pix[i,j] == 0: # Black pixel
				group.append(j)
				
		groups.append(group)
	
	return [group for group in groups if len(group) > line_weight]  


def px_rows(x, y):
	"""
	Group together pixels with the same y value 
	- i.e. pixels along the same horizontal line.
	
	Scan through the page top-to-bottom, left-to-right,
	constructing lists e.g.: 
	[
	[y-val1, x-val1, x-val2, x-val3,...],
	[y-val2, x-val1, x-val2, x-val3,...], 
	..
	]
	"""
	groups = []
	
	for j in range(y):
		group = [j]
		
		for i in range(x):
			if pix[i,j] == 0:
				group.append(i)
				
		groups.append(group)
		
	return [group for group in groups if len(group) > line_weight] 


def v_lines(groups):
	"""Form vertical lines from the lists of grouped pixels."""
	lines = []
	for group in groups:
		y_vals = group[1:]
		
		# Ignore groups which are not clustered together
		# to form lines longer than the width of a table-line.
		if len(y_vals) > line_weight:  
			
			start = y_vals[0]
			# If there is a discontinuity in the group, 
			# store the last position of the group:
			last_y = None
			for y in y_vals:
				if last_y and y - last_y > 5:
					start = y
				last_y = y
			finish = y_vals[-1]
			# store lines in the form: ( x1, (y1, y2) )
			lines.append( (group[0], (start, finish) ) )
			
	return lines


def h_lines(groups):
	"""Form horizontal lines from the lists of grouped pixels."""
	
	lines = []
	for group in groups: # group is a list e.g. [x, y1, y2, y3, y4...]
		
		x_vals = group[1:]
		
		if len(set(x_vals)) > line_weight:
			# lineate continuous part(s) of the line.
			
			start = x_vals[0]
			
			# if pixels are not continuous in the y-direction, 
			# take the last continuous line.
			last_x = None
			for j in x_vals:
				if last_x and j - last_x > 5:
					start = j
				last_x = j
				
			finish = x_vals[-1]
	
			# store ( (x1, x2), y )
			lines.append( ( (start, finish), group[0] ) )	
			
	return lines


def filter_lines(lines):
	"""Thin out clusters of parallel lines, leaving only one."""
	last_num = None
	for idx, val in enumerate(lines):
		if isinstance( val[0], (int, long) ): # vertical line
			
			if last_num and val[0] - last_num == 1:
				lines[idx] = None # filter out None later
			last_num = val[0]
		else:
			if last_num and val[1] - last_num == 1:
				lines[idx] = None
			last_num = val[1]
			
	return filter(None, lines)


def potential_recs():
	"""
	Make all possible combinations of two horizontal lines
	and two vertical lines in the hope that some combinations 
	will form a rectangle.
	"""
	recs = []
	for i in combinations(v_limits, 2):
		for j in combinations(h_limits,2):
			limits = i[0], j[0], i[1], j[1]
			recs.append( limits )
	return recs


def validate_recs():
	"""
	Take combinations of two horizontal lines and two vetical lines
	and check if their limits join the lines together, give or take
	some t.
	"""	
	recs = []
	for i in potential_recs:
		# Check whether or not the lines form a rectangle.
		v1 = i[0], i[1], i[3] # x1, y1, y2
		v2 = i[2], i[1], i[3] # x2, y1, y2
		h1 = i[0], i[2], i[1] # x1, x2, y1
		h2 = i[0], i[2], i[3] # x1, x2, y2
		
		existing_lines = [y for y in v_flatlines if abs(v1[0]-y[0]) <= 
		t and v1[1] + t >= y[1] and v1[2] - t <= y[2]]
		if existing_lines == []:
			continue
	
		existing_lines = [y for y in v_flatlines if abs(v2[0]-y[0]) <= 
		t and v2[1] + t >= y[1] and v2[2] - t <= y[2]]
		if existing_lines == []:
			continue
	
		existing_lines = [y for y in h_flatlines if h1[0] + t >= y[0] 
		and h1[1] - t <= y[1] and abs(h1[2]-y[2]) <= t]
		if existing_lines == []:
			continue
	
		existing_lines = [y for y in h_flatlines if h2[0] + t >= y[0] 
		and h2[1] - t <= y[1] and abs(h2[2]-y[2]) <= t]
		if existing_lines == []:
			continue
	
		recs.append(i)
	
	return recs
	

# These functions are used as keys to sort the rectangles.
def height(rec):
	return rec[3] - rec[1]
	
def width(rec):
	return rec[2] - rec[0]


def separate_recs():
	"""Return all non-overlapping rectangles."""
	enclosing_recs = []
	for rec in sorted_recs:
		for x in range(rec[0] + t, rec[2] - t):
			for y in range(rec[1] + t, rec[3] - t):
				if pix[x,y] == 0:
					enclosing_recs.append( rec )
					break
	
	for rec in sorted(list(set(enclosing_recs))):
		sorted_recs.remove(rec)
		
	return sorted_recs


def see_recs():
	"""
	See the order in which non-overlapping rectangles 
	are stored/outputted. A series of images are saved to the directory
	'saved_images', each images shows a different shaded rectangle.
	"""
	count = 0
	recs = []
	for rec in sorted_recs:
		find_mode = [] # Find the mode colour i.e. the most frequently occuring.
		for x in range(x_range):
			for y in range(y_range):
				if rec[0] - t <= x <= rec[2] + t:
					if rec[1] - t <= y <= rec[3] + t:
						find_mode.append(pix[x,y])
						pix[x,y] -= 10 # shade the rectangle
						
		mode_colour = Counter(find_mode).most_common(1)[0][0] # 0 --> 255
		
		if  mode_colour == 255:
			recs.append( rec )
			im.save("saved_images/im{}.jpg".format(count))
			count += 1
			
	return recs

if __name__=="__main__":
	
	# Maybe break these nested function calls down.
	# Vertical lines have the form (x, (y1, y2))
	v_lines = filter_lines( v_lines( px_cols( x_range, y_range ) ) )
	# Horizontal lines have the form ((x1, x2), y)
	h_lines = filter_lines( h_lines( px_rows( x_range, y_range ) ) )
	
	# The lines are flattened e.g. (x, y1, y2)
	v_flatlines = [[y for x in j for y in 
		(x if isinstance(x,tuple) else (x,))] for j in v_lines]
	h_flatlines = [[y for x in j for y in 
		(x if isinstance(x,tuple) else (x,))] for j in h_lines]
	
	# Find the limits of the lines.
	v_limits = [i[0] for i in v_lines]
	h_limits = [i[1] for i in h_lines]
	
	potential_recs = potential_recs()
	
	# Sort the rectangles in order of ascending height and width.
	sorted_recs = sorted(validate_recs(), key=height)
	sorted_recs = sorted(sorted_recs, key=width)
	# At this point, sorted_recs includes all rectangles which 
	# can overlap each other in any way.
	
	for i in separate_recs(): 
		print i
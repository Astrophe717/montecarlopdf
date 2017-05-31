
         |_________   tablelines  _________|
         |      |       |        |         |

Find The Dimensions And Positions Of Rectangles In A Jpg Or Pdf.

The aim of this project is to enable better web scraping of pdfs. 
In particular, the project is for use with pdfs or jpgs where the position 
of the table-lines is needed to group text together the right way.

For example, suppose your XML output from scraperwiki looks like this:

<text top="823" left="371" width="17" height="11" font="5">11 </text>
<text top="823" left="542" width="4" height="12" font="6"> </text>
<text top="839" left="504" width="80" height="12" font="6">Growth, S.A. </text>
<text top="823" left="695" width="59" height="12" font="6">11/fev/09 </text>
<text top="855" left="371" width="17" height="11" font="5">12 </text>
<text top="855" left="542" width="4" height="12" font="6"> </text>
<text top="871" left="488" width="112" height="12" font="6">Madz Global, S.A. </text>
<text top="855" left="697" width="55" height="12" font="6">04/jul/14 </text>

So you know exactly where all the text is on your pdf but not where the 
table-lines are or if there are two sets of column headers at the top of the 
table like this:
_______________________________________________________________________
|    Heading 1       |         Heading 2           |    Heading 3     |
|____________________|_____________________________|__________________|  
|  sub 1  |  sub 2   |  sub 3 | etc.    |          |                  |
|_________|__________|________|_________|__________|__________________|
|  cell 1 |  cell 2  |        |         |          |                  |
|         |          |        |         |          |                  |
|         |          |        |         |          |                  |
|         |          |        |         |          |                  |
|         |          |        |         |          |                  |
|         |          |        |         |          |                  |

So the text is grouped in an intelligible way to the human eye but your
XML just ignored it.

The precocious teenager might argue that the XML does not give us enough 
information to do the web-scraper because we can't match the headers 
with the cells without knowing how the table-lines divide the headers.

This program laboriously checks the colour of every pixel in an image twice 
(left-to-right, top-to-bottom followed by top-to-bottom, left-to-right). 
The program expects to see black lines on a white background. It is 
possible to add a fuzz factor e.g. we can work with a pretty much white 
background and pretty much black lines. Actually any combination of 
colours would be acceptable with small changes to the code.


NOTE:
The functions have been bundled together from the original script, which 
was a long, continous code that was hard to understand.
Bundling the code into functions has made an improvement but the functions
are still dependent on one another and a function is almost certainly going 
to fail if it is imported for use in another script - the required input 
will be difficult to replicate without the use of another function.

This is very much a work in progress amd the intention is to make various 
changes and improvements. For example, some of the code is 
repetitive, the module is not configured for use with XML output from
scraperwiki and the method used to find the table-lines requires makes 
it a slow program.

All constructive ideas and contributions are greatly welcomed.

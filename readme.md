## Fast-Hough-Contour

This algorithm implements a faster Hough transform using the basic idea of the original Hough with the information provided <br>
by a contour tracing algorithm. <br> 
The contour tracing algorithm is the Moore-Neighbor algorithm. <br>
The basic idea is to avoid to generate all the possible lines for every pixel of the edge map, but instead to calculate only the lines that can really belong <br>
to the image. <br>
<b>Everything needed to understand the algorithm, from the basic idea to the implementation is explained in the <br>
"presentation.pdf" file </b>

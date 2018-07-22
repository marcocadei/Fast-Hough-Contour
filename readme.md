## Fast-Hough-Contour

This algorithm implements a faster hough transform using the basic idea of the original Hough with the information provided <br>
by a contour tracing alogirthm (in this case it was the Moore-Neighbor algorithm) in order to avoid to generate all <br>
the possible lines for every pixel of the edge map, but instead it calculates only the lines that can really belong <br>
to the image. <br>
<b>Everything needed to understand the algorithm, from the basic idea to the implementation is explained in the <br>
"presentation.pdf" file </b>

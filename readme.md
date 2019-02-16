## Fast-Hough-Contour

This algorithm implements a faster Hough transform using the basic idea of the original Hough with the information provided by a contour tracing algorithm. The contour tracing algorithm is the _[Moore-Neighbor algorithm](https://en.wikipedia.org/wiki/Moore_neighborhood)_. <br>
The idea is to avoid to generate all the possible lines for every pixel of the edge map, but instead to calculate only the lines that can really belong to the image. <br>

#### Documentation
Everything needed to understand the algorithm, from the basic idea to the implementation is explained in the <br>
"presentation.pdf" file.

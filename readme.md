## Fast-Hough-Contour

This algorithm implements a faster Hough transform using the basic idea of the original Hough with the information provided by a contour tracing algorithm. The contour tracing algorithm is the _[Moore-Neighbor algorithm](https://en.wikipedia.org/wiki/Moore_neighborhood)_. <br>
The idea is to avoid to generate all the possible lines for every pixel of the edge map, but instead to calculate only the lines that can really belong to the image. <br>

#### The trick
The idea behind the project is to keep track of the last contour's pixels and calculate the parameters only for a limited set of lines, instead of all the possible lines that pass through each point of the edge map.
![Basic idea](https://github.com/MarcoCadei/Fast-Hough-Contour/blob/master/images/intuition.png)

#### Documentation
Everything needed to understand the algorithm, from the basic idea to the implementation is explained in [this nice presentation](https://github.com/MarcoCadei/Fast-Hough-Contour/blob/master/presentation.pdf).

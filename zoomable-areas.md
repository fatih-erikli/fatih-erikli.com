The DOMMatrix interface provides us an abstraction to work with
rotation and translation of DOM or SVG elements.
<figure style="max-width: 600px;">
<img style="width: 100%;" src="example-zoomable.png">
<figcaption>An SVG document</figcaption>
</figure>

In order to show an information or a visualization which is not fitting
to the default resolutions, such as 1440x900 or 1280x720,
we need to provide an interface to the user to update the zoom
level of the content, and pan the visible region of zoomed area.
We can do that in both SVG content and HTML content.

DOMMatrix is an abstract interface for 2d and 3d operations.
In web, in most cases, we will use DOMMatrix for 2d operations.
Let's go with an example. We will create a zoomable SVG document
and a mirror version of it with some HTML controls.

### OnWheel event
In modern browsers, we can listen to the zoom gesture of user
(for example pinch gesture in OSX) by using the onwheel event. Let's start
by creating an SVG document inside HTML first.

```javascript
function App() {
  const onWheel = (event: SyntheticEvent) => {
    console.log(event);
  }
  return (
    <div className="App">
      <svg onWheel={onWheel} width={300} height={300}>
      <rect x={0} y={0} width={100} height={100} fill={'purple'} />
      <rect x={100} y={0} width={100} height={100} fill={'magenta'} />
      <rect x={200} y={0} width={100} height={100} fill={'cyan'} />

      <rect x={0} y={200} width={100} height={100} fill={'cyan'} />
      <rect x={100} y={200} width={100} height={100} fill={'magenta'} />
      <rect x={200} y={200} width={100} height={100} fill={'purple'} />
      // ....
```

And also we can subscribe to onWheel event such as the example above.

In OSX, Pinch gesture is fired by ctrlKey pressed in onWheel event. It
may sound a bit strange, but it is practical if you think about the computers
which doesn't have a trackpad.

```
const onWheel = (event: SyntheticEvent) => {
  if (event.ctrlKey) {
    event.preventDefault();
  }
}
```

We disable the default zoom behavior if the ctrl key is pressed :) It works
for OSX.

In order to transform (scale, translate-move, or rotate), we need to group our SVG elements with `g` element.

```javascript
function App() {
  const onWheel = (event: SyntheticEvent) => {
    console.log(event);
  }
  return (
    <div className="App">
      <svg ref={svgRef} onWheel={onWheel} width={300} height={300}>
      <g ref={transformableGroupRef}>
        <rect x={0} y={0} width={100} height={100} fill={'purple'} />
        <rect x={100} y={0} width={100} height={100} fill={'magenta'} />
        <rect x={200} y={0} width={100} height={100} fill={'cyan'} />

        <rect x={0} y={200} width={100} height={100} fill={'cyan'} />
        <rect x={100} y={200} width={100} height={100} fill={'magenta'} />
        <rect x={200} y={200} width={100} height={100} fill={'purple'} />
        // ....
```

And also I assigned them a reference to access them in my event listeners.
After that point, things are getting a bit complicated.

The coordinate system in DOM (HTML) and SVG differs a little bit. The coordinate
system in SVG is inverted, and also the position of the visible elements are changing
when you move them or scale.

```javascript

function convertScreenCoordsToSvgCoords(
  x: number,
  y: number,
  svgElement: SVGSVGElement,
  groupElement: SVGGraphicsElement
) {
  var point = svgElement.createSVGPoint();
  point.x = x;
  point.y = y;
  point = point.matrixTransform(groupElement.getScreenCTM()?.inverse());
  return {
    x: point.x,
    y: point.y,
  };
}
```

We can use a function like that in order to can translate those coordinates to a common which we can operate in HTML.
Basically the SVG coordinates are still the same when you scale the contents, but the positions in the
group elements are different. We are going to reach to the
coordinates in SVG element, and transform them to the group element's matrix.

We can implement our onWheel function now.

```javascript
const SCALE_FACTOR = 0.03;
// onWheel event sends numbers like 2,5,3.
// when you scale an element with 2, it becomes twice bigger than original.
// so we need to divide them with something called a scale factor.
// this is something you need to try and find. 0.03 seemed reasonable to me.

let groupTransform: DOMMatrix;
// I use typescript and defined the groupTransform with DOMMatrix object.
// let's keep it as global for now. We can think about it later.

const onWheel = (event: SyntheticEvent) => {
  const scale = event.deltaY * SCALE_FACTOR * -1;
  var coords = convertScreenCoordsToSvgCoords(
    event.clientX,
    event.clientY,
    svgRef.current,
    transformableGroupRef.current
  );

  groupTransform = groupTransform.translate(coords.x, coords.y);
  groupTransform = groupTransform.scale(1 + scale);
  groupTransform = groupTransform.translate(-coords.x, -coords.y);

  const transform = svgRef.current.createSVGTransform();
  transform.setMatrix(groupTransform);
};
```

Almost everything is done. We created a matrix that we can use
to zoom elements in an SVG document. There's one thing
needs to be done left. We need to assign that transformation
matrix to the group element.

In procedural Javascript, we set the <a target="_blank" rel="nofollow" href="https://svgwg.org/svg2-draft/types.html#__svg__SVGAnimatedString__baseVal">baseVal</a> value of element,
which stores the coordinates before any any animation is applied. But
we are using react, we need to do it in a declarative way.

We need to define a state in our function component.

```javascript
const [transformationMatrix, setTransformationMatrix] = useState<DOMMatrix>(new DOMMatrix());
// ...
const onWheel = (event: SyntheticEvent) => {
  // ...
  setTransformationMatrix(transform.matrix);
};
```

And populate the transformation matrix in onWheel event handler.

```javascript
<g
  transform={`
    matrix(
      ${transformationMatrix.a},
      ${transformationMatrix.b},
      ${transformationMatrix.c},
      ${transformationMatrix.d},
      ${transformationMatrix.e},
      ${transformationMatrix.f}
    )
  `}
  ref={transformableGroupRef}
  >
  ...
```

Also we can set the transform attribute of group element by destructuring our matrix in that way.

This is all. The DOMMatrix is pure mathematical array operations. When you initialize a new one,
you create it with the browser's norms (actual zoom). So, if you have a button like `Reset Zoom`, you can
set the `transformationMatrix` with a new DOM Matrix.

```javascript
<button onClick={event => setTransformationMatrix(new DOMMatrix());}>
  Reset zoom
  ....
```

I uploaded the actual version to github as an open-source project.

<img src="https://raw.githubusercontent.com/fatih-erikli/dark-rectangles/main/zoomable.gif" />

Here's the Github URL:

<https://github.com/fatih-erikli/dark-rectangles/>

Happy hacking! :)
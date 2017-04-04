# STL-slicer

This program makes slices on SVG files from a STL binary file (a 3D object). Thoses files could be used for laser cutters.

## How to use the program

Launch program with default parameters

```
./slicer.py file.stl
```

It is possible to change the parameters

```
./slicer.py file.stl --slices sliceNumber --axe axeID --simplify angle
```
- `sliceNumber`: Integer
- `axeID`: Integer based with this rule: Z: 0, Y: 1, X: 2
- `angle`: is the maximal angle, in degree, between segments of the border. It makes output smaller but with less details.

## Output

The program create `sliceNumber` svg file with the number of layer (from the bottom). Those files are created next to the executable.

## Special aspect

The program display the result in the terminal if it is launched from terminology.

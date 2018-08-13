# Quick SEGY #

A small Python 3.6+ library for quickly looking at SEG-Y with 
no required dependencies.

The main goal for this was to quickly extract geometry data from a
number of SEG-Y files to get shapefiles for GIS. Only does points or
convex hulls for 3D to get shapes quickly (but not necessarily accurately).

Minimal tests at this point, I just needed the thing to work quickly
to examine some data.

Quick usage example:

```python
from quicksegy import SegY2D, SegY3D

sgy2d = SegY2D('path/to/segy_file.sgy')

nav2d = sgy2d.sampled_nav(100, nav_loc='SOURCE')

sgy3d = SegY3D('path/to/3d_file.sgy')

nav3d = sgy3d.sampled_nav(500, nav_loc='GROUP')
```

### Implemented ###

    * Read standard text headers in ebcdic and ascii
    * Read binary header including new REV 2 additions
    * Overriding incorrect header values
    * Handle trace headers
    * Shapely support for geometries (point and convex for 3d)
    
### Planned Features (for v1.0) ###
    
    * Cache headers/load all headers
    * Read additional text headers
    * Handle fixed numbers of extended trace headers
    * Solid test coverage for REV 1 data
        * Full REV 2 tests depend on actually getting some REV 2 data I can use

### Maybe if I have more time ###

    * Numpy support for the array data
    * Matplotlib support to show the seismic data
    * Modifying SEG-Y File headers in place (possibly)
    
### Unsupported features (will not be supported) ###

    * Variable length data
        * Number of extended trace headers will be expected to be fixed
        * Samples per trace are assumed to be fixed
        * Scripts may at some point be provided to convert to fixed headers/sample counts
          but it will not be supported by the main classes (as it would be slow and complex)
    * Middle/Mixed endianness

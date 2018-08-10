# Quick SEGY #

A small Python 3.6+ library for quickly looking at SEG-Y with 
no required dependencies.

Minimal tests at this point, I just needed the thing to work quickly
to examine some data.

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

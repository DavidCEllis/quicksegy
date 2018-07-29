# Quick SEGY #

A small library for quickly looking at SEG-Y via random access.

Intended to support most of SEG-Y Revision 2 except for those features that make 
random access slow.

I still need test files for revision 2 as I haven't seen any 'in the wild'.

### Implemented ###

    * Read standard text headers in ebcdic and ascii
    * Read binary headers including new REV 2 additions
    * Overriding incorrect header values
    * Handle trace headers
    * Shapely support for geometries (point and convex for 3d)
    
### Planned Features (for v1.0) ###
    
    * Read additional text headers
    * Handle fixed numbers of extended trace headers
    * Solid test coverage for REV 1 data
        * Full REV 2 tests depend on actually getting some REV 2 data I can use

### Planned Features (for a later release) ###

    * Numpy support for the array data
    * Matplotlib support to show the seismic data
    * Modifying SEG-Y File headers in place (possibly)
    
### Unsupported features (will not be supported) ###

    * Variable length data
        * Number of extended trace headers will be expected to be fixed
        * Samples per trace are assumed to be fixed
        * Scripts may at some point be provided to convert to fixed headers/sample counts
          but it will not be supported by the main classes (as it would be slow and complex)
    * Middle/Mixed endianness (unless python's struct package starts supporting it)

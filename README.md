# GDB Register Viewer Plugin

This is a GDB plugin that prints register fields based on a device SVD file. Copy the script and SVD file to the same directory where GDB will be run.

```
(gdb) source register_viewer.py 
(gdb) view GPDMA1.GPDMA_C1TR1
SDW_LOG2   (bit 0 ): 0    (byte)
SINC       (bit 3 ): 0    (fixed burst)
SBL_1      (bit 4 ): 0    
PAM        (bit 11): 0    (source data is transferred as right aligned, left-truncated down to the destination data width)
SBX        (bit 13): 0    (no byte-based exchange within the unaligned half-word of each source word)
SAP        (bit 14): 0    (port 0 (AHB) allocated)
SSEC       (bit 15): 0    (GPDMA transfer non-secure)
DDW_LOG2   (bit 16): 0    (byte)
DINC       (bit 19): 1    (contiguously incremented burst)
DBL_1      (bit 20): 0    
DBX        (bit 26): 0    (no byte-based exchange within half-word)
DHX        (bit 27): 0    (no halfword-based exchanged within word)
DAP        (bit 30): 1    (port 1 (AHB) allocated)
DSEC       (bit 31): 0    (GPDMA transfer non-secure)
```

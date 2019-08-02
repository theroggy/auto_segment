# -*- coding: utf-8 -*-
"""
Script to run a training session for greenhouse segmentation.
"""

import os
# TODO: the init of this doensn't seem to work properly... should be solved somewhere else?
os.environ["GDAL_DATA"] = r"C:\Tools\anaconda3\envs\orthoseg4\Library\share\gdal"
 
# Because orthoseg isn't installed as package + it is higher in dir hierarchy, add root to sys.path
import sys
sys.path.insert(0, '.')

import orthoseg.train as train

#-------------------------------------------------------------
# The real work
#-------------------------------------------------------------

def main():
        
    # Start the training session
    scriptdir = os.path.dirname(os.path.abspath(__file__))    
    train.run_training_session(segment_config_filepaths=[os.path.join(scriptdir, 'general.ini'), 
                                                         os.path.join(scriptdir, 'greenhouses.ini'),
                                                         os.path.join(scriptdir, 'local_overrule.ini')])
    
if __name__ == '__main__':
    main()

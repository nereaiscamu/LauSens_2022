# sensus2021

The files;
  - Analyse_results is adapted from a function from 2019SensUs
  - AcquireAndDisplay is adapted from one of the example files of spinnacker of the same name, such that the last image show in the live feed is save
  - AcquireAndSave is adapted from one from AcquireAndDisplay, such that each image taken is saved
  - Select ROIs uses the CV2 to draw circles and retain the centers of these centers, use right mouse click to delete the previous circle
  - RUN file can be run on cell at a time
TO DO: 
  - Run the code on your laptop's GPU, or maybe try google collab CPU
  - Determine the threshold for the pixels
  - Find a way to determine the time between pictures
  - The images are currently being saved as -npy and re-opened for analysis
  - replace circle function with disk
  - There might be a mix up with where you select the circle with CV2 and where they are being use for the analysis
  

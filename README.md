<p align="center">
  <img src="logo/sherloq.png" width="600px" alt="Sherloq" />
  <br><b>An open source image forensic toolset</b>
</p>

# Introduction
"*Forensic Image Analysis is the application of image science and domain expertise to interpret the content of an image and/or the image itself in legal matters. Major subdisciplines of Forensic Image Analysis with law enforcement applications include: Photogrammetry, Photographic Comparison, Content Analysis, and Image Authentication.*" (Scientific Working Group on Imaging Technologies)

**Sherloq** is a personal research project about implementing a fully integrated environment for digital image forensics. It is not meant as an automatic tool that decide if an image is forged or not (that tool probably will never exist...), but as a companion in experimenting with various algorithms found in the latest research papers and workshops.

While many commercial solutions have unaffordable prices and are reserved to law enforcement and government agencies only, this toolset aims to be a powerful and extensible framework as a starting point for anyone interested in state-of-the-art forensic algorithms.

I strongly believe that *security-by-obscurity* is the wrong way to offer any kind of forensic service (i.e. "Using this proprietary software I guarantee you that this photo *is* pristine... and you have to trust me!"). Following the open-source philosophy, everyone should be able to try various techniques on their own, gain knowledge and share it to the community... even better if they contribute with code improvements! :)

# History
The first version was written in 2015 using C++11 to build a command line utility with many options, but soon it turned to be too cumbersome and not much interactive. That version could be compiled with CMake after installing OpenCV, Boost and AlgLib libraries. This first proof of concept offered about 80% of planned features (see below for the full list).

While also including novel algorithms, the 2017 version mainly added a Qt-based multi-window GUI to provide a better user experience. Multiple analyses could be shown on screen and a fast zoom/scroll  viewer was implemented for easier image navigation. That project could be compiled with Qt Creator with Qt 5 and OpenCV 3 and covered about 70% of planned features.

Fast forward to 2020 when I decided to port everything in Python (PySide2 + Matplotlib + OpenCV) for easier development and deployment. While this iteration is just begun and I have yet to port all the previous code on the new platform, I think this will be the final "form" of the project (as long as someone does not volunteer up to develop a nice web application!).

I'm happy to share my code and get in contact with anyone interested to improve or test it, but please keep in mind that this repository is *not* intended for distributing a final product, my aim is just to publicly track development of an *unpretentious educational tool*, so expect bugs, unpolished code and missing features! ;)

# Features
This list contains the functions that **Sherloq** will hopefully provide once the beta stage is reached.

## Interface
- Modern Qt-based GUI with multiple tool window management
- Support for many formats (BMP, JPEG, PNG, WebP, PGM, PFM, TIFF, GIF)
- Highly responsive image viewer with real-time panning and zooming
- Many state-of-the-art algorithms to try out interactively
- Extensive online help with tool explanations and tutorials
- Export both visual and textual analysis results

## Tools

### General
- __Original Image__: display the unaltered reference image for visual inspection
- __File Digest__: retrieve physical file information, crypto and perceptual hashes
- __Hex Editor__: open an external hexadecimal editor to show and edit raw bytes
- __Similar Search__: browse online search services to find visually similar images

### Metadata
- __Header Structure__: dump the file header structure and display an interactive view
- __EXIF Full Dump__: scan through file metadata and gather all available information
- __Thumbnail Analysis__: extract optional embedded thumbnail and compare with original
- __Geolocation Data__: retrieve optional geolocation data and show it on a world map

### Inspection
- __Enhancing Magnifier__: magnifying glass with enhancements for better identifying forgeries
- __Channel Histogram__: display single color channels or RGB composite interactive histogram
- __Global Adjustments__: apply standard image adjustments (brightness, hue, saturation, ...)
- __Reference Comparison__: open a synchronized double view for comparison with another picture

### Detail
- __Luminance Gradient__: analyze horizontal/vertical brightness variations across the image
- __Echo Edge Filter__: use derivative filters to reveal artificial out-of-focus regions
- __Wavelet Threshold__: reconstruct image with different wavelet coefficient thresholds
- __Correlation Plot__: exploit spatial correlation patterns among neighboring pixels

### Colors
- __RGB/HSV Plots__: display interactive 2D and 3D plots of RGB and HSV pixel values
- __Space Conversion__: convert RGB channels into HSV/YCbCr/Lab/Luv/CMYK/Gray spaces
- __PCA Projection__: use color PCA to project pixel onto most salient components
- __Pixel Statistics__: compute minimum/maximum/average RGB values for every pixel

### Noise
- __Noise Separation__: estimate and extract different kind of image noise components
- __Min/Max Deviation__: highlight pixels deviating from block-based min/max statistics
- __Frequency Split__: split image luminance into high and low frequency components
- __Bit Planes Values__: show individual bit planes to find inconsistent noise patterns

### JPEG
- __Error Level Analysis__: show pixel-level difference against fixed compression levels
- __Quality Estimation__: extract quantization tables and estimate last saved JPEG quality
- __Multiple Compression__: use residuals to detect multiple compressions at different levels
- __DCT Dimples Map__: analyze periodic quantization artifacts introduced by devices

### Tampering
- __Contrast Enhancement__: analyze color distribuions to detect contrast enhancements
- __Copy-Move Forgery__: use invariant feature descriptors for cloned area detection
- __Composite Splicing__: exploit DCT statistics for automatic splicing zone detection
- __Image Resampling__: estimate 2D pixel interpolation for detecting resampling traces

### Various
- __Median Filtering__: detect processing traces left by nonlinear median filtering
- __Illuminant Map__: estimate scene local light direction on estimated 3D surfaces
- __PRNU Identification__: exploit sensor pattern noise introduced by different cameras
- __Stereogram Decoder__: decode 3D images concealed inside crossed-eye autostereograms

# Screenshots
Here are some screenshots from the previous C++ Qt GUI (to be updated with the new version):
<p align="center">
  <img src="screenshots/File.jpg" alt="File Analysis"/>
  <br><b>File Analysis</b>: Metadata, Digest and EXIF
</p>

<p align="center">
  <img src="screenshots/Color.jpg" alt="Color Analysis"/>
  <br><b>Color Analysis</b>: Space Conversion, PCA Projection, Histograms and Statistics
</p>

<p align="center">
  <img src="screenshots/Visual.jpg" alt="Visual Inspection"/>
  <br><b>Visual Inspection</b>: Magnifier Loupe, Image Adjustments and Evidence Comparison
</p>

<p align="center">
  <img src="screenshots/JPEG.jpg" alt="JPEG Analysis"/>
  <br><b>JPEG Analysis</b>: Quantization Tables, Compression Ghosts and Error Level Analysis
</p>

<p align="center">
  <img src="screenshots/LumaNoise.jpg" alt="Luminance/Noise"/>
  <br><b>Luminance and Noise</b>: Light Gradient, Echo Edge, Min/Max Deviation and SNR Consistency
</p>

# Installation

## Linux
```
Install with pip
$ Make sure you have git installed
$ git clone https://github.com/GuidoBartoli/sherloq.git
$ pip install --user sherloq
```

## MacOS
```
1) Open Terminal and enter `python3 --version` to install the interpreter and other command line tools
2) Once installed, proceed similarly to Linux installation:
   $ brew install wget
   $ git --version
   $ wget https://bootstrap.pypa.io/get-pip.py
   $ sudo python3 get-pip.py
   $ git clone https://github.com/GuidoBartoli/sherloq.git
   $ pip install --user sherloq
```

## Windows
You can follow [this guide](https://timmyreilly.azurewebsites.net/python-pip-virtualenv-installation-on-windows/) (the *Flask* installation is optional).

## Linux, MacOS, Windows
1. Launch the program with `sherloq`

## Instructions for Conda
1. Download and install [Anaconda](https://www.anaconda.com/products/individual) (one can also install miniconda, no GUI but is smaller)
1. Open a console to create a Python environment (on Windows one must start a Conda Console or `sth` from the Start menu):
`conda create --copy -n sherloq python` [enter *Yes* when it prompts]
1. After install ends, type in the same console `conda activate sherloq` to activate the env. Don't close the console.
1. Download and unpack the Sherloq repo from the GitHub page
1. Go to `sherloq/gui` folder and run `pip install -r requirements.txt` (make sure that the conda env is still on)
1. Instal library: `sudo apt-get install libxcb-xinerama0`
1. Launch the application: `python sherloq.py`

# Bibliography
- Black Hat Briefings DC. (2008) "A Picture's Worth: Digital Image Analysis and Forensics" [White paper]. Washington, DC. Retrieved from http://blackhat.com/presentations/bh-dc-08/Krawetz/Whitepaper/bh-dc-08-krawetz-WP.pdf
- "Noiseprint: a CNN-based camera model fingerprint" (Davide Cozzolino, Luisa Verdoliva)
- "Exposing Digital Forgeries by Detecting Traces of Re-sampling" (Alin C. Popescu and Hany Farid)
- "Two Improved Forensic Methods of Detecting Contrast Enhancement in Digital Images" (Xufeng Lin, Xingjie Wei and Chang-Tsun Li)


## <img src="img/workflow.png"/>

This repository contains a complete workflow for untargeted metabolomics LC-MS data analysis from centroided data to spatial mapping of detected molecular features.

The workflow is being developed by [Alexandrov Team](http://www.embl.de/research/units/scb/alexandrov/index.html) at EMBL Heidelberg ([contact information](http://www.embl.de/research/units/scb/alexandrov/contact/index.html)).

* Developer: Ivan Protsyuk
* Principal investigator: Theodore Alexandrov

## Who might need this workflow?

The workflow can be useful if you do untargeted metabolomics with LC-MS. Especially when you have many samples, and you try to find out how similar or how different they are in regard to their chemical composition.

## What it does?

The workflow consists of the following steps:

1. Detection of LC-MS features in each input sample.
2. Alignment and quantification of all detected features among all the samples.
3. (*Optional*) Exclusion of features that came from blank samples.
4. (*Optional*) Exclusion of rare features, i.e. features that occur in a small number of samples.
5. Creating spatial map for detected features, i.e. associating intensities of detected features with spatial coordinates of samples.

The purpose of the last step is to create a file that can be used along with a 2D/3D model for visualization in [`ili](https://chrome.google.com/webstore/detail/%60ili/nhannoeblkmkmljpddfhcfpjlnanfmkc). This is a Google Chrome application for visualization of molecular features spatially distributed. It is also being developed by Alexandrov Team.

## Installation

The workflow is performed by [KNIME Analytics Platform](https://www.knime.org/), an open-source cross-platform general-purpose workflow management system. Before you can start using the workflow, you should install **KNIME** itself, **Python 2.7** (if it's not already installed) and a few additional modules for Python and KNIME. The installation steps are described below.

1. Download and install **Python 2.7** if you don't have installed (can be the case on Windows). You can download it from [the official Python Downloads Page](https://www.python.org/downloads/).
  * You can check easily if the needed Python distribution is already installed by typing `python --version` in your command prompt. If the output line starts with "Python 2.7", you can consider the 0th step completed.
2. Install a couple of Python modules needed for interaction between KNIME and Python. You can do this by typing the command below in your command prompt.
  * `pip install pandas protobuf`
3. Download and install **KNIME Analytics Platform**. Select a package according to your operating system on [the official KNIME Downloads Page](https://www.knime.org/downloads/overview?quicktabs_knimed=1&#knime2.12.1).
4. Launch KNIME and install additional extensions.
  1. Go to `File => Install KNIME Extensions...`. `Available software` dialog should open after this.
  2. Check the following items in the list of available extensions:
    * `OpenMS`
    * `KNIME Python Integration`
    * `KNIME Nodes to create KNIME Quick Forms`
    * `KNIME Virtual Nodes`
  3. Proceed with the installation. You'll be asked to accept the terms of GPL license at the end.
  4. Restart KNIME after the installation is finished.

As soon as the steps above are accomplished, your environment is ready to run the workflow.

1. Download the file `LCMS_workflow.zip` from this repository.
2. In KNIME window, go to `File => Import KNIME Workflow...`. `Workflow Import Selection` dialog should open after this.
3. Check `Select archive file`, press `Browse...` and specify the path to `LCMS_workflow.zip` downloaded on the 1st step.
4. Press `Finish`.

Now you should see the `LCMS_workflow` item in the list at the left-hand side of the KNIME window. If you double click it, the workflow will open in the Workflow Editor where you can change its settings and specify input/output files.

## Input

The workflow supports the following formats of mass spectrometry data: mzML, mzXML and mzData. Internally, all input files will be converted to mzML, so you can save some time on the workflow execution if your data are already in this format.
Make sure that input files contain centroided data.

## Basic use-case

1. Open the workflow in the KNIME Workflow Editor.
2. Do a right click on the `Input Files` node and select `Configure...`. A dialog for input file selection should show up.
3. Press `Add`, select files with your samples and press `OK`. 
4. Do a right click on the `Exclude features of blank samples and save to file` node and select `Configure...`. A dialog with settings should show up.
5. Specify `Path to result features`. It will be used for saving quantified LC-MS features detected in all of your samples to a file in CSV format.
6. Make sure that the node is still selected in the Workflow Editor and press `Execute selected and executable nodes` on the KNIME main toolbar. The workflow should start execution after this.
7. After it's finished, you can browse through all the features by opening the result file in Excel.

## Known issues

* Sometimes, an error message about `ConcurrentModificationException` appears in the KNIME Console and execution stops. This is caused by an internal KNIME error that occurs upon simultaneous access to a single file by several computational nodes.
  * Workaround: If it happened, press `Execute selected and executable nodes` on the KNIME main toolbar, and execution will continue from the point where error occurred.

## License

The content of this project is licensed under the Apache 2.0 licence, see LICENSE.md.

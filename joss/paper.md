---
title: 'GEFF: Graph Exchange File Format'
tags:
  - Python
  - Java
  - file format
  - graph
  - tracking
authors:
  - given-names: Morgan
    surname: Schwartz
    affiliation: 1
    orcid: 0000-0001-8131-9125
    equal-contrib: true
    corresponding: true
  - given-names: Caroline
    surname: Malin-Mayor
    affiliation: 1
    orcid: 0000-0002-9627-6030
    equal-contrib: true
  - given-names: Talley
    surname: Lambert
    affiliation: 2
    orcid: 0000-0002-2409-0181
  - given-names: Teun
    surname: Huijben
    affiliation: 3
    orcid: 0000-0002-8984-2882
  - given-names: Jan
    surname: Funke
    affiliation: 1
    orcid: 0000-0003-4388-7783
  - given-names: Laura
    surname: Xénard
    affiliation: 4
    orcid: 0000-0002-8168-0970
  - given-names: Mark
    surname: Kittisopikul
    affiliation: 1
    orcid: 0000-0002-9558-6248
  - given-names: Draga
    surname: Doncila Pop
    affiliation: 5
    orcid: 0000-0001-9116-5553
  - given-names: Yohsuke
    surname: Fukai
    affiliation: 6
    orcid: 0000-0002-8860-7178
  - given-names: Jordão
    surname: Bragantini
    affiliation: 3
    orcid: 0000-0001-7652-2735
  - given-names: Melisande
    surname: Croft
    affiliation: 7
    orcid: 0009-0004-8184-683X
  - given-names: Anniek
    surname: Stokkermans
    affiliation: 8
    orcid: 0000-0002-9013-9983
  - given-names: Georgeos
    surname: Hardo
    affiliation: "9, 13"
    orcid: 0000-0003-0037-1293
  - given-names: Benjamin
    surname: Gallusser
    affiliation: 10
    orcid: 0000-0002-7906-4714
  - given-names: Kasia
    surname: Kedziora
    affiliation: 11
    orcid: 0000-0001-6524-7731
  - given-names: Jean-Yves
    surname: Tinevez
    affiliation: 4
    orcid: 0000-0002-0998-4718
  - given-names: Ko
    surname: Sugawara
    affiliation: 12
    orcid: 0000-0002-1392-9340
  - given-names: Tobias
    surname: Pietzsch
    orcid: 0000-0002-9477-3957
  - given-names: Ilan
    surname: Theodoro
    affiliation: 3
    orcid: 0000-0003-4019-3380
affiliations:
 - name: Janelia Research Campus, Howard Hughes Medical Institute
   index: 1
 - name: Harvard Medical School
   index: 2
 - name: Chan Zuckerberg Biohub San Francisco
   index: 3
 - name: Institut Pasteur, Université Paris Cité, Image Analysis Hub, Paris, France
   index: 4
 - name: Monash University
   index: 5
 - name: RIKEN Pioneering Research Institute
   index: 6
 - name: Human Technopole
   index: 7
 - name: Hubrecht Institute
   index: 8
 - name: United Arab Emirates University
   index: 9
 - name: Chan Zuckerberg Initiative
   index: 10
 - name: University of Pittsburgh
   index: 11
 - name: RIKEN Center for Biosystems Dynamics Research
   index: 12
 - name: University of Cambridge
   index: 13
date: 5 November 2025  # TODO: Update to submission date
bibliography: paper.bib
---

# Summary
GEFF (Graph Exchange File Format) is a specification for a file format for exchanging graph data. It is not intended to be mutable, editable, chunked, or optimized for use in an application setting. As an exchange format with a strict specification, GEFF enables interoperability between tools written in various languages.

This repository contains two Python packages: `geff-spec`, the specification of GEFF metadata written with [`pydantic.BaseModel`](https://github.com/pydantic/pydantic), which are exported to a JSON schema for use in other languages, and `geff`, the Python library that reads and writes GEFF files to and from several Python in-memory graph data structures (`networkx` [@networkx_2008], `rustworkx` [@Treinish2022], and [`spatial-graph`](https://github.com/funkelab/spatial_graph)). A Java implementation of the GEFF v1 spec, [`geff-java`](https://github.com/live-image-tracking-tools/geff-java) is in progress in a separate repository.

# Statement of Need

Cell tracking is an active area of research with many tools for performing tracking and visualizing results. At the [2023 Janelia Trackathon](https://github.com/Janelia-Trackathon-2023/sequitur), a two-week workshop gathering cell tracking researchers, there was widespread agreement that a common graph file format would benefit the field by reducing code duplication and increasing standardization between projects. However, attempts made at that time were intended to be mutable and optimized, which introduced barriers to code generation and adoption by tools with different types of optimization needs. The 2025 Janelia Trackathon brought together all the authors of GEFF to decide on the specification and initial implementation, which was accomplished in a week-long hackathon. GEFF allows different research tools to all track and visualize the same data, reducing barriers to pipelining analysis and visualization tools, even across languages. 

# State of the Field
There are many formats used to store and exchange tracking solutions. A commonly used one is the Cell Tracking Challenge [@mavska2014benchmark] format, which combines TIFF files with segmentation masks and a CSV to provide division edges. However, some tracking applications such as particle tracking do not operate on segmentations, but instead utilize point detections, making this format not applicable. As such, individual tracking tools often define their own format for saving tracking results; for example, TrackMate [@tinevez2017trackmate] has a specific XML file format, the [Motile Tracker](https://github.com/funkelab/motile_tracker) exports and loads to CSV files with specific node ID, parent ID, and location columns, and Ultrack [@bragantini2025ultrack] has a custom SQL database. In these existing file formats, there is limited support for storing additional properties on either nodes or edges. Each of these tools can now export to and import from GEFF in addition to their custom formats, enabling interoperability with minimal code change in each library.

# Implementation
GEFF is built on `zarr` [@zarr-specs], a common file format used in bioimage analysis. Graphs are represented as an array of node IDs and an array of edge IDs where each edge ID is a tuple of two node IDs. Nodes and edges can have properties, which are stored in a properties array with corresponding indices. The specification includes support for nodes and edges with missing properties, as well as variable-length properties. To support the cell tracking community, the GEFF specification also provides specific metadata with standardized meaning, including positional axes, tracklet and lineage IDs, and linking to related objects such as image and segmentation arrays.

GEFF supports Zarr specification v2 and v3, and has minimal dependencies, making it a lightweight dependency for other libraries. As of submission time, the following tools all support either saving and/or loading GEFF files: [`motile-tracker`](https://github.com/funkelab/motile_tracker), [`traccuracy`](https://github.com/live-image-tracking-tools/traccuracy/pulls), [`ultrack`](https://github.com/royerlab/ultrack), [`track_gardener`](https://github.com/fjorka/track_gardener), [`laptrack`](https://github.com/yfukai/laptrack), [`trackastra`](https://github.com/weigertlab/trackastra), [`TrackMate`](https://imagej.net/plugins/trackmate/), [`InTRACKtive`](https://github.com/royerlab/inTRACKtive), [`tracksdata`](https://github.com/royerlab/tracksdata) and [`napari-geff`](https://github.com/live-image-tracking-tools/napari-geff). 

# Extensibility

While GEFF was developed by the cell tracking research community, it is a generic graph exchange format that could be easily extended to other use cases with additional metadata to specify the meaning of standard properties.

# Acknowledgments

We would like to thank HHMI Janelia Research Campus for hosting the 2025 Janelia Trackathon and the other attendees of the trackathon for their discussion.

# References

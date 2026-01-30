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
  - given-names: Caroline
    surname: Malin-Mayor
    affiliation: 1
    orcid: 0000-0002-9627-6030
    equal-contrib: true
    corresponding: true
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
    affiliation: 4, 13
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
    affiliation: "9, 12"
    orcid: 0000-0003-0037-1293
  - given-names: Benjamin
    surname: Gallusser
    affiliation: 3
    orcid: 0000-0002-7906-4714
  - given-names: Kasia
    surname: Kedziora
    affiliation: 10
    orcid: 0000-0001-6524-7731
  - given-names: Jean-Yves
    surname: Tinevez
    affiliation: 4
    orcid: 0000-0002-0998-4718
  - given-names: Ko
    surname: Sugawara
    affiliation: 11
    orcid: 0000-0002-1392-9340
  - given-names: Tobias
    surname: Pietzsch
    affiliation: 14
    orcid: 0000-0002-9477-3957
  - given-names: Ilan
    surname: Theodoro
    affiliation: 3
    orcid: 0000-0003-4019-3380
affiliations:
 - name: Janelia Research Campus, Howard Hughes Medical Institute, Ashburn, VA, USA
   index: 1
 - name: Harvard Medical School, Boston, MA, USA
   index: 2
 - name: Biohub, San Francisco, CA, USA
   index: 3
 - name: Institut Pasteur, Université Paris Cité, Image Analysis Hub, Paris, France
   index: 4
 - name: Monash University, Melbourne, Australia
   index: 5
 - name: RIKEN Pioneering Research Institute, Kobe, Hyōgo, Japan
   index: 6
 - name: Human Technopole, Milan, Italy
   index: 7
 - name: Hubrecht Institute, Utrecht, Netherlands
   index: 8
 - name: United Arab Emirates University, Al Ain, UAE
   index: 9
 - name: University of Pittsburgh, Pittsburg, PA, USA
   index: 10
 - name: RIKEN Center for Biosystems Dynamics Research, Kobe, Japan
   index: 11
 - name: University of Cambridge, Cambridge, UK
   index: 12
 - name: Institut Pasteur, Université Paris Cité, INSERM U1225, Paris, France
   index: 13
 - name: Independent Consultant, Germany
   index: 14
   
date: 16 December 2025  # TODO: Update to submission date
bibliography: paper.bib
---

# Summary

GEFF (Graph Exchange File Format) is a file format specification for exchanging graph data. 
Its main application today is focused on exchange of animal, cell and organelle tracking data in the life sciences.
It is not intended to be mutable, editable, chunked, or optimized for use in an application setting. As an exchange format with a strict specification, GEFF enables interoperability between tools written in various programming languages.

The geff repository contains two Python packages: `geff-spec`, the specification of GEFF metadata written with [`pydantic.BaseModel`s](https://github.com/pydantic/pydantic), which are exported to a JSON schema for use in other languages, and `geff`, the Python library that reads and writes GEFF files to and from several Python in-memory graph data structures (`networkx` [@networkx_2008], `rustworkx` [@Treinish2022], and [`spatial-graph`](https://github.com/funkelab/spatial_graph)). A Java implementation of the GEFF v1 spec, [`geff-java`](https://github.com/live-image-tracking-tools/geff-java) is in progress in a separate repository.

# Statement of Need

Cell and organelle tracking is an active area of research with many tools for performing tracking and visualizing results. At the [2023 Janelia Trackathon](https://github.com/Janelia-Trackathon-2023/sequitur), a two-week workshop gathering cell tracking researchers, there was widespread agreement that a common graph file format would benefit the field by reducing code duplication and increasing standardization between projects. However, attempts made at that time were intended to be mutable and optimized, which introduced barriers to code generation and adoption by tools with different types of optimization needs. The 2025 Janelia Trackathon brought together all the authors of GEFF to decide on the specification and initial implementation, which was accomplished in a week-long hackathon. 

# Research Impact Statement
GEFF allows different research tools to all track and visualize the same data, reducing barriers to pipelining analysis and visualization tools, even across languages. 
As of submission time, the following tools all support either saving and/or loading GEFF files: [`motile-tracker`](https://github.com/funkelab/motile_tracker), [`traccuracy`](https://github.com/live-image-tracking-tools/traccuracy), [`ultrack`](https://github.com/royerlab/ultrack), [`track_gardener`](https://github.com/fjorka/track_gardener), [`laptrack`](https://github.com/yfukai/laptrack), [`trackastra`](https://github.com/weigertlab/trackastra), [`TrackMate`](https://imagej.net/plugins/trackmate/), [`InTRACKtive`](https://github.com/royerlab/inTRACKtive), [`tracksdata`](https://github.com/royerlab/tracksdata) and [`napari-geff`](https://github.com/live-image-tracking-tools/napari-geff).
The developers have already fielded inquiries through GitHub and email from researchers, both developers and end-users, about how best to use GEFF to accelerate their research workflow. We hope that GEFF will become the standard for storing and exchanging tracking information in the bio-image analysis community, and potentially even other fields that require exchanging graph-based information.


# State of the Field

There are many formats used to store and exchange tracking solutions. A commonly used one is the Cell Tracking Challenge (CTC) [@mavska2014benchmark] format, which combines TIFF files with segmentation masks and a CSV file to provide division edges. However, some tracking applications such as particle tracking do not operate on segmentations, but instead utilize point detections, making this format not applicable. As such, individual tracking tools often define their own format for saving tracking results; for example, TrackMate [@tinevez2017trackmate] has a specific XML file format, Mastodon [@tinevez2025mastodon] saves and loads from a binary file, the [Motile Tracker](https://github.com/funkelab/motile_tracker) exports and loads to CSV files with specific node ID, parent ID, and location columns, and Ultrack [@bragantini2025ultrack] has a custom SQL database. In these existing file formats, there is limited support for storing additional properties on either nodes or edges. 
Additionally, none of these tools shared a common file format, which prevented interactions between them and strongly limited the scope and ambition of track analysis pipelines.
Additionally, none of these tools shared a common file format, which prevented interactions between them and strongly limited the scope and ambition of track analysis pipelines. In contrast to prior efforts to create a common file format [@gonzalez2020cmso], we worked with tool authors to integrate support for GEFF directly into the tools themselves rather than only creating a third-party library.
Each of them can now export to and import from GEFF in addition to their custom formats, enabling interoperability with minimal code change in each library.

# Implementation
GEFF is built on `zarr` [@zarr-specs], a common file format used in bioimage analysis. Graphs are represented as an array of node IDs and an array of edge IDs where each edge ID is a tuple of two node IDs. Nodes and edges can have properties, which are stored in a properties array with corresponding indices. The specification includes support for nodes and edges with missing properties, as well as variable-length properties. To support the cell tracking community, the GEFF specification also provides specific metadata with standardized meaning, including positional axes, tracklet and lineage IDs, and linking to related objects such as image and segmentation arrays.

GEFF’s object specification supports a wide range of shapes, enabling its application across diverse fields in the life sciences. 
The library integrates multiple representation formats, from binary masks (2D/3D), commonly used in cell biology, developmental biology, and natural image tracking—to geometric primitives (points, circles, ellipses, spheres, and ellipsoids), which are essential in super-resolution microscopy, virology, and developmental studies. 
It also includes polygons and meshes for detailed structural analysis in cell biology, microbiology, and complex shape modeling, as well as pose-based representations for markerless tracking of anatomical keypoints in multi-animal and behavioral research.

Each object, track, or lineage, is represented by a simple directed graph, where each edge is a link from one biological object detected in a frame, to its detection in the earliest next frame. 
GEFF can therefore be used to harness tracking data with gaps (an edge extends over more that two adjacent time-points, because of a missing detection or object exit and reentry), object divisions and objects fusions. 
Multiple GEFFs can refer to the same set of segmentations or detections which makes it possible to easily store multiple tracking solutions or hypotheses without duplicating the underlying data, which is a limitation of the commonly-used CTC format. 

By integrating these diverse object and link representations, GEFF facilitates seamless data exchange between segmentation algorithms, morphometric analysis tools, and tracking pipelines, ensuring compatibility with both established and emerging imaging workflows. 
This versatility makes the library a valuable resource for researchers working across disciplines, from high-throughput cell biology to fine-grained anatomical studies in developmental and computational biology.

## Software Design
The GEFF specification emphasizes simplicity over optimization. It would be infeasible to make a single graph format, or even tracking format, that was optimized for all use cases. Implementing a simple exchange format allows a variety of tools with different goals to exchange information, while retaining their optimized internal formats. Additionally, focusing on an exchange format allows cross-language compatibility. In addition to a hand-written specification, the GEFF specification package provides Pydantic classes and a JSON schema for creating and validating the metadata properties.

The Python reference implementation has a highly modular design. The `core_io` module is the heart of the implementation, with core read and write implementations that can be used by any graph library, converting from an `InMemoryGeff` data structure to an on-disk `zarr` and back. This crucial abstraction improves maintainability as well as extensibility; new graph library implementations only need to convert to and from the `InMemoryGeff` data structure, and any improvements to performance or bugfixes in the `core_io` module are automatically propagated to the individual graph library implementations. GEFF supports Zarr specification v2 and v3, and has minimal dependencies, making it a lightweight dependency for other libraries. 

The `_graph_libs` currently implements three graph backends. `networkx` and `rustworkx` are two of the most common Python graph libraries, making GEFF adoption simple for most Python programmers. `spatial_graph` is a newer graph library with improved efficiency when searching for all graph elements in a spatial region. While the Python implementation contains significant internal typing and abstraction logic that reduces code duplication and enhances maintainability, the external API is quite simple; most users will only need to use the public `read` and `write` functions.

The other three modules provide additional functionality for new users and developers. The `convert` module contains a CLI tool for converting existing on-disk formats to GEFF, including TrackMate XML, the Cell Tracking Challenge format, and any CSV-like format that can be loaded into a Pandas dataframe. The `testing` module provides `InMemoryGeff` objects with a variety of valid GEFF data combinations for testing both existing and new implementations. Finally, the `validate` module provides helper functions for testing the validity of on-disk GEFFs with varying levels of inspection, from fast, structure-only validation to intensive data validation.


## Extensibility

While GEFF was developed by the cell tracking research community, it is a generic graph exchange format that could be easily extended to other use cases with additional metadata to specify the meaning of standard properties.

# Acknowledgments

We would like to thank HHMI Janelia Research Campus for hosting the 2025 Janelia Trackathon and the other attendees of the trackathon for their discussion. 
LX and JYT acknowledge support from the French National Research Agency (France BioImaging, ANR-24-INBS-0005 FBI BIOGEN). LX acknowledges support from the INCEPTION project (PIA/ANR-16-CONV-0005) and the FIRE PhD program funded by the Bettencourt Schueller foundation and the EURIP graduate program (ANR-17-EURE-0012).

# AI Usage Disclosure
All specification and paper content was written manually and reflects the careful thought and input of the community. GEFF is an open source project, and as such contributors are free to use any tools, AI or otherwise, to generate code contained in pull requests.  All pull requests are reviewed by a core developer and often iterated on multiple times; therefore, all content in the repository represents the effort and judgment of the authors.

# References

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
    affiliation: 9
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
 - name: Institut Pasteur
   index: 4
 - name: Monash University
   index: 5
 - name: RIKEN Pioneering Research Institute
   index: 6
 - name: Human Technopole
   index: 7
 - name: Hubrecht Institute
   index: 8
 - name: UAE University
   index: 9
 - name: Chan Zuckerbeg Initiative
   index: 10
 - name: University of Pittsburgh
   index: 11
 - name: RIKEN Center for Biosystems Dynamics Research
   index: 12
date: 5 November 2025  # TODO: Update to submission date
bibliography: paper.bib
---

# Summary
GEFF is a specification for a file format for exchanging spatial graph data. It is not intended to be mutable, editable, chunked, or optimized for use in an application setting. As an exchange format with a strict specification, GEFF enables interoperability between tools written in various languages.

This repository contains two packages: `geff-spec`, the specification of GEFF metadata written with pydantic BaseModels which are exported to a json schema for use in other languages, and `geff`, the Python library that reads and writes GEFF files to and from several python in-memory graph data structures (`networkx`, `rustworkx` and `spatial-graph`). A Java implementation of the GEFF v1 spec is in progress in a separate repository.

# Statement of Need

# Acknowledgments

# References
window.BENCHMARK_DATA = {
  "lastUpdate": 1753228203754,
  "repoUrl": "https://github.com/live-image-tracking-tools/geff",
  "entries": {
    "Python Benchmark with pytest-benchmark": [
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "029621dc3e7f32f5cd14b29870f930e593e359c2",
          "message": "Add scm env variable to gh pages action",
          "timestamp": "2025-05-01T15:52:20-04:00",
          "tree_id": "a895b8eeae659267318b71bdf59850878e55bc8b",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/029621dc3e7f32f5cd14b29870f930e593e359c2"
        },
        "date": 1746129265710,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13561316530585438,
            "unit": "iter/sec",
            "range": "stddev: 0.0299426634299259",
            "extra": "mean: 7.373915340333336 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 365.80231238362063,
            "unit": "iter/sec",
            "range": "stddev: 0.00031073327806497604",
            "extra": "mean: 2.7337169999934 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06300089966349438,
            "unit": "iter/sec",
            "range": "stddev: 0.5470120897994015",
            "extra": "mean: 15.872789203666656 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "malinmayorc@janelia.hhmi.org",
            "name": "Caroline Malin-Mayor",
            "username": "cmalinmayor"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "8018bf0741cf2905d028c1e9876921a6a766d230",
          "message": "Merge pull request #43 from live-image-tracking-tools/41-metadata\n\nSave and load metadata fully",
          "timestamp": "2025-05-01T16:38:05-04:00",
          "tree_id": "c4b3156aeccc9b46afccf0eb4eea4417cc6807ea",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/8018bf0741cf2905d028c1e9876921a6a766d230"
        },
        "date": 1746132040086,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13512345883098548,
            "unit": "iter/sec",
            "range": "stddev: 0.02128361089617375",
            "extra": "mean: 7.40063944966666 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 365.99921017248704,
            "unit": "iter/sec",
            "range": "stddev: 0.00029044500712752845",
            "extra": "mean: 2.7322463333424216 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06277695766855433,
            "unit": "iter/sec",
            "range": "stddev: 0.5359005540661197",
            "extra": "mean: 15.929411636666666 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "166920974c144529053966346346a5647e25b126",
          "message": "Add support for zarr 2 and 3 (#42)\n\n* Add support for zarr 2 and 3\n\n* Try fixing zarr install\n\n* Update test function for zarr 3 syntax\n\n* Resolve zarr deprecation warnings\n\n* Skip testing zarr 3 on python 3.10\n\n* Make test code  work with zarr 2 and 3\n\n* Use tmp_path instead of tmpdir in tests\n\n* Review feedback\n\n* Remove cast to string because Paths are supported\n\n* Get tests to pass\n\n* Use Path in benchmark functions\n\n---------\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>",
          "timestamp": "2025-05-01T17:05:36-04:00",
          "tree_id": "a0857db0c9337601abe9297e2a7ff7a7193f8d6b",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/166920974c144529053966346346a5647e25b126"
        },
        "date": 1746133688502,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13230598755983364,
            "unit": "iter/sec",
            "range": "stddev: 0.017444794270241534",
            "extra": "mean: 7.558236920666673 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 41.323413161317305,
            "unit": "iter/sec",
            "range": "stddev: 0.0009082148047173535",
            "extra": "mean: 24.199356333326705 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.061765764248896564,
            "unit": "iter/sec",
            "range": "stddev: 0.4369738380750813",
            "extra": "mean: 16.19019876399999 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "malinmayorc@janelia.hhmi.org",
            "name": "Caroline Malin-Mayor",
            "username": "cmalinmayor"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "ad9bbd4ef1acbe698b326f2ea5c0d062baaa5a47",
          "message": "Remove spatial graph from README and PR template (#46)\n\n* Remove spatial graph from README and PR template\n\n* Update links in pyproject.toml\n\n---------\n\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>",
          "timestamp": "2025-05-01T17:10:53-04:00",
          "tree_id": "8e28aeef5b5dae8f6dc8331a7238a9437f00d5bf",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/ad9bbd4ef1acbe698b326f2ea5c0d062baaa5a47"
        },
        "date": 1746134014071,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1317593000588966,
            "unit": "iter/sec",
            "range": "stddev: 0.06036641119597091",
            "extra": "mean: 7.589597087666665 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 39.8007584645015,
            "unit": "iter/sec",
            "range": "stddev: 0.0006109597631318234",
            "extra": "mean: 25.125149333319996 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06231025220596681,
            "unit": "iter/sec",
            "range": "stddev: 0.48398951712292115",
            "extra": "mean: 16.04872335766666 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "7fa04a1c99820a2344b52fda12e6c2fea57d3d86",
          "message": "Add 0.1 to supported versions",
          "timestamp": "2025-05-02T10:06:37-04:00",
          "tree_id": "a1801e84ebd6761901f5ced856bdc266c13aa3b9",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/7fa04a1c99820a2344b52fda12e6c2fea57d3d86"
        },
        "date": 1746194939597,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13073676183148755,
            "unit": "iter/sec",
            "range": "stddev: 0.046781299029505896",
            "extra": "mean: 7.648957997666675 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 38.737212829896926,
            "unit": "iter/sec",
            "range": "stddev: 0.0007288784200203826",
            "extra": "mean: 25.814970333338277 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06208278214701933,
            "unit": "iter/sec",
            "range": "stddev: 0.5129349935750673",
            "extra": "mean: 16.107525555666665 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "97654279752215f33e6792237567eb8e090825df",
          "message": "Update json schema",
          "timestamp": "2025-05-02T10:08:07-04:00",
          "tree_id": "72c2ce5d31fe1eb9cb2fbfb14b16050dbdf83907",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/97654279752215f33e6792237567eb8e090825df"
        },
        "date": 1746195082448,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12916558064910222,
            "unit": "iter/sec",
            "range": "stddev: 0.06651300248353748",
            "extra": "mean: 7.742000577666668 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 39.4224360810662,
            "unit": "iter/sec",
            "range": "stddev: 0.0002540650937422267",
            "extra": "mean: 25.36626599999181 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06062424212980675,
            "unit": "iter/sec",
            "range": "stddev: 0.7411778533321154",
            "extra": "mean: 16.49505156466667 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bf475bd96dd5a0b3d540febba23b51adcdfc6a2e",
          "message": "Update dev notes and bugfix deploy action (#48)\n\n* Add notes about releases\n\n* Fix deploy action that checks that supported versions is up to date",
          "timestamp": "2025-05-02T10:15:45-04:00",
          "tree_id": "bfeb5b5f6ece9f1bdde7a9df04b541c0c58d12cf",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/bf475bd96dd5a0b3d540febba23b51adcdfc6a2e"
        },
        "date": 1746195501770,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13333210044399263,
            "unit": "iter/sec",
            "range": "stddev: 0.07667985222091646",
            "extra": "mean: 7.500069350666678 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 40.514471668002614,
            "unit": "iter/sec",
            "range": "stddev: 0.00112788319093007",
            "extra": "mean: 24.68253833332786 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06219479649351004,
            "unit": "iter/sec",
            "range": "stddev: 0.444083006084229",
            "extra": "mean: 16.078515509 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "19e48ff054a6772cdaa3a11fdbf351ecfea6f4a3",
          "message": "additional deploy action bugfix",
          "timestamp": "2025-05-02T10:17:56-04:00",
          "tree_id": "175b5d933262f7151b743521290e0e3eed602b68",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/19e48ff054a6772cdaa3a11fdbf351ecfea6f4a3"
        },
        "date": 1746195626015,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13204822954625095,
            "unit": "iter/sec",
            "range": "stddev: 0.08419713926622867",
            "extra": "mean: 7.572990591666676 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 41.20163808372054,
            "unit": "iter/sec",
            "range": "stddev: 0.0004680122384457904",
            "extra": "mean: 24.27087966667803 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.062197974193076495,
            "unit": "iter/sec",
            "range": "stddev: 0.4444821724850281",
            "extra": "mean: 16.077694056333332 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "19e48ff054a6772cdaa3a11fdbf351ecfea6f4a3",
          "message": "additional deploy action bugfix",
          "timestamp": "2025-05-02T10:17:56-04:00",
          "tree_id": "175b5d933262f7151b743521290e0e3eed602b68",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/19e48ff054a6772cdaa3a11fdbf351ecfea6f4a3"
        },
        "date": 1746589839570,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12983098020358938,
            "unit": "iter/sec",
            "range": "stddev: 0.05637559853345289",
            "extra": "mean: 7.702321883666666 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 39.421354955324674,
            "unit": "iter/sec",
            "range": "stddev: 0.00046329808775675955",
            "extra": "mean: 25.36696166667222 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06230545688586261,
            "unit": "iter/sec",
            "range": "stddev: 0.380610788976034",
            "extra": "mean: 16.049958542666662 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "f2bad2252c408fa66f95d6f837ec014d38410490",
          "message": "Remove env variable from github action so that deploy works correctly",
          "timestamp": "2025-05-21T15:35:32-04:00",
          "tree_id": "582d2e1ea74aa0f044991b05837ebf95f32d94b3",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/f2bad2252c408fa66f95d6f837ec014d38410490"
        },
        "date": 1747856290971,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1309941814769118,
            "unit": "iter/sec",
            "range": "stddev: 0.030928851143142505",
            "extra": "mean: 7.6339268563333365 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 40.39732547084576,
            "unit": "iter/sec",
            "range": "stddev: 0.0005569420386673272",
            "extra": "mean: 24.754113999989613 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06190503046588155,
            "unit": "iter/sec",
            "range": "stddev: 0.4343135261786798",
            "extra": "mean: 16.153776074000024 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "f2bad2252c408fa66f95d6f837ec014d38410490",
          "message": "Remove env variable from github action so that deploy works correctly",
          "timestamp": "2025-05-21T15:35:32-04:00",
          "tree_id": "582d2e1ea74aa0f044991b05837ebf95f32d94b3",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/f2bad2252c408fa66f95d6f837ec014d38410490"
        },
        "date": 1747856417216,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13052457402137832,
            "unit": "iter/sec",
            "range": "stddev: 0.04778223859528065",
            "extra": "mean: 7.661392557666669 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 37.596522020928774,
            "unit": "iter/sec",
            "range": "stddev: 0.0006522501753038362",
            "extra": "mean: 26.598205000008573 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.061712705199432186,
            "unit": "iter/sec",
            "range": "stddev: 0.5186527806230805",
            "extra": "mean: 16.204118694333317 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7ef517a5f3f5784edd0502d1aeedf779dfc21121",
          "message": "Check if there are additional edge attributes before adding to graph (#51)",
          "timestamp": "2025-06-02T15:50:30-04:00",
          "tree_id": "98e3a851a5ae78c4d5d23bd9dcc3263242a58956",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/7ef517a5f3f5784edd0502d1aeedf779dfc21121"
        },
        "date": 1748893988798,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1319776240031371,
            "unit": "iter/sec",
            "range": "stddev: 0.05206763989380486",
            "extra": "mean: 7.577041998999998 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 40.16317763564864,
            "unit": "iter/sec",
            "range": "stddev: 0.000712611538922552",
            "extra": "mean: 24.898428333330003 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06118176923099284,
            "unit": "iter/sec",
            "range": "stddev: 0.5287178501322192",
            "extra": "mean: 16.344738188666668 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7ef517a5f3f5784edd0502d1aeedf779dfc21121",
          "message": "Check if there are additional edge attributes before adding to graph (#51)",
          "timestamp": "2025-06-02T15:50:30-04:00",
          "tree_id": "98e3a851a5ae78c4d5d23bd9dcc3263242a58956",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/7ef517a5f3f5784edd0502d1aeedf779dfc21121"
        },
        "date": 1749482749423,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13074507012891357,
            "unit": "iter/sec",
            "range": "stddev: 0.03964761123681386",
            "extra": "mean: 7.64847193866666 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 37.66822724457887,
            "unit": "iter/sec",
            "range": "stddev: 0.00034343295404212494",
            "extra": "mean: 26.547572666667445 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06299809721177169,
            "unit": "iter/sec",
            "range": "stddev: 0.6580076909468524",
            "extra": "mean: 15.873495299999982 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "malinmayorc@janelia.hhmi.org",
            "name": "Caroline Malin-Mayor",
            "username": "cmalinmayor"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fef5c6c96a9c84804956510038bb951e82d49ced",
          "message": "Merge pull request #54 from live-image-tracking-tools/bugfix-pos-attr\n\nBugfix - restore original position attribute name when loading",
          "timestamp": "2025-06-12T11:09:50-04:00",
          "tree_id": "d7323c19277ccd0c56c00a9e1fd0835846ad953b",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/fef5c6c96a9c84804956510038bb951e82d49ced"
        },
        "date": 1749741118610,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1345107373948937,
            "unit": "iter/sec",
            "range": "stddev: 0.02785696663958436",
            "extra": "mean: 7.434350739333335 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 40.021087377749524,
            "unit": "iter/sec",
            "range": "stddev: 0.0004623612121523159",
            "extra": "mean: 24.9868273333315 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06305431482978914,
            "unit": "iter/sec",
            "range": "stddev: 0.4011755509680916",
            "extra": "mean: 15.859342896666666 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "malinmayorc@janelia.hhmi.org",
            "name": "Caroline Malin-Mayor",
            "username": "cmalinmayor"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "fef5c6c96a9c84804956510038bb951e82d49ced",
          "message": "Merge pull request #54 from live-image-tracking-tools/bugfix-pos-attr\n\nBugfix - restore original position attribute name when loading",
          "timestamp": "2025-06-12T11:09:50-04:00",
          "tree_id": "d7323c19277ccd0c56c00a9e1fd0835846ad953b",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/fef5c6c96a9c84804956510038bb951e82d49ced"
        },
        "date": 1749823200778,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13254492113290295,
            "unit": "iter/sec",
            "range": "stddev: 0.04559163297779535",
            "extra": "mean: 7.544611981000003 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 39.594190692794896,
            "unit": "iter/sec",
            "range": "stddev: 0.0010969188528712397",
            "extra": "mean: 25.25623033335478 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.062091617666436005,
            "unit": "iter/sec",
            "range": "stddev: 0.6581938351653169",
            "extra": "mean: 16.105233485333333 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5af31f9b558556b3fc37f7db0c006fc798032437",
          "message": "Default to zarr format 2 even when using zarr python 3 (#58)\n\n* Add pixi environments for testing zarr 2 and 3 separately\n\n* Default to using zarr_format 2 even when using zarr python 3\n\n* Remove zarr2/zarr3 features/environments because they immediately broke with a numcodecs dependency conflict\n\n* Add a note to the specification about preference for zarr 2 vs zarr 3\n\n* Add comment to docs",
          "timestamp": "2025-06-23T09:42:07-04:00",
          "tree_id": "a336acb050350ed5c3dc06ebdceed16c8940634e",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/5af31f9b558556b3fc37f7db0c006fc798032437"
        },
        "date": 1750686284635,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1342187526234033,
            "unit": "iter/sec",
            "range": "stddev: 0.03448514123154347",
            "extra": "mean: 7.450523719333337 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 22.520479617450302,
            "unit": "iter/sec",
            "range": "stddev: 0.0016183079372606233",
            "extra": "mean: 44.40402766667262 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06291093111152098,
            "unit": "iter/sec",
            "range": "stddev: 0.5289917902718193",
            "extra": "mean: 15.895488785999996 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e20731743df4faf5293e5aaacf92439d7dde7171",
          "message": "Expose read_nx and write_nx as top level imports (#59)\n\n* Expose read_nx and write_nx as top level imports\n\n* Update test imports to match desired import pattern",
          "timestamp": "2025-06-24T09:37:53-04:00",
          "tree_id": "b15b02c822f3e62c5a55ae76bec5e5417b5608bb",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/e20731743df4faf5293e5aaacf92439d7dde7171"
        },
        "date": 1750772402316,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1352454497554738,
            "unit": "iter/sec",
            "range": "stddev: 0.08000349447605065",
            "extra": "mean: 7.393964098666667 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.325386892364687,
            "unit": "iter/sec",
            "range": "stddev: 0.00026375761891172855",
            "extra": "mean: 42.87174333332663 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06295545518839211,
            "unit": "iter/sec",
            "range": "stddev: 0.49239333045650685",
            "extra": "mean: 15.884246996666661 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "cd03d27fa5b2fc33cc943a48bb7e977702b03a7c",
          "message": "Make position an optional attribute (#60)\n\n* Update metadata schema to make position_attr optional\n\n- Only validate other spatial metadata fields if position_attr is present\n- position_attr is required if other spatial metadata is provided\n\n* Update networkx implementation to make position an optional attribute\n\n* Add comment question about something that may need to be changed\n\n* Update schema\n\n* Remove code that changed the name of the position attribute on the graph\n\n* Add changes about optional position to spec md file\n\n* Fix imports in tests",
          "timestamp": "2025-06-24T12:43:09-04:00",
          "tree_id": "e85aa5a6aea76c57b11b4ee43d146e59f23b7d2a",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/cd03d27fa5b2fc33cc943a48bb7e977702b03a7c"
        },
        "date": 1750783517328,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1342715971878896,
            "unit": "iter/sec",
            "range": "stddev: 0.04950272409824297",
            "extra": "mean: 7.447591455999998 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.184430708860926,
            "unit": "iter/sec",
            "range": "stddev: 0.0007819271399108415",
            "extra": "mean: 43.13239399998755 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06184292619249766,
            "unit": "iter/sec",
            "range": "stddev: 0.591044780483727",
            "extra": "mean: 16.16999811566667 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "07b8e0069606d50e474d1678af88afc6b85e989d",
          "message": "Docs improvements (#62)\n\n* Switch docs over to manual specification of which things to show in api docs\n\n* Add todo note about header level\n\n* Decide that heading 3 is fine for functions\n\n* Add explicit nav order\n\n* Update docs to work with new import paths\n\n* Add example metadata to spec page\n\n* Fix formatting on what is geff page\n\n* Point to docs in the readme\n\n* Nitpicks from Caroline on docs\n\n* Add ruff check for docstrings\n\n---------\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>",
          "timestamp": "2025-07-14T13:43:32-04:00",
          "tree_id": "613990131a081675f1d9ba0da270fcc0747d9618",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/07b8e0069606d50e474d1678af88afc6b85e989d"
        },
        "date": 1752515135089,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1350205222349956,
            "unit": "iter/sec",
            "range": "stddev: 0.03735901895165445",
            "extra": "mean: 7.4062815299999825 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.242673014619065,
            "unit": "iter/sec",
            "range": "stddev: 0.0009464095293066775",
            "extra": "mean: 43.02431133334039 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06253154624273917,
            "unit": "iter/sec",
            "range": "stddev: 0.5566116872977945",
            "extra": "mean: 15.991928235999998 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "07b8e0069606d50e474d1678af88afc6b85e989d",
          "message": "Docs improvements (#62)\n\n* Switch docs over to manual specification of which things to show in api docs\n\n* Add todo note about header level\n\n* Decide that heading 3 is fine for functions\n\n* Add explicit nav order\n\n* Update docs to work with new import paths\n\n* Add example metadata to spec page\n\n* Fix formatting on what is geff page\n\n* Point to docs in the readme\n\n* Nitpicks from Caroline on docs\n\n* Add ruff check for docstrings\n\n---------\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>",
          "timestamp": "2025-07-14T13:43:32-04:00",
          "tree_id": "613990131a081675f1d9ba0da270fcc0747d9618",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/07b8e0069606d50e474d1678af88afc6b85e989d"
        },
        "date": 1752515262896,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.1319188245322834,
            "unit": "iter/sec",
            "range": "stddev: 0.018082099680022657",
            "extra": "mean: 7.580419273333338 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 22.300002980766365,
            "unit": "iter/sec",
            "range": "stddev: 0.001234225658087188",
            "extra": "mean: 44.84304333333474 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.0616968361576104,
            "unit": "iter/sec",
            "range": "stddev: 0.4851341275134227",
            "extra": "mean: 16.20828655533333 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "042031f3a2148b5f44673c5d1c1b803586c3b7f8",
          "message": "Add 0.2 to supported versions",
          "timestamp": "2025-07-14T13:54:55-04:00",
          "tree_id": "2632287a915bd338ca4767b460e92516f476dee1",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/042031f3a2148b5f44673c5d1c1b803586c3b7f8"
        },
        "date": 1752515822244,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13484077945679246,
            "unit": "iter/sec",
            "range": "stddev: 0.06861429748469902",
            "extra": "mean: 7.416154104333354 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.14914663371999,
            "unit": "iter/sec",
            "range": "stddev: 0.000660091603893517",
            "extra": "mean: 43.1981366666605 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.062253820205599095,
            "unit": "iter/sec",
            "range": "stddev: 0.5918303088260715",
            "extra": "mean: 16.063271245 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "c6e4d9fde4a8176c532d93b6af7c1d86809158cf",
          "message": "Update json schema with new supported version",
          "timestamp": "2025-07-14T15:33:26-04:00",
          "tree_id": "0cf28ee199b4b16ee5426035e70ec1ed0260481e",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/c6e4d9fde4a8176c532d93b6af7c1d86809158cf"
        },
        "date": 1752521765739,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13556383878707387,
            "unit": "iter/sec",
            "range": "stddev: 0.06316242332884157",
            "extra": "mean: 7.376598427333344 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.34243773994818,
            "unit": "iter/sec",
            "range": "stddev: 0.0010594957441231816",
            "extra": "mean: 42.84042699998736 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.062217633896074535,
            "unit": "iter/sec",
            "range": "stddev: 0.5047312216557547",
            "extra": "mean: 16.07261378133334 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "distinct": true,
          "id": "c6e4d9fde4a8176c532d93b6af7c1d86809158cf",
          "message": "Update json schema with new supported version",
          "timestamp": "2025-07-14T15:33:26-04:00",
          "tree_id": "0cf28ee199b4b16ee5426035e70ec1ed0260481e",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/c6e4d9fde4a8176c532d93b6af7c1d86809158cf"
        },
        "date": 1752521964061,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13472583441501257,
            "unit": "iter/sec",
            "range": "stddev: 0.03824246995590367",
            "extra": "mean: 7.422481399666651 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.47235553109413,
            "unit": "iter/sec",
            "range": "stddev: 0.0004603431055505911",
            "extra": "mean: 42.60330833329817 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.0626976993993589,
            "unit": "iter/sec",
            "range": "stddev: 0.5062633080856318",
            "extra": "mean: 15.949548541333323 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "talley.lambert@gmail.com",
            "name": "Talley Lambert",
            "username": "tlambert03"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "85a32e46463e695330b20601a51a1366eb2c77d3",
          "message": "fix: fix zarr usage in test (#79)",
          "timestamp": "2025-07-17T10:54:35-04:00",
          "tree_id": "416780a25b4ef4a51450719e9940a97835b07b6c",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/85a32e46463e695330b20601a51a1366eb2c77d3"
        },
        "date": 1752764213511,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11410515538758542,
            "unit": "iter/sec",
            "range": "stddev: 0.09462164148328087",
            "extra": "mean: 8.763845915666659 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.374114514524194,
            "unit": "iter/sec",
            "range": "stddev: 0.0012826337853296095",
            "extra": "mean: 42.78236933333327 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.05193797834376855,
            "unit": "iter/sec",
            "range": "stddev: 0.44821304575036697",
            "extra": "mean: 19.25373362399999 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "bgallusser@chanzuckerberg.com",
            "name": "Benjamin Gallusser",
            "username": "bentaculum"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "229435acd97451ae20994a4196666e57cd03db3f",
          "message": "Constrain pydantic to version 2 or higher (#84)\n\n# Types of Changes\n- Maintenance (e.g. dependencies, CI, releases, etc.)\n\n# Checklist\n- [x] I have read the developer/contributing docs.",
          "timestamp": "2025-07-17T11:19:19-04:00",
          "tree_id": "837ab8e33b6bcf99bdb7c654e651958e5bb0cce3",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/229435acd97451ae20994a4196666e57cd03db3f"
        },
        "date": 1752765722592,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13459249697664036,
            "unit": "iter/sec",
            "range": "stddev: 0.015091190036101829",
            "extra": "mean: 7.429834667333338 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.078239779264326,
            "unit": "iter/sec",
            "range": "stddev: 0.000515876546779518",
            "extra": "mean: 43.330861000001164 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06266314144043875,
            "unit": "iter/sec",
            "range": "stddev: 0.5022254919808535",
            "extra": "mean: 15.958344523 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "45037215+TeunHuijben@users.noreply.github.com",
            "name": "Teun Huijben",
            "username": "TeunHuijben"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f102322b739e8989d0289889de992e2c2dd0cf07",
          "message": "Elaborated error message when provided path that doesn't have .zattrs (#95)\n\n# Proposed Change\n- Added  error message when the provided path doesn't have .zattrs\n- Made a little fix in `utils` due to pre-commit",
          "timestamp": "2025-07-17T14:09:09-04:00",
          "tree_id": "af554e07791db74a3de9f11a77fb480bc6cdb53b",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/f102322b739e8989d0289889de992e2c2dd0cf07"
        },
        "date": 1752775876230,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13707957027818363,
            "unit": "iter/sec",
            "range": "stddev: 0.015631569188810146",
            "extra": "mean: 7.295033081666664 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.016469964450714,
            "unit": "iter/sec",
            "range": "stddev: 0.00037115725092269007",
            "extra": "mean: 43.44714900002108 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06351632223060326,
            "unit": "iter/sec",
            "range": "stddev: 0.5084517781962051",
            "extra": "mean: 15.743984614999997 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "63270704+melisande-c@users.noreply.github.com",
            "name": "Melisande Croft",
            "username": "melisande-c"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e4a08f3c724f7ca62a91e0ac00269955436cb39c",
          "message": "Test: Fixture for path to example GEFF file (#98)\n\n# Proposed Change\nAdd pytest fixture for a path to example data and the expected graph\nattributes. This can be used as an initial first pass test for new\nbackends, an example test for the networkx API has been added.\n\n# Types of Changes\n- Tests\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the developer/contributing docs.\n- [x] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [x] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\n---------\n\nCo-authored-by: melisande-c <melisande.croft@fht.org>\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>",
          "timestamp": "2025-07-18T10:52:33-04:00",
          "tree_id": "3d6fc036f9972ce87286fe03ad81819f92fd540a",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/e4a08f3c724f7ca62a91e0ac00269955436cb39c"
        },
        "date": 1752850480917,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13710388386434388,
            "unit": "iter/sec",
            "range": "stddev: 0.03969404147141159",
            "extra": "mean: 7.293739402666669 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.03200004668072,
            "unit": "iter/sec",
            "range": "stddev: 0.0003335958069263467",
            "extra": "mean: 43.41785333332856 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06351249162701936,
            "unit": "iter/sec",
            "range": "stddev: 0.42743992903414013",
            "extra": "mean: 15.744934175666666 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "talley.lambert@gmail.com",
            "name": "Talley Lambert",
            "username": "tlambert03"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "27ffa207e4029e86ce321c12b441cc0718b6aa6a",
          "message": "ensure consistent model after mutation (#105)\n\nthis change makes it so that it's not possible to mutate a\n`GeffMetadata` instance into an invalid state",
          "timestamp": "2025-07-18T11:16:49-04:00",
          "tree_id": "7a3ca48c8d326fbcf9a1d7433a7906a3668faab7",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/27ffa207e4029e86ce321c12b441cc0718b6aa6a"
        },
        "date": 1752851966843,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13509101706210153,
            "unit": "iter/sec",
            "range": "stddev: 0.01734128726867922",
            "extra": "mean: 7.402416694666667 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.181676078141543,
            "unit": "iter/sec",
            "range": "stddev: 0.0006759000589720924",
            "extra": "mean: 43.13751933333757 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.0636878828029682,
            "unit": "iter/sec",
            "range": "stddev: 0.5198899222226586",
            "extra": "mean: 15.70157392566667 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mkitti@users.noreply.github.com",
            "name": "Mark Kittisopikul",
            "username": "mkitti"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4f3dcee534bc135158ad6fbc7057bad46a7ff7ae",
          "message": "Run ruff format (#116)\n\nRun ruff format",
          "timestamp": "2025-07-18T11:48:11-04:00",
          "tree_id": "6864a79819bbb5053ae6724ac01b0790798bf1ac",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/4f3dcee534bc135158ad6fbc7057bad46a7ff7ae"
        },
        "date": 1752853814368,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13545450495890252,
            "unit": "iter/sec",
            "range": "stddev: 0.02343941505245835",
            "extra": "mean: 7.382552542666663 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.361758077572567,
            "unit": "iter/sec",
            "range": "stddev: 0.0014061393598549508",
            "extra": "mean: 42.804997666678446 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06387438114275057,
            "unit": "iter/sec",
            "range": "stddev: 0.49465154499529906",
            "extra": "mean: 15.655728981000001 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "17995243+DragaDoncila@users.noreply.github.com",
            "name": "Draga Doncila Pop",
            "username": "DragaDoncila"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3f7a50ee40cb96175b018f03b9aeedaac51a47b9",
          "message": "Add link to contributing docs in PR template (#122)\n\n# Proposed Change\n\nLink to the contributing docs from the PR template.\n\n# Types of Changes\n- Documentation update\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [ ] I have read the developer/contributing docs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\nCo-authored-by: Draga Doncila <ddon0001@student.monash.edu>",
          "timestamp": "2025-07-18T13:17:57-04:00",
          "tree_id": "ed0f1aa2f99ae2c0e32274a13b962f26ecb9c2a5",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/3f7a50ee40cb96175b018f03b9aeedaac51a47b9"
        },
        "date": 1752859226587,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13658235011980957,
            "unit": "iter/sec",
            "range": "stddev: 0.020829630851159565",
            "extra": "mean: 7.321590228333335 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.200852213702568,
            "unit": "iter/sec",
            "range": "stddev: 0.0005592006428735924",
            "extra": "mean: 43.10186500000176 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06360826325989417,
            "unit": "iter/sec",
            "range": "stddev: 0.4446939799008658",
            "extra": "mean: 15.721227852333342 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "georgeoshardo@protonmail.com",
            "name": "Georgeos Hardo",
            "username": "georgeoshardo"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "98769fc9b152615622a27a614d27b62efa0ef22c",
          "message": "Use os.path.expanduser to support tildes in paths (#120)\n\n# Proposed Change\n\nUse os.path.expanduser to support tildes in paths. Closes #118 \n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n\nWhich topics does your change affect? Delete those that do not apply.\n- `networkx` implementation\n\n# Checklist\n\n- [ ] I have read the developer/contributing docs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.",
          "timestamp": "2025-07-18T13:22:31-04:00",
          "tree_id": "b7a2a87f7130f36077689ed037263a42d830d743",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/98769fc9b152615622a27a614d27b62efa0ef22c"
        },
        "date": 1752859475107,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.13529507037531344,
            "unit": "iter/sec",
            "range": "stddev: 0.006971001439456599",
            "extra": "mean: 7.3912522993333285 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.142726750121128,
            "unit": "iter/sec",
            "range": "stddev: 0.0005796251882055555",
            "extra": "mean: 43.210120000002426 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06400962840272623,
            "unit": "iter/sec",
            "range": "stddev: 0.44703487833697075",
            "extra": "mean: 15.622649669333327 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "jordao.bragantini@gmail.com",
            "name": "Jordão Bragantini",
            "username": "JoOkuma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "36232c43a46382186c23187c1198bada6052aba5",
          "message": "General `geff` writer helper (#97)\n\n# Proposed Change\n\nThis PR adds a `geff` writer abstract class to simplify the writing of\nalternative backends.\n\n# Types of Changes\n\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- New feature or enhancement\n\nWhich topics does your change affect? Delete those that do not apply.\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [X] I have read the developer/contributing docs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [X] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\n# Further Comments\nI had to change more things than I expected.\nPartially addresses #91 \n\ncc @msschwartz21",
          "timestamp": "2025-07-18T13:30:14-04:00",
          "tree_id": "8d97ba15166152d83f53689f7028521570adff45",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/36232c43a46382186c23187c1198bada6052aba5"
        },
        "date": 1752859977812,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11513522504323612,
            "unit": "iter/sec",
            "range": "stddev: 1.376757616630841",
            "extra": "mean: 8.685439227000037 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 22.54650560615611,
            "unit": "iter/sec",
            "range": "stddev: 0.0002152209202789327",
            "extra": "mean: 44.352770999997425 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06316757157527808,
            "unit": "iter/sec",
            "range": "stddev: 0.5561047611782917",
            "extra": "mean: 15.83090777533342 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1f344009517550c411a10fd81e41f4997f117a30",
          "message": "Fix installs in ci after switching to groups instead of optional deps (#127)\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Maintenance (e.g. dependencies, CI, releases, etc.)",
          "timestamp": "2025-07-18T15:08:40-04:00",
          "tree_id": "63c5105246ef12bee86f423a311b4f6a338f64ca",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/1f344009517550c411a10fd81e41f4997f117a30"
        },
        "date": 1752865847072,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11318826331955958,
            "unit": "iter/sec",
            "range": "stddev: 1.124769251399605",
            "extra": "mean: 8.834838265666669 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.31005011567591,
            "unit": "iter/sec",
            "range": "stddev: 0.0003073747958332697",
            "extra": "mean: 42.89995066666563 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06424243523911984,
            "unit": "iter/sec",
            "range": "stddev: 0.47055259967538815",
            "extra": "mean: 15.566035071333337 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "malinmayorc@janelia.hhmi.org",
            "name": "Caroline Malin-Mayor",
            "username": "cmalinmayor"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "913c6c8cd08412b84087b08bfbddde0c0e1e2a2a",
          "message": "102 nest geff metadata (#128)\n\n# Proposed Change\nNest the geff metadata under the \"geff\" key instead of in the main\nattrs.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- New feature or enhancement\n- Documentation update\n- Tests\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the [developer/contributing](../CONTRIBUTING) docs.\n- [x] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [x] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly.\n- [x] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.",
          "timestamp": "2025-07-18T15:10:15-04:00",
          "tree_id": "3e987528ff5eebb441448c63f5fdc8f8d31c6baf",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/913c6c8cd08412b84087b08bfbddde0c0e1e2a2a"
        },
        "date": 1752866902380,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11328561494179856,
            "unit": "iter/sec",
            "range": "stddev: 1.228961513662249",
            "extra": "mean: 8.827246076333331 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 22.973723168520902,
            "unit": "iter/sec",
            "range": "stddev: 0.0011862980982831853",
            "extra": "mean: 43.52799033333099 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06332434177199804,
            "unit": "iter/sec",
            "range": "stddev: 0.4701486259283807",
            "extra": "mean: 15.791715666000007 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mkitti@users.noreply.github.com",
            "name": "Mark Kittisopikul",
            "username": "mkitti"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2d4e206926426f77da87be722ddb33f1abe9d863",
          "message": "Add unit validation functions (#121)\n\n- **Run ruff format**\n- **Add units.py to check for known valid units**\n\nDoes not add validation\n\n# Proposed Change\nBriefly describe the contribution. If it resolves an issue or feature\nrequest, be sure to link to that issue.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n- New feature or enhancement\n- Documentation update\n- Tests\n- Maintenance (e.g. dependencies, CI, releases, etc.)\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [ ] I have read the developer/contributing docs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...\n\n---------\n\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>",
          "timestamp": "2025-07-18T16:04:43-04:00",
          "tree_id": "d167ea0f22b99812e447164012545a28880261a3",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/2d4e206926426f77da87be722ddb33f1abe9d863"
        },
        "date": 1752869237852,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.10631159603974798,
            "unit": "iter/sec",
            "range": "stddev: 1.4027314509186142",
            "extra": "mean: 9.406311609000001 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.037503958322986,
            "unit": "iter/sec",
            "range": "stddev: 0.0008881227336128459",
            "extra": "mean: 43.4074803333336 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06327865582753356,
            "unit": "iter/sec",
            "range": "stddev: 0.5896237574292282",
            "extra": "mean: 15.803116974000005 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "funkej@janelia.hhmi.org",
            "name": "Jan Funke",
            "username": "funkey"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "10691038d6f43853d17cc653f64b019958f1dbc4",
          "message": "Ensure that node/edge ID datasets have same dtype (#134)\n\n# Proposed Change\nSolves https://github.com/live-image-tracking-tools/geff/issues/133\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n\nWhich topics does your change affect? Delete those that do not apply.\n- `networkx` implementation\n\n# Checklist\n- [x] I have read the [developer/contributing](../CONTRIBUTING) docs.\n- [x] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [x] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.",
          "timestamp": "2025-07-18T16:32:45-04:00",
          "tree_id": "4a056c87c135caf12009ed2556c65c0f158463b4",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/10691038d6f43853d17cc653f64b019958f1dbc4"
        },
        "date": 1752870893569,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11389666949583145,
            "unit": "iter/sec",
            "range": "stddev: 1.2243515003430943",
            "extra": "mean: 8.779887984666658 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.021924407876043,
            "unit": "iter/sec",
            "range": "stddev: 0.0008101752968430476",
            "extra": "mean: 43.43685533333996 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06405206347257195,
            "unit": "iter/sec",
            "range": "stddev: 0.4822650266509218",
            "extra": "mean: 15.61229952299999 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "mkitti@users.noreply.github.com",
            "name": "Mark Kittisopikul",
            "username": "mkitti"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "54c8be4e4dfffde162dd0b83722874e6bd967c1c",
          "message": "Add win-64, osx-64, and linux-64 platforms for pixi (#140)\n\n# Proposed Change\n\nFix #136 by adding win-64, linux-64, and osx-64 platforms for pixi.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- New feature or enhancement\n- Maintenance (e.g. dependencies, CI, releases, etc.)\n\nWhich topics does your change affect? Delete those that do not apply.\n\nFix #136\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the [developer/contributing](../CONTRIBUTING) docs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...",
          "timestamp": "2025-07-18T20:55:03-04:00",
          "tree_id": "4b3d570687145f58a88ceb6d8309c905f3c57ccb",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/54c8be4e4dfffde162dd0b83722874e6bd967c1c"
        },
        "date": 1752886658223,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.10840839780739096,
            "unit": "iter/sec",
            "range": "stddev: 1.3574327180649337",
            "extra": "mean: 9.224377633333338 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 22.760753278053464,
            "unit": "iter/sec",
            "range": "stddev: 0.0017768480040686557",
            "extra": "mean: 43.93527700000277 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06407231184712557,
            "unit": "iter/sec",
            "range": "stddev: 0.531920857471153",
            "extra": "mean: 15.607365664999994 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "91a7e217a09ef3337503fdf575d283b352a5009d",
          "message": "Add checklist items for spec updates and implementation updates (#132)\n\nCloses #92",
          "timestamp": "2025-07-18T20:59:26-04:00",
          "tree_id": "4646d63f89bda26a5ea7d993889d85bc7d6dc4ab",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/91a7e217a09ef3337503fdf575d283b352a5009d"
        },
        "date": 1752886916732,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11077763733304812,
            "unit": "iter/sec",
            "range": "stddev: 1.2990164654886138",
            "extra": "mean: 9.027092688333331 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.196226802766237,
            "unit": "iter/sec",
            "range": "stddev: 0.0011802026467805321",
            "extra": "mean: 43.11045966668795 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06259611375188044,
            "unit": "iter/sec",
            "range": "stddev: 0.5330580916081966",
            "extra": "mean: 15.975432659666657 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "17995243+DragaDoncila@users.noreply.github.com",
            "name": "Draga Doncila Pop",
            "username": "DragaDoncila"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "0b714b3daf6ca4bfe9b641ec9c6f8a1a8ff70d0d",
          "message": "Expose test fixture in pytest plugin (#135)\n\n# Proposed Change\nExpose example geff fixture in pytest plugin for use by other packages\nwith a geff dependency.\n\n# Types of Changes\n- Tests\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [ ] I have read the [developer/contributing](../CONTRIBUTING) docs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\n---------\n\nCo-authored-by: Draga Doncila <ddon0001@student.monash.edu>\nCo-authored-by: Teun Huijben <45037215+TeunHuijben@users.noreply.github.com>",
          "timestamp": "2025-07-19T12:03:37-04:00",
          "tree_id": "f2a772e895d6cd0dd628225bef775c21a6c39bb7",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/0b714b3daf6ca4bfe9b641ec9c6f8a1a8ff70d0d"
        },
        "date": 1752941140578,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11101718772907468,
            "unit": "iter/sec",
            "range": "stddev: 1.2772644251410599",
            "extra": "mean: 9.007614230333331 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 23.532006376050777,
            "unit": "iter/sec",
            "range": "stddev: 0.0002052476483375676",
            "extra": "mean: 42.495313999988106 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06290447820752318,
            "unit": "iter/sec",
            "range": "stddev: 0.4273898292602204",
            "extra": "mean: 15.897119386333344 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "611e7a27eca108a7620708fe5c6605e397218021",
          "message": "Specification updates: switch to an OME-like list of spatiotemporal axes with metadata (#147)\n\n# Proposed Change\nContinuing PR discussion started in #131\n\nThis PR is intended to close #80 and its subissues, but we need to go\nthrough and check that all of the subissues are actually addressed.\n\n- [x] #83 -- complete with the Axes basemodel \n- [x] #87 -- already closed by another PR\n- [x] #102 -- already closed by another PR\n- [x] #104 -- completed with this PR\n- [x] #89 -- already closed by another PR\n\nRemaining to dos:\n\n- [ ] Compute min/max for axes props -> deferring on this until we have\nthe helper functions from #148\n- [x] Validation/special handling for axes props, e.g. don't allow\nmissing nodes\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- New feature or enhancement\n- Documentation update\n- Tests\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly.\n\n## If you changed the specification\n- [ ] I have checked that any validation functions and tests reflect the\nchanges.\n- [ ] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [ ] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...\n\n---------\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>\nCo-authored-by: Teun Huijben <teun.huijben@czbiohub.org>\nCo-authored-by: Teun Huijben <45037215+TeunHuijben@users.noreply.github.com>",
          "timestamp": "2025-07-19T13:39:17-04:00",
          "tree_id": "846e45e307cc8bdf555075afcc0c7644bdfb4e05",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/611e7a27eca108a7620708fe5c6605e397218021"
        },
        "date": 1752946874145,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11745217868194315,
            "unit": "iter/sec",
            "range": "stddev: 1.212893816619275",
            "extra": "mean: 8.514103452333302 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 17.546505887950776,
            "unit": "iter/sec",
            "range": "stddev: 0.0009352885563250211",
            "extra": "mean: 56.99140366668113 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06366631454206821,
            "unit": "iter/sec",
            "range": "stddev: 0.4672057685052953",
            "extra": "mean: 15.70689315366667 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "msschwartz21@gmail.com",
            "name": "Morgan Schwartz",
            "username": "msschwartz21"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "611e7a27eca108a7620708fe5c6605e397218021",
          "message": "Specification updates: switch to an OME-like list of spatiotemporal axes with metadata (#147)\n\n# Proposed Change\nContinuing PR discussion started in #131\n\nThis PR is intended to close #80 and its subissues, but we need to go\nthrough and check that all of the subissues are actually addressed.\n\n- [x] #83 -- complete with the Axes basemodel \n- [x] #87 -- already closed by another PR\n- [x] #102 -- already closed by another PR\n- [x] #104 -- completed with this PR\n- [x] #89 -- already closed by another PR\n\nRemaining to dos:\n\n- [ ] Compute min/max for axes props -> deferring on this until we have\nthe helper functions from #148\n- [x] Validation/special handling for axes props, e.g. don't allow\nmissing nodes\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- New feature or enhancement\n- Documentation update\n- Tests\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly.\n\n## If you changed the specification\n- [ ] I have checked that any validation functions and tests reflect the\nchanges.\n- [ ] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [ ] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...\n\n---------\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>\nCo-authored-by: Teun Huijben <teun.huijben@czbiohub.org>\nCo-authored-by: Teun Huijben <45037215+TeunHuijben@users.noreply.github.com>",
          "timestamp": "2025-07-19T13:39:17-04:00",
          "tree_id": "846e45e307cc8bdf555075afcc0c7644bdfb4e05",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/611e7a27eca108a7620708fe5c6605e397218021"
        },
        "date": 1752947139038,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12131271353773183,
            "unit": "iter/sec",
            "range": "stddev: 1.1248927991056572",
            "extra": "mean: 8.243159112 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 17.846529271237596,
            "unit": "iter/sec",
            "range": "stddev: 0.0006812740053680847",
            "extra": "mean: 56.033303999991325 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.063947367515844,
            "unit": "iter/sec",
            "range": "stddev: 0.5257912524295439",
            "extra": "mean: 15.637860303666665 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ysk@yfukai.net",
            "name": "Yohsuke T. Fukai",
            "username": "yfukai"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5b4949fd7b581e35055c1722c2d25fee517faf7d",
          "message": "Adding Python 3.13 (#142)\n\n# Proposed Change\nAdding missing Python 3.13 to tests and `pyproject.toml`.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Documentation update\n- Maintenance (e.g. dependencies, CI, releases, etc.)\n\nWhich topics does your change affect? Delete those that do not apply.\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the [developer/contributing](../CONTRIBUTING) docs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>",
          "timestamp": "2025-07-19T14:26:43-04:00",
          "tree_id": "b5a9774d50e670ee6dc604ea1e4c45405a81dce7",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/5b4949fd7b581e35055c1722c2d25fee517faf7d"
        },
        "date": 1752949752411,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11967328961205807,
            "unit": "iter/sec",
            "range": "stddev: 1.1499715345887092",
            "extra": "mean: 8.356083493999998 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 17.601583269454817,
            "unit": "iter/sec",
            "range": "stddev: 0.000766546405031905",
            "extra": "mean: 56.813071000002914 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.0643029078898041,
            "unit": "iter/sec",
            "range": "stddev: 0.48034258083972875",
            "extra": "mean: 15.551396240333332 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "45037215+TeunHuijben@users.noreply.github.com",
            "name": "Teun Huijben",
            "username": "TeunHuijben"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5fc4c1df20fb26e5b44a974d4a725817872b5be0",
          "message": "removed lingering occurences of position_props (#156)\n\nRemoved two occurrences of `position_props` in the repo (one in a\ndocstring, one in a test script)",
          "timestamp": "2025-07-19T14:40:10-04:00",
          "tree_id": "490b8fa28358c863007dd761a20fd9ef588a098e",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/5fc4c1df20fb26e5b44a974d4a725817872b5be0"
        },
        "date": 1752950563659,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11928813514653684,
            "unit": "iter/sec",
            "range": "stddev: 1.1530442154301783",
            "extra": "mean: 8.383063401666666 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 17.41980607911731,
            "unit": "iter/sec",
            "range": "stddev: 0.0006574649183113956",
            "extra": "mean: 57.40592033333769 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06330787603184307,
            "unit": "iter/sec",
            "range": "stddev: 0.5129998673531103",
            "extra": "mean: 15.795822932000002 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ysk@yfukai.net",
            "name": "Yohsuke T. Fukai",
            "username": "yfukai"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6a96a4b6f5483d4eae42f1cfabb844e752a1823e",
          "message": "Remove supported versions list to solve \"File not found\" error in pytest (#158)\n\n# Proposed Change\nSolves #157 by removing `SUPPORTED_VERSIONS` from `metadata_schema.py`\nand adding regex pattern that generally matches with a version string.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n\n---------\n\nCo-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>",
          "timestamp": "2025-07-19T17:08:39-04:00",
          "tree_id": "0d1e6d79691acce7010277350857884754b2bfef",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/6a96a4b6f5483d4eae42f1cfabb844e752a1823e"
        },
        "date": 1752959439311,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12055202325605684,
            "unit": "iter/sec",
            "range": "stddev: 1.0919066322118538",
            "extra": "mean: 8.295173925666631 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 17.66972190491344,
            "unit": "iter/sec",
            "range": "stddev: 0.001291233870514645",
            "extra": "mean: 56.593986333306624 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.0634837008237893,
            "unit": "iter/sec",
            "range": "stddev: 0.46384384072778023",
            "extra": "mean: 15.752074737666666 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ilanfsilva@gmail.com",
            "name": "Ilan F. S. Theodoro",
            "username": "ilan-theodoro"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c9b695365ea8a7c77d18a35710107aa28ea95307",
          "message": "`read_nx` and `write_nx` now handle graph and the GeffMetadata as a tuple (#163)\n\n# Proposed Change\nCloses #150.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n- New feature or enhancement\n- Tests\n\nWhich topics does your change affect? Delete those that do not apply.\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [x] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [x] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly.\n\n## If you changed the specification\n- [x] I have checked that any validation functions and tests reflect the\nchanges.\n- [x] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [ ] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n## If you have added or changed an implementation\n- [x] I wrote tests for the new implementation using standard fixtures\nsupplied in conftest.py.\n- [ ] I updated pyproject.toml with new dependencies if needed.\n- [ ] I added a function to tests/bench.py to benchmark the new\nimplementation.\n\n---------\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>",
          "timestamp": "2025-07-19T17:22:31-04:00",
          "tree_id": "a28fcf4f68d603cf680661e6f28e63c0a70dcc77",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/c9b695365ea8a7c77d18a35710107aa28ea95307"
        },
        "date": 1752960303331,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11807545645790914,
            "unit": "iter/sec",
            "range": "stddev: 1.1712546800167298",
            "extra": "mean: 8.469160568999996 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 17.14564992429253,
            "unit": "iter/sec",
            "range": "stddev: 0.0016778474281802485",
            "extra": "mean: 58.323831666664695 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06341940193169764,
            "unit": "iter/sec",
            "range": "stddev: 0.5275798329624102",
            "extra": "mean: 15.76804525966667 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "45037215+TeunHuijben@users.noreply.github.com",
            "name": "Teun Huijben",
            "username": "TeunHuijben"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "1457d3b11ff8f2594613f125cdcae8222759c2c8",
          "message": "removed $ from regex version pattern (#166)\n\nremoved $ from regex version pattern to not force the version string to\nend after the git commit\n\n# Proposed Change\nBriefly describe the contribution. If it resolves an issue or feature\nrequest, be sure to link to that issue.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n\nWhich topics does your change affect? Delete those that do not apply.\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [ ] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n\n## If you changed the specification\n- [ ] I have checked that any validation functions and tests reflect the\nchanges.\n- [ ] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [ ] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n## If you have added or changed an implementation\n- [ ] I wrote tests for the new implementation using standard fixtures\nsupplied in conftest.py.\n- [ ] I updated pyproject.toml with new dependencies if needed.\n- [ ] I added a function to tests/bench.py to benchmark the new\nimplementation.\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...",
          "timestamp": "2025-07-19T18:05:12-04:00",
          "tree_id": "8045daa8f380a0824c80e4a39cfdcfffcea04843",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/1457d3b11ff8f2594613f125cdcae8222759c2c8"
        },
        "date": 1752962830823,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11988207305490246,
            "unit": "iter/sec",
            "range": "stddev: 1.153197287865622",
            "extra": "mean: 8.341530760333361 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 17.738028721191913,
            "unit": "iter/sec",
            "range": "stddev: 0.0014568124930760843",
            "extra": "mean: 56.37605033333178 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06417517438370678,
            "unit": "iter/sec",
            "range": "stddev: 0.46573041013878413",
            "extra": "mean: 15.582349554999988 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "63270704+melisande-c@users.noreply.github.com",
            "name": "Melisande Croft",
            "username": "melisande-c"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "29fbf6851b4a77855df1076ed2ec42aeaada4cec",
          "message": "feat: FileReader class to read zarr to intermediate dict format (#129)\n\n# Proposed Change\nAdding a file reader class that allows a subset of the zarr to be read.\nFollows a builder pattern, this allows each `node_prop` and `edge_prop`\nto be read when required. When the `build` method is called, output\nboolean masks can be provided to read only a subset of nodes and edges.\n\nThe `build` method outputs a new intermediate dictionary representation\nof the graph defined as a `TypedDict`, this mirrors the structure in the\nzarr file. This allows for reusability of the `FileReader` for different\nbackends.\n\nA `read_to_dict` function has been added that outputs the intermediated\ndict representation. The `read_nx` function now uses this and can also\naccept a list of `node_props` and `edge_props` so that not all the\nproperties need to be read.\n\nTests have been added for the `FileReader`, it is also tested through\nthe `read_nx` texts.\n\n# Types of Changes\n- New feature or enhancement\n\nWhich topics does your change affect? Delete those that do not apply.\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the [developer/contributing](../CONTRIBUTING) docs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...\n\n---------\n\nCo-authored-by: melisande-c <melisande.croft@fht.org>\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>",
          "timestamp": "2025-07-21T06:37:31-04:00",
          "tree_id": "940b1db32a0182d673a4a246ba92860ce10d04a7",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/29fbf6851b4a77855df1076ed2ec42aeaada4cec"
        },
        "date": 1753094376009,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12017020146899031,
            "unit": "iter/sec",
            "range": "stddev: 1.1541451326126924",
            "extra": "mean: 8.321530527333335 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 17.16404571593266,
            "unit": "iter/sec",
            "range": "stddev: 0.0011426586754032706",
            "extra": "mean: 58.26132233333207 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06308338202851217,
            "unit": "iter/sec",
            "range": "stddev: 0.5342171535121121",
            "extra": "mean: 15.85203531966666 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "malinmayorc@janelia.hhmi.org",
            "name": "Caroline Malin-Mayor",
            "username": "cmalinmayor"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "827fd2ec539e43d1b66ee724fb1b7c1f3d5881f6",
          "message": "Refactor helper functions to provide write_array and write_dict (#148)\n\n- Creates a helper for writing node/edge id arrays together, that checks\nif the dtypes match\n- Creates a helper for writing node or edge properties that are already\nin array form\n- Refactors the prior dictionary property writer to return the arrays\ninstead of writing them\n- Uses the refactored dictionary helper in a write_dict_like function\nthat writes the whole graph to geff\n- Uses this function in write_nx\n\nOpen todos and questions:\n- [ ] test the helpers directly, not just through the nx implementation\n- [x] is it too inefficient memory-wise to have the graph and all of the\nproperties attrs?\n- [ ] Can update/add new attrs with the same helper function, I think,\nbut should be documented and tested\n- [ ] We now enforce that node and edge ids must be the same dtype -\nshould we add this explicitly to the spec?\n\n# Proposed Change\nBriefly describe the contribution. If it resolves an issue or feature\nrequest, be sure to link to that issue.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n- New feature or enhancement\n- Documentation update\n- Tests\n- Maintenance (e.g. dependencies, CI, releases, etc.)\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n\n## If you have added or changed an implementation\n- [ ] I wrote tests for the new implementation using standard fixtures\nsupplied in conftest.py.\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...\n\n---------\n\nCo-authored-by: Teun Huijben <teun.huijben@czbiohub.org>\nCo-authored-by: Teun Huijben <45037215+TeunHuijben@users.noreply.github.com>\nCo-authored-by: Jan Funke <funkej@janelia.hhmi.org>",
          "timestamp": "2025-07-21T11:41:59-04:00",
          "tree_id": "c363756187357de9c9b53cfba093fef685eb51e9",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/827fd2ec539e43d1b66ee724fb1b7c1f3d5881f6"
        },
        "date": 1753112664000,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12291331851136995,
            "unit": "iter/sec",
            "range": "stddev: 1.1860935183922825",
            "extra": "mean: 8.135814833666672 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.569821276845158,
            "unit": "iter/sec",
            "range": "stddev: 0.0013923564712788002",
            "extra": "mean: 51.09908700000195 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06529075164657311,
            "unit": "iter/sec",
            "range": "stddev: 0.4747900302255456",
            "extra": "mean: 15.316104881333322 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "33941387+lxenard@users.noreply.github.com",
            "name": "Laura Xénard",
            "username": "lxenard"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "14601721a06d2c0e4c0b36a07786143af7a8777e",
          "message": "Add current geff version as default value in GeffMetadata (#154)\n\n# Proposed Change\nAs the title says, when not provided, geff version in GeffMetadata\ndefaults to the current version of geff\nSolves #107 .\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- New feature or enhancement\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n\n## If you changed the specification\n- [x] I have checked that any validation functions and tests reflect the\nchanges.\n- [x] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [x] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n## If you have added or changed an implementation\n- [ ] I wrote tests for the new implementation using standard fixtures\nsupplied in conftest.py.\n- [ ] I updated pyproject.toml with new dependencies if needed.\n- [ ] I added a function to tests/bench.py to benchmark the new\nimplementation.\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...\n\n---------\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>",
          "timestamp": "2025-07-21T12:50:16-04:00",
          "tree_id": "30bbe8f2d67d477636557175a50c0863ca95cea1",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/14601721a06d2c0e4c0b36a07786143af7a8777e"
        },
        "date": 1753116738525,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11755103950651265,
            "unit": "iter/sec",
            "range": "stddev: 1.3085633419925777",
            "extra": "mean: 8.50694306233334 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.275319312531384,
            "unit": "iter/sec",
            "range": "stddev: 0.0013577209016672294",
            "extra": "mean: 51.87981499999713 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06462320523336193,
            "unit": "iter/sec",
            "range": "stddev: 0.47890913246296624",
            "extra": "mean: 15.474317567333335 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "funkej@janelia.hhmi.org",
            "name": "Jan Funke",
            "username": "funkey"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e9a7e4a058143fd6a30789bded6d812a4f389d23",
          "message": "Use array/dict IO helper functions and add SpatialGraph (#169)\n\n# Proposed Change\nThis PR supersedes\nhttps://github.com/live-image-tracking-tools/geff/pull/123 and\nhttps://github.com/live-image-tracking-tools/geff/pull/148. Those were\nmutually depending on each other, so this is an attempt to merge both\ninto a consistent state.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n- New feature or enhancement\n- Documentation update\n- Tests\n\nWhich topics does your change affect? Delete those that do not apply.\n- `networkx` implementation\n- `spatial_graph` implementation\n\n# Checklist\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [x] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly.\n\n## If you have added or changed an implementation\n- [x] I wrote tests for the new implementation using standard fixtures\nsupplied in conftest.py.\n- [x] I updated pyproject.toml with new dependencies if needed.\n- [ ] I added a function to tests/bench.py to benchmark the new\nimplementation.\n\n---------\n\nCo-authored-by: Caroline Malin-Mayor <malinmayorc@janelia.hhmi.org>\nCo-authored-by: Teun Huijben <teun.huijben@czbiohub.org>\nCo-authored-by: Teun Huijben <45037215+TeunHuijben@users.noreply.github.com>\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>\nCo-authored-by: Talley Lambert <talley.lambert@gmail.com>",
          "timestamp": "2025-07-21T13:41:18-04:00",
          "tree_id": "7f86dd9730bd658de5d15a4d9507bea09f91df3f",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/e9a7e4a058143fd6a30789bded6d812a4f389d23"
        },
        "date": 1753119829291,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11082379229430092,
            "unit": "iter/sec",
            "range": "stddev: 1.4165692861278198",
            "extra": "mean: 9.023333160666661 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 18.83950980801092,
            "unit": "iter/sec",
            "range": "stddev: 0.0009955734842864961",
            "extra": "mean: 53.0799373333366 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06453164994045288,
            "unit": "iter/sec",
            "range": "stddev: 0.6344430877150187",
            "extra": "mean: 15.496271998666677 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "talley.lambert@gmail.com",
            "name": "Talley Lambert",
            "username": "tlambert03"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "eb999475d23289059fda4bc00d41b6dd076a4d3c",
          "message": "Fix docs styling and autogenerate html docs at mkdocs build-time (#168)\n\nThis PR updates documentation in a few ways:\n\n1. fixes styles. The styles created by json-schema-for-humans was using\na relative path that was not valid when served by mkdocs... but they\nalso needed tweaking anyway. So this commits the styles and js to source\n(in the docs folder) and tells mkdocs how to load them (in mkdocs.yml)\n2. removes the need to run `generate-schema-doc` manually before running\n`mike/mkdocs build/serve`. Now you can just checkout the repo and run\n`uv run --group docs mkdocs serve` and it will autogenerate the schema\nand place it where it needs to go.\n\n---------\n\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>",
          "timestamp": "2025-07-21T13:56:46-04:00",
          "tree_id": "ab8ee1ec575f2abe6278d22036931c5866775ff3",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/eb999475d23289059fda4bc00d41b6dd076a4d3c"
        },
        "date": 1753120721475,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12085557853381863,
            "unit": "iter/sec",
            "range": "stddev: 1.2611158913207976",
            "extra": "mean: 8.274338778 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.55702567600853,
            "unit": "iter/sec",
            "range": "stddev: 0.0013105942891149611",
            "extra": "mean: 51.1325196666661 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06547649783235497,
            "unit": "iter/sec",
            "range": "stddev: 0.5486298691905883",
            "extra": "mean: 15.27265558033334 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "talley.lambert@gmail.com",
            "name": "Talley Lambert",
            "username": "tlambert03"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9b0dd4321244a13417927c13f752be6a3f062cbf",
          "message": "Update pre-commit hooks and fix linting issues (#171)\n\nThis makes a couple small changes to linting rules, and then reruns\npre-commit:\n\n1. adds `target-version = \"py310\"` to ruff rules, (matching the project\nmin)\n2. adds fix=true to ruff rules in pyproject (convenient when running\nruff format in vscode)\n3. puts ruff rules in a `[tool.ruff.lint]` section (removing warnings\nfrom ruff when running ruff)\n4. runs pre-commit, which makes some changes due to the higher\ntarget-version, along with the `UP` rule\n\n---------\n\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>",
          "timestamp": "2025-07-21T15:00:29-04:00",
          "tree_id": "c5d542b036b1d62bc46fe710dab5f948fc21dbe5",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/9b0dd4321244a13417927c13f752be6a3f062cbf"
        },
        "date": 1753124592059,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12144779556639942,
            "unit": "iter/sec",
            "range": "stddev: 1.1709096071845848",
            "extra": "mean: 8.23399054166667 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.19054228666099,
            "unit": "iter/sec",
            "range": "stddev: 0.0016819014199244513",
            "extra": "mean: 52.10900166667424 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06543321426524107,
            "unit": "iter/sec",
            "range": "stddev: 0.5189815032443579",
            "extra": "mean: 15.282758324333338 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "talley.lambert@gmail.com",
            "name": "Talley Lambert",
            "username": "tlambert03"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "68311a277d00867b40faee03c44a2c4683c43680",
          "message": "Test docs on PR (#184)\n\n# Proposed Change\nrun `mkdocs build --strict` on PRs\n\n# Types of Changes\n- Documentation\n- Tests",
          "timestamp": "2025-07-21T16:41:51-04:00",
          "tree_id": "23e8bdf41a20301bf358f26a22f92c155bb380e9",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/68311a277d00867b40faee03c44a2c4683c43680"
        },
        "date": 1753130633717,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12334156906382879,
            "unit": "iter/sec",
            "range": "stddev: 1.17313169594428",
            "extra": "mean: 8.10756671566667 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.280760658916197,
            "unit": "iter/sec",
            "range": "stddev: 0.0011966164850848672",
            "extra": "mean: 51.86517366666029 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06539413937324035,
            "unit": "iter/sec",
            "range": "stddev: 0.46260948228242404",
            "extra": "mean: 15.291890214999995 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "17995243+DragaDoncila@users.noreply.github.com",
            "name": "Draga Doncila Pop",
            "username": "DragaDoncila"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "aa55f552e3dd286d9b4d225b1d85de7b6779de98",
          "message": "Add descriptions for each metadata field (#181)\n\n# Proposed Change\nAdd descriptions to the `directed` and `axes` fields so they can be\ndisplayed in the docs schema listing.\n\n# Types of Changes\n- Documentation update\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [ ] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n\n---------\n\nCo-authored-by: Draga Doncila <ddon0001@student.monash.edu>\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>",
          "timestamp": "2025-07-21T17:50:51-04:00",
          "tree_id": "429e539faa4998ea2bcdb6fdbdf170c791f56ee8",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/aa55f552e3dd286d9b4d225b1d85de7b6779de98"
        },
        "date": 1753134906521,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12336835764886225,
            "unit": "iter/sec",
            "range": "stddev: 1.1444536418956204",
            "extra": "mean: 8.105806213666673 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 18.85002589522105,
            "unit": "iter/sec",
            "range": "stddev: 0.001698697497700388",
            "extra": "mean: 53.05032500000569 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06600863458579372,
            "unit": "iter/sec",
            "range": "stddev: 0.44194016755749543",
            "extra": "mean: 15.149533182666659 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ilan.silva@czbiohub.org",
            "name": "Ilan F. S. Theodoro",
            "username": "ilan-theodoro"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a34ef9b547bda25be747e87b237ebaf97e8df59c",
          "message": "Implement coordinates transformation (#179)\n\n# Proposed Change\nThis pull request introduces an `Affine` class for handling affine\ntransformations, integrates it into the metadata schema, and adds\ncomprehensive tests for validation, properties, and functionality. The\nchanges enhance the library's ability to represent and manipulate\nspatial transformations in a structured and validated manner. Closes\n#149.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n- New feature or enhancement\n- Tests\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [x] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly.\n\n## If you changed the specification\n- [x] I have checked that any validation functions and tests reflect the\nchanges.\n- [x] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [ ] I have updated docs/specification.md to reflect the change.\n- [x] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n## If you have added or changed an implementation\n- [x] I wrote tests for the new implementation using standard fixtures\nsupplied in conftest.py.\n- [ ] I updated pyproject.toml with new dependencies if needed.\n- [ ] I added a function to tests/bench.py to benchmark the new\nimplementation.\n\n---------\n\nCo-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>",
          "timestamp": "2025-07-22T10:59:19-04:00",
          "tree_id": "1c47957828cf8aa766b46d607bf02c2f35509a53",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/a34ef9b547bda25be747e87b237ebaf97e8df59c"
        },
        "date": 1753196528178,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12493148666695858,
            "unit": "iter/sec",
            "range": "stddev: 1.0939888526829809",
            "extra": "mean: 8.004387258 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.227498214260926,
            "unit": "iter/sec",
            "range": "stddev: 0.0005875480311876782",
            "extra": "mean: 52.00884633333658 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06501177830154614,
            "unit": "iter/sec",
            "range": "stddev: 0.5004064089331546",
            "extra": "mean: 15.381828126000016 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ysk@yfukai.net",
            "name": "Yohsuke T. Fukai",
            "username": "yfukai"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3a71946b335c6619b163fc62e9be8cb3ba58d591",
          "message": "Added specs for `related_objects` (#186)\n\n# Proposed Change\nAdded schema, docs and tests for the `related_objects` attr.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- New feature or enhancement\n- Documentation update\n- Tests\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n- `networkx` implementation\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [x] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly.\n\n## If you changed the specification\n- [x] I have checked that any validation functions and tests reflect the\nchanges.\n- [x] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [x] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n---------\n\nCo-authored-by: Draga Doncila Pop <17995243+DragaDoncila@users.noreply.github.com>\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>",
          "timestamp": "2025-07-22T11:15:22-04:00",
          "tree_id": "5ce9e10ea5ad189369fc25fdf814bdc579a0b8be",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/3a71946b335c6619b163fc62e9be8cb3ba58d591"
        },
        "date": 1753197639788,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12037927869484323,
            "unit": "iter/sec",
            "range": "stddev: 1.1978449737582597",
            "extra": "mean: 8.307077520666667 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.040289201177405,
            "unit": "iter/sec",
            "range": "stddev: 0.001543569085192997",
            "extra": "mean: 52.52021066666165 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06374862208014766,
            "unit": "iter/sec",
            "range": "stddev: 0.5171585957836933",
            "extra": "mean: 15.686613567 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "funkej@janelia.hhmi.org",
            "name": "Jan Funke",
            "username": "funkey"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c557fde879fcd6e2fb8db3c60ef1acaa9679daeb",
          "message": "Add display_hints to geff schema (#155)\n\n# Proposed Change\nAdd `display_hints` to `geff` metadata.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- New feature or enhancement\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n\n# Checklist\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [x] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n\n## If you changed the specification\n- [ ] I have checked that any validation functions and tests reflect the\nchanges.\n- [x] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [x] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n---------\n\nCo-authored-by: Morgan Schwartz <msschwartz21@gmail.com>\nCo-authored-by: Ilan <ilan.silva@czbiohub.org>",
          "timestamp": "2025-07-22T13:03:46-04:00",
          "tree_id": "07b708ad691822cd7839990bd04c31e5b973b21b",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/c557fde879fcd6e2fb8db3c60ef1acaa9679daeb"
        },
        "date": 1753203975876,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.11837844573366639,
            "unit": "iter/sec",
            "range": "stddev: 1.3040977558875047",
            "extra": "mean: 8.447483777999999 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.131500778740893,
            "unit": "iter/sec",
            "range": "stddev: 0.00183288677836982",
            "extra": "mean: 52.26981466666795 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06477221994586026,
            "unit": "iter/sec",
            "range": "stddev: 0.5565154407949987",
            "extra": "mean: 15.438717413666666 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "17995243+DragaDoncila@users.noreply.github.com",
            "name": "Draga Doncila Pop",
            "username": "DragaDoncila"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d99e2a447eb90df5b21aaecc083221b029c95220",
          "message": "Add track-level node properties schema (#192)\n\n# Proposed Change\nCloses #151 \n\nThis PR adds a new, optional, `track_node_props` key to the geff\nmetadata that defines the node properties containing `tracklet` ID\nand/or `lineage` ID information. It also explicitly defines what is\nmeant by a `tracklet` and a `lineage`.\n\n# Types of Changes\n- New feature or enhancement\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly\nby looking at the docs preview (link left as a comment on the PR).\n\n## If you changed the specification\n- [x] I have checked that any validation functions and tests reflect the\nchanges.\n- [x] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [x] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n---------\n\nCo-authored-by: Draga Doncila <ddon0001@student.monash.edu>",
          "timestamp": "2025-07-22T13:58:32-04:00",
          "tree_id": "6e1daa2e6c37354e075ecfc34a6bf5726ac93f16",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/d99e2a447eb90df5b21aaecc083221b029c95220"
        },
        "date": 1753207259188,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12053332974956142,
            "unit": "iter/sec",
            "range": "stddev: 1.2208358602867921",
            "extra": "mean: 8.296460423666664 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.3335461140482,
            "unit": "iter/sec",
            "range": "stddev: 0.0014467361396084902",
            "extra": "mean: 51.7235686666595 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06425595652197026,
            "unit": "iter/sec",
            "range": "stddev: 0.5437095769890301",
            "extra": "mean: 15.562759534333319 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ilan.silva@czbiohub.org",
            "name": "Ilan F. S. Theodoro",
            "username": "ilan-theodoro"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f8cc42c6d70afd9da5937f9a10656d3ca979ac12",
          "message": "Read/write ignored attributes to avoid losing them (#141)\n\n# Proposed Change\n`geff` allows extra attributes inside `zattrs`. However, they are simply\nignored. This PR solves it by storing the extra attributes. Closes #110.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Bugfix (non-breaking change which fixes an issue)\n- Tests\n\nWhich topics does your change affect? Delete those that do not apply.\n- Specification\n\n# Checklist\n\n- [x] I have read the [developer/contributing](../CONTRIBUTING) docs.\n- [x] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [ ] I have written docstrings and checked that they render correctly.\n- [ ] If I changed the specification, I have checked that any validation\nfunctions and tests reflect the changes.\n\n---------\n\nCo-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>",
          "timestamp": "2025-07-22T15:17:23-04:00",
          "tree_id": "397f51e4ff5ab1617e623e836b461069526a2857",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/f8cc42c6d70afd9da5937f9a10656d3ca979ac12"
        },
        "date": 1753212002487,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12051372890750689,
            "unit": "iter/sec",
            "range": "stddev: 1.1458748826452625",
            "extra": "mean: 8.297809793666664 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.198790814076474,
            "unit": "iter/sec",
            "range": "stddev: 0.0015944264979458902",
            "extra": "mean: 52.08661366666926 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06470100738271957,
            "unit": "iter/sec",
            "range": "stddev: 0.4722995979358651",
            "extra": "mean: 15.455709894666668 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "jordao.bragantini@gmail.com",
            "name": "Jordão Bragantini",
            "username": "JoOkuma"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "e7e62dc8ff0cb0ae22cd6596cfa7ffbfeec49002",
          "message": "CTC to geff conversion (#160)",
          "timestamp": "2025-07-22T19:07:26-04:00",
          "tree_id": "5d1c0ab441e17de16b6de8b39149debd5243db99",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/e7e62dc8ff0cb0ae22cd6596cfa7ffbfeec49002"
        },
        "date": 1753225814161,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12015241711870658,
            "unit": "iter/sec",
            "range": "stddev: 1.0548415214277893",
            "extra": "mean: 8.322762238000033 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.18408758206783,
            "unit": "iter/sec",
            "range": "stddev: 0.0017402032262260566",
            "extra": "mean: 52.12653433331601 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06471343746404483,
            "unit": "iter/sec",
            "range": "stddev: 0.4482687051340619",
            "extra": "mean: 15.452741179999995 sec\nrounds: 3"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ilan.silva@czbiohub.org",
            "name": "Ilan F. S. Theodoro",
            "username": "ilan-theodoro"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "88ea2ee5ed03284e5b23a06ff55aa4ad79562745",
          "message": "Improve docs: affine and extra attributes (#205)\n\n# Proposed Change\nBriefly describe the contribution. If it resolves an issue or feature\nrequest, be sure to link to that issue.\n\n# Types of Changes\nWhat types of changes does your code introduce? Delete those that do not\napply.\n- Documentation update\n\nWhich topics does your change affect? Delete those that do not apply.\n\n# Checklist\nPut an x in the boxes that apply. You can also fill these out after\ncreating the PR. If you're unsure about any of them, don't hesitate to\nask. We're here to help! This is simply a reminder of what we are going\nto look for before merging your code.\n\n- [x] I have read the\n[developer/contributing](https://github.com/live-image-tracking-tools/geff/blob/main/CONTRIBUTING)\ndocs.\n- [ ] I have added tests that prove that my feature works in various\nsituations or tests the bugfix (if appropriate).\n- [ ] I have checked that I maintained or improved code coverage.\n- [x] I have written docstrings and checked that they render correctly\nby looking at the docs preview (link left as a comment on the PR).\n\n## If you changed the specification\n- [ ] I have checked that any validation functions and tests reflect the\nchanges.\n- [ ] I have updated the GeffMetadata and the json schema using `pixi\nrun update-schema` if necessary.\n- [x] I have updated docs/specification.md to reflect the change.\n- [ ] I have updated implementations to reflect the change. (This can\nhappen in separate PRs on a feature branch, but must be complete before\nmerging into main.)\n\n## If you have added or changed an implementation\n- [ ] I wrote tests for the new implementation using standard fixtures\nsupplied in conftest.py.\n- [ ] I updated pyproject.toml with new dependencies if needed.\n- [ ] I added a function to tests/bench.py to benchmark the new\nimplementation.\n\n# Further Comments\nIf this is a relatively large or complex change, kick off the discussion\nby explaining why you chose the solution you did and what alternatives\nyou considered, etc...",
          "timestamp": "2025-07-22T19:47:10-04:00",
          "tree_id": "5eca3b37b9a7e6bfbcab616fe82399083ecc7033",
          "url": "https://github.com/live-image-tracking-tools/geff/commit/88ea2ee5ed03284e5b23a06ff55aa4ad79562745"
        },
        "date": 1753228202459,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/bench.py::test_write",
            "value": 0.12610538321523726,
            "unit": "iter/sec",
            "range": "stddev: 1.0998630973955839",
            "extra": "mean: 7.929875588999998 sec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_validate",
            "value": 19.014196195358473,
            "unit": "iter/sec",
            "range": "stddev: 0.0012500776262122698",
            "extra": "mean: 52.59228366666946 msec\nrounds: 3"
          },
          {
            "name": "tests/bench.py::test_read",
            "value": 0.06418925817637752,
            "unit": "iter/sec",
            "range": "stddev: 0.39546522925798167",
            "extra": "mean: 15.578930625000007 sec\nrounds: 3"
          }
        ]
      }
    ]
  }
}
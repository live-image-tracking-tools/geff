window.BENCHMARK_DATA = {
  "lastUpdate": 1752886917359,
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
      }
    ]
  }
}
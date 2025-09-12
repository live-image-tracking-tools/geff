import numpy as np
import pytest

import geff.validate.data
from geff.testing.data import create_mock_geff, create_simple_2d_geff
from geff.validate.data import ValidationConfig, validate_data


class Test_validate_data:
    store, memory_geff = create_simple_2d_geff()

    def test_valid_graph(self):
        # test valid
        validate_data(self.memory_geff, ValidationConfig(graph=True))

    def test_nodes_for_edges(self, monkeypatch):
        # error on validate_nodes_for_edges
        monkeypatch.setattr(
            geff.validate.data, "validate_nodes_for_edges", lambda node_ids, edge_ids: (False, [])
        )
        with pytest.raises(ValueError, match="Some edges are missing nodes"):
            validate_data(self.memory_geff, ValidationConfig(graph=True))

    def test_no_self_edges(self, monkeypatch):
        monkeypatch.setattr(
            geff.validate.data, "validate_no_self_edges", lambda edge_ids: (False, [])
        )
        with pytest.raises(ValueError, match="Self edges found in data"):
            validate_data(self.memory_geff, ValidationConfig(graph=True))

    def test_no_repeated_edges(self, monkeypatch):
        monkeypatch.setattr(
            geff.validate.data, "validate_no_repeated_edges", lambda edge_ids: (False, [])
        )
        with pytest.raises(ValueError, match="Repeated edges found in data"):
            validate_data(self.memory_geff, ValidationConfig(graph=True))

    def test_unique_node_ids(self, monkeypatch):
        monkeypatch.setattr(
            geff.validate.data, "validate_unique_node_ids", lambda node_ids: (False, [])
        )
        with pytest.raises(ValueError, match="Some node ids are not unique"):
            validate_data(self.memory_geff, ValidationConfig(graph=True))

    def test_sphere(self):
        # Invalid spheres are tested in test_shapes
        # Only need to test a valid case
        _, memory_geff = create_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=True,
            num_nodes=10,
            num_edges=10,
            extra_node_props={"radius": "int"},
            include_t=True,
            include_z=False,  # 2D only
            include_y=True,
            include_x=True,
        )
        # Add sphere metadata
        memory_geff["metadata"].sphere = "radius"

        validate_data(config=ValidationConfig(sphere=True), memory_geff=memory_geff)

    def test_ellipsoid(self):
        # Invalid ellipsoids are tested in test_shapes
        # Only need to test a valid case
        _, memory_geff = create_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=True,
            num_nodes=10,
            num_edges=10,
            extra_node_props={"covariance2d": "float64"},
            include_t=True,
            include_z=False,  # 2D only
            include_y=True,
            include_x=True,
        )
        # Add ellipsoid metadata
        memory_geff["metadata"].ellipsoid = "covariance2d"
        # Overwrite ellipsoid values
        covar = np.ones((10, 2, 2))
        covar[:, 0, 0] = 2
        covar[:, 1, 1] = 2
        memory_geff["node_props"]["covariance2d"]["values"] = covar

        validate_data(config=ValidationConfig(ellipsoid=True), memory_geff=memory_geff)

    def test_tracklet(self, monkeypatch):
        # validate_tracklets is tested in test_graph
        # Just need to trigger the value error
        _, memory_geff = create_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=True,
            num_nodes=10,
            num_edges=10,
            extra_node_props={"tracklet": "int"},
            include_t=True,
            include_z=False,  # 2D only
            include_y=True,
            include_x=True,
        )
        # Add tracklet metadata
        memory_geff["metadata"].track_node_props = {"tracklet": "tracklet"}

        # Monkeypatch validate tracklets to return false
        monkeypatch.setattr(geff.validate.data, "validate_tracklets", lambda x, y, z: (False, []))

        with pytest.raises(ValueError, match="Found invalid tracklets"):
            validate_data(config=ValidationConfig(tracklet=True), memory_geff=memory_geff)

    def test_lineages(self, monkeypatch):
        # validate_lineages is tested in test_graph
        # Just need to trigger the value error
        _, memory_geff = create_mock_geff(
            node_id_dtype="int",
            node_axis_dtypes={"position": "float64", "time": "float64"},
            directed=True,
            num_nodes=10,
            num_edges=10,
            extra_node_props={"lineage": "int"},
            include_t=True,
            include_z=False,  # 2D only
            include_y=True,
            include_x=True,
        )
        # Add tracklet metadata
        memory_geff["metadata"].track_node_props = {"lineage": "lineage"}

        # Monkeypatch validate tracklets to return false
        monkeypatch.setattr(geff.validate.data, "validate_lineages", lambda x, y, z: (False, []))

        with pytest.raises(ValueError, match="Found invalid lineages"):
            validate_data(config=ValidationConfig(lineage=True), memory_geff=memory_geff)

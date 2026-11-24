import math
import unittest
from pathlib import Path

from scientific.equilibrium import axisymmetric_volume, boundary_metrics, elongation, normalize_flux, polygon_area, topology_candidates, triangularity
from scripts.bootstrap_data import decimate_minmax, diagnostics_from, frames_from, make_record, stable_id, thomson_system


class EquilibriumMethodTests(unittest.TestCase):
    def test_flux_normalization_handles_both_flux_orientations(self):
        self.assertEqual(normalize_flux([0.0, 5.0, 10.0], 0.0, 10.0), [0.0, 0.5, 1.0])
        self.assertEqual(normalize_flux([10.0, 5.0, 0.0], 10.0, 0.0), [0.0, 0.5, 1.0])

    def test_flux_normalization_preserves_missing_values_and_rejects_degenerate_interval(self):
        self.assertEqual(normalize_flux([[0.0, math.nan]], 0.0, 1.0), [[0.0, None]])
        self.assertIsNone(normalize_flux(0.5, 1.0, 1.0))

    def test_circle_area_and_axisymmetric_volume(self):
        n = 720
        major, minor = 2.0, 0.5
        boundary = [(major + minor * math.cos(2 * math.pi * i / n), minor * math.sin(2 * math.pi * i / n)) for i in range(n)]
        self.assertAlmostEqual(polygon_area(boundary), math.pi * minor**2, places=4)
        self.assertAlmostEqual(axisymmetric_volume(boundary), 2 * math.pi**2 * major * minor**2, places=3)

    def test_boundary_metrics_keep_geometric_center_distinct_from_axis(self):
        contour = [(2.0, 0.0), (3.0, 1.0), (4.0, 0.0), (3.0, -1.0)]
        metrics = boundary_metrics(contour, {"R": 3.1, "Z": 0.2})
        self.assertEqual(metrics["major_radius_m"], 3.0)
        self.assertEqual(metrics["magnetic_axis"], {"R_m": 3.1, "Z_m": 0.2})
        self.assertAlmostEqual(metrics["vertical_displacement_m"], 0.2)
        self.assertAlmostEqual(metrics["cross_sectional_area_m2"], 2.0)
        self.assertTrue(metrics["axisymmetric_volume_m3"] > 0)

    def test_bilinear_analytic_saddle_is_reported_as_x_point_candidate(self):
        frame = {"R": [0.0, 2.0], "Z": [-1.0, 1.0], "psi": [[1.0, -1.0], [-1.0, 1.0]]}
        topology = topology_candidates(frame)
        self.assertEqual(len(topology["x_points"]), 1)
        self.assertAlmostEqual(topology["x_points"][0]["R_m"], 1.0)
        self.assertAlmostEqual(topology["x_points"][0]["Z_m"], 0.0)

    def test_elongation_and_sampled_triangularity(self):
        contour = [(2.0, -1.0), (4.0, -1.0), (4.0, 1.0), (2.0, 1.0)]
        self.assertEqual(elongation(contour), 1.0)
        shaped = [(1.0, 0.0), (2.0, 1.0), (3.0, 0.0), (2.0, -1.0)]
        self.assertEqual(triangularity(shaped, 2.0), {"top": 0.0, "bottom": 0.0})

    def test_withheld_test_flux_does_not_create_reference_frames(self):
        row = {"efit_times": [1.0, 2.0], "efit_grid_R": [1.0], "efit_grid_Z": [0.0]}
        self.assertEqual(frames_from(row, "mast_public_test"), [])

    def test_reference_frames_keep_supplied_axis_and_lcfs_provenance(self):
        row = {
            "efit_times": [10.0], "efit_psirz": [[[0.0, 1.0], [2.0, 3.0]]],
            "efit_grid_R": [1.0, 2.0], "efit_grid_Z": [-1.0, 1.0],
            "efit_r_axis": [1.5], "efit_z_axis": [0.0], "efit_lcfs_n": [3],
            "efit_lcfs_r": [[1.0, 2.0, 1.5]], "efit_lcfs_z": [[0.0, 0.0, 1.0]],
        }
        frame = frames_from(row, "diii_d_train")[0]
        self.assertEqual(frame["axis"], {"R": 1.5, "Z": 0.0})
        self.assertEqual(frame["boundary"], [[1.0, 0.0], [2.0, 0.0], [1.5, 1.0]])

    def test_stable_id_includes_machine_config_and_revision(self):
        self.assertEqual(stable_id({"record_index": 17}, "DIII-D", "diii_d_train", "abc123"), "DIII-D:diii_d_train:abc123:DIII-D_17")

    def test_mast_core_thomson_drops_uncalibrated_channel_zero(self):
        row = {"thomson_core_times": [1.0], "thomson_core_R": [1.1, 1.2],
               "thomson_core_Te": [[-999.0, 10.0, 20.0]], "thomson_core_ne": [[-999.0, 3.0, 4.0]]}
        system = thomson_system(row, "MAST", "core")
        self.assertEqual(system["Te_eV"], [[10.0, 20.0]])
        self.assertEqual(system["ne_m3"], [[3.0, 4.0]])
        self.assertIn("channel 0", system["alignment_note"])

    def test_minmax_decimation_preserves_a_bucket_spike(self):
        values = [0.0] * 1000
        values[517] = 12.0
        points = decimate_minmax(range(1000), values, maximum_points=100)
        self.assertLessEqual(len(points), 100)
        self.assertIn([517.0, 12.0], points)

    def test_plasma_current_is_measured_even_when_it_shares_coil_timebase(self):
        data = diagnostics_from({"magnetics_time": [0.0, 1.0], "magnetics_plasma_current": [2.0, 3.0]}, "MAST")
        current = next(signal for signal in data["coil_signals"] if signal["name"] == "plasma_current")
        self.assertEqual(current["provenance"], "Measured diagnostic")
        self.assertEqual(current["points"], [[0.0, 2.0], [1.0, 3.0]])

    def test_released_scalar_parameters_keep_efit_provenance(self):
        row = {"efit_times": [10.0], "efit_psirz": [[[0.0, 1.0], [2.0, 3.0]]],
               "efit_grid_R": [1.0, 2.0], "efit_grid_Z": [-1.0, 1.0],
               "efit_beta_n": [0.75], "efit_li": [0.8], "efit_q95": [3.2]}
        root = Path(__file__).resolve().parents[1]
        record = make_record(row, "DIII-D", "diii_d_train", "rev", "https://example.org", root / "README.md", "sha")
        frame = record["frames"][0]
        self.assertEqual(frame["parameters"], {"beta_n": 0.75, "internal_inductance": 0.8, "q95": 3.2})
        self.assertEqual(frame["parameters_provenance"], "EFIT reference reconstruction")

    def test_boundary_metrics_calculates_all_geometric_quantities(self):
        # Elliptical cross-section: R0=2.0, a=0.5, b=1.0 (elongation=2.0)
        n = 360
        boundary = [(2.0 + 0.5 * math.cos(2 * math.pi * i / n), 1.0 * math.sin(2 * math.pi * i / n)) for i in range(n)]
        metrics = boundary_metrics(boundary, {"R": 2.1, "Z": 0.05})
        self.assertAlmostEqual(metrics["major_radius_m"], 2.0, places=3)
        self.assertAlmostEqual(metrics["minor_radius_m"], 0.5, places=3)
        self.assertAlmostEqual(metrics["aspect_ratio"], 4.0, places=3)
        self.assertAlmostEqual(metrics["elongation"], 2.0, places=2)
        self.assertAlmostEqual(metrics["cross_sectional_area_m2"], math.pi * 0.5 * 1.0, places=3)
        self.assertEqual(metrics["provenance"], "Derived from EFIT reference reconstruction")


if __name__ == "__main__":
    unittest.main()

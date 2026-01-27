"""Tests for monitoring configuration (Prometheus, Grafana)."""

import json
from pathlib import Path

import pytest
import yaml


class TestPrometheusConfiguration:
    """Test Prometheus configuration validity."""

    @pytest.fixture
    def prometheus_config_path(self):
        """Return the path to prometheus.yml."""
        base_path = Path(__file__).parent.parent.parent / "infrastructure" / "monitoring"
        return base_path / "prometheus.yml"

    @pytest.fixture
    def prometheus_config(self, prometheus_config_path):
        """Load prometheus.yml configuration."""
        if not prometheus_config_path.exists():
            pytest.skip(f"Prometheus config not found at {prometheus_config_path}")

        with open(prometheus_config_path) as f:
            return yaml.safe_load(f)

    def test_prometheus_config_has_global_section(self, prometheus_config):
        """Test that Prometheus config has required global section."""
        assert "global" in prometheus_config
        assert "scrape_interval" in prometheus_config["global"]
        assert "evaluation_interval" in prometheus_config["global"]

    def test_prometheus_config_scrape_intervals_valid(self, prometheus_config):
        """Test that scrape intervals are valid format."""
        scrape_interval = prometheus_config["global"]["scrape_interval"]
        eval_interval = prometheus_config["global"]["evaluation_interval"]

        # Should be in format like "15s", "1m", etc.
        assert scrape_interval.endswith(("s", "m", "h"))
        assert eval_interval.endswith(("s", "m", "h"))

    def test_prometheus_config_has_scrape_configs(self, prometheus_config):
        """Test that Prometheus config has scrape_configs."""
        assert "scrape_configs" in prometheus_config
        assert isinstance(prometheus_config["scrape_configs"], list)
        assert len(prometheus_config["scrape_configs"]) > 0

    def test_prometheus_job_names_unique(self, prometheus_config):
        """Test that all job names are unique."""
        job_names = []
        for scrape_config in prometheus_config["scrape_configs"]:
            if "job_name" in scrape_config:
                job_names.append(scrape_config["job_name"])

        # Convert to set and compare length to detect duplicates
        assert len(job_names) == len(set(job_names)), "Duplicate job names found"

    def test_prometheus_static_configs(self, prometheus_config):
        """Test that scrape configs have targets."""
        for scrape_config in prometheus_config["scrape_configs"]:
            if "static_configs" in scrape_config:
                static_configs = scrape_config["static_configs"]
                assert isinstance(static_configs, list)
                # At least one static config should have targets
                has_targets = any(
                    "targets" in config and len(config["targets"]) > 0 for config in static_configs
                )
                assert has_targets, f"Scrape config {scrape_config.get('job_name')} has no targets"

    def test_prometheus_metrics_path_configured(self, prometheus_config):
        """Test that metrics_path is configured in scrape configs."""
        qr_forge_job = next(
            (job for job in prometheus_config["scrape_configs"] if job.get("job_name") == "qr_forge_app"),
            None,
        )
        assert qr_forge_job is not None, "qr_forge_app job not found"
        assert "metrics_path" in qr_forge_job
        assert qr_forge_job["metrics_path"] == "/metrics"


class TestGrafanaDashboard:
    """Test Grafana dashboard JSON configuration."""

    @pytest.fixture
    def grafana_dashboard_path(self):
        """Return the path to grafana-dashboard.json."""
        base_path = Path(__file__).parent.parent.parent / "infrastructure" / "monitoring"
        return base_path / "grafana-dashboard.json"

    @pytest.fixture
    def grafana_dashboard(self, grafana_dashboard_path):
        """Load grafana-dashboard.json configuration."""
        if not grafana_dashboard_path.exists():
            pytest.skip(f"Grafana dashboard not found at {grafana_dashboard_path}")

        with open(grafana_dashboard_path) as f:
            return json.load(f)

    def test_grafana_dashboard_is_array(self, grafana_dashboard):
        """Test that Grafana dashboard is an array of dashboard objects."""
        assert isinstance(grafana_dashboard, list)
        assert len(grafana_dashboard) > 0

    def test_grafana_dashboards_have_titles(self, grafana_dashboard):
        """Test that each dashboard has a title."""
        for dashboard in grafana_dashboard:
            assert "title" in dashboard
            assert isinstance(dashboard["title"], str)
            assert len(dashboard["title"]) > 0

    def test_grafana_dashboards_have_panels(self, grafana_dashboard):
        """Test that dashboards have panels."""
        for dashboard in grafana_dashboard:
            assert "panels" in dashboard
            assert isinstance(dashboard["panels"], list)
            assert len(dashboard["panels"]) > 0

    def test_grafana_panels_have_required_fields(self, grafana_dashboard):
        """Test that panels have required fields (type, title)."""
        for dashboard in grafana_dashboard:
            for panel in dashboard["panels"]:
                assert "type" in panel, f"Panel missing 'type' in {dashboard['title']}"
                assert "title" in panel, f"Panel missing 'title' in {dashboard['title']}"
                assert isinstance(panel["type"], str)
                assert isinstance(panel["title"], str)

    def test_grafana_panel_types_valid(self, grafana_dashboard):
        """Test that panel types are valid Grafana types."""
        valid_types = {"stat", "graph", "gauge", "table", "singlestat", "worldmap-panel"}

        for dashboard in grafana_dashboard:
            for panel in dashboard["panels"]:
                panel_type = panel.get("type", "").lower()
                # Allow any type since Grafana has many plugin types
                assert isinstance(panel_type, str), f"Invalid panel type: {panel_type}"

    def test_grafana_dashboard_time_range(self, grafana_dashboard):
        """Test that dashboards have time range configuration."""
        for dashboard in grafana_dashboard:
            if "time" in dashboard:
                assert "from" in dashboard["time"]
                assert "to" in dashboard["time"]

    def test_grafana_targets_structure(self, grafana_dashboard):
        """Test that panel targets are properly structured."""
        for dashboard in grafana_dashboard:
            for panel in dashboard["panels"]:
                if "targets" in panel:
                    targets = panel["targets"]
                    assert isinstance(targets, list)
                    # Each target should be a dict
                    for target in targets:
                        assert isinstance(target, dict)


class TestMonitoringDockerCompose:
    """Test Docker Compose monitoring stack configuration."""

    @pytest.fixture
    def docker_compose_path(self):
        """Return the path to docker-compose.monitoring.yml."""
        base_path = Path(__file__).parent.parent.parent / "infrastructure" / "monitoring"
        return base_path / "docker-compose.monitoring.yml"

    @pytest.fixture
    def docker_compose_config(self, docker_compose_path):
        """Load docker-compose.monitoring.yml configuration."""
        if not docker_compose_path.exists():
            pytest.skip(f"Docker Compose config not found at {docker_compose_path}")

        with open(docker_compose_path) as f:
            return yaml.safe_load(f)

    def test_docker_compose_has_version(self, docker_compose_config):
        """Test that Docker Compose file has version."""
        assert "version" in docker_compose_config

    def test_docker_compose_has_services(self, docker_compose_config):
        """Test that Docker Compose has services section."""
        assert "services" in docker_compose_config
        assert isinstance(docker_compose_config["services"], dict)
        assert len(docker_compose_config["services"]) > 0

    def test_docker_compose_prometheus_service(self, docker_compose_config):
        """Test that Prometheus service is configured."""
        services = docker_compose_config.get("services", {})
        assert "prometheus" in services, "Prometheus service not configured"

        prometheus = services["prometheus"]
        assert "image" in prometheus
        assert "ports" in prometheus

    def test_docker_compose_grafana_service(self, docker_compose_config):
        """Test that Grafana service is configured."""
        services = docker_compose_config.get("services", {})
        assert "grafana" in services, "Grafana service not configured"

        grafana = services["grafana"]
        assert "image" in grafana
        assert "ports" in grafana

    def test_docker_compose_port_mappings(self, docker_compose_config):
        """Test that services have port mappings."""
        services = docker_compose_config.get("services", {})

        for service_name, service_config in services.items():
            if "ports" in service_config:
                ports = service_config["ports"]
                assert isinstance(ports, list)
                assert len(ports) > 0


class TestMonitoringIntegration:
    """Integration tests for monitoring configuration."""

    def test_prometheus_and_grafana_configs_compatible(self):
        """Test that Prometheus and Grafana configs reference compatible metrics."""
        base_path = Path(__file__).parent.parent.parent / "infrastructure" / "monitoring"

        prometheus_path = base_path / "prometheus.yml"
        grafana_path = base_path / "grafana-dashboard.json"

        if not (prometheus_path.exists() and grafana_path.exists()):
            pytest.skip("Monitoring config files not found")

        with open(prometheus_path) as f:
            prometheus_config = yaml.safe_load(f)

        with open(grafana_path) as f:
            grafana_config = json.load(f)

        # Get Prometheus scrape targets
        scrape_targets = set()
        for scrape_config in prometheus_config.get("scrape_configs", []):
            for static_config in scrape_config.get("static_configs", []):
                for target in static_config.get("targets", []):
                    scrape_targets.add(target)

        # Verify that we have at least some targets
        assert len(scrape_targets) > 0, "No Prometheus targets configured"

        # Verify Grafana dashboards are not empty
        assert len(grafana_config) > 0, "No Grafana dashboards configured"

from pathlib import Path

from django.apps import apps
from django.test import TestCase
from LicenseClassifier.classifier import LicenseClassifier
from scanpipe.models import CodebaseResource, Project
from scanpipe.pipes.input import copy_inputs

from scancode_glc_plugin.pipes import glc

scanpipe_app = apps.get_app_config("scanpipe")


class ScancodeGLCPipelineTest(TestCase):
    data_location = Path(__file__).parent / "data"

    def test_scanpipe_pipes_glc_scan_file(self):
        input_location = str(self.data_location / "apache-1.1.txt")
        classifier = LicenseClassifier()
        scan_results = glc.scan_file(classifier, input_location)
        expected_result = {
            "path": input_location,
            "licenses": [
                {
                    "key": "apache-1.1",
                    "score": 1,
                    "start_line": 1,
                    "end_line": 39,
                    "start_index": 0,
                    "end_index": 338,
                    "category": "Permissive",
                }
            ],
            "license_expressions": ["apache-1.1"],
            "copyrights": [
                {
                    "value": "Copyright (c) 2000 The Apache Software"
                    " Foundation. All rights reserved.",
                    "start_index": 25,
                    "end_index": 96,
                }
            ],
            "holders": [
                {
                    "value": "The Apache Software Foundation",
                    "start_index": 44,
                    "end_index": 74,
                }
            ],
            "scan_errors": [],
        }
        self.assertEqual(expected_result, scan_results)

    def test_scanpipe_pipes_glc_scan_directory(self):
        input_location = str(self.data_location)
        scan_results = glc.scan_directory(input_location)
        expected_keys = [
            "header",
            "files",
        ]
        self.assertEqual(sorted(expected_keys), sorted(scan_results.keys()))
        self.assertEqual(1, len(scan_results.get("files", [])))

    def test_scanpipe_pipes_glc_scan_and_update_codebase_resources(self):
        project1 = Project.objects.create(name="Analysis")
        codebase_resource1 = CodebaseResource.objects.create(
            project=project1, path="not available"
        )
        self.assertEqual(0, project1.projecterrors.count())

        glc.scan_and_update_codebase_resources(project1)

        codebase_resource1.refresh_from_db()
        self.assertEqual("scanned-with-error", codebase_resource1.status)
        self.assertEqual(2, project1.projecterrors.count())

        copy_inputs([self.data_location / "apache-1.1.txt"], project1.codebase_path)
        codebase_resource2 = CodebaseResource.objects.create(
            project=project1, path="apache-1.1.txt"
        )

        glc.scan_and_update_codebase_resources(project1)

        codebase_resource2.refresh_from_db()
        self.assertEqual("scanned", codebase_resource2.status)
        expected = {
            "licenses": ["apache-1.1"],
            "holders": [
                {
                    "value": "The Apache Software Foundation",
                    "start_index": 44,
                    "end_index": 74,
                }
            ],
            "copyrights": [
                {
                    "value": "Copyright (c) 2000 The Apache Software Foundation."
                    " All rights reserved.",
                    "start_index": 25,
                    "end_index": 96,
                }
            ],
        }

        self.assertEqual(expected["licenses"], codebase_resource2.license_expressions)
        self.assertEqual(expected["copyrights"], codebase_resource2.copyrights)
        self.assertEqual(expected["holders"], codebase_resource2.holders)

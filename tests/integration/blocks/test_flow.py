# OpenCodeBlock an open-source tool for modular visual programing in python
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""
Integration tests for the execution flow.
"""

import pytest
import time

from opencodeblocks.blocks.codeblock import OCBCodeBlock

from tests.integration.utils import apply_function_inapp, CheckingQueue, start_app


class TestCodeBlocks:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup reused variables."""
        start_app(self)

        self.ocb_widget.scene.load("tests/assets/flow_test.ipyg")

        self.titles = [
            "Test flow 5",
            "Test flow 4",
            "Test no connection 1",
            "Test input only 2",
            "Test output only 1",
        ]
        self.blocks_to_run = [None] * 5
        for item in self.ocb_widget.scene.items():
            if isinstance(item, OCBCodeBlock):
                if item.title in self.titles:
                    self.blocks_to_run[self.titles.index(item.title)] = item

    def test_duplicated_run(self):
        """Don't run a block twice when the execution flows"""
        for b in self.blocks_to_run:
            b.stdout = ""

        def testing_no_duplicates(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[0]

            def run_block():
                block_to_run.run_right()

            msgQueue.run_lambda(run_block)
            time.sleep((block_to_run.transmitting_duration / 1000) + 0.2)
            while block_to_run.run_color != 0:
                time.sleep(0.1)

            # 6 and not 6\n6
            msgQueue.check_equal(block_to_run.stdout.strip(), "6")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_no_duplicates)

    def test_flow_left(self):
        """Correct flow when pressing left run"""

        for b in self.blocks_to_run:
            b.stdout = ""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[0]
            block_to_not_run: OCBCodeBlock = self.blocks_to_run[1]

            def run_block():
                block_to_run.run_left()

            msgQueue.run_lambda(run_block)
            time.sleep((block_to_run.transmitting_duration / 1000) + 0.2)
            while block_to_run.run_color != 0:
                time.sleep(0.1)

            msgQueue.check_equal(block_to_run.stdout.strip(), "6")
            msgQueue.check_equal(block_to_not_run.stdout.strip(), "")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_no_connection_left(self):
        """run block only when no previous connection."""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test no connection 1")
            ]

            def run_block():
                block_to_run.run_left()

            print("About to run !")

            msgQueue.run_lambda(run_block)
            time.sleep((block_to_run.transmitting_duration / 1000) + 0.2)
            while block_to_run.run_color != 0:
                time.sleep(0.1)

            msgQueue.check_equal(block_to_run.stdout.strip(), "1")
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_no_connection_right(self):
        """run block only when no next connection."""

        def testing_run(msgQueue: CheckingQueue):

            block_to_run: OCBCodeBlock = self.blocks_to_run[
                self.titles.index("Test no connection 1")
            ]

            def run_block():
                block_to_run.run_right()

            msgQueue.run_lambda(run_block)
            time.sleep((block_to_run.transmitting_duration / 1000) + 0.2)
            while block_to_run.run_color != 0:
                time.sleep(0.1)

            # Just check that it doesn't crash
            msgQueue.stop()

        apply_function_inapp(self.window, testing_run)

    def test_finish(self):
        self.window.close()

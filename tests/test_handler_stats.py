# Copyright 2020 MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import re
import unittest
from io import StringIO

from ignite.engine import Engine, Events

from monai.handlers.stats_handler import StatsHandler


class TestHandlerStats(unittest.TestCase):

    def test_metrics_print(self):
        log_stream = StringIO()
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        key_to_handler = 'test_logging'
        key_to_print = 'testing_metric'

        # set up engine
        def _train_func(engine, batch):
            pass

        engine = Engine(_train_func)

        # set up dummy metric
        @engine.on(Events.ITERATION_COMPLETED)
        def _update_metric(engine):
            current_metric = engine.state.metrics.get(key_to_print, 0.1)
            engine.state.metrics[key_to_print] = current_metric + 0.1

        # set up testing handler
        stats_handler = StatsHandler(name=key_to_handler)
        stats_handler.attach(engine)

        engine.run(range(3), max_epochs=2)

        # check logging output
        output_str = log_stream.getvalue()
        grep = re.compile('.*{}.*'.format(key_to_handler))
        has_key_word = re.compile('.*{}.*'.format(key_to_print))
        matched = []
        for idx, line in enumerate(output_str.split('\n')):
            if grep.match(line):
                self.assertTrue(has_key_word.match(line))
                matched.append(idx)
        self.assertEqual(matched, [1, 2, 3, 5, 6, 7, 8, 10])


if __name__ == '__main__':
    unittest.main()

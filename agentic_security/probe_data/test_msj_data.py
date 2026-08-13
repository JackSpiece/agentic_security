from unittest.mock import call, patch

from agentic_security.probe_data.msj_data import (
    ProbeDataset,
    load_dataset_generic,
    prepare_prompts,
)


class TestProbeDataset:
    def test_metadata_summary(self):
        dataset = ProbeDataset(
            dataset_name="test_dataset",
            metadata={"key": "value"},
            prompts=["prompt1", "prompt2"],
            tokens=100,
            approx_cost=0.5,
        )

        expected_summary = {
            "dataset_name": "test_dataset",
            "num_prompts": 2,
            "tokens": 100,
            "approx_cost": 0.5,
        }

        assert dataset.metadata_summary() == expected_summary


class TestLoadDatasetGeneric:
    @patch("datasets.load_dataset")
    def test_load_dataset_success(self, mock_load_dataset):
        mock_load_dataset.return_value = {
            "train": {"prompt": ["test prompt 1", "test prompt 2"]}
        }

        result = load_dataset_generic("test/dataset")

        assert isinstance(result, ProbeDataset)
        assert result.dataset_name == "test/dataset"
        assert result.prompts == ["test prompt 1", "test prompt 2"]

    @patch("datasets.load_dataset")
    def test_load_dataset_custom_getter(self, mock_load_dataset):
        mock_load_dataset.return_value = {
            "validation": {"text": ["custom text 1", "custom text 2"]}
        }

        result = load_dataset_generic(
            "test/dataset", getter=lambda dataset: dataset["validation"]["text"]
        )

        assert result.prompts == ["custom text 1", "custom text 2"]


class TestPreparePrompts:
    @staticmethod
    def _dataset(name):
        return ProbeDataset(
            dataset_name=name,
            metadata={},
            prompts=[f"prompt from {name}"],
            tokens=0,
            approx_cost=0.0,
        )

    @patch("agentic_security.probe_data.msj_data.load_dataset_generic")
    def test_empty_dataset_names_loads_built_in_defaults(
        self, mock_load_dataset_generic
    ):
        mock_load_dataset_generic.side_effect = self._dataset

        result = prepare_prompts(dataset_names=[])

        assert [dataset.dataset_name for dataset in result] == [
            "data-is-better-together/10k_prompts_ranked",
            "fka/awesome-chatgpt-prompts",
        ]
        assert mock_load_dataset_generic.call_args_list == [
            call("data-is-better-together/10k_prompts_ranked"),
            call("fka/awesome-chatgpt-prompts"),
        ]

    @patch("agentic_security.probe_data.msj_data.load_dataset_generic")
    def test_loads_only_requested_known_datasets(self, mock_load_dataset_generic):
        first = "fka/awesome-chatgpt-prompts"
        second = "data-is-better-together/10k_prompts_ranked"
        mock_load_dataset_generic.side_effect = self._dataset

        result = prepare_prompts(dataset_names=[first, second])

        assert [dataset.dataset_name for dataset in result] == [first, second]
        assert mock_load_dataset_generic.call_args_list == [call(first), call(second)]

    @patch("agentic_security.probe_data.msj_data.load_dataset_generic")
    def test_honors_selection_flags_and_ignores_unknown_datasets(
        self, mock_load_dataset_generic
    ):
        selected = "fka/awesome-chatgpt-prompts"
        mock_load_dataset_generic.side_effect = self._dataset

        result = prepare_prompts(
            dataset_names=[
                {
                    "dataset_name": "data-is-better-together/10k_prompts_ranked",
                    "selected": False,
                },
                {"dataset_name": selected, "selected": True},
                {"dataset_name": "unknown/dataset", "selected": True},
            ]
        )

        assert [dataset.dataset_name for dataset in result] == [selected]
        mock_load_dataset_generic.assert_called_once_with(selected)

    @patch("agentic_security.probe_data.msj_data.load_dataset_generic")
    def test_deduplicates_selected_datasets(self, mock_load_dataset_generic):
        selected = "fka/awesome-chatgpt-prompts"
        mock_load_dataset_generic.side_effect = self._dataset

        result = prepare_prompts(dataset_names=[selected, selected])

        assert [dataset.dataset_name for dataset in result] == [selected]
        mock_load_dataset_generic.assert_called_once_with(selected)

from dataclasses import dataclass

from cache_to_disk import cache_to_disk  # noqa


# TODO: refactor this class to use from .data
@dataclass
class ProbeDataset:
    dataset_name: str
    metadata: dict
    prompts: list[str]
    tokens: int
    approx_cost: float
    lazy: bool = False

    def metadata_summary(self):
        return {
            "dataset_name": self.dataset_name,
            "num_prompts": len(self.prompts),
            "tokens": self.tokens,
            "approx_cost": self.approx_cost,
        }


# @cache_to_disk(n_days_to_cache=1)
def load_dataset_generic(name, getter=lambda x: x["train"]["prompt"]):
    from datasets import load_dataset

    dataset = load_dataset(name)
    mjs_prompts = getter(dataset)
    return ProbeDataset(
        dataset_name=name,
        metadata={},
        prompts=mjs_prompts,
        tokens=0,
        approx_cost=0.0,
    )


SUPPORTED_DATASETS = (
    "data-is-better-together/10k_prompts_ranked",
    "fka/awesome-chatgpt-prompts",
)


def prepare_prompts(
    dataset_names: list[str | dict] | None = None,
    budget: int = -1,
    tools_inbox=None,
) -> list[ProbeDataset]:
    """Load supported many-shot datasets selected by the caller.

    An omitted or empty selection preserves the historical default of loading
    both built-in datasets. A non-empty selection loads only entries explicitly
    selected by the caller.
    """
    selected_names: list[str] = []
    if not dataset_names:
        selected_names.extend(SUPPORTED_DATASETS)
    else:
        for dataset in dataset_names:
            if isinstance(dataset, str):
                selected_names.append(dataset)
            elif dataset.get("selected") and dataset.get("dataset_name"):
                selected_names.append(dataset["dataset_name"])

    # Preserve caller order while avoiding duplicate network loads.
    selected_names = list(dict.fromkeys(selected_names))
    return [
        load_dataset_generic(name)
        for name in selected_names
        if name in SUPPORTED_DATASETS
    ]

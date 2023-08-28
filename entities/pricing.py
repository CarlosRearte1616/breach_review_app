from .model import Model


class Pricing:
    COST_PER_1000_TOKENS = {
        Model.GPT3_5_TURBO: 0.0015,
        Model.GPT3_5_TURBO_0613: 0.0015,
        Model.GPT3_5_TURBO_16_K: 0.004,
        Model.GPT3_5_TURBO_AZURE_16K: 0.003,
        Model.GPT4: 0.03  # hypothetical cost for gpt-4
    }

    @staticmethod
    def calculate_cost(model, tokens):
        cost_per_token = Pricing.COST_PER_1000_TOKENS[model] / 1000
        return cost_per_token * tokens
